# How to Set Up .env File

## Quick Setup

### Step 1: Generate Keys

Run this command to generate secure keys:

```bash
python generate_keys.py
```

This will output:
```
FLASK_SECRET_KEY=...
FERNET_KEY=...
```

### Step 2: Create .env File

**Option A: Copy from example (recommended)**
```bash
# Windows PowerShell
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

**Option B: Create manually**
Create a new file named `.env` in your project root.

### Step 3: Edit .env File

Open `.env` in a text editor and fill in the values:

```env
# Your MongoDB Atlas connection string
MONGO_URI=mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp

# Generated keys (from generate_keys.py)
FLASK_SECRET_KEY=ou6qY3L4llkCZpXKS9MEZjiKf7ZhjqOj1cSs2mXPjxE
FERNET_KEY=M_uk9Sd8YFRkn819wFotCX1SBVgAcJutpAJQBf2V9RQ=

# Optional settings
VIEW_SECONDS=10
UPLOAD_DIR=uploads
PORT=5000
```

## Your Current Values

Based on your setup, your `.env` file should contain:

```env
MONGO_URI=mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp
FLASK_SECRET_KEY=ou6qY3L4llkCZpXKS9MEZjiKf7ZhjqOj1cSs2mXPjxE
FERNET_KEY=M_uk9Sd8YFRkn819wFotCX1SBVgAcJutpAJQBf2V9RQ=
VIEW_SECONDS=10
```

## Important Notes

1. **Never commit .env to Git**
   - `.env` is already in `.gitignore`
   - Contains sensitive information (passwords, keys)

2. **For Deployment (Railway/Render)**
   - Don't upload `.env` file
   - Add environment variables in the platform's dashboard instead
   - Go to your service → Variables tab → Add each variable

3. **Format**
   - No spaces around `=`
   - No quotes needed (unless value contains spaces)
   - One variable per line

## Verify .env is Working

Run your app:
```bash
python app.py
```

If you see:
- ✅ "MongoDB connection successful" → `.env` is working!
- ❌ "Database connection error" → Check `MONGO_URI` in `.env`

## Troubleshooting

### .env file not found
- Make sure `.env` is in the same directory as `app.py`
- Check the filename is exactly `.env` (not `.env.txt`)

### Variables not loading
- Make sure `python-dotenv` is installed: `pip install python-dotenv`
- Restart your app after changing `.env`

### Wrong values
- Run `python generate_keys.py` to get new keys
- Update MongoDB URI if you changed your database

