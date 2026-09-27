import sys
import os

# Add root directory to sys.path so app modules are discoverable
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app
from database.init_db import init_database

# Initialize database tables and seed data
init_database()

# Instantiate Flask WSGI application for Vercel Serverless
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
