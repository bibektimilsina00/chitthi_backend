from .base import CRUDBase
from .crud_auth import oauth_provider, refresh_token, user_session
from .crud_contact import block, contact, contact_permissions
from .crud_conversation import conversation, conversation_member
from .crud_crypto import device_keys, identity_keys, key_backups, one_time_prekeys
from .crud_device import device, push_notifications
from .crud_item import item
from .crud_media import media_stores
from .crud_message import (
    message,
    message_attachment,
    message_drafts,
    message_encrypted_keys,
    message_reaction,
    message_status,
    starred_messages,
)
from .crud_moderation import (
    bans,
    call_logs,
    reported_message,
    reports,
    scheduled_messages,
)
from .crud_user import user

__all__ = [
    "CRUDBase",
    # User management
    "user",
    # Auth
    "user_session",
    "refresh_token",
    "oauth_provider",
    # Devices
    "device",
    "push_notifications",
    # Crypto
    "identity_keys",
    "one_time_prekeys",
    "device_keys",
    "key_backups",
    # Contacts
    "contact",
    "block",
    "contact_permissions",
    # Conversations
    "conversation",
    "conversation_member",
    # Messages
    "message",
    "message_attachment",
    "message_encrypted_keys",
    "message_status",
    "message_reaction",
    "starred_messages",
    "message_drafts",
    # Media
    "media_stores",
    # Moderation
    "reports",
    "bans",
    "scheduled_messages",
    "call_logs",
    "reported_message",
    # Items (legacy)
    "item",
]
