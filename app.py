import os
import io
import secrets
import hashlib
from datetime import datetime, timedelta, timezone

from flask import Flask, request, redirect, url_for, render_template_string, session, send_file, jsonify, abort
from werkzeug.utils import secure_filename
from PIL import Image
from cryptography.fernet import Fernet
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from bson import ObjectId
import bcrypt
from dotenv import load_dotenv

load_dotenv()

# config
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
MONGO_URI = os.environ.get("MONGO_URI") or "mongodb://localhost:27017/"
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or secrets.token_urlsafe(16)
FERNET_KEY_ENV = os.environ.get("FERNET_KEY")
VIEW_SECONDS = int(os.environ.get("VIEW_SECONDS", "10"))

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# Generate or validate Fernet key
try:
    if FERNET_KEY_ENV and FERNET_KEY_ENV != "your-generated-key-here":
        # Try to use the provided key
        fernet = Fernet(FERNET_KEY_ENV.encode())
        FERNET_KEY = FERNET_KEY_ENV
    else:
        # Generate a new key
        FERNET_KEY = Fernet.generate_key().decode()
        fernet = Fernet(FERNET_KEY.encode())
        print("⚠️  Generated new FERNET_KEY (not set in .env or invalid)")
        print(f"   Add this to your .env file: FERNET_KEY={FERNET_KEY}")
except (ValueError, Exception):
    # Invalid key, generate a new one
    FERNET_KEY = Fernet.generate_key().decode()
    fernet = Fernet(FERNET_KEY.encode())
    print("⚠️  Invalid FERNET_KEY in .env, generated a new one")
    print(f"   Add this to your .env file: FERNET_KEY={FERNET_KEY}")

# mongo - with timeout settings
try:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,  # 5 second timeout
        connectTimeoutMS=5000,
        socketTimeoutMS=20000
    )
    # Test the connection
    client.admin.command('ping')
    db = client["secAppDB"]
    users = db.get_collection("users")
    messages = db.get_collection("messages")
    pairings = db.get_collection("pairings")
    print("✓ MongoDB connection successful")
except (ServerSelectionTimeoutError, ConnectionFailure) as e:
    print(f"✗ MongoDB connection failed: {e}")
    print(f"  Make sure MongoDB is running at {MONGO_URI}")
    print(f"  On Windows, start it with: net start MongoDB")
    print(f"  Or install MongoDB and start the service")
    client = None
    db = None
    users = None
    messages = None
    pairings = None

def get_db_error_msg():
    return "Database connection error. Please ensure MongoDB is running.", 503

# ---------- simple auth helpers ----------
def current_user():
    uid = session.get("user_id")
    if not uid or users is None:
        return None
    try:
        return users.find_one({"_id": uid})
    except (ServerSelectionTimeoutError, ConnectionFailure):
        return None

# ---------- stego helpers (LSB RGB) ----------
def _bytes_to_bits(b: bytes):
    for byte in b:
        for i in range(8):
            yield (byte >> (7 - i)) & 1

def embed_bytes_in_image(img: Image.Image, payload: bytes) -> Image.Image:
    if len(payload) > 2000*10:  # crude safety
        raise ValueError("Payload too large")
    length_prefix = len(payload).to_bytes(4, "big")
    data = length_prefix + payload
    bits = list(_bytes_to_bits(data))
    rgba_img = img.convert("RGBA")
    pixels = list(rgba_img.getdata())  # type: ignore
    new_pixels = []
    bit_idx = 0
    for px in pixels:
        r,g,b,a = px
        if bit_idx < len(bits):
            r = (r & ~1) | bits[bit_idx]; bit_idx += 1
        if bit_idx < len(bits):
            g = (g & ~1) | bits[bit_idx]; bit_idx += 1
        if bit_idx < len(bits):
            b = (b & ~1) | bits[bit_idx]; bit_idx += 1
        new_pixels.append((r,g,b,a))
    if bit_idx < len(bits):
        raise ValueError("Image too small to hold payload")
    out = Image.new("RGBA", img.size)
    out.putdata(new_pixels)
    return out

def extract_bytes_from_image(img: Image.Image) -> bytes:
    rgba_img = img.convert("RGBA")
    pixels = list(rgba_img.getdata())  # type: ignore
    bits = []
    for px in pixels:
        r,g,b,a = px
        bits.append(r & 1)
        bits.append(g & 1)
        bits.append(b & 1)
    if len(bits) < 32:
        return b""
    length = 0
    for bit in bits[:32]:
        length = (length << 1) | bit
    total_bits_needed = 32 + length*8
    if total_bits_needed > len(bits):
        raise ValueError("Incomplete payload in image")
    payload_bits = bits[32:32 + length*8]
    payload_bytes = bytearray()
    for i in range(0, len(payload_bits), 8):
        byte = 0
        for bit in payload_bits[i:i+8]:
            byte = (byte << 1) | bit
        payload_bytes.append(byte)
    return bytes(payload_bytes)

