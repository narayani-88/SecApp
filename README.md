# SecApp 🔐

**Secure one-time secret messenger: pair with friends using secret codes, send encrypted messages hidden in images that auto-delete after 10 seconds.**

## 🚀 Deploy Now (Railway - 2 minutes)

### ⚠️ Netlify Cannot Run Flask Apps

**Error**: `dependency_installation script returned non-zero exit code: 1`

**Why**: Netlify expects Node.js (`package.json`), but your app is Python/Flask (`requirements.txt`).  
**Netlify doesn't support Flask apps** - it's for static sites only.

**This is NOT a bug you can fix** - it's a platform limitation.  
See `WHY_NETLIFY_FAILS.md` for technical explanation.

### ✅ Use Railway Instead (Works Immediately)

#### Quick Steps:

1. **Go to Railway**:
   - Visit [railway.app](https://railway.app)
   - Click **"Start a New Project"** or **"Login"**
   - Sign up/login with GitHub (recommended)

2. **Deploy from GitHub**:
   - Click **"New Project"** → **"Deploy from GitHub repo"**
   - Authorize Railway (if first time)
   - Select your `SecApp` repository
   - Railway **auto-detects Flask** and starts building!

3. **Add Environment Variables** (Railway dashboard → Your Service → Variables):
   ```
   MONGO_URI = mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp
   FLASK_SECRET_KEY = ou6qY3L4llkCZpXKS9MEZjiKf7ZhjqOj1cSs2mXPjxE
   FERNET_KEY = M_uk9Sd8YFRkn819wFotCX1SBVgAcJutpAJQBf2V9RQ=
   ```

4. **Get Your URL**:
   - Railway automatically generates a URL
   - Click **"Settings"** → **"Generate Domain"** if needed
   - Your app is live! 🎉

**If you get "workspaceId" error**: See `RAILWAY_DEPLOY.md` for detailed steps.

**Why Railway?** Built for Flask, auto-detects your app, deploys in 2 minutes, free $5 credit monthly.

### Test Locally First

```bash
# Verify your app works
python test_local.py

# Run locally
pip install -r requirements.txt
python app.py
```

If it works locally, your app is fine - just use Railway instead of Netlify.

### Alternative: Render (Free Tier)
- See `DEPLOY.md` for Render instructions
- Or use `render.yaml` (already configured)

## ✨ Features

🔐 Secret code pairing | 🖼️ Image steganography | ⏱️ 10s auto-expire | 🔒 One-time view
