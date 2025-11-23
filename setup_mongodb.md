# MongoDB Setup Guide

## Option 1: MongoDB Atlas (Cloud - Easiest & Recommended)

1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create a free account (M0 Free Tier)
3. Create a new cluster (choose any cloud provider/region)
4. In "Network Access", add IP `0.0.0.0/0` (allows all IPs) or your specific IP
5. In "Database Access", create a database user (username/password)
6. Click "Connect" → "Connect your application" → Copy the connection string
7. Create a `.env` file in your project root:
   ```
   MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
   Replace `username` and `password` with your database user credentials

## Option 2: Docker (Requires Docker Desktop running)

1. Start Docker Desktop
2. Run this command:
   ```powershell
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```
3. MongoDB will be available at `mongodb://localhost:27017/`
4. Create `.env` file:
   ```
   MONGO_URI=mongodb://localhost:27017/
   ```

## Option 3: Install MongoDB Locally (Windows)

1. Download MongoDB Community Server from: https://www.mongodb.com/try/download/community
2. Run the installer
3. Choose "Complete" installation
4. Install as a Windows Service
5. MongoDB will run on `mongodb://localhost:27017/`
6. Create `.env` file:
   ```
   MONGO_URI=mongodb://localhost:27017/
   ```

## After Setup

Restart your Flask application:
```powershell
python app.py
```

