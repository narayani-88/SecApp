# Quick MongoDB Atlas Setup

Since you have MongoDB Atlas ready, follow these steps:

## 1. Get Your MongoDB Atlas Connection String

1. Go to your MongoDB Atlas dashboard
2. Click **"Connect"** on your cluster
3. Choose **"Connect your application"**
4. Copy the connection string (it will look like):
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

## 2. Update Your .env File

Open your `.env` file and add/update these variables:

```env
# Your MongoDB Atlas connection string


# Generate these using: python generate_keys.py
FLASK_SECRET_KEY=your-flask-secret-key-here
FERNET_KEY=your-fernet-key-here

# Optional settings (these have defaults)
UPLOAD_DIR=uploads
VIEW_SECONDS=60
PORT=5000
```

**Important Notes:**
- Replace `your-username` and `your-password` with your actual MongoDB Atlas credentials
- Make sure there are NO spaces around the `=` sign
- If your password contains special characters like `@`, `#`, `%`, etc., you need to URL-encode them:
  - `@` becomes `%40`
  - `#` becomes `%23`
  - `%` becomes `%25`
  - `&` becomes `%26`

## 3. Generate Security Keys

Run this command to generate secure keys:

```powershell
python generate_keys.py
```

Copy the output `FLASK_SECRET_KEY` and `FERNET_KEY` to your `.env` file.

## 4. Test Your Connection

After updating your `.env` file, restart your Flask app:

```powershell
python app.py
```

You should see:
```
✓ MongoDB connection successful
```

If you see connection errors, check:
- Your MongoDB Atlas cluster is running (not paused)
- Your IP address is whitelisted in Network Access
- Your username and password are correct
- Your connection string format is correct

## 5. Stop Local MongoDB (Optional)

Since you're using MongoDB Atlas, you can stop your local MongoDB Docker container:

```powershell
docker-compose stop mongodb
```

Or remove it entirely:
```powershell
docker-compose down
```

---

**Need help?** Check `MONGODB_ATLAS_SETUP.md` for detailed troubleshooting.

