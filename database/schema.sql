-- Queue Management System Database Schema (PostgreSQL)

-- Create database (if not exists)
-- (Usually handled outside the schema file in PostgreSQL)

-- Enable uuid-ossp extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create applications table
CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    callback_url VARCHAR(255) NOT NULL,
    api_key VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL
);

CREATE INDEX IF NOT EXISTS IX_applications_api_key ON applications(api_key);
CREATE INDEX IF NOT EXISTS IX_applications_created_at ON applications(created_at);
CREATE INDEX IF NOT EXISTS IX_applications_is_active ON applications(is_active);

-- Create queues table
CREATE TABLE IF NOT EXISTS queues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    max_users_per_minute INT DEFAULT 10 NOT NULL,
    priority INT DEFAULT 1 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL
);

CREATE INDEX IF NOT EXISTS IX_queues_application_id ON queues(application_id);
CREATE INDEX IF NOT EXISTS IX_queues_created_at ON queues(created_at);
CREATE INDEX IF NOT EXISTS IX_queues_is_active ON queues(is_active);

-- Create queue_users table
CREATE TABLE IF NOT EXISTS queue_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    queue_id UUID NOT NULL REFERENCES queues(id) ON DELETE CASCADE,
    visitor_id VARCHAR(64) NOT NULL,
    status VARCHAR(20) DEFAULT 'waiting' NOT NULL,
    token VARCHAR(64) UNIQUE NOT NULL,
    redirect_url VARCHAR(255),
    wait_time INT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
    CONSTRAINT CK_queue_users_status CHECK (status IN ('waiting', 'ready', 'expired', 'rejected'))
);

CREATE INDEX IF NOT EXISTS IX_queue_users_queue_id ON queue_users(queue_id);
CREATE INDEX IF NOT EXISTS IX_queue_users_visitor_id ON queue_users(visitor_id);
CREATE INDEX IF NOT EXISTS IX_queue_users_token ON queue_users(token);
CREATE INDEX IF NOT EXISTS IX_queue_users_status ON queue_users(status);
CREATE INDEX IF NOT EXISTS IX_queue_users_created_at ON queue_users(created_at);
CREATE INDEX IF NOT EXISTS IX_queue_users_expires_at ON queue_users(expires_at);

-- Create logs table
CREATE TABLE IF NOT EXISTS logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,
    message VARCHAR(255) NOT NULL,
    details TEXT,
    application_id UUID REFERENCES applications(id) ON DELETE SET NULL,
    queue_id UUID REFERENCES queues(id) ON DELETE SET NULL,
    queue_user_id UUID REFERENCES queue_users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL
);

CREATE INDEX IF NOT EXISTS IX_logs_event_type ON logs(event_type);
CREATE INDEX IF NOT EXISTS IX_logs_created_at ON logs(created_at);
CREATE INDEX IF NOT EXISTS IX_logs_application_id ON logs(application_id);
CREATE INDEX IF NOT EXISTS IX_logs_queue_id ON logs(queue_id);

-- Sample data for testing
INSERT INTO applications (id, name, domain, callback_url, api_key)
SELECT uuid_generate_v4(), 'Sample Application', 'sample.com', 'https://sample.com/callback', 'sample-api-key-123'
WHERE NOT EXISTS (SELECT 1 FROM applications WHERE name = 'Sample Application');

INSERT INTO queues (id, application_id, name, max_users_per_minute, priority)
SELECT uuid_generate_v4(), a.id, 'Main Queue', 10, 1 FROM applications a WHERE a.name = 'Sample Application'
AND NOT EXISTS (SELECT 1 FROM queues WHERE name = 'Main Queue');

-- Update triggers for updated_at (PostgreSQL uses triggers differently)
-- Example for applications table
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'tr_applications_updated_at') THEN
        CREATE TRIGGER tr_applications_updated_at
        BEFORE UPDATE ON applications
        FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'tr_queues_updated_at') THEN
        CREATE TRIGGER tr_queues_updated_at
        BEFORE UPDATE ON queues
        FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'tr_queue_users_updated_at') THEN
        CREATE TRIGGER tr_queue_users_updated_at
        BEFORE UPDATE ON queue_users
        FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'tr_logs_updated_at') THEN
        CREATE TRIGGER tr_logs_updated_at
        BEFORE UPDATE ON logs
        FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
    END IF;
END $$;

-- Done 