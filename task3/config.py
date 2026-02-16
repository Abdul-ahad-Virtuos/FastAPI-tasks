# Configuration file for JWT auth app
# Contains env vars and constants

import os
from datetime import timedelta

# JWT config - should come from env in prod
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-prod")
ALGORITHM = "HS256"
TOKEN_EXPIRATION = timedelta(minutes=int(os.getenv("TOKEN_EXPIRE_MINUTES", 30)))

# Database - using in memory dict for now
USERS_DB = {}
