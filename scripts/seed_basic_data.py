#!/usr/bin/env python3
"""
Simplified data seeding script for the chat application.
Creates basic test data without complex relationships to avoid SQLAlchemy issues.
"""

import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, create_engine

from app.core.config import settings
from app.core.security import get_password_hash


def create_basic_test_data():
    """Create basic test data using raw SQL to avoid relationship issues."""
    print("🌱 Starting simplified database seeding...")

    # Create engine
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    with Session(engine) as session:

        # Clear existing data
        print("🧹 Clearing existing data...")
        session.exec("DELETE FROM item")
        session.exec("DELETE FROM userprofile")
        session.exec("DELETE FROM user")
        session.commit()

        # Create users
        print("👥 Creating test users...")
        users_data = [
            {
                "id": str(uuid.uuid4()),
                "username": "alice_smith",
                "normalized_username": "alice_smith",
                "email": "alice@example.com",
                "display_name": "Alice Smith",
                "about": "Software engineer passionate about privacy and security",
                "password_hash": get_password_hash("password123"),
                "salt": "test_salt",
                "is_active": True,
                "is_superuser": True,
                "created_at": datetime.utcnow(),
            },
            {
                "id": str(uuid.uuid4()),
                "username": "bob_jones",
                "normalized_username": "bob_jones",
                "email": "bob@example.com",
                "display_name": "Bob Jones",
                "about": "Product manager who loves clean interfaces",
                "password_hash": get_password_hash("password123"),
                "salt": "test_salt",
                "is_active": True,
                "is_superuser": False,
                "created_at": datetime.utcnow(),
            },
            {
                "id": str(uuid.uuid4()),
                "username": "charlie_dev",
                "normalized_username": "charlie_dev",
                "email": "charlie@example.com",
                "display_name": "Charlie Developer",
                "about": "Full-stack developer building the future",
                "password_hash": get_password_hash("password123"),
                "salt": "test_salt",
                "is_active": True,
                "is_superuser": False,
                "created_at": datetime.utcnow(),
            },
        ]

        for user_data in users_data:
            session.exec(
                f"""
                INSERT INTO "user" (
                    id, username, normalized_username, email, display_name, about,
                    password_hash, salt, is_active, is_superuser, is_bot, created_at
                ) VALUES (
                    '{user_data["id"]}', '{user_data["username"]}', '{user_data["normalized_username"]}',
                    '{user_data["email"]}', '{user_data["display_name"]}', '{user_data["about"]}',
                    '{user_data["password_hash"]}', '{user_data["salt"]}', 
                    {user_data["is_active"]}, {user_data["is_superuser"]}, false, 
                    '{user_data["created_at"]}'
                )
            """
            )

        session.commit()

        # Create some items for users
        print("📋 Creating test items...")
        item_data = [
            {
                "id": str(uuid.uuid4()),
                "title": "Welcome to the Chat App",
                "description": "This is a sample item created during seeding",
                "owner_id": users_data[0]["id"],  # Alice's item
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Project Roadmap",
                "description": "Q4 roadmap for the chat application features",
                "owner_id": users_data[1]["id"],  # Bob's item
            },
            {
                "id": str(uuid.uuid4()),
                "title": "API Documentation",
                "description": "Complete REST API documentation for developers",
                "owner_id": users_data[2]["id"],  # Charlie's item
            },
        ]

        for item in item_data:
            session.exec(
                f"""
                INSERT INTO item (id, title, description, owner_id) 
                VALUES ('{item["id"]}', '{item["title"]}', '{item["description"]}', '{item["owner_id"]}')
            """
            )

        session.commit()

        # Create user profiles
        print("👤 Creating user profiles...")
        for user_data in users_data:
            profile_json = {
                "preferences": {
                    "theme": (
                        "dark" if user_data["username"] == "alice_smith" else "light"
                    ),
                    "notifications": {"push_enabled": True, "email_enabled": True},
                },
                "settings": {"language": "en", "auto_download_media": True},
            }

            # Convert dict to JSON string for SQL
            import json

            profile_json_str = json.dumps(profile_json).replace("'", "''")

            session.exec(
                f"""
                INSERT INTO userprofile (user_id, profile_json, updated_at) 
                VALUES ('{user_data["id"]}', '{profile_json_str}', '{datetime.utcnow()}')
            """
            )

        session.commit()

        print("\n🎉 Simplified database seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"   👥 Users: {len(users_data)}")
        print(f"   📋 Items: {len(item_data)}")
        print(f"   👤 Profiles: {len(users_data)}")

        print(f"\n🔐 Test Users (password: 'password123'):")
        for user in users_data:
            role = " (Superuser)" if user["is_superuser"] else ""
            print(f"   📧 {user['email']} - {user['display_name']}{role}")

        print(f"\n💡 Tips for testing:")
        print(f"   🌐 Start the server: uv run uvicorn app.main:app --reload")
        print(f"   📖 API docs: http://localhost:8000/docs")
        print(f"   🔑 Login with any test user using 'password123'")


if __name__ == "__main__":
    create_basic_test_data()
