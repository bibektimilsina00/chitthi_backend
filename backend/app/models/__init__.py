# Model imports for SQLModel metadata
from app.models.auth import OAuthProvider, RefreshToken, UserSession
from app.models.contact import Block, Contact
from app.models.conversation import (
    Conversation,
    ConversationMember,
    ConversationSettings,
)
from app.models.crypto import DeviceKeys, IdentityKeys, KeyBackups, OneTimePrekeys
from app.models.device import Device
from app.models.item import Item
from app.models.media import MediaStore, PushNotifications
from app.models.message import (
    Message,
    MessageAttachment,
    MessageDrafts,
    MessageEditHistory,
    MessageEncryptedKeys,
    MessageParticipantsCache,
    MessageReaction,
    MessageStatus,
    PinnedItems,
    ReadReceiptsSummary,
    StarredMessages,
)
from app.models.moderation import (
    CallLogs,
    ModerationLogs,
    Reports,
    ScheduledMessages,
    UserBans,
)
from app.models.user import User, UserProfile

__all__ = [
    "User",
    "UserProfile",
    "Item",
    "Device",
    "Conversation",
    "ConversationMember",
    "ConversationSettings",
    "Message",
    "MessageParticipantsCache",
    "MessageEncryptedKeys",
    "MessageAttachment",
    "MessageStatus",
    "MessageReaction",
    "ReadReceiptsSummary",
    "PinnedItems",
    "StarredMessages",
    "MessageEditHistory",
    "MessageDrafts",
    "UserSession",
    "RefreshToken",
    "OAuthProvider",
    "IdentityKeys",
    "OneTimePrekeys",
    "DeviceKeys",
    "KeyBackups",
    "Contact",
    "Block",
    "MediaStore",
    "PushNotifications",
    "Reports",
    "ModerationLogs",
    "UserBans",
    "ScheduledMessages",
    "CallLogs",
]
