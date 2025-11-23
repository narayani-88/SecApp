# MongoDB Atlas Setup Guide

## Step 1: Get Your Connection String

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Log in to your account
3. Click on your cluster (or create one if you haven't)
4. Click **"Connect"** button
5. Choose **"Connect your application"**
6. Copy the connection string (it looks like):
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

## Step 2: Create Database User

1. In MongoDB Atlas, go to **"Database Access"** (left sidebar)
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Enter a username and generate a secure password
5. Set user privileges to **"Read and write to any database"** (or create specific database access)
6. Click **"Add User"**
7. **IMPORTANT:** Save the username and password - you'll need them!

## Step 3: Configure Network Access

1. Go to **"Network Access"** (left sidebar)
2. Click **"Add IP Address"**
3. Choose one of:
   - **"Allow Access from Anywhere"** (0.0.0.0/0) - for development/testing
   - **"Add Current IP Address"** - for more security
4. Click **"Confirm"**

## Step 4: Create Your .env File

1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` and replace:
   - `<username>` with your MongoDB Atlas username
   - `<password>` with your MongoDB Atlas password
   - `cluster0.xxxxx.mongodb.net` with your actual cluster URL

Example:
```
MONGO_URI=mongodb+srv://myuser:mypassword123@cluster0.abcd123.mongodb.net/?retryWrites=true&w=majority
```

## Step 5: Generate Encryption Keys

Run these commands to generate secure keys:

```powershell
# Generate Flask Secret Key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate Fernet Key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output to your `.env` file for `FLASK_SECRET_KEY` and `FERNET_KEY`.

## Step 6: Test Connection

1. Make sure your `.env` file is configured correctly
2. Restart your Flask app:
   ```powershell
   python app.py
   ```
3. You should see: `✓ MongoDB connection successful`

## Troubleshooting

### "Authentication failed"
- Double-check your username and password in the connection string
- Make sure the user has proper database access permissions

### "Connection timeout"
- Check your Network Access settings in Atlas
- Make sure your IP is whitelisted
- Try "Allow Access from Anywhere" (0.0.0.0/0) for testing

### "DNS lookup failed"
- Verify your cluster URL is correct
- Check if you're using the correct connection string format (mongodb+srv://)

### "Server selection timeout"
- Check if your cluster is paused (Atlas pauses free tier clusters after inactivity)
- Wake up your cluster in MongoDB Atlas dashboard
- Wait a few minutes for it to start

## Security Notes

- **NEVER commit your `.env` file to git** - it contains sensitive credentials
- Use strong, unique passwords for your database user
- Rotate your keys periodically (FLASK_SECRET_KEY, FERNET_KEY)
- For production, use environment-specific configurations
- Consider using Atlas IP whitelisting for better security

