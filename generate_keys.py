#!/usr/bin/env python3
"""
Helper script to generate secure keys for your .env file
"""
import secrets
from cryptography.fernet import Fernet

print("=" * 60)
print("Generating secure keys for your .env file")
print("=" * 60)
print()

# Generate Flask Secret Key
flask_key = secrets.token_urlsafe(32)
print("FLASK_SECRET_KEY=" + flask_key)
print()

# Generate Fernet Key
fernet_key = Fernet.generate_key().decode()
print("FERNET_KEY=" + fernet_key)
print()

print("=" * 60)
print("Copy these values to your .env file")
print("=" * 60)
print()
print("IMPORTANT: Keep these keys secret and never commit them to git!")
print()

