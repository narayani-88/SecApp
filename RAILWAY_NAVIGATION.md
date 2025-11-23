# Railway Navigation Guide

## Finding Services and Environment Variables

### Step 1: Access Your Project

1. Go to [railway.app](https://railway.app)
2. Login to your account
3. You should see your project in the dashboard

### Step 2: Find Environment Variables

Railway's interface can be a bit different depending on the view. Here's where to find variables:

#### Method 1: Project View (Most Common)

1. **Click on your project** (the card/tile with your project name)
2. You'll see your **service** (usually named after your repo, like "SecApp")
3. **Click on the service** (not the project, but the service inside)
4. Look for tabs at the top:
   - **Variables** ← Click this!
   - Or **Settings** → **Variables**

#### Method 2: Service Settings

1. Click on your project
2. Click on your service
3. Click the **"..."** (three dots) menu or **Settings** icon
4. Select **"Variables"** from the dropdown

#### Method 3: Right Sidebar

1. Click on your project
2. Click on your service
3. Look at the **right sidebar** - there might be a **"Variables"** section
4. Click **"New Variable"** or **"Add Variable"**

### Step 3: Add Environment Variables

Once you find the Variables section:

1. Click **"New Variable"** or **"Add Variable"** button
2. For each variable, enter:
   - **Name**: `MONGO_URI`
   - **Value**: `mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp`
   - Click **"Add"** or **"Save"**

3. Repeat for:
   - **Name**: `FLASK_SECRET_KEY`
   - **Value**: `ou6qY3L4llkCZpXKS9MEZjiKf7ZhjqOj1cSs2mXPjxE`

4. And:
   - **Name**: `FERNET_KEY`
   - **Value**: `M_uk9Sd8YFRkn819wFotCX1SBVgAcJutpAJQBf2V9RQ=`

### Alternative: Using Railway CLI

If you can't find it in the UI, use the CLI:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Add variables
railway variables set MONGO_URI="mongodb+srv://narayanip868_db_user:N8WhoSaEZinRNR4a@secapp.wj3dw5a.mongodb.net/?appName=SecApp"
railway variables set FLASK_SECRET_KEY="ou6qY3L4llkCZpXKS9MEZjiKf7ZhjqOj1cSs2mXPjxE"
railway variables set FERNET_KEY="M_uk9Sd8YFRkn819wFotCX1SBVgAcJutpAJQBf2V9RQ="
```

### Visual Guide

```
Railway Dashboard
├── Your Project (click here)
    ├── Service: "SecApp" or your repo name (click here)
        ├── Variables Tab ← LOOK HERE
        ├── Settings Tab
        ├── Deployments Tab
        └── Metrics Tab
```

### Common Issues

**"I don't see Variables tab"**
- Make sure you clicked on the **service**, not just the project
- Try clicking **Settings** first, then look for Variables
- Check if your service has deployed (it might need to build first)

**"I see the project but no service"**
- Your project might still be building
- Wait a few minutes for Railway to detect and create the service
- Check the **Deployments** tab to see build status

**"Variables section is empty"**
- That's normal! Click **"New Variable"** or **"Add Variable"** to add them

### Quick Check: Is Your Service Running?

1. Click on your project
2. You should see a service card
3. Check if it shows:
   - ✅ "Active" or "Running"
   - Or 🔄 "Building" or "Deploying"
4. If it's building, wait for it to finish, then add variables

### Still Can't Find It?

Try this:
1. **Refresh the page** (sometimes Railway UI needs a refresh)
2. **Check if you're in the right project** (click your project name at the top)
3. **Look for a hamburger menu** (☰) - Variables might be there
4. **Use Railway CLI** (see above) - it's sometimes easier

### Need Help?

Railway's interface updates frequently. If you still can't find it:
- Check Railway's docs: https://docs.railway.app
- Or use the CLI method (it's more reliable)

