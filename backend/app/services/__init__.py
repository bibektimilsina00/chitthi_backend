"""Service layer initialization."""

from app.services.auth_service import auth_service
from app.services.contact_service import contact_service
from app.services.conversation_service import conversation_service
from app.services.crypto_service import crypto_service
from app.services.device_service import device_service
from app.services.media_service import media_service
from app.services.message_service import message_service

from .item_service import item_service
from .user_service import user_service

# Export all services for easy importing
__all__ = [
    "auth_service",
    "contact_service",
    "conversation_service",
    "crypto_service",
    "device_service",
    "media_service",
    "message_service",
    "user_service",
    "item_service",
]
