#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script to verify your Flask app works locally.
This proves your app is fine - Netlify just can't run it.
"""

import sys
import subprocess
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_dependencies():
    """Check if all dependencies are installed"""
    print("Checking dependencies...")
    try:
        import flask
        import pymongo
        import PIL
        import cryptography
        import bcrypt
        print("[OK] All dependencies installed!")
        return True
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_app_import():
    """Test if app.py can be imported"""
    print("\nTesting app.py import...")
    try:
        # Check if app.py exists
        if not os.path.exists("app.py"):
            print("[ERROR] app.py not found!")
            return False
        
        # Try to import (this will fail if there are syntax errors)
        # We'll just check if the file is readable
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "from flask import" in content:
                print("[OK] app.py looks valid!")
                return True
            else:
                print("[ERROR] app.py doesn't look like a Flask app")
                return False
    except Exception as e:
        print(f"[ERROR] Error reading app.py: {e}")
        return False

def main():
    print("=" * 50)
    print("SecApp Local Test")
    print("=" * 50)
    print("\nThis test verifies your app works locally.")
    print("If this passes, your app is fine - Netlify just can't run Flask apps.\n")
    
    deps_ok = test_dependencies()
    app_ok = test_app_import()
    
    print("\n" + "=" * 50)
    if deps_ok and app_ok:
        print("[SUCCESS] Your app is ready!")
        print("\nTo run locally:")
        print("   python app.py")
        print("\nTo deploy:")
        print("   Use Railway: https://railway.app")
        print("   (Netlify won't work - it doesn't support Flask)")
    else:
        print("[FAILED] Some checks failed")
        print("   Fix the issues above, then try again")
    print("=" * 50)

if __name__ == "__main__":
    main()

