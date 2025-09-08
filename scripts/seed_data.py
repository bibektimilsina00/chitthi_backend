#!/usr/bin/env python3
"""
Data seeding script for the chat application.
Creates test users, conversations, messages, and other data for testing.
"""

import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.auth import RefreshToken, UserSession
from app.models.contact import Contact
from app.models.conversation import (
    Conversation,
    ConversationMember,
    ConversationSettings,
)
from app.models.device import Device
from app.models.item import Item
from app.models.message import Message, MessageReaction, MessageStatus
from app.models.user import User, UserProfile


def create_test_users(session: Session) -> List[User]:
    """Create test users with realistic data."""
    users_data = [
        {
            "username": "alice_smith",
            "email": "alice@example.com",
            "display_name": "Alice Smith",
            "about": "Software engineer passionate about privacy and security",
            "is_active": True,
            "is_superuser": True,  # Make first user a superuser
        },
        {
            "username": "bob_jones",
            "email": "bob@example.com",
            "display_name": "Bob Jones",
            "about": "Product manager who loves clean interfaces",
            "is_active": True,
        },
        {
            "username": "charlie_dev",
            "email": "charlie@example.com",
            "display_name": "Charlie Developer",
            "about": "Full-stack developer building the future",
            "is_active": True,
        },
        {
            "username": "diana_ux",
            "email": "diana@example.com",
            "display_name": "Diana Cooper",
            "about": "UX designer focused on human-centered design",
            "is_active": True,
        },
        {
            "username": "eve_crypto",
            "email": "eve@example.com",
            "display_name": "Eve Cryptographer",
            "about": "Cryptography researcher and security enthusiast",
            "is_active": True,
        },
    ]

    users = []
    for user_data in users_data:
        # Check if user already exists
        existing = session.exec(
            select(User).where(User.username == user_data["username"])
        ).first()

        if existing:
            users.append(existing)
            continue

        # Create new user
        password_hash = get_password_hash("password123")  # Default password for testing
        user = User(
            username=user_data["username"],
            normalized_username=user_data["username"].lower(),
            email=user_data["email"],
            display_name=user_data["display_name"],
            about=user_data["about"],
            password_hash=password_hash,
            salt="test_salt",  # In production, this would be random
            is_active=user_data["is_active"],
            is_superuser=user_data.get("is_superuser", False),
        )
        session.add(user)
        users.append(user)

    session.commit()

    # Refresh to get IDs
    for user in users:
        session.refresh(user)

    print(f"✅ Created {len(users)} test users")
    return users


def create_test_devices(session: Session, users: List[User]) -> List[Device]:
    """Create test devices for users."""
    devices = []

    device_types = ["mobile", "desktop", "web"]
    platforms = ["iOS", "Android", "macOS", "Windows", "Web"]

    for i, user in enumerate(users):
        # Create 1-2 devices per user
        num_devices = 1 if i % 2 == 0 else 2

        for j in range(num_devices):
            device = Device(
                user_id=user.id,
                device_id=f"device_{user.username}_{j}",
                device_name=f"{user.display_name}'s {device_types[j % len(device_types)]}",
                platform=platforms[j % len(platforms)],
                app_version="1.0.0",
                push_token=f"push_token_{user.username}_{j}",
                last_seen=datetime.utcnow() - timedelta(minutes=j * 5),
            )
            session.add(device)
            devices.append(device)

    session.commit()

    # Refresh to get IDs
    for device in devices:
        session.refresh(device)

    print(f"✅ Created {len(devices)} test devices")
    return devices


