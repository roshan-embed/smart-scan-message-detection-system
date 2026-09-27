-- =====================================================================
-- SMART SCAM MESSAGE DETECTION SYSTEM
-- Module 1: User Account & Authentication Database Schema (MySQL 8.0+)
-- Architecture: 3-Tier Layered Architecture (Data Tier)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS smart_scam_detection 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE smart_scam_detection;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone_number VARCHAR(25) DEFAULT NULL,
    bio TEXT DEFAULT NULL,
    role ENUM('admin', 'analyst', 'user') DEFAULT 'user',
    status ENUM('active', 'suspended', 'pending') DEFAULT 'active',
    last_login_at DATETIME DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_username (username),
    INDEX idx_user_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. User Sessions Table (Session Management & Multi-device Tracking)
CREATE TABLE IF NOT EXISTS user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(128) NOT NULL UNIQUE,
    ip_address VARCHAR(45) DEFAULT '127.0.0.1',
    user_agent TEXT DEFAULT NULL,
    device_info VARCHAR(100) DEFAULT 'Desktop / Web Browser',
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_session_token (session_token),
    INDEX idx_session_user (user_id),
    INDEX idx_session_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Login Audit Logs Table (Security Tracking & Brute-force Prevention)
CREATE TABLE IF NOT EXISTS login_audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT DEFAULT NULL,
    attempted_identifier VARCHAR(100) NOT NULL,
    status ENUM('success', 'failed', 'blocked') NOT NULL,
    ip_address VARCHAR(45) DEFAULT '127.0.0.1',
    user_agent TEXT DEFAULT NULL,
    failure_reason VARCHAR(255) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_audit_created (created_at),
    INDEX idx_audit_identifier (attempted_identifier)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- Module 2: Smart Message Scanner
-- Table: scanned_messages
-- =====================================================================
CREATE TABLE IF NOT EXISTS scanned_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message_type ENUM('sms', 'whatsapp', 'email', 'general') NOT NULL DEFAULT 'sms',
    sender_info VARCHAR(150) DEFAULT NULL,
    subject VARCHAR(255) DEFAULT NULL,
    raw_content TEXT NOT NULL,
    sanitized_content TEXT NOT NULL,
    char_count INT NOT NULL DEFAULT 0,
    word_count INT NOT NULL DEFAULT 0,
    extracted_urls TEXT DEFAULT NULL,
    extracted_phones TEXT DEFAULT NULL,
    extracted_emails TEXT DEFAULT NULL,
    has_urgency TINYINT(1) DEFAULT 0,
    scan_status ENUM('submitted', 'ready', 'analyzed', 'flagged') DEFAULT 'ready',
    threat_verdict VARCHAR(50) DEFAULT 'Pending Analysis',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_scan_user (user_id),
    INDEX idx_scan_type (message_type),
    INDEX idx_scan_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

