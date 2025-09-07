from fastapi import APIRouter

from app.api.routes import (
    calls,
    contacts,
    conversations,
    devices,
    items,
    login,
    messages,
    users,
    utils,
    websocket,
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(
    conversations.router, prefix="/conversations", tags=["conversations"]
)
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(websocket.router, prefix="/chat", tags=["websocket"])
