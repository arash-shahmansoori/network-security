import os
import ssl

import certifi
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

load_dotenv()

# Prefer the same var used by app.py
MONGO_DB_URL = os.getenv("MONGODB_URL_KEY") or os.getenv("MONGO_DB_URL")

if not MONGO_DB_URL:
    raise SystemExit("MongoDB URL not configured. Set MONGODB_URL_KEY in your .env.")

# Create a new client and connect to the server with certifi CA bundle (needed for Atlas)
from pymongo.server_api import ServerApi

print(f"SSL/OpenSSL: {ssl.OPENSSL_VERSION}")
print(f"Certifi CA bundle: {certifi.where()}")
print("Attempting secure TLS connection (strict cert validation)...")

try:
    client = MongoClient(
        MONGO_DB_URL,
        tls=True,
        tlsCAFile=certifi.where(),
        server_api=ServerApi("1"),
    )
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Secure connection failed: {e}")
    print("Retrying with tlsAllowInvalidCertificates=True (NOT for production)...")
    try:
        client = MongoClient(
            MONGO_DB_URL,
            tls=True,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=True,
            server_api=ServerApi("1"),
        )
        client.admin.command("ping")
        print(
            "Connected with tlsAllowInvalidCertificates=True. This indicates a local TLS trust/proxy issue."
        )
    except Exception as e2:
        print(f"Fallback connection also failed: {e2}")
