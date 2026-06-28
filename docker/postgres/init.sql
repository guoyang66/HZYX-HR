-- HZYX-HR PostgreSQL 初始化脚本
-- @author QinFeng Luo
-- @date 2026/01/09

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- pgvector 向量扩展已不再使用

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) NOT NULL,
    preferred_model VARCHAR(50) DEFAULT 'aliyun',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 岗位表
CREATE TABLE IF NOT EXISTS positions (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    company VARCHAR(100),
    salary_range VARCHAR(50),
    experience VARCHAR(50),
    education VARCHAR(50),
    location VARCHAR(50),
    responsibilities TEXT,
    requirements TEXT,
    skills TEXT[],
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 简历表
CREATE TABLE IF NOT EXISTS resumes (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) NOT NULL,
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    content TEXT,
    extracted_skills TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 匹配记录表
CREATE TABLE IF NOT EXISTS match_records (
    id BIGSERIAL PRIMARY KEY,
    resume_id BIGINT REFERENCES resumes(id) NOT NULL,
    position_id BIGINT REFERENCES positions(id) NOT NULL,
    final_score REAL,
    rag_score REAL,
    graph_score REAL,
    llm_score REAL,
    matched_skills TEXT[],
    missing_skills TEXT[],
    llm_report TEXT,
    matched_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 面试题记录表
CREATE TABLE IF NOT EXISTS interview_records (
    id BIGSERIAL PRIMARY KEY,
    position_id BIGINT REFERENCES positions(id),
    user_id BIGINT REFERENCES users(id) NOT NULL,
    difficulty VARCHAR(20),
    question_type VARCHAR(20),
    questions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_positions_title ON positions(title);
CREATE INDEX IF NOT EXISTS idx_positions_created_by ON positions(created_by);
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_match_records_resume_id ON match_records(resume_id);
CREATE INDEX IF NOT EXISTS idx_match_records_position_id ON match_records(position_id);
CREATE INDEX IF NOT EXISTS idx_interview_records_user_id ON interview_records(user_id);
CREATE INDEX IF NOT EXISTS idx_interview_records_position_id ON interview_records(position_id);

-- 插入演示用户（密码: password，使用 BCrypt 加密）
INSERT INTO users (username, password, email, role, preferred_model)
VALUES 
    ('hr_admin', '$2b$10$wrA6F7V7jdctCpWMqe3oZ.M0TZo22ql54qFIhWfohsf9jmOYe1m0m', 'hr@smarthr.com', 'HR', 'aliyun'),
    ('interviewer_admin', '$2b$10$.FFINX6Pzzi585b1flaPQePV.kYw2OsDwq7hWsZyf74GLGlzbKCxK', 'interviewer@smarthr.com', 'INTERVIEWER', 'aliyun')
ON CONFLICT (username) DO NOTHING;

COMMENT ON TABLE users IS '用户表';
COMMENT ON TABLE positions IS '岗位表';
COMMENT ON TABLE resumes IS '简历表';
COMMENT ON TABLE match_records IS '匹配记录表';
COMMENT ON TABLE interview_records IS '面试题记录表';
