import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from app.models.user import User
from app.models.device import Device
from app.repositories.device import DeviceRepository
from app.repositories.user import UserRepository
from app.schemas.device import DeviceCreate, DeviceUpdate
from app.schemas.user import UserCreate
from app.services.user import register_user
from app.core import security

TEST_DATABASE_URL = "sqlite:///./test_sifa.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def user_owner(db_session):
    """Create a user who will own devices"""
    user_data = UserCreate(
        email="device_owner@sifa.com",
        full_name="Device Owner",
        password="SecurePassword123"
    )
    return register_user(db_session, user_data)

@pytest.fixture
def other_user(db_session):
    """Create another user to test access control"""
    user_data = UserCreate(
        email="other_user@sifa.com",
        full_name="Other User",
        password="SecurePassword123"
    )
    return register_user(db_session, user_data)

@pytest.fixture
def device_in_db(db_session, user_owner):
    """Create a device in the database for the owner"""
    device = Device(
        name="TestDevice",
        status="online",
        owner_id=user_owner.id
    )
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)
    return device

@pytest.fixture
def multiple_devices_in_db(db_session, user_owner, other_user):
    """Create multiple devices for different users"""
    # Devices for user_owner
    device1 = Device(name="Device1", status="online", owner_id=user_owner.id)
    device2 = Device(name="Device2", status="offline", owner_id=user_owner.id)
    
    # Devices for other_user
    device3 = Device(name="Device3", status="online", owner_id=other_user.id)
    
    db_session.add_all([device1, device2, device3])
    db_session.commit()
    
    return {"owner": [device1, device2], "other": [device3], "user_owner": user_owner, "other_user": other_user}


class TestGetUserDevices:
    """Test getting devices owned by a specific user"""
    
    def test_get_user_devices_returns_only_user_owned_devices(self, db_session, multiple_devices_in_db):
        """Test that get_user_devices returns only devices owned by the specified user"""
        user_owner = multiple_devices_in_db["user_owner"]
        repo = DeviceRepository(db_session)
        
        devices = repo.get_user_devices(user_owner.id)
        
        assert len(devices) == 2
        assert all(device.owner_id == user_owner.id for device in devices)
        assert any(device.name == "Device1" for device in devices)
        assert any(device.name == "Device2" for device in devices)
    
    def test_get_user_devices_excludes_other_users_devices(self, db_session, multiple_devices_in_db):
        """Test that get_user_devices does not return devices from other users"""
        user_owner = multiple_devices_in_db["user_owner"]
        repo = DeviceRepository(db_session)
        
        devices = repo.get_user_devices(user_owner.id)
        device_names = [device.name for device in devices]
        
        assert "Device3" not in device_names
    
    def test_get_user_devices_returns_empty_for_user_with_no_devices(self, db_session, user_owner, other_user):
        """Test that get_user_devices returns empty list for user with no devices"""
        repo = DeviceRepository(db_session)
        
        # other_user has no devices
        devices = repo.get_user_devices(other_user.id)
        
        assert len(devices) == 0
        assert devices == []


class TestGetDeviceById:
    """Test getting a specific device by ID with ownership verification"""
    
    def test_get_device_by_id_returns_device_if_owner(self, db_session, device_in_db, user_owner):
        """Test that get_device_by_id returns device if user is the owner"""
        repo = DeviceRepository(db_session)
        
        device = repo.get_device_by_id(device_in_db.id, user_owner.id)
        
        assert device is not None
        assert device.id == device_in_db.id
        assert device.name == "TestDevice"
        assert device.owner_id == user_owner.id
    
    def test_get_device_by_id_returns_none_if_not_owner(self, db_session, device_in_db, other_user):
        """Test that get_device_by_id returns None if user is not the owner"""
        repo = DeviceRepository(db_session)
        
        device = repo.get_device_by_id(device_in_db.id, other_user.id)
        
        assert device is None
    
    def test_get_device_by_id_returns_none_if_device_not_found(self, db_session, user_owner):
        """Test that get_device_by_id returns None for non-existent device"""
        repo = DeviceRepository(db_session)
        
        device = repo.get_device_by_id(9999, user_owner.id)
        
        assert device is None


