import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import CurrentUser, SessionDep
from app.schemas.common import Message
from app.schemas.device import DeviceCreate, DevicePublic, DevicesPublic, DeviceUpdate
from app.services import device_service

router = APIRouter()


@router.get("/", response_model=DevicesPublic)
def read_devices(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = Query(default=100, le=100),
) -> Any:
    """
    Retrieve devices for current user.
    """
    devices = device_service.get_user_devices(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )
    count = len(devices)
    devices_public = [DevicePublic.model_validate(device) for device in devices]
    return DevicesPublic(data=devices_public, count=count)


@router.post("/", response_model=DevicePublic)
def register_device(
    *, session: SessionDep, current_user: CurrentUser, device_in: DeviceCreate
) -> Any:
    """
    Register a new device.
    """
    device = device_service.register_device(
        session=session,
        user_id=current_user.id,
        device_id=device_in.device_id,
        device_name=device_in.device_name,
        platform=device_in.platform,
        push_token=getattr(device_in, "push_token", None),
        app_version=getattr(device_in, "app_version", None),
    )
    return DevicePublic.model_validate(device)


@router.get("/{id}", response_model=DevicePublic)
def read_device(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get device by ID.
    """
    from app import crud

    device = crud.device.get(session=session, id=id)
    if not device or device.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Device not found")

    return DevicePublic.model_validate(device)


@router.put("/{id}", response_model=DevicePublic)
def update_device(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    device_in: DeviceUpdate,
) -> Any:
    """
    Update a device.
    """
    device = device_service.update_device(
        session=session,
        device_id=id,
        user_id=current_user.id,
        updates=device_in.model_dump(exclude_unset=True),
    )
    return DevicePublic.model_validate(device)


@router.delete("/{id}")
def deregister_device(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Deregister a device.
    """
    device = device_service.revoke_device(
        session=session, device_id=id, user_id=current_user.id
    )
    return Message(message="Device deregistered")


@router.post("/{id}/verify")
def verify_device(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Verify a device for secure messaging.
    """
    # For now, just update the device activity to mark it as recently used
    device = device_service.update_device_activity(
        session=session, device_id=id, user_id=current_user.id
    )
    return Message(message="Device verified")


@router.get("/{id}/keys", response_model=dict)
def get_device_keys(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get public keys for a device.
    """
    from app import crud

    device = crud.device.get(session=session, id=id)
    if not device or device.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Device not found")

    # For now, return basic device info - crypto keys would be implemented later
    return {
        "device_id": device.device_id,
        "device_name": device.device_name,
        "platform": device.platform,
        "public_key": "placeholder_key",  # Would be actual crypto key in production
    }
