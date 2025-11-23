# Fix "Application failed to respond" on Railway

## Error: Application failed to respond

This means Railway can't reach your Flask app. Common causes and fixes:

## Step 1: Check Railway Logs

1. Go to Railway dashboard
2. Click on your project → Your service
3. Click **"Deployments"** tab
4. Click on the latest deployment
5. Check the **logs** for errors

Look for:
- ❌ Import errors
- ❌ Database connection errors
- ❌ Port binding errors
- ❌ Missing environment variables

## Step 2: Common Issues & Fixes

### Issue 1: Port Configuration

**Problem**: Railway sets `PORT` environment variable, but app might not be using it.

**Fix**: Your `app.py` should use:
```python
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
```

**Check**: Look at the end of `app.py` - it should read `PORT` from environment.

### Issue 2: Missing Environment Variables

**Problem**: App crashes on startup because MongoDB connection fails.

**Fix**: 
1. Go to Railway → Your service → **Variables** tab
2. Make sure these are set:
   ```
   MONGO_URI = mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp
   FLASK_SECRET_KEY = ou6qY3L4llkCZpXKS9MEZjiKf7ZhjqOj1cSs2mXPjxE
   FERNET_KEY = M_uk9Sd8YFRkn819wFotCX1SBVgAcJutpAJQBf2V9RQ=
   ```
3. **Redeploy** after adding variables

### Issue 3: Gunicorn Not Starting

**Problem**: `Procfile` might be wrong or gunicorn not installed.

**Fix**: 
1. Check `Procfile` contains: `web: gunicorn app:app`
2. Make sure `gunicorn` is in `requirements.txt`
3. Railway should auto-detect, but you can set start command manually:
   - Go to Settings → **Deploy** tab
   - Set **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

### Issue 4: MongoDB Atlas IP Whitelist

**Problem**: Railway's IP is not whitelisted in MongoDB Atlas.

**Fix**:
1. Go to MongoDB Atlas → **Network Access**
2. Click **"Add IP Address"**
3. Add `0.0.0.0/0` (allows all IPs - less secure but works)
   - Or find Railway's IP from logs and add it specifically
4. Wait 2-3 minutes for changes to propagate
5. Redeploy on Railway

### Issue 5: App Crashes on Startup

**Problem**: Python errors when app starts.

**Fix**: Check logs for:
- Import errors → Check `requirements.txt` has all packages
- Syntax errors → Test locally first: `python app.py`
- Database errors → Test connection: `python test_mongodb_connection.py`

## Step 3: Quick Fixes

### Fix 1: Verify Procfile

Your `Procfile` should be:
```
web: gunicorn app:app
```

Make sure:
- File is named exactly `Procfile` (no extension)
- `gunicorn` is in `requirements.txt`
- No extra spaces or characters

### Fix 2: Check Start Command

In Railway:
1. Go to Settings → **Deploy**
2. Check **Start Command** is: `gunicorn app:app --bind 0.0.0.0:$PORT`
3. Or leave empty (Railway will use Procfile)

### Fix 3: Test Locally First

Before deploying, test locally:
```bash
# Install dependencies
pip install -r requirements.txt

# Test MongoDB connection
python test_mongodb_connection.py

# Run app
python app.py
```

If it works locally, the issue is deployment-specific.

### Fix 4: Check Railway Logs

**Most important**: Check the deployment logs in Railway dashboard.

Common log errors:
- `ModuleNotFoundError` → Add missing package to `requirements.txt`
- `Connection refused` → MongoDB IP whitelist issue
- `Address already in use` → Port conflict (rare on Railway)
- `ImportError` → Check Python version compatibility

## Step 4: Manual Deployment Check

1. **Check Build Logs**:
   - Railway → Deployments → Latest → Build logs
   - Should show: `Successfully installed...`

2. **Check Runtime Logs**:
   - Railway → Deployments → Latest → Runtime logs
   - Should show: `Starting gunicorn...` or `Application startup complete`

3. **Check Variables**:
   - Railway → Service → Variables
   - All 3 variables should be set

4. **Check Domain**:
   - Railway → Settings → Generate Domain
   - Make sure domain is active

## Step 5: Redeploy

After fixing issues:
1. Go to Railway → Your service
2. Click **"Redeploy"** or **"Deploy"**
3. Watch the logs in real-time
4. Wait for "Deployed successfully"

## Still Not Working?

1. **Check Railway Status**: https://status.railway.app
2. **Try Different Port**: Set `PORT=8080` in variables
3. **Simplify Start**: Try `python app.py` as start command (temporary test)
4. **Check MongoDB**: Make sure Atlas cluster is running
5. **Contact Railway Support**: Use Railway's help chat

## Debug Checklist

- [ ] All environment variables set in Railway
- [ ] MongoDB Atlas IP whitelist includes `0.0.0.0/0`
- [ ] `gunicorn` in `requirements.txt`
- [ ] `Procfile` exists and is correct
- [ ] App works locally (`python app.py`)
- [ ] Build logs show successful installation
- [ ] Runtime logs show app starting
- [ ] No errors in Railway logs

