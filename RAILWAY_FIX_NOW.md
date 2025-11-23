# 🚨 URGENT: Fix Railway Deployment - Add Environment Variables

## The Problem
Your Railway app is crashing because these environment variables are missing:
1. ❌ `MONGO_URI` - Defaulting to `localhost:27017` (wrong!)
2. ❌ `FERNET_KEY` - App generated a new one, but it's not saved
3. ⚠️ `FLASK_SECRET_KEY` - May be missing too

## Quick Fix (5 minutes)

### Step 1: Open Railway Dashboard
1. Go to https://railway.app
2. Click on your project: **proactive-essence**
3. Click on the **web** service (the one that's crashing)

### Step 2: Find Variables Tab
Look for one of these:
- **Variables** tab at the top
- **Settings** → **Variables**
- Right sidebar → **Variables**

### Step 3: Add These 3 Variables

Click **"New Variable"** or **"Add Variable"** and add each one:

#### Variable 1: MONGO_URI
- **Name**: `MONGO_URI`
- **Value**: `mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp`
- Click **Add** or **Save**

#### Variable 2: FERNET_KEY
- **Name**: `FERNET_KEY`
- **Value**: `yDG2RaP1OjvhY8uorahk8hJk3MjRju_hc4H4mAxm1SM=`
  *(This is the one generated in your logs - use this exact value)*
- Click **Add** or **Save**

#### Variable 3: FLASK_SECRET_KEY
- **Name**: `FLASK_SECRET_KEY`
- **Value**: `ou6qY3L4llkCZpXKS9MEZjiKf7ZhjqOj1cSs2mXPjxE`
  *(Or generate a new one with: `python generate_keys.py`)*
- Click **Add** or **Save**

### Step 4: Redeploy
After adding all 3 variables:
1. Railway will **automatically redeploy** (or click **Redeploy**)
2. Wait 1-2 minutes
3. Check the **Deploy Logs** - you should see:
   - ✅ "MongoDB connection successful"
   - ✅ No more "Connection refused" errors

## Verify It's Fixed

1. Go to **Deploy Logs** tab
2. Look for:
   - ✅ "MongoDB connection successful"
   - ✅ No "Connection refused" errors
   - ✅ App listening on port 8080

3. Visit your app URL: `https://web-production-7ee9a.up.railway.app`
   - Should load without errors!

## Still Not Working?

### Check MongoDB Atlas IP Whitelist
1. Go to https://cloud.mongodb.com
2. **Network Access** → **IP Access List**
3. Make sure `0.0.0.0/0` is added (allows all IPs)
   - If not, click **Add IP Address** → **Allow Access from Anywhere** → `0.0.0.0/0`

### Check Railway Logs
1. Railway Dashboard → Your Service → **Deploy Logs**
2. Look for error messages
3. Common errors:
   - "Connection refused" → MongoDB IP whitelist issue
   - "Authentication failed" → Wrong password in MONGO_URI
   - "Invalid FERNET_KEY" → Use the exact value from logs

## Quick Reference: All 3 Variables

Copy-paste these into Railway Variables:

```
MONGO_URI=mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp
FERNET_KEY=yDG2RaP1OjvhY8uorahk8hJk3MjRju_hc4H4mAxm1SM=
FLASK_SECRET_KEY=ou6qY3L4llkCZpXKS9MEZjiKf7ZhjqOj1cSs2mXPjxE
```

**Important**: Add each one separately in Railway (don't paste all 3 at once).