# ---------- routes ----------
INDEX_HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🔐 One-time Secret</title>
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
    min-height: 100vh;
    padding: 20px;
  }
  @keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  .container {
    max-width: 800px;
    margin: 0 auto;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    animation: slideIn 0.5s ease;
  }
  @keyframes slideIn {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  h1 {
    color: #667eea;
    text-align: center;
    margin-bottom: 10px;
    font-size: 2.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
  }
  h2 {
    color: #764ba2;
    margin: 25px 0 15px 0;
    font-size: 1.8em;
  }
  h3 {
    color: #4facfe;
    margin: 20px 0 15px 0;
    font-size: 1.4em;
  }
  .user-info {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .user-info a {
    color: white;
    text-decoration: none;
    padding: 8px 15px;
    background: rgba(255,255,255,0.2);
    border-radius: 5px;
    transition: all 0.3s;
  }
  .user-info a:hover {
    background: rgba(255,255,255,0.3);
    transform: scale(1.05);
  }
  form {
    background: #f8f9fa;
    padding: 25px;
    border-radius: 15px;
    margin: 20px 0;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  }
  label {
    display: block;
    margin: 15px 0 5px 0;
    color: #555;
    font-weight: 600;
  }
  input[type="text"], input[type="email"], input[type="password"], input[type="file"], textarea {
    width: 100%;
    padding: 12px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 16px;
    transition: all 0.3s;
    font-family: inherit;
  }
  input:focus, textarea:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  textarea {
    resize: vertical;
    min-height: 120px;
  }
  button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 15px 30px;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    margin-top: 10px;
  }
  button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
  }
  button:active {
    transform: translateY(0);
  }
  .nav-links {
    text-align: center;
    margin: 30px 0;
  }
  .nav-links a {
    display: inline-block;
    margin: 0 15px;
    padding: 12px 25px;
    background: linear-gradient(135deg, #4facfe, #00f2fe);
    color: white;
    text-decoration: none;
    border-radius: 25px;
    font-weight: 600;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
  }
  .nav-links a:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 6px 20px rgba(79, 172, 254, 0.6);
  }
  .inbox {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 15px;
    margin-top: 20px;
  }
  .inbox ul {
    list-style: none;
  }
  .inbox li {
    background: white;
    padding: 15px;
    margin: 10px 0;
    border-radius: 10px;
    border-left: 4px solid #667eea;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: all 0.3s;
  }
  .inbox li:hover {
    transform: translateX(5px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
  }
  .inbox a {
    color: #667eea;
    text-decoration: none;
    font-weight: 600;
    padding: 5px 10px;
    background: rgba(102, 126, 234, 0.1);
    border-radius: 5px;
    transition: all 0.3s;
  }
  .inbox a:hover {
    background: rgba(102, 126, 234, 0.2);
  }
  hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #667eea, transparent);
    margin: 30px 0;
  }
