-- 校园失物招领系统数据库设计

-- 创建数据库
CREATE DATABASE IF NOT EXISTS lost_found_db DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE lost_found_db;

-- 1. 物品类型表
CREATE TABLE IF NOT EXISTS item_category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '类型名称',
    parent_id INT DEFAULT NULL COMMENT '父类型ID，用于多级分类',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 地点表
CREATE TABLE IF NOT EXISTS location (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '地点名称',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_location_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 用户表
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL COMMENT '用户名（学号/工号）',
    password VARCHAR(128) NOT NULL COMMENT '密码',
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    phone VARCHAR(20) NOT NULL COMMENT '联系电话',
    role ENUM('student', 'teacher', 'admin', 'system_admin') NOT NULL COMMENT '角色',
    status ENUM('normal', 'disabled') DEFAULT 'normal' COMMENT '账号状态',
    first_login BOOLEAN DEFAULT TRUE COMMENT '是否首次登录',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_username (username),
    INDEX idx_role (role),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 公告表
CREATE TABLE IF NOT EXISTS announcement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL COMMENT '公告标题',
    content TEXT NOT NULL COMMENT '公告内容',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否生效',
    created_by INT NOT NULL COMMENT '创建人ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_is_active (is_active),
    FOREIGN KEY (created_by) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 失物信息表
CREATE TABLE IF NOT EXISTS lost_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '发布人ID',
    name VARCHAR(100) NOT NULL COMMENT '物品名称',
    category_id INT NOT NULL COMMENT '物品类型ID',
    location_id INT NOT NULL COMMENT '丢失地点ID',
    lost_time DATETIME NOT NULL COMMENT '丢失时间',
    description TEXT NOT NULL COMMENT '物品特征描述',
    reward_amount DECIMAL(10,2) DEFAULT 0 COMMENT '悬赏金额',
    reward_description VARCHAR(200) DEFAULT NULL COMMENT '悬赏说明',
    contact_name VARCHAR(50) NOT NULL COMMENT '联系人姓名',
    contact_phone VARCHAR(20) NOT NULL COMMENT '联系电话',
    status ENUM('pending', 'approved', 'matched', 'claimed', 'rejected', 'cancelled') DEFAULT 'pending' COMMENT '状态',
    reject_reason VARCHAR(200) DEFAULT NULL COMMENT '驳回原因',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_category_id (category_id),
    INDEX idx_location_id (location_id),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES item_category(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES location(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. 招领信息表
CREATE TABLE IF NOT EXISTS found_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '发布人ID',
    name VARCHAR(100) NOT NULL COMMENT '物品名称',
    category_id INT NOT NULL COMMENT '物品类型ID',
    location_id INT NOT NULL COMMENT '拾取地点ID',
    found_time DATETIME NOT NULL COMMENT '拾取时间',
    description TEXT NOT NULL COMMENT '物品特征描述',
    contact_name VARCHAR(50) NOT NULL COMMENT '联系人姓名',
    contact_phone VARCHAR(20) NOT NULL COMMENT '联系电话',
    status ENUM('pending', 'approved', 'claimed', 'rejected', 'archived') DEFAULT 'pending' COMMENT '状态',
    reject_reason VARCHAR(200) DEFAULT NULL COMMENT '驳回原因',
    archive_reason VARCHAR(200) DEFAULT NULL COMMENT '归档原因',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_category_id (category_id),
    INDEX idx_location_id (location_id),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES item_category(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES location(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. 图片表（用于存储失物和招领信息的照片）
CREATE TABLE IF NOT EXISTS item_image (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_type ENUM('lost', 'found') NOT NULL COMMENT '物品类型',
    item_id INT NOT NULL COMMENT '物品ID',
    image_url VARCHAR(255) NOT NULL COMMENT '图片URL',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_item_type_item_id (item_type, item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. 认领申请表
CREATE TABLE IF NOT EXISTS claim_application (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '申请人ID',
    found_item_id INT NOT NULL COMMENT '招领信息ID',
    lost_item_id INT DEFAULT NULL COMMENT '失物信息ID（如有）',
    additional_proof TEXT NOT NULL COMMENT '额外特征证明',
    status ENUM('pending', 'approved', 'rejected', 'claimed') DEFAULT 'pending' COMMENT '状态',
    reject_reason VARCHAR(200) DEFAULT NULL COMMENT '驳回原因',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_found_item_id (found_item_id),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (found_item_id) REFERENCES found_item(id) ON DELETE CASCADE,
    FOREIGN KEY (lost_item_id) REFERENCES lost_item(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. 操作日志表
CREATE TABLE IF NOT EXISTS operation_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    operator_id INT NOT NULL COMMENT '操作人ID',
    operation_type VARCHAR(50) NOT NULL COMMENT '操作类型',
    target_type VARCHAR(50) DEFAULT NULL COMMENT '操作目标类型',
    target_id INT DEFAULT NULL COMMENT '操作目标ID',
    operation_content TEXT NOT NULL COMMENT '操作内容',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_operator_id (operator_id),
    INDEX idx_operation_type (operation_type),
    FOREIGN KEY (operator_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. 站内通知表
CREATE TABLE IF NOT EXISTS notification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '接收用户ID',
    title VARCHAR(100) NOT NULL COMMENT '通知标题',
    content TEXT NOT NULL COMMENT '通知内容',
    is_read BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 初始化数据
-- 1. 物品类型
INSERT INTO item_category (name, parent_id) VALUES
('电子设备', NULL),
('手机', 1),
('电脑', 1),
('平板', 1),
('耳机', 1),
('证件', NULL),
('身份证', 6),
('学生证', 6),
('教师证', 6),
('银行卡', 6),
('文具', NULL),
('书包', 11),
('笔记本', 11),
('笔', 11),
('衣物', NULL),
('外套', 15),
('裤子', 15),
('鞋子', 15),
('其他', NULL);

-- 2. 地点
INSERT INTO location (name) VALUES
('教学楼A栋'),
('教学楼B栋'),
('教学楼C栋'),
('图书馆'),
('食堂1楼'),
('食堂2楼'),
('食堂3楼'),
('操场'),
('体育馆'),
('宿舍区'),
('校门口'),
('其他');

-- 3. 系统管理员账号（默认密码：123456，首次登录需修改）
INSERT INTO user (username, password, name, phone, role, status, first_login) VALUES
('admin', 'pbkdf2_sha256$600000$nJ6Wt3G9z6vzJ4Q4c4Q4c4$K7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f', '系统管理员', '13800138000', 'system_admin', 'normal', TRUE);
