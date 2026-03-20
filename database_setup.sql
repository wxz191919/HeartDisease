-- 创建数据库
CREATE DATABASE IF NOT EXISTS heart_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE heart_disease_db;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    role ENUM('doctor', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;



-- 创建患者表
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender ENUM('male', 'female') NOT NULL,
    age INT NOT NULL,
    contact_number VARCHAR(20),
    address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    doctor_id INT NOT NULL,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX (doctor_id)
) ENGINE=InnoDB;

-- 创建预测记录表
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(100) NOT NULL,
    prediction_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    probability FLOAT NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    result VARCHAR(200),
    features TEXT,
    INDEX (patient_name),
    INDEX (prediction_time)
) ENGINE=InnoDB;

-- 创建管理员账户
INSERT INTO users (username, password_hash, role) VALUES 
('admin', '$2b$12$1xxxxxxxxxxxxxxxxxxxxuZLbwxnpY0o58unSvIPxddLxGystLu', 'admin');

-- 注意: 上面的密码哈希是示例，实际应用中应该使用正确的哈希值
-- 可以使用Python的werkzeug.security.generate_password_hash函数生成密码哈希
-- 示例密码为 'admin123' 