</style>
</head>
<body>
<div class="container">
  <h1>🔐 One-time Secret</h1>
  {% if user %}
    <div class="user-info">
      <span>✨ Logged in as <strong>{{ user['email'] }}</strong></span>
      <div>
        <strong>Your Pairing Code:</strong> <code style="background: rgba(255,255,255,0.3); padding: 5px 10px; border-radius: 5px;">{{ pairing_code }}</code>
        <a href="/logout" style="margin-left: 15px;">Logout</a>
      </div>
    </div>
    
    <h3>🤝 Manage Partners</h3>
    <div style="background: #f8f9fa; padding: 20px; border-radius: 15px; margin: 20px 0;">
      <h4 style="color: #764ba2; margin-bottom: 15px;">Request Pairing</h4>
      <form action="/pairing/request" method="post">
        <div style="margin-bottom: 15px;">
          <label>Search User by Email:</label>
          <input type="email" name="partner_email" placeholder="friend@example.com" required style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px;" />
          <small style="color: #666; display: block; margin-top: 5px;">Enter your friend's email address</small>
        </div>
        <div style="margin-bottom: 15px;">
          <label>Secret Code (e.g., "kiwi"):</label>
          <input type="text" name="secret_code" placeholder="Enter a secret code you both know" required style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px;" />
          <small style="color: #666; display: block; margin-top: 5px;">Both of you need to use the same secret code (e.g., "kiwi", "apple123")</small>
        </div>
        <button type="submit" style="width: 100%; margin-top: 0;">🔗 Send Pairing Request</button>
      </form>
      
      {% if pairing_requests %}
        <h4 style="color: #4facfe; margin: 25px 0 15px 0;">Pending Requests</h4>
        <ul style="list-style: none;">
          {% for req in pairing_requests %}
            <li style="background: white; padding: 15px; margin: 10px 0; border-radius: 10px; border-left: 4px solid #4facfe;">
              <div style="margin-bottom: 10px;">
                <strong>{{ req['from_email'] }}</strong> wants to pair with you
              </div>
              <form action="/pairing/accept/{{ req['id'] }}" method="post" style="display: flex; gap: 10px; align-items: end;">
                <div style="flex: 1;">
                  <label style="font-size: 14px; color: #555;">Enter the secret code they provided:</label>
                  <input type="text" name="secret_code" placeholder="e.g., kiwi" required style="width: 100%; padding: 8px; border: 2px solid #e0e0e0; border-radius: 5px; margin-top: 5px;" />
                </div>
                <button type="submit" style="background: #4caf50; padding: 10px 20px; margin: 0; white-space: nowrap;">✓ Accept</button>
              </form>
              <form action="/pairing/reject/{{ req['id'] }}" method="post" style="margin-top: 10px;">
                <button type="submit" style="background: #f44336; padding: 8px 15px; width: 100%;">✗ Reject</button>
              </form>
            </li>
          {% endfor %}
        </ul>
      {% endif %}
      
      {% if partners %}
        <h4 style="color: #667eea; margin: 25px 0 15px 0;">Paired Partners</h4>
        <ul style="list-style: none;">
          {% for partner in partners %}
            <li style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 12px 15px; margin: 8px 0; border-radius: 10px;">
              🤝 {{ partner.get('email', partner) }}
            </li>
          {% endfor %}
        </ul>
      {% else %}
        <p style="text-align: center; color: #999; padding: 15px; margin-top: 20px;">No partners yet. Request a pairing to get started! 👆</p>
      {% endif %}
    </div>
    
    <h3>📤 Send Secret</h3>
    {% if partners %}
      <form action="/send" method="post" enctype="multipart/form-data">
        <label>Recipient (Must be paired):</label>
        <select name="recipient" required style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px;">
          <option value="">Select a partner...</option>
          {% for partner in partners %}
            <option value="{{ partner.get('email', partner) }}">{{ partner.get('email', partner) }}</option>
          {% endfor %}
        </select>
        <label>Image (PNG recommended):</label>
        <input type="file" name="image" accept="image/*" required>
        <label>Secret Message:</label>
        <textarea name="secret" placeholder="Type your secret message here..." required></textarea>
        <button type="submit">🚀 Send Secret</button>
      </form>
    {% else %}
      <div style="background: #fff3cd; border: 2px solid #ffc107; border-radius: 10px; padding: 20px; text-align: center;">
        <p style="color: #856404; margin: 0;">⚠️ You need to pair with someone before sending messages. Request a pairing above! 👆</p>
      </div>
    {% endif %}
    <hr>
    <h3>📥 Your Inbox</h3>
    <div class="inbox">
      {% if inbox %}
        <ul>
        {% for m in inbox %}
          <li>
            <strong>From:</strong> {{ m['sender_email'] }} → <strong>You</strong><br>
            <strong>ID:</strong> {{ m['message_id'] }}<br>
            <strong>Created:</strong> {{ m['created_at'] }}<br>
            {% if m['viewed'] %}
              <span style="color: #999;">(already viewed - message deleted)</span>
            {% elif m['token'] %}
              <a href="/view/{{ m['token'] }}" style="display: inline-block; margin-top: 10px; padding: 10px 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">👁️ View Message</a>
            {% else %}
              <span style="color: #999;">(waiting for sender to share link)</span>
            {% endif %}
          </li>
        {% endfor %}
        </ul>
      {% else %}
        <p style="text-align: center; color: #999; padding: 20px;">No messages yet! 🎉</p>
      {% endif %}
    </div>
  {% else %}
    <div class="nav-links">
      <a href="/register">✨ Register</a>
      <a href="/login">🔑 Login</a>
    </div>
  {% endif %}
</div>
</body>
</html>
"""

REGISTER_HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>✨ Register - One-time Secret</title>
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  @keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  .container {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 40px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    width: 100%;
    max-width: 450px;
    animation: slideIn 0.5s ease;
  }
  @keyframes slideIn {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  h1 {
    color: #667eea;
    text-align: center;
    margin-bottom: 30px;
    font-size: 2.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
  }
  h2 {
    color: #764ba2;
    text-align: center;
    margin-bottom: 30px;
    font-size: 1.8em;
  }
  form {
    background: #f8f9fa;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  }
  label {
    display: block;
    margin: 15px 0 5px 0;
    color: #555;
    font-weight: 600;
  }
  input {
    width: 100%;
    padding: 12px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 16px;
    transition: all 0.3s;
    font-family: inherit;
  }
  input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  button {
    width: 100%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 15px;
    border: none;
    border-radius: 10px;
    font-size: 18px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    margin-top: 20px;
  }
  button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
  }
  .back-link {
    text-align: center;
    margin-top: 20px;
  }
  .back-link a {
    color: #667eea;
    text-decoration: none;
    font-weight: 600;
  }
  .back-link a:hover {
    text-decoration: underline;
  }
  .error {
    background: #fee;
    color: #c33;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
    border-left: 4px solid #c33;
  }
</style>
</head>
<body>
<div class="container">
  <h1>✨ Register</h1>
  {% if error %}
    <div class="error">{{ error }}</div>
  {% endif %}
  <form action="/register" method="post">
    <label>📧 Email:</label>
    <input type="email" name="email" placeholder="your@email.com" required>
    <label>🔒 Password:</label>
    <input type="password" name="password" placeholder="Enter a strong password" required>
    <button type="submit">🚀 Create Account</button>
  </form>
  <div class="back-link">
    <a href="/">← Back to Home</a> | <a href="/login">Already have an account? Login</a>
  </div>
</div>
</body>
</html>
"""

