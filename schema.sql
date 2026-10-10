-- SIFA Database Schema and Entity Relationship Diagram (ERD)
-- This SQL file defines the complete database structure for the SIFA system

-- ============================================================================
-- Users Table
-- ============================================================================
-- Stores user account information
-- Relationships: One user can own many devices (1:N relationship with devices)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_is_active (is_active)
);

-- ============================================================================
-- Devices Table
-- ============================================================================
-- Stores device information
-- Relationships: 
--   - Many devices belong to one user (N:1 relationship with users)
--   - Foreign Key: owner_id references users.id with CASCADE delete
-- ============================================================================
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'offline',
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    owner_id INTEGER NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_devices_owner_id (owner_id),
    INDEX idx_devices_status (status),
    INDEX idx_devices_last_seen (last_seen)
);

-- ============================================================================
-- Entity Relationship Diagram (ERD) Description
-- ============================================================================
-- 
-- users (1) ----< (N) devices
--
-- One user can own multiple devices.
-- Each device is owned by exactly one user.
-- If a user is deleted, all their devices are also deleted (CASCADE).
--
-- Entity: users
--   - id: Primary Key (unique identifier)
--   - email: Unique email address for login (indexed)
--   - full_name: User's full name
--   - hashed_password: Securely hashed password
--   - is_active: Boolean flag for account status (indexed)
--   - created_at: Account creation timestamp
--
-- Entity: devices
--   - id: Primary Key (unique identifier)
--   - name: Device name/label
--   - status: Current device status (online/offline/maintenance)
--   - last_seen: Last activity timestamp
--   - owner_id: Foreign Key referencing users.id (indexed, enforces ownership)
--
-- ============================================================================
