-- Add missing columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_token TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_token_expires_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_token TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_expires_at TIMESTAMPTZ;

-- Add missing columns to oauth_identities
ALTER TABLE oauth_identities ADD COLUMN IF NOT EXISTS provider_email TEXT;
ALTER TABLE oauth_identities ADD COLUMN IF NOT EXISTS provider_name TEXT;
ALTER TABLE oauth_identities ADD COLUMN IF NOT EXISTS provider_avatar TEXT;

-- Add missing columns to user_quotas
ALTER TABLE user_quotas ADD COLUMN IF NOT EXISTS plan_id UUID REFERENCES plans(id);
ALTER TABLE user_quotas ADD COLUMN IF NOT EXISTS period_start TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE user_quotas ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

-- Set default plan for existing quotas
UPDATE user_quotas SET plan_id = (SELECT id FROM plans WHERE name = 'free' LIMIT 1) WHERE plan_id IS NULL;
