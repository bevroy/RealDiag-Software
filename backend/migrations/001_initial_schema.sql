-- RealDiag Initial Database Schema
-- PostgreSQL 15+
-- Migration: 001_initial_schema.sql
-- Created: 2025-11-19

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    specialty VARCHAR(100),
    institution VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    search_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_specialty ON users(specialty);

-- User settings table
CREATE TABLE user_settings (
    user_id VARCHAR(50) PRIMARY KEY,
    default_specialty VARCHAR(100),
    notification_preferences JSONB DEFAULT '{"email_updates": true, "new_features": true, "weekly_digest": false}'::jsonb,
    display_preferences JSONB DEFAULT '{"theme": "light", "results_per_page": 10, "show_icd_codes": true, "show_snomed_codes": false}'::jsonb,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Search history table
CREATE TABLE search_history (
    search_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    symptoms JSONB NOT NULL,
    age INTEGER,
    sex VARCHAR(20),
    family VARCHAR(100),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    result_count INTEGER DEFAULT 0,
    top_diagnosis VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_search_history_user_timestamp ON search_history(user_id, timestamp DESC);
CREATE INDEX idx_search_history_timestamp ON search_history(timestamp DESC);

-- Favorites table
CREATE TABLE favorites (
    favorite_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    rule_id VARCHAR(100) NOT NULL,
    diagnosis_label VARCHAR(255) NOT NULL,
    family VARCHAR(100) NOT NULL,
    notes TEXT,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE (user_id, rule_id)
);

CREATE INDEX idx_favorites_user_added ON favorites(user_id, added_at DESC);
CREATE INDEX idx_favorites_family ON favorites(family);

-- Custom lists table
CREATE TABLE custom_lists (
    list_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    specialty VARCHAR(100),
    diagnoses JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_public BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_custom_lists_user_created ON custom_lists(user_id, created_at DESC);
CREATE INDEX idx_custom_lists_public ON custom_lists(is_public, created_at DESC) WHERE is_public = TRUE;
CREATE INDEX idx_custom_lists_specialty ON custom_lists(specialty);

-- Refresh tokens table (for secure token rotation)
CREATE TABLE refresh_tokens (
    token_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- Audit log table (HIPAA compliance & security)
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details JSONB
);

CREATE INDEX idx_audit_log_user_timestamp ON audit_log(user_id, timestamp DESC);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_log_resource ON audit_log(resource_type, resource_id);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for user_settings
CREATE TRIGGER update_user_settings_updated_at
    BEFORE UPDATE ON user_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for custom_lists
CREATE TRIGGER update_custom_lists_updated_at
    BEFORE UPDATE ON custom_lists
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to clean up expired refresh tokens
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS void AS $$
BEGIN
    DELETE FROM refresh_tokens 
    WHERE expires_at < CURRENT_TIMESTAMP 
    OR revoked = TRUE;
END;
$$ LANGUAGE plpgsql;

-- Grants (adjust as needed for your database user)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO realdiag_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO realdiag_user;

-- Verification queries
DO $$ 
BEGIN
    RAISE NOTICE 'Schema created successfully!';
    RAISE NOTICE 'Tables created: %', (SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public');
    RAISE NOTICE 'Indexes created: %', (SELECT count(*) FROM pg_indexes WHERE schemaname = 'public');
END $$;
