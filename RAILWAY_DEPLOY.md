# Railway Deployment - Step by Step

## Error: "You must specify a workspaceId to create a project"

This error means you need to create a workspace first, or you're using the wrong method.

## ✅ Correct Deployment Steps

### Method 1: Railway Web Dashboard (Easiest)

1. **Go to Railway**:
   - Visit [railway.app](https://railway.app)
   - Click **"Start a New Project"** or **"Login"**

2. **Sign Up/Login**:
   - Sign up with GitHub (recommended) or email
   - This automatically creates a workspace for you

3. **Create New Project**:
   - Click **"New Project"** button
   - Select **"Deploy from GitHub repo"**
   - Authorize Railway to access your GitHub (if first time)
   - Select your `SecApp` repository

4. **Railway Auto-Detects**:
   - Railway automatically:
     - Detects it's a Python/Flask app
     - Installs dependencies from `requirements.txt`
     - Runs `gunicorn app:app` (from `Procfile` or auto-detects)
     - Starts building

5. **Add Environment Variables**:
   - Click on your service
   - Go to **"Variables"** tab
   - Click **"New Variable"** and add:
     ```
     MONGO_URI = mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp
     FLASK_SECRET_KEY = ou6qY3L4llkCZpXKS9MEZjiKf7ZhjqOj1cSs2mXPjxE
     FERNET_KEY = M_uk9Sd8YFRkn819wFotCX1SBVgAcJutpAJQBf2V9RQ=
     ```

6. **Get Your URL**:
   - Railway automatically generates a URL
   - Click **"Settings"** → **"Generate Domain"** if needed
   - Your app is live! 🎉

### Method 2: Railway CLI (If you prefer command line)

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login**:
   ```bash
   railway login
   ```
   (This opens browser to authenticate)

3. **Initialize Project**:
   ```bash
   railway init
   ```
   - Select "Create new project"
   - This creates a workspace automatically

4. **Link to GitHub** (optional):
   ```bash
   railway link
   ```

5. **Add Environment Variables**:
   ```bash
   railway variables set MONGO_URI="mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp"
   railway variables set FLASK_SECRET_KEY="ou6qY3L4llkCZpXKS9MEZjiKf7ZhjqOj1cSs2mXPjxE"
   railway variables set FERNET_KEY="M_uk9Sd8YFRkn819wFotCX1SBVgAcJutpAJQBf2V9RQ="
   ```

6. **Deploy**:
   ```bash
   railway up
   ```

## Common Issues

### "You must specify a workspaceId"
- **Solution**: Use the web dashboard first to create a workspace
- Or use `railway init` which creates one automatically

### "No workspace found"
- **Solution**: Make sure you're logged in at railway.app
- Create a project from the dashboard first

### "Project not found"
- **Solution**: Make sure your GitHub repo is public (or you've authorized Railway)
- Or use `railway init` to create a new project

## Quick Start (Recommended)

**Just use the web dashboard** - it's the easiest:
1. Go to railway.app
2. Login with GitHub
3. New Project → Deploy from GitHub
4. Select SecApp repo
5. Add environment variables
6. Done!

The web dashboard handles everything automatically.

