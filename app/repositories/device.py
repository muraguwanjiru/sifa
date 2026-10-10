from sqlalchemy.orm import Session
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate

class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_devices(self, owner_id: int) -> list[Device]:
        return self.db.query(Device).filter(Device.owner_id == owner_id).all()

    def get_device_by_id(self, device_id: int, owner_id: int) -> Device | None:
        return self.db.query(Device).filter(Device.id == device_id, Device.owner_id == owner_id).first()

    def create_device(self, data: DeviceCreate, owner_id: int) -> Device:
        db_device = Device(
            name=data.name,
            status=data.status,
            owner_id=owner_id
        )
        self.db.add(db_device)
        self.db.commit()
        self.db.refresh(db_device)
        return db_device

    def update_device(self, db_device: Device, updates: DeviceUpdate) -> Device:
        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_device, key, value)
        self.db.commit()
        self.db.refresh(db_device)
        return db_device
