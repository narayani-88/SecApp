# 🚀 Deployment Guide

## ⚠️ IMPORTANT: Netlify Will NOT Work

**Netlify is failing because it doesn't support Flask applications.**  
Netlify is designed for static sites (HTML/CSS/JS) and simple serverless functions, not full Flask apps with:
- Multiple routes
- Session management  
- File uploads
- Persistent database connections

## ✅ Use Railway Instead (Recommended - 2 minutes)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### Step 2: Deploy on Railway
1. Go to **[railway.app](https://railway.app)**
2. Click **"New Project"** → **"Deploy from GitHub"**
3. Select your `SecApp` repository
4. Railway **auto-detects Python** and starts building automatically!

### Step 3: Add Environment Variables
In Railway dashboard → Your Service → Variables tab, add:

```
MONGO_URI = mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp
FLASK_SECRET_KEY = ou6qY3L4llkCZpXKS9MEZjiKf7ZhjqOj1cSs2mXPjxE
FERNET_KEY = M_uk9Sd8YFRkn819wFotCX1SBVgAcJutpAJQBf2V9RQ=
```

### Step 4: Get Your URL
Railway automatically:
- Builds your app
- Runs `gunicorn app:app`
- Gives you a live URL (like `https://your-app.railway.app`)

**That's it! Your app is live in 2 minutes.**

---

## Alternative: Render (Free Tier Available)

### Step 1: Push to GitHub (same as above)

### Step 2: Deploy on Render
1. Go to **[render.com](https://render.com)**
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository
4. Settings:
   - **Name**: `secapp`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add environment variables (same as Railway above)
6. Click **"Create Web Service"**

Render will build and deploy your app. Free tier includes 750 hours/month.

---

## Why Railway is Better for Flask

✅ **Auto-detection**: No configuration needed  
✅ **Instant deploy**: Works out of the box  
✅ **Free tier**: $5 credit monthly  
✅ **Easy env vars**: Simple dashboard  
✅ **Auto HTTPS**: SSL certificate included  
✅ **Logs**: Real-time deployment logs  

---

## Generate New Keys (Optional)

If you want fresh encryption keys:
```bash
python generate_keys.py
```

Copy the output to your deployment platform's environment variables.
