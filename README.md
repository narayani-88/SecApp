# SecApp 🔐

**Secure one-time secret messenger: pair with friends using secret codes, send encrypted messages hidden in images that auto-delete after 10 seconds.**

## Quick Deploy

- **Railway**: Connect GitHub repo → Add MongoDB Atlas URI → Deploy
- **Render**: Connect repo → Use `render.yaml` → Add env vars  
- **Heroku**: `git push heroku main` (see `Procfile`)

## Setup

```bash
pip install -r requirements.txt
# Add MongoDB Atlas URI to .env
python app.py
```

## Features

🔐 Secret code pairing | 🖼️ Image steganography | ⏱️ 10s auto-expire | 🔒 One-time view
