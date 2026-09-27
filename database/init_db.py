import os
import sys

# Ensure root project path is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

from app.config import Config
from app.models.db import db
from app.models.user_model import UserModel
from werkzeug.security import generate_password_hash

def init_database():
    """
    Initializes database tables and creates initial seed users if not already present.
    """
    try:
        active_type = db.get_active_db_type() or "sqlite"
        print(f"[*] Initializing Database (Active Engine: {active_type.upper()})...")

        # If active engine is MySQL, run the schema.sql file
        if active_type == "mysql":
            schema_path = os.path.join(current_dir, "schema.sql")
            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as f:
                    sql_statements = f.read()
                
                # Execute individual statements
                commands = [cmd.strip() for cmd in sql_statements.split(";") if cmd.strip()]
                for cmd in commands:
                    try:
                        db.execute_query(cmd, commit=True)
                    except Exception as e:
                        print(f"[!] Warning executing statement: {e}")
                print("[+] MySQL schema applied successfully.")
        else:
            print("[+] SQLite tables already verified via DatabaseManager.")

        # Check if a sample default user exists, if not create one
        try:
            admin_email = "admin@scamdetect.internal"
            existing_admin = UserModel.get_by_email(admin_email)
            if not existing_admin:
                pwd_hash = generate_password_hash("Admin@12345!")
                UserModel.create(
                    username="sec_admin",
                    email=admin_email,
                    password_hash=pwd_hash,
                    first_name="Security",
                    last_name="Administrator",
                    phone_number="+1 555-0199",
                    role="admin"
                )
                print(f"[+] Created default administrative user: {admin_email} / Admin@12345!")

            analyst_email = "analyst@scamdetect.internal"
            existing_analyst = UserModel.get_by_email(analyst_email)
            if not existing_analyst:
                pwd_hash = generate_password_hash("Analyst@12345!")
                UserModel.create(
                    username="threat_analyst",
                    email=analyst_email,
                    password_hash=pwd_hash,
                    first_name="Cyber",
                    last_name="Analyst",
                    phone_number="+1 555-0144",
                    role="analyst"
                )
                print(f"[+] Created default analyst user: {analyst_email} / Analyst@12345!")
        except Exception as seed_err:
            print(f"[!] Warning seeding users: {seed_err}")

        print("[OK] Database initialization complete.")
    except Exception as e:
        print(f"[!] Database init warning: {e}")

if __name__ == "__main__":
    init_database()
