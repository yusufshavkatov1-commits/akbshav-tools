CREATE TABLE IF NOT EXISTS app_users (
    telegram_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language TEXT NOT NULL DEFAULT 'ru' CHECK(language IN ('ru','uz','en')),
    rules_accepted BOOLEAN NOT NULL DEFAULT FALSE,
    subscription_ok BOOLEAN NOT NULL DEFAULT FALSE,
    blocked BOOLEAN NOT NULL DEFAULT FALSE,
    strikes INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS app_business_connections (
    user_id BIGINT PRIMARY KEY REFERENCES app_users(telegram_id) ON DELETE CASCADE,
    connection_id TEXT NOT NULL UNIQUE,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    rights_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS app_admins (
    telegram_id BIGINT PRIMARY KEY,
    role TEXT NOT NULL DEFAULT 'admin' CHECK(role IN ('owner','admin','moderator')),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS app_admin_permissions (
    telegram_id BIGINT NOT NULL REFERENCES app_admins(telegram_id) ON DELETE CASCADE,
    permission TEXT NOT NULL,
    PRIMARY KEY(telegram_id, permission)
);
CREATE TABLE IF NOT EXISTS app_admin_sessions (
    telegram_id BIGINT PRIMARY KEY REFERENCES app_admins(telegram_id) ON DELETE CASCADE,
    session_hash TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS app_admin_logins (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    success BOOLEAN NOT NULL,
    ip TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS app_admin_actions (
    id BIGSERIAL PRIMARY KEY,
    admin_id BIGINT NOT NULL,
    action TEXT NOT NULL,
    target_id BIGINT,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS app_tickets (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES app_users(telegram_id) ON DELETE CASCADE,
    topic TEXT NOT NULL DEFAULT 'other',
    status TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('new','in_progress','answered','waiting_user','closed','rejected')),
    assigned_admin_id BIGINT,
    unread_user INTEGER NOT NULL DEFAULT 0,
    unread_admin INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS app_ticket_messages (
    id BIGSERIAL PRIMARY KEY,
    ticket_id BIGINT NOT NULL REFERENCES app_tickets(id) ON DELETE CASCADE,
    sender_type TEXT NOT NULL CHECK(sender_type IN ('user','admin')),
    sender_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS app_ticket_ratings (
    id BIGSERIAL PRIMARY KEY,
    ticket_id BIGINT NOT NULL UNIQUE REFERENCES app_tickets(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL,
    admin_id BIGINT,
    stars INTEGER NOT NULL CHECK(stars BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS app_functions (
    key TEXT PRIMARY KEY,
    category TEXT NOT NULL DEFAULT 'tools',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    usage_count BIGINT NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS app_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS app_events (
    id BIGSERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    delivered BOOLEAN NOT NULL DEFAULT FALSE,
    locked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    delivered_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS app_message_archive (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES app_users(telegram_id) ON DELETE CASCADE,
    connection_id TEXT NOT NULL,
    chat_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    sender_id BIGINT,
    text TEXT,
    message_date TIMESTAMPTZ,
    kind TEXT NOT NULL DEFAULT 'text',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(connection_id, chat_id, message_id)
);
CREATE TABLE IF NOT EXISTS app_quick_replies (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES app_users(telegram_id) ON DELETE CASCADE,
    shortcut TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, shortcut)
);
CREATE TABLE IF NOT EXISTS app_auto_replies (
    user_id BIGINT PRIMARY KEY REFERENCES app_users(telegram_id) ON DELETE CASCADE,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    text TEXT NOT NULL DEFAULT '',
    cooldown_seconds INTEGER NOT NULL DEFAULT 30,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_reply_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS app_usage (
    user_id BIGINT NOT NULL REFERENCES app_users(telegram_id) ON DELETE CASCADE,
    function_key TEXT NOT NULL,
    used_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS app_jobs (
    id BIGSERIAL PRIMARY KEY,
    job_type TEXT NOT NULL,
    user_id BIGINT REFERENCES app_users(telegram_id) ON DELETE CASCADE,
    run_at TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','processing','done','failed','cancelled')),
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    locked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS app_broadcasts (
    id BIGSERIAL PRIMARY KEY,
    admin_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    audience TEXT NOT NULL DEFAULT 'all',
    status TEXT NOT NULL DEFAULT 'queued',
    sent INTEGER NOT NULL DEFAULT 0,
    failed INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_users_last_seen ON app_users(last_seen_at DESC);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON app_tickets(status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_delivery ON app_events(delivered, locked_at, created_at);
CREATE INDEX IF NOT EXISTS idx_archive_user ON app_message_archive(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_due ON app_jobs(status, run_at);


CREATE TABLE IF NOT EXISTS app_security_events (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'info',
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_security_events_created ON app_security_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_events_user ON app_security_events(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS app_function_errors (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    function_key TEXT NOT NULL,
    error_code TEXT NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_function_errors_created ON app_function_errors(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_function_errors_function ON app_function_errors(function_key, created_at DESC);

CREATE TABLE IF NOT EXISTS app_localization_strings (
    language TEXT NOT NULL CHECK(language IN ('ru','uz','en')),
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_by BIGINT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(language,key)
);

CREATE TABLE IF NOT EXISTS app_promotion_events (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES app_users(telegram_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL CHECK(event_type IN ('shown','continued','subscribed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_promotion_events ON app_promotion_events(event_type, created_at DESC);

CREATE TABLE IF NOT EXISTS app_rate_limits (
    user_id BIGINT NOT NULL,
    bucket TEXT NOT NULL,
    window_started_at TIMESTAMPTZ NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(user_id,bucket)
);

ALTER TABLE app_message_archive ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE app_broadcasts ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMPTZ;
ALTER TABLE app_broadcasts ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMPTZ;
ALTER TABLE app_broadcasts ADD COLUMN IF NOT EXISTS targeted INTEGER NOT NULL DEFAULT 0;
ALTER TABLE app_broadcasts ADD COLUMN IF NOT EXISTS language TEXT;
ALTER TABLE app_broadcasts ADD COLUMN IF NOT EXISTS active_only BOOLEAN NOT NULL DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_broadcasts_scheduled ON app_broadcasts(status, scheduled_at);


CREATE TABLE IF NOT EXISTS app_user_states (
    user_id BIGINT PRIMARY KEY REFERENCES app_users(telegram_id) ON DELETE CASCADE,
    state TEXT NOT NULL,
    data JSONB NOT NULL DEFAULT '{}'::jsonb,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '30 minutes'),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_user_states_expiry ON app_user_states(expires_at);

CREATE TABLE IF NOT EXISTS app_admin_states (
    admin_id BIGINT PRIMARY KEY REFERENCES app_admins(telegram_id) ON DELETE CASCADE,
    state TEXT NOT NULL,
    data JSONB NOT NULL DEFAULT '{}'::jsonb,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '15 minutes'),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_admin_states_expiry ON app_admin_states(expires_at);

CREATE TABLE IF NOT EXISTS app_function_registry (
    key TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0.0',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    description TEXT NOT NULL DEFAULT ''
);


CREATE TABLE IF NOT EXISTS app_broadcast_deliveries (
    broadcast_id BIGINT NOT NULL REFERENCES app_broadcasts(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES app_users(telegram_id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK(status IN ('sent','failed')),
    error TEXT,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(broadcast_id,user_id)
);
CREATE INDEX IF NOT EXISTS idx_broadcast_deliveries_status ON app_broadcast_deliveries(broadcast_id,status);
