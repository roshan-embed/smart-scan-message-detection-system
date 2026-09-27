import os
import socket
from app import create_app
from database.init_db import init_database

# Initialize database tables and seed data if needed
init_database()

# Create Flask application
app = create_app()

def get_lan_ip():
    """Detect local area network IP for mobile device access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    lan_ip = get_lan_ip()

    print(f"\n=======================================================")
    print(f" SMART SCAM MESSAGE DETECTION SYSTEM")
    print(f" Architecture: MVC + 3-Tier Layered Architecture")
    print(f" Laptop Local Access  : http://127.0.0.1:{port}")
    print(f" Phone / Network Access: http://{lan_ip}:{port}")
    print(f"=======================================================\n")
    app.run(host=host, port=port, debug=debug)
