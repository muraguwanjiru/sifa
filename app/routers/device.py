from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse
from app.repositories.device import DeviceRepository
from app.repositories.user import UserRepository
from app.services.auth_security import get_current_user_email

router = APIRouter(prefix="/devices", tags=["SIFA Device Management"])

@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_new_device(
    device_in: DeviceCreate,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email)
    
    device_repo = DeviceRepository(db)
    return device_repo.create_device(device_in, owner_id=user.id)

@router.get("/", response_model=list[DeviceResponse])
def list_my_devices(
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email)
    
    device_repo = DeviceRepository(db)
    return device_repo.get_user_devices(owner_id=user.id)

@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: int,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email)
    
    device_repo = DeviceRepository(db)
    db_device = device_repo.get_device_by_id(device_id, owner_id=user.id)
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or unauthorized access"
        )
    return db_device

@router.put("/{device_id}", response_model=DeviceResponse)
def update_existing_device(
    device_id: int,
    device_updates: DeviceUpdate,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email)
    
    device_repo = DeviceRepository(db)
    db_device = device_repo.get_device_by_id(device_id, owner_id=user.id)
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or unauthorized access"
        )
    return device_repo.update_device(db_device, device_updates)

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
    device_id: int,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email)
    
    device_repo = DeviceRepository(db)
    db_device = device_repo.get_device_by_id(device_id, owner_id=user.id)
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or unauthorized access"
        )
    db.delete(db_device)
    db.commit()