class TestCreateDevice:
    """Test creating a new device for a user"""
    
    def test_create_device_success(self, db_session, user_owner):
        """Test successfully creating a new device"""
        repo = DeviceRepository(db_session)
        device_data = DeviceCreate(name="NewDevice", status="online")
        
        new_device = repo.create_device(device_data, user_owner.id)
        
        assert new_device.id is not None
        assert new_device.name == "NewDevice"
        assert new_device.status == "online"
        assert new_device.owner_id == user_owner.id
    
    def test_create_device_with_default_status(self, db_session, user_owner):
        """Test creating a device with default status"""
        repo = DeviceRepository(db_session)
        device_data = DeviceCreate(name="DefaultStatusDevice")
        
        new_device = repo.create_device(device_data, user_owner.id)
        
        assert new_device.status == "offline"
        assert new_device.owner_id == user_owner.id
    
    def test_create_multiple_devices_for_same_user(self, db_session, user_owner):
        """Test creating multiple devices for the same user"""
        repo = DeviceRepository(db_session)
        device_data1 = DeviceCreate(name="Device1", status="online")
        device_data2 = DeviceCreate(name="Device2", status="offline")
        
        device1 = repo.create_device(device_data1, user_owner.id)
        device2 = repo.create_device(device_data2, user_owner.id)
        
        assert device1.id != device2.id
        assert device1.owner_id == user_owner.id
        assert device2.owner_id == user_owner.id
        
        # Verify both devices are in the database for this user
        devices = repo.get_user_devices(user_owner.id)
        assert len(devices) == 2


class TestUpdateDevice:
    """Test updating an existing device"""
    
    def test_update_device_name(self, db_session, device_in_db):
        """Test updating device name"""
        repo = DeviceRepository(db_session)
        update_data = DeviceUpdate(name="UpdatedDeviceName")
        
        updated_device = repo.update_device(device_in_db, update_data)
        
        assert updated_device.name == "UpdatedDeviceName"
        assert updated_device.status == "online"  # status unchanged
    
    def test_update_device_status(self, db_session, device_in_db):
        """Test updating device status"""
        repo = DeviceRepository(db_session)
        update_data = DeviceUpdate(status="offline")
        
        updated_device = repo.update_device(device_in_db, update_data)
        
        assert updated_device.status == "offline"
        assert updated_device.name == "TestDevice"  # name unchanged
    
    def test_update_device_multiple_fields(self, db_session, device_in_db):
        """Test updating multiple fields at once"""
        repo = DeviceRepository(db_session)
        update_data = DeviceUpdate(name="NewName", status="offline")
        
        updated_device = repo.update_device(device_in_db, update_data)
        
        assert updated_device.name == "NewName"
        assert updated_device.status == "offline"
    
    def test_update_device_persists_to_database(self, db_session, device_in_db, user_owner):
        """Test that updated device changes persist in the database"""
        repo = DeviceRepository(db_session)
        update_data = DeviceUpdate(name="PersistentName", status="maintenance")
        
        repo.update_device(device_in_db, update_data)
        
        # Fetch the device again from the database
        retrieved_device = repo.get_device_by_id(device_in_db.id, user_owner.id)
        
        assert retrieved_device.name == "PersistentName"
        assert retrieved_device.status == "maintenance"


class TestDeviceAccessControl:
    """Test that devices are properly protected and only accessible by their owner"""
    
    def test_user_cannot_access_other_users_device(self, db_session, device_in_db, other_user):
        """Test that a user cannot get a device they don't own"""
        repo = DeviceRepository(db_session)
        
        device = repo.get_device_by_id(device_in_db.id, other_user.id)
        
        assert device is None
    
    def test_user_sees_only_own_devices_in_list(self, db_session, multiple_devices_in_db):
        """Test that user can only see their own devices when listing"""
        user_owner = multiple_devices_in_db["user_owner"]
        other_user = multiple_devices_in_db["other_user"]
        repo = DeviceRepository(db_session)
        
        owner_devices = repo.get_user_devices(user_owner.id)
        other_user_devices = repo.get_user_devices(other_user.id)
        
        assert len(owner_devices) == 2
        assert len(other_user_devices) == 1
        
        # Verify no overlap
        owner_ids = {d.owner_id for d in owner_devices}
        other_ids = {d.owner_id for d in other_user_devices}
        
        assert owner_ids == {user_owner.id}
        assert other_ids == {other_user.id}
