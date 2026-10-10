from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class DeviceBase(BaseModel):
    name: str
    status: str = "offline"

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class DeviceResponse(DeviceBase):
    id: int
    last_seen: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
