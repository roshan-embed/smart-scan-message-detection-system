import os
from app import create_app
from database.init_db import init_database

# Initialize database tables and seed data if needed
init_database()

# Create Flask application
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    print(f"\n=======================================================")
    print(f" SMART SCAM MESSAGE DETECTION SYSTEM")
    print(f" Module 1: User Account & Authentication [Active]")
    print(f" Architecture: MVC + 3-Tier Layered Architecture")
    print(f" Server running at: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host="127.0.0.1", port=port, debug=debug)
