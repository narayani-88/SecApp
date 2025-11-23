# Why Netlify Fails - Technical Explanation

## The Error You're Seeing

```
Failed during stage 'Install dependencies': dependency_installation script returned non-zero exit code: 1
```

## Root Cause (Not a Bug - Platform Limitation)

**Netlify's build system is designed for Node.js/JavaScript projects.**

When Netlify sees your repository, it:
1. Looks for `package.json` (Node.js project file)
2. Tries to run `npm install` or `yarn install`
3. Expects JavaScript dependencies
4. **Your project has `requirements.txt` (Python), not `package.json` (Node.js)**
5. Netlify fails because it doesn't know how to handle Python/Flask apps

## What Netlify Supports

✅ **Static sites** (HTML, CSS, JavaScript)  
✅ **Serverless functions** (single functions, not full apps)  
✅ **Node.js apps** (React, Vue, Next.js, etc.)  
❌ **Python/Flask apps** (what you have)

## What Your Flask App Needs

Your app (`app.py`) requires:
- **Full Python runtime** (not just serverless functions)
- **Persistent server process** (Gunicorn running continuously)
- **Session management** (Flask sessions stored server-side)
- **File uploads** (image steganography)
- **Multiple routes** (`/send`, `/view`, `/pairing`, etc.)
- **Database connections** (MongoDB with persistent connections)

**None of these work on Netlify's architecture.**

## Why You Can't Fix This

This is **not** a configuration issue you can fix. It's like trying to run a Windows .exe file on a Mac - the platforms are fundamentally incompatible.

Even if you:
- Add `package.json` → Netlify will try to build a Node.js app (wrong)
- Configure Python in `netlify.toml` → Netlify doesn't support full Python runtimes
- Use Netlify Functions → Can't handle Flask's routing, sessions, uploads

## The Solution: Use Railway

Railway is **designed** for Flask apps:
- ✅ Native Python support
- ✅ Auto-detects Flask
- ✅ Handles all your requirements
- ✅ Deploys in 2 minutes

## Proof: Your App Works Locally

Run this locally to prove your app works:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Your app works fine - it's just Netlify that can't run it.

## Deploy to Railway (2 Minutes)

1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Select your repo
4. Add environment variables
5. Done!

See `DEPLOY.md` for detailed steps.

## Bottom Line

**Stop trying Netlify.** It's like trying to fit a square peg in a round hole.  
**Use Railway.** It's designed for your Flask app and will work immediately.

