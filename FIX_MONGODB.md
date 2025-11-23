# Fix MongoDB Connection Error

## Error: "Database connection error. Please ensure MongoDB is running."

This error can happen for several reasons. Follow these steps:

## Step 1: Test Your Connection

Run this diagnostic script:
```bash
python test_mongodb_connection.py
```

This will tell you exactly what's wrong.

## Step 2: Common Issues & Fixes

### Issue 1: .env File Not Loading

**Symptoms**: `python-dotenv could not parse statement starting at line 1`

**Fix**:
1. Check your `.env` file format:
   - No spaces around `=`
   - No quotes (unless value has spaces)
   - One variable per line
   - No blank lines at the start

2. Correct format:
   ```env
   MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?appName=SecApp
   FLASK_SECRET_KEY=your-key-here
   FERNET_KEY=your-key-here
   ```

3. Make sure `python-dotenv` is installed:
   ```bash
   pip install python-dotenv
   ```

### Issue 2: MongoDB Atlas Connection Issues

**If using MongoDB Atlas**, check:

1. **IP Whitelist**:
   - Go to MongoDB Atlas → Network Access
   - Add your IP address (or `0.0.0.0/0` for all IPs - less secure)
   - Wait 2-3 minutes for changes to propagate

2. **Database User**:
   - Go to MongoDB Atlas → Database Access
   - Make sure user exists and has correct password
   - User should have "Read and write to any database" permission

3. **Connection String**:
   - Make sure it's correct format: `mongodb+srv://username:password@cluster.mongodb.net/?appName=SecApp`
   - URL-encode special characters in password (e.g., `@` → `%40`)

4. **Network Access**:
   - Make sure "Network Access" is enabled
   - Check if your IP is blocked

### Issue 3: Local MongoDB Not Running

**If using local MongoDB**:

1. **Check if MongoDB is running**:
   ```bash
   # Windows
   Get-Service MongoDB
   
   # Or check if port 27017 is in use
   netstat -an | findstr 27017
   ```

2. **Start MongoDB**:
   ```bash
   # Using Docker (recommended)
   docker-compose up -d mongodb
   
   # Or start MongoDB service
   net start MongoDB
   ```

3. **Test connection**:
   ```bash
   python test_mongodb_connection.py
   ```

### Issue 4: Wrong Connection String

**Check your `.env` file**:
```env
MONGO_URI=mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp
```

Make sure:
- Username is correct: `narayanip868_db_user`
- Password is correct: `N8WhoSaEZinRNR4a`
- Cluster URL is correct: `secapp.wj3dw5a.mongodb.net`

## Step 3: Quick Fixes

### Fix 1: Recreate .env File

1. Delete `.env` file
2. Create new `.env` with this content:
   ```env
   MONGO_URI=mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp
   FLASK_SECRET_KEY=ou6qY3L4llkCZpXKS9MEZjiKf7ZhjqOj1cSs2mXPjxE
   FERNET_KEY=M_uk9Sd8YFRkn819wFotCX1SBVgAcJutpAJQBf2V9RQ=
   VIEW_SECONDS=10
   ```
3. Make sure no extra spaces or characters
4. Restart your Flask app

### Fix 2: Test Connection Directly

```python
from pymongo import MongoClient

uri = "mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp"
client = MongoClient(uri, serverSelectionTimeoutMS=5000)
client.admin.command('ping')
print("Connected!")
```

### Fix 3: For Railway/Deployment

If deploying on Railway:
1. Go to Railway dashboard
2. Your service → Variables
3. Add `MONGO_URI` variable
4. Make sure it's exactly: `mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp`
5. Redeploy

## Step 4: Verify Fix

After fixing, test:
```bash
python test_mongodb_connection.py
```

Should show: `[SUCCESS] MongoDB connection successful!`

Then restart your Flask app:
```bash
python app.py
```

## Still Not Working?

1. **Check MongoDB Atlas Dashboard**:
   - Is your cluster running?
   - Is your IP whitelisted?
   - Are credentials correct?

2. **Check Firewall**:
   - Is port 27017 blocked?
   - Is your network blocking MongoDB?

3. **Try Different Connection String**:
   - Get fresh connection string from Atlas
   - Click "Connect" → "Connect your application"
   - Copy the connection string

4. **Check Logs**:
   - Look at Flask app output for detailed error
   - Check MongoDB Atlas logs

