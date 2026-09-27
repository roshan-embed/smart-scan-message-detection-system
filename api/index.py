import sys
import os

# Add root directory to sys.path so app modules are discoverable
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

# Instantiate Flask WSGI application for Vercel Serverless
app = create_app()

_db_initialized = False

@app.before_request
def ensure_db_ready():
    global _db_initialized
    if not _db_initialized:
        try:
            from database.init_db import init_database
            init_database()
            _db_initialized = True
        except Exception as e:
            app.logger.warning(f"Database initialization deferred: {e}")
            _db_initialized = True

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