def create_test_contacts(session: Session, users: List[User]) -> List[Contact]:
    """Create contact relationships between users."""
    contacts = []

    # Create a contact network where most users know each other
    for i, user in enumerate(users):
        for j, contact_user in enumerate(users):
            if i != j and i < j:  # Avoid self-contacts and duplicates
                contact = Contact(
                    owner_id=user.id,
                    contact_user_id=contact_user.id,
                    alias=contact_user.display_name,
                    is_favorite=(i + j) % 3 == 0,  # Some favorites
                )
                session.add(contact)
                contacts.append(contact)

                # Create reverse contact relationship
                reverse_contact = Contact(
                    owner_id=contact_user.id,
                    contact_user_id=user.id,
                    alias=user.display_name,
                    is_favorite=(i + j) % 4 == 0,
                )
                session.add(reverse_contact)
                contacts.append(reverse_contact)

    session.commit()
    print(f"✅ Created {len(contacts)} contact relationships")
    return contacts


def create_test_conversations(
    session: Session, users: List[User]
) -> List[Conversation]:
    """Create test conversations."""
    conversations = []

    # Create different types of conversations
    conversation_data = [
        {
            "title": "Project Alpha Team",
            "type": "group",
            "visibility": "private",
            "participants": users[:4],  # Alice, Bob, Charlie, Diana
        },
        {
            "title": "Security Discussion",
            "type": "group",
            "visibility": "private",
            "participants": [users[0], users[4]],  # Alice, Eve
        },
        {
            "title": "Design Reviews",
            "type": "group",
            "visibility": "private",
            "participants": [users[1], users[3]],  # Bob, Diana
        },
        {
            "title": None,  # Direct message (no title)
            "type": "direct",
            "visibility": "private",
            "participants": [users[0], users[1]],  # Alice, Bob
        },
        {
            "title": None,  # Direct message
            "type": "direct",
            "visibility": "private",
            "participants": [users[2], users[4]],  # Charlie, Eve
        },
    ]

    for conv_data in conversation_data:
        conversation = Conversation(
            title=conv_data["title"],
            type=conv_data["type"],
            visibility=conv_data["visibility"],
            creator_id=conv_data["participants"][0].id,
            member_count=len(conv_data["participants"]),
            archived=False,
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        # Add conversation members
        for participant in conv_data["participants"]:
            member = ConversationMember(
                conversation_id=conversation.id,
                user_id=participant.id,
                role=(
                    "admin" if participant == conv_data["participants"][0] else "member"
                ),
                unread_count=0,
            )
            session.add(member)

        conversations.append(conversation)

    session.commit()
    print(f"✅ Created {len(conversations)} test conversations")
    return conversations


def create_test_messages(
    session: Session, conversations: List[Conversation], users: List[User]
) -> List[Message]:
    """Create test messages in conversations."""
    messages = []

    # Sample message content for different conversation types
    message_templates = {
        "Project Alpha Team": [
            "Hey team! Let's kick off our new project discussion.",
            "I've prepared the initial requirements document. What do you think?",
            "Great work! I think we should focus on the user authentication first.",
            "Agreed! Security should be our top priority.",
            "I'll start working on the database schema design.",
        ],
        "Security Discussion": [
            "Have you seen the latest security best practices for E2E encryption?",
            "Yes! The Signal protocol documentation is really comprehensive.",
            "We should implement similar forward secrecy in our app.",
        ],
        "Design Reviews": [
            "The new UI mockups look fantastic!",
            "Thanks! I focused on improving the user experience flow.",
            "The color scheme really enhances readability.",
        ],
        "direct": [
            "Hey! How's the project going?",
            "Pretty well! Just finished the API documentation.",
            "That's awesome. Want to grab coffee later?",
            "Sure! How about 3 PM?",
            "Perfect! See you then.",
        ],
    }

    for conversation in conversations:
        # Get conversation participants
        members_result = session.exec(
            select(ConversationMember).where(
                ConversationMember.conversation_id == conversation.id
            )
        )
        members = list(members_result)

        # Choose message template
        template_key = conversation.title if conversation.title else "direct"
        templates = message_templates.get(template_key, message_templates["direct"])

        # Create messages
        for i, content in enumerate(templates):
            sender = members[i % len(members)].user_id

            # Create encrypted message (simplified for testing)
            message = Message(
                conversation_id=conversation.id,
                sender_id=sender,
                ciphertext=f"encrypted_{content}",  # In real app, this would be actual encryption
                ciphertext_nonce=f"nonce_{i}",
                encryption_algo="aes-256-gcm",
                message_type="text",
                preview_text_hash=f"hash_{i}",
                is_edited=False,
                is_deleted=False,
                created_at=datetime.utcnow() - timedelta(hours=len(templates) - i),
            )
            session.add(message)
            session.commit()
            session.refresh(message)

            # Update conversation's last message
            conversation.last_message_id = message.id
            session.add(conversation)

            # Create message status for all participants
            for member in members:
                status = MessageStatus(
                    message_id=message.id,
                    user_id=member.user_id,
                    status="delivered" if member.user_id != sender else "sent",
                )
                session.add(status)

            messages.append(message)

    session.commit()
    print(f"✅ Created {len(messages)} test messages")
    return messages


def create_test_items(session: Session, users: List[User]) -> List[Item]:
    """Create test items for users."""
    items = []

    item_templates = [
        {"title": "Meeting Notes", "description": "Notes from the weekly team meeting"},
        {
            "title": "Project Roadmap",
            "description": "Q4 roadmap for the chat application",
        },
        {
            "title": "API Documentation",
            "description": "Complete REST API documentation",
        },
        {"title": "User Stories", "description": "User stories for the next sprint"},
        {
            "title": "Security Audit",
            "description": "Security audit results and recommendations",
        },
    ]

    for i, user in enumerate(users):
        # Create 2-3 items per user
        num_items = 2 + (i % 2)

        for j in range(num_items):
            template = item_templates[j % len(item_templates)]
            item = Item(
                title=f"{template['title']} - {user.display_name}",
                description=template["description"],
                owner_id=user.id,
            )
            session.add(item)
            items.append(item)

    session.commit()
    print(f"✅ Created {len(items)} test items")
    return items


def create_test_user_profiles(session: Session, users: List[User]) -> List[UserProfile]:
    """Create extended user profiles."""
    profiles = []

    for user in users:
        # Check if profile already exists
        existing = session.exec(
            select(UserProfile).where(UserProfile.user_id == user.id)
        ).first()

        if existing:
            profiles.append(existing)
            continue

        profile_data = {
            "preferences": {
                "theme": "dark" if user.username.startswith("eve") else "light",
                "notifications": {
                    "push_enabled": True,
                    "email_enabled": user.username
                    != "charlie_dev",  # Charlie disabled emails
                    "sound_enabled": True,
                },
                "privacy": {
                    "read_receipts": True,
                    "last_seen": user.username != "diana_ux",  # Diana hides last seen
                    "profile_photo": True,
                },
            },
            "settings": {
                "language": "en",
                "auto_download_media": True,
                "message_preview": True,
            },
        }

        profile = UserProfile(
            user_id=user.id,
            profile_json=profile_data,
        )
        session.add(profile)
        profiles.append(profile)

    session.commit()
    print(f"✅ Created {len(profiles)} user profiles")
    return profiles


def main():
    """Main seeding function."""
    print("🌱 Starting database seeding...")

    # Create engine and session
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    with Session(engine) as session:
        # Create test data in dependency order
        users = create_test_users(session)
        devices = create_test_devices(session, users)
        contacts = create_test_contacts(session, users)
        conversations = create_test_conversations(session, users)
        messages = create_test_messages(session, conversations, users)
        items = create_test_items(session, users)
        profiles = create_test_user_profiles(session, users)

        print("\n🎉 Database seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"   👥 Users: {len(users)}")
        print(f"   📱 Devices: {len(devices)}")
        print(f"   🤝 Contacts: {len(contacts)}")
        print(f"   💬 Conversations: {len(conversations)}")
        print(f"   📨 Messages: {len(messages)}")
        print(f"   📋 Items: {len(items)}")
        print(f"   👤 Profiles: {len(profiles)}")

        print(f"\n🔐 Test Users (password: 'password123'):")
        for user in users:
            role = " (Superuser)" if user.is_superuser else ""
            print(f"   📧 {user.email} - {user.display_name}{role}")


if __name__ == "__main__":
    main()