LOGIN_HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🔑 Login - One-time Secret</title>
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  @keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  .container {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 40px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    width: 100%;
    max-width: 450px;
    animation: slideIn 0.5s ease;
  }
  @keyframes slideIn {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  h1 {
    color: #667eea;
    text-align: center;
    margin-bottom: 30px;
    font-size: 2.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
  }
  h2 {
    color: #764ba2;
    text-align: center;
    margin-bottom: 30px;
    font-size: 1.8em;
  }
  form {
    background: #f8f9fa;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  }
  label {
    display: block;
    margin: 15px 0 5px 0;
    color: #555;
    font-weight: 600;
  }
  input {
    width: 100%;
    padding: 12px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 16px;
    transition: all 0.3s;
    font-family: inherit;
  }
  input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  button {
    width: 100%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 15px;
    border: none;
    border-radius: 10px;
    font-size: 18px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    margin-top: 20px;
  }
  button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
  }
  .back-link {
    text-align: center;
    margin-top: 20px;
  }
  .back-link a {
    color: #667eea;
    text-decoration: none;
    font-weight: 600;
  }
  .back-link a:hover {
    text-decoration: underline;
  }
  .error {
    background: #fee;
    color: #c33;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
    border-left: 4px solid #c33;
  }
</style>
</head>
<body>
<div class="container">
  <h1>🔑 Login</h1>
  {% if error %}
    <div class="error">{{ error }}</div>
  {% endif %}
  <form action="/login" method="post">
    <label>📧 Email:</label>
    <input type="email" name="email" placeholder="your@email.com" required>
    <label>🔒 Password:</label>
    <input type="password" name="password" placeholder="Enter your password" required>
    <button type="submit">🚀 Login</button>
  </form>
  <div class="back-link">
    <a href="/">← Back to Home</a> | <a href="/register">Don't have an account? Register</a>
  </div>
</div>
</body>
</html>
"""

@app.route("/")
def index():
    if db is None or messages is None:
        return get_db_error_msg()
    user = current_user()
    inbox = []
    pairing_code = None
    pairing_requests = []
    partners = []
    
    if user:
        try:
            # Get inbox messages
            for doc in messages.find({"recipient": user["email"]}).sort("created_at", -1):
                inbox.append({
                    "message_id": doc["message_id"],
                    "sender_email": doc.get("sender"),
                    "created_at": doc.get("created_at").strftime("%Y-%m-%d %H:%M"),
                    "viewed": doc.get("viewed", False),
                    "token": doc.get("token")  # Include token for direct viewing
                })
            
            # Get pairing code
            pairing_code = user.get("pairing_code", "N/A")
            
            # Get pairing requests (pending, where user is recipient)
            if pairings is not None:
                for req in pairings.find({"user2_email": user["email"], "status": "pending"}):
                    pairing_requests.append({
                        "id": str(req["_id"]),
                        "from_email": req.get("user1_email"),
                        "created_at": req.get("created_at").strftime("%Y-%m-%d %H:%M") if req.get("created_at") else "N/A"
                    })
                
                # Get paired partners with their secret codes
                for pair in pairings.find({
                    "$or": [
                        {"user1_email": user["email"], "status": "paired"},
                        {"user2_email": user["email"], "status": "paired"}
                    ]
                }):
                    partner_email = pair["user2_email"] if pair["user1_email"] == user["email"] else pair["user1_email"]
                    partners.append({
                        "email": partner_email,
                        "pairing_id": str(pair["_id"]),
                        "secret_code_hash": pair.get("secret_code_hash")
                    })
        except (ServerSelectionTimeoutError, ConnectionFailure):
            return get_db_error_msg()
    
    return render_template_string(INDEX_HTML, 
                                 user=user, 
                                 inbox=inbox, 
                                 pairing_code=pairing_code,
                                 pairing_requests=pairing_requests,
                                 partners=partners)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template_string(REGISTER_HTML)
    if users is None:
        return get_db_error_msg()
    email_val = request.form.get("email")
    pw_val = request.form.get("password")
    if not email_val or not pw_val:
        return render_template_string(REGISTER_HTML, error="❌ Email and password are required")
    email = email_val.strip().lower()
    pw = pw_val.encode()
    try:
        if users.find_one({"email": email}):
            return render_template_string(REGISTER_HTML, error="❌ This email is already registered. Try logging in instead!")
        pw_hash = bcrypt.hashpw(pw, bcrypt.gensalt())
        uid = secrets.token_urlsafe(12)
        pairing_code = secrets.token_urlsafe(8).upper()  # Generate pairing code
        users.insert_one({
            "_id": uid,
            "email": email,
            "password": pw_hash,
            "pairing_code": pairing_code
        })
        session['user_id'] = uid
        return redirect(url_for('index'))
    except (ServerSelectionTimeoutError, ConnectionFailure):
        return get_db_error_msg()

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template_string(LOGIN_HTML)
    if users is None:
        return get_db_error_msg()
    email_val = request.form.get("email")
    pw_val = request.form.get("password")
    if not email_val or not pw_val:
        return render_template_string(LOGIN_HTML, error="❌ Email and password are required")
    email = email_val.strip().lower()
    pw = pw_val.encode()
    try:
        u = users.find_one({"email": email})
        if not u or not bcrypt.checkpw(pw, u['password']):
            return render_template_string(LOGIN_HTML, error="❌ Invalid email or password. Please try again or register a new account.")
        session['user_id'] = u['_id']
        return redirect(url_for('index'))
    except (ServerSelectionTimeoutError, ConnectionFailure):
        return get_db_error_msg()

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

# ---------- Pairing routes ----------
@app.route("/pairing/search", methods=["POST"])
def search_user():
    """Search for users by email"""
    if users is None:
        return jsonify({"error": "Database connection error"}), 503
    user = current_user()
    if not user:
        return jsonify({"error": "login required"}), 401
    
    json_data = request.get_json(silent=True) or {}
    search_query = (request.form.get("query") or json_data.get("query") or "").strip().lower()
    if not search_query:
        return jsonify({"error": "Search query required"}), 400
    
    try:
        # Search users by email (exact match or partial)
        results = []
        for u in users.find({"email": {"$regex": search_query, "$options": "i"}}):
            if u['email'] != user['email']:  # Don't show yourself
                results.append({
                    "email": u['email'],
                    "id": u['_id']
                })
        return jsonify({"users": results})
    except (ServerSelectionTimeoutError, ConnectionFailure):
        return jsonify({"error": "Database connection error"}), 503

@app.route("/pairing/request", methods=["POST"])
def request_pairing():
    if users is None or pairings is None:
        return get_db_error_msg()
    user = current_user()
    if not user:
        return "login required", 401
    
    partner_email = (request.form.get("partner_email") or "").strip().lower()
    secret_code = (request.form.get("secret_code") or "").strip()
    
    if not partner_email:
        return "Partner email required", 400
    if not secret_code:
        return "Secret code required", 400
    
    try:
        # Find user by email
        partner = users.find_one({"email": partner_email})
        if not partner:
            return "User not found", 404
        
        if partner['email'] == user['email']:
            return "Cannot pair with yourself", 400
        
        # Check if already paired
        existing = pairings.find_one({
            "$or": [
                {"user1_email": user['email'], "user2_email": partner['email'], "status": "paired"},
                {"user1_email": partner['email'], "user2_email": user['email'], "status": "paired"}
            ]
        })
        if existing:
            return "Already paired with this user", 400
        
        # Check if request already exists
        existing_request = pairings.find_one({
            "$or": [
                {"user1_email": user['email'], "user2_email": partner['email'], "status": "pending"},
                {"user1_email": partner['email'], "user2_email": user['email'], "status": "pending"}
            ]
        })
        if existing_request:
            return "Pairing request already sent or received", 400
        
        # Store secret code hash for verification
        secret_hash = hashlib.sha256(secret_code.encode()).hexdigest()
        
        # Create pairing request with secret code
        pairings.insert_one({
            "user1_email": user['email'],
            "user2_email": partner['email'],
            "status": "pending",
            "requested_by": user['email'],
            "secret_code_hash": secret_hash,  # Store hash of secret code
            "created_at": datetime.now(timezone.utc)
        })
        return redirect(url_for('index'))
    except (ServerSelectionTimeoutError, ConnectionFailure):
        return get_db_error_msg()

@app.route("/pairing/accept/<request_id>", methods=["POST"])
def accept_pairing(request_id):
    if pairings is None:
        return get_db_error_msg()
    user = current_user()
    if not user:
        return "login required", 401
    
    secret_code = (request.form.get("secret_code") or "").strip()
    if not secret_code:
        return "Secret code required to accept pairing", 400
    
    try:
        # Find the pairing request
        try:
            pairing = pairings.find_one({"_id": ObjectId(request_id)})
        except:
            pairing = pairings.find_one({"_id": request_id})
        
        if not pairing:
            return "Pairing request not found", 404
        
        # Check if user is the recipient
        if pairing['user2_email'] != user['email']:
            return "Not authorized", 403
        
        # Verify secret code
        secret_hash = hashlib.sha256(secret_code.encode()).hexdigest()
        if pairing.get('secret_code_hash') != secret_hash:
            return "Invalid secret code. Please enter the correct code that the sender provided.", 403
        
        # Store the secret code hash with pairing (for message decryption)
        try:
            pairings.update_one(
                {"_id": ObjectId(request_id)},
                {"$set": {
                    "status": "paired", 
                    "accepted_at": datetime.now(timezone.utc),
                    "secret_code_hash": secret_hash  # Store for later use
                }}
            )
        except:
            pairings.update_one(
                {"_id": request_id},
                {"$set": {
                    "status": "paired", 
                    "accepted_at": datetime.now(timezone.utc),
                    "secret_code_hash": secret_hash
                }}
            )
        return redirect(url_for('index'))
    except (ServerSelectionTimeoutError, ConnectionFailure):
        return get_db_error_msg()

@app.route("/pairing/reject/<request_id>", methods=["POST"])
def reject_pairing(request_id):
    if pairings is None:
        return get_db_error_msg()
    user = current_user()
    if not user:
        return "login required", 401
    
    try:
        try:
            pairing = pairings.find_one({"_id": ObjectId(request_id)})
        except:
            pairing = pairings.find_one({"_id": request_id})
        
        if not pairing:
            return "Pairing request not found", 404
        
        if pairing['user2_email'] != user['email']:
            return "Not authorized", 403
        
        try:
            pairings.delete_one({"_id": ObjectId(request_id)})
        except:
            pairings.delete_one({"_id": request_id})
        return redirect(url_for('index'))
    except (ServerSelectionTimeoutError, ConnectionFailure):
        return get_db_error_msg()

@app.route("/send", methods=["POST"])
def send():
    if users is None or messages is None:
        return get_db_error_msg()
    user = current_user()
    if not user:
        return "login required", 401
    recipient = (request.form.get("recipient") or "").strip().lower()
    secret_val = request.form.get("secret") or ""
    secret_text = secret_val.encode()
    file = request.files.get("image")
    if not file or not recipient or not secret_text:
        return "missing fields", 400
    try:
        # ensure recipient exists
        rec = users.find_one({"email": recipient})
        if not rec:
            return "recipient not found (they must register first)", 404
        
        # Check if users are paired
        if pairings is None:
            return get_db_error_msg()
        
        paired = pairings.find_one({
            "$or": [
                {"user1_email": user['email'], "user2_email": recipient, "status": "paired"},
                {"user1_email": recipient, "user2_email": user['email'], "status": "paired"}
            ]
        })
        if not paired:
            error_html = """
            <!doctype html>
            <html><head><meta charset="utf-8"><title>Pairing Required</title></head>
            <body style="font-family: Arial; padding: 50px; text-align: center;">
            <h2>❌ Pairing Required</h2>
            <p>You must be paired with this user to send messages.</p>
            <p>Go back and request a pairing first!</p>
            <a href="/" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px;">← Back</a>
            </body></html>
            """
            return error_html, 403
        
        # Get the secret code hash from pairing for message decryption
        secret_code_hash = paired.get('secret_code_hash')
    except (ServerSelectionTimeoutError, ConnectionFailure):
        return get_db_error_msg()

    # encrypt secret
    cipher = fernet.encrypt(secret_text)

    # embed into image
    img = Image.open(file.stream)
    try:
        stego = embed_bytes_in_image(img, cipher)
    except Exception as e:
        return f"embed error: {e}", 400

    message_id = secrets.token_urlsafe(10)
    fname = secure_filename(f"stego_{message_id}.png")
    path = os.path.join(UPLOAD_DIR, fname)
    stego.save(path, "PNG")

    token = secrets.token_urlsafe(18)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    try:
        messages.insert_one({
            "message_id": message_id,
            "sender": user['email'],
            "recipient": recipient,
            "image_path": path,
            "token": token,  # Store plain token so recipient can view
            "token_hash": token_hash,
            "secret_code_hash": secret_code_hash,  # Store secret code hash for decryption
            "created_at": datetime.now(timezone.utc),
            "viewed": False
        })
    except (ServerSelectionTimeoutError, ConnectionFailure):
        return get_db_error_msg()

    # Show success message to sender
    success_html = """
    <!doctype html>
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message Sent</title>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
      }
      @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
      }
      .container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        max-width: 600px;
        text-align: center;
      }
      h1 { color: #667eea; font-size: 2.5em; margin-bottom: 20px; }
      p { color: #555; font-size: 1.1em; margin: 20px 0; line-height: 1.6; }
      .info-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
        text-align: left;
      }
      a.button {
        display: inline-block;
        margin-top: 20px;
        padding: 12px 25px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        text-decoration: none;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
      }
      a.button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
      }
    </style>
    </head>
    <body>
    <div class="container">
      <h1>✅ Message Sent!</h1>
      <div class="info-box">
        <strong>✓ Success!</strong> Your message has been sent securely. The recipient can view it directly from their inbox.
      </div>
      <p>The recipient will see this message in their inbox and can view it by entering the secret code you both share.</p>
      <a href="/" class="button">← Back to Home</a>
    </div>
    </body>
    </html>
    """
    return success_html

@app.route("/claim/<message_id>")
def claim_link(message_id):
    if messages is None:
        return get_db_error_msg()
    # convenience: returns link if you're the recipient and unviewed
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    try:
        doc = messages.find_one({"message_id": message_id})
        if not doc:
            return "not found", 404
        if doc.get('recipient') != user.get('email'):
            return "not for you", 403
        # we don't store the plain token; send a pseudo-link (in this simple app we cannot retrieve original token)
        return "The sender must share the link URL (it contains the token)."
    except (ServerSelectionTimeoutError, ConnectionFailure):
        return get_db_error_msg()

@app.route("/view/<token>", methods=["GET", "POST"])
def view_token(token):
    if messages is None:
        error_html = """
        <!doctype html>
        <html>
        <head><meta charset="utf-8"><title>Database Error</title></head>
        <body style="font-family: Arial; padding: 50px; text-align: center;">
        <h2>Database Connection Error</h2>
        <p>Please ensure MongoDB is running.</p>
        <a href="/">Back to Home</a>
        </body>
        </html>
        """
        return error_html, 503
    # find message by token hash
    th = hashlib.sha256(token.encode()).hexdigest()
    try:
        doc = messages.find_one({"token_hash": th})
        if not doc:
            error_html = """
            <!doctype html>
            <html>
            <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🔍 Link Not Found</title>
            <style>
              * { margin: 0; padding: 0; box-sizing: border-box; }
              body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
                background-size: 400% 400%;
                animation: gradientShift 15s ease infinite;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
              }
              @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
              }
              .container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 500px;
                text-align: center;
                animation: slideIn 0.5s ease;
              }
              @keyframes slideIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
              }
              h1 { color: #f93; font-size: 3em; margin-bottom: 20px; }
              h2 { color: #555; margin-bottom: 20px; }
              p { color: #555; font-size: 1.1em; margin: 20px 0; line-height: 1.6; }
              a {
                display: inline-block;
                margin-top: 20px;
                padding: 12px 25px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                font-weight: 600;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
              }
              a:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
              }
            </style>
            </head>
            <body>
            <div class="container">
              <h1>🔍</h1>
              <h2>Link Not Found</h2>
              <p>This link is invalid or has expired. The message may have already been viewed or deleted.</p>
              <a href="/">← Back to Home</a>
            </div>
            </body>
            </html>
            """
            return error_html, 404
        # ensure logged-in recipient
        user = current_user()
        if not user:
            # redirect to login then come back
            session['next'] = request.path
            return redirect(url_for('login'))
        if user.get('email') != doc.get('recipient'):
            error_html = """
            <!doctype html>
            <html>
            <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>⚠️ Access Denied</title>
            <style>
              * { margin: 0; padding: 0; box-sizing: border-box; }
              body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
                background-size: 400% 400%;
                animation: gradientShift 15s ease infinite;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
              }
              @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
              }
              .container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 500px;
                text-align: center;
                animation: slideIn 0.5s ease;
              }
              @keyframes slideIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
              }
              h1 { color: #c33; font-size: 3em; margin-bottom: 20px; }
              p { color: #555; font-size: 1.2em; margin: 20px 0; line-height: 1.6; }
              a {
                display: inline-block;
                margin-top: 20px;
                padding: 12px 25px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                font-weight: 600;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
              }
              a:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
              }
            </style>
            </head>
            <body>
            <div class="container">
              <h1>⚠️</h1>
              <h2 style="color: #c33; margin-bottom: 20px;">Access Denied</h2>
              <p>This message was sent to someone else. You can only view messages that were sent to you.</p>
              <a href="/">← Back to Home</a>
            </div>
            </body>
            </html>
            """
            return error_html, 403
        # Check if secret code is provided in session or form
        secret_code = request.form.get("secret_code") or session.get(f"secret_code_{doc['message_id']}")
        
        if not secret_code:
            # Show secret code entry form
            secret_code_html = """
            <!doctype html>
            <html>
            <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Enter Secret Code</title>
            <style>
              * { margin: 0; padding: 0; box-sizing: border-box; }
              body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
                background-size: 400% 400%;
                animation: gradientShift 15s ease infinite;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
              }
              @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
              }
              .container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 450px;
                width: 100%;
                animation: slideIn 0.5s ease;
              }
              @keyframes slideIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
              }
              h1 { color: #667eea; text-align: center; margin-bottom: 10px; font-size: 2.5em; }
              h2 { color: #764ba2; text-align: center; margin-bottom: 30px; }
              form { margin-top: 20px; }
              label { display: block; margin: 15px 0 5px 0; color: #555; font-weight: 600; }
              input {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
                transition: all 0.3s;
                font-family: inherit;
              }
              input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
              }
              button {
                width: 100%;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 15px;
                border: none;
                border-radius: 10px;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                margin-top: 20px;
              }
              button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
              }
              .error {
                background: #fee;
                color: #c33;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                border-left: 4px solid #c33;
              }
            </style>
            </head>
            <body>
            <div class="container">
              <h1>🔐</h1>
              <h2>Enter Secret Code</h2>
              <p style="color: #666; text-align: center; margin-bottom: 20px;">
                Enter the secret code you shared with the sender to view this message.
              </p>
              <form action="/view/""" + token + """" method="post">
                <label>Secret Code:</label>
                <input type="text" name="secret_code" placeholder="e.g., kiwi" required autofocus />
                <button type="submit">🔓 View Message</button>
              </form>
            </div>
            </body>
            </html>
            """
            return secret_code_html
        
        # Verify secret code
        secret_hash = hashlib.sha256(secret_code.encode()).hexdigest()
        if doc.get('secret_code_hash') != secret_hash:
            secret_code_html = """
            <!doctype html>
            <html>
            <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Invalid Secret Code</title>
            <style>
              * { margin: 0; padding: 0; box-sizing: border-box; }
              body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
                background-size: 400% 400%;
                animation: gradientShift 15s ease infinite;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
              }
              @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
              }
              .container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 450px;
                width: 100%;
              }
              h1 { color: #c33; text-align: center; margin-bottom: 10px; font-size: 2.5em; }
              h2 { color: #764ba2; text-align: center; margin-bottom: 20px; }
              .error {
                background: #fee;
                color: #c33;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                border-left: 4px solid #c33;
                text-align: center;
              }
              form { margin-top: 20px; }
              label { display: block; margin: 15px 0 5px 0; color: #555; font-weight: 600; }
              input {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
                font-family: inherit;
              }
              button {
                width: 100%;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 15px;
                border: none;
                border-radius: 10px;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                margin-top: 20px;
              }
            </style>
            </head>
            <body>
            <div class="container">
              <h1>❌</h1>
              <h2>Invalid Secret Code</h2>
              <div class="error">The secret code you entered is incorrect. Please try again.</div>
              <form action="/view/""" + token + """" method="post">
                <label>Secret Code:</label>
                <input type="text" name="secret_code" placeholder="e.g., kiwi" required autofocus />
                <button type="submit">🔓 View Message</button>
              </form>
            </div>
            </body>
            </html>
            """
            return secret_code_html
        
        # Store secret code in session for API reveal
        session[f"secret_code_{doc['message_id']}"] = secret_code
        
        # render viewer HTML with image url and token
        image_url = url_for('get_image', filename=os.path.basename(doc.get('image_path', '')), _external=True)
        try:
            with open("viewer.html", "r", encoding="utf-8") as f:
                viewer_content = f.read()
            return render_template_string(viewer_content, image_url=image_url, token=token, secret_code=secret_code)
        except Exception as e:
            return f"Error loading viewer: {str(e)}", 500
    except (ServerSelectionTimeoutError, ConnectionFailure):
        error_html = """
        <!doctype html>
        <html>
        <head><meta charset="utf-8"><title>Database Error</title></head>
        <body style="font-family: Arial; padding: 50px; text-align: center;">
        <h2>Database Connection Error</h2>
        <p>Please ensure MongoDB is running.</p>
        <a href="/">Back to Home</a>
        </body>
        </html>
        """
        return error_html, 503

@app.route("/uploads/<filename>")
def get_image(filename):
    path = os.path.join(UPLOAD_DIR, secure_filename(filename))
    if not os.path.exists(path):
        abort(404)
    return send_file(path, mimetype="image/png")

@app.route("/favicon.ico")
def favicon():
    return send_file("favicon.ico", mimetype="image/x-icon")

@app.route("/favicon-<size>.png")
def favicon_png(size):
    if size in ["16x16", "32x32"]:
        return send_file(f"favicon-{size}.png", mimetype="image/png")
    abort(404)

@app.route("/apple-touch-icon.png")
def apple_touch_icon():
    if os.path.exists("apple-touch-icon.png"):
        return send_file("apple-touch-icon.png", mimetype="image/png")
    abort(404)

@app.route("/api/reveal/<token>", methods=["GET"])
def api_reveal(token):
    if messages is None:
        return jsonify({"error": "Database connection error"}), 503
    th = hashlib.sha256(token.encode()).hexdigest()
    try:
        doc = messages.find_one({"token_hash": th})
        if not doc:
            return jsonify({"error":"Invalid or expired link"}), 404
        user = current_user()
        if not user:
            return jsonify({"error":"login required"}), 401
        if user.get('email') != doc.get('recipient'):
            return jsonify({"error":"not authorized"}), 403
        if doc.get("viewed"):
            return jsonify({"error":"already viewed"}), 410
        
        # Get secret code from session (stored when viewing)
        secret_code = session.get(f"secret_code_{doc['message_id']}")
        if not secret_code:
            return jsonify({"error": "Secret code required. Please visit the view page first."}), 403
        
        # Verify secret code
        secret_hash = hashlib.sha256(secret_code.encode()).hexdigest()
        if doc.get('secret_code_hash') != secret_hash:
            # Clear invalid code from session
            session.pop(f"secret_code_{doc['message_id']}", None)
            return jsonify({"error": "Invalid secret code"}), 403

        # mark viewed first
        messages.update_one({"_id": doc['_id']}, {"$set":{"viewed": True, "viewed_at": datetime.now(timezone.utc)}})

        # extract payload from image and decrypt
        image_path = doc.get('image_path')
        if not image_path:
            return jsonify({"error": "Image path not found"}), 404
            
        try:
            img = Image.open(image_path)
            payload = extract_bytes_from_image(img)
            plaintext = fernet.decrypt(payload).decode('utf-8')
        except Exception as e:
            plaintext = "[error extracting or decrypting]"

        # delete file to reduce future extraction (best-effort)
        try:
            os.remove(image_path)
        except:
            pass

        return jsonify({"message": plaintext, "view_seconds": VIEW_SECONDS})
    except (ServerSelectionTimeoutError, ConnectionFailure):
        return jsonify({"error": "Database connection error"}), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
