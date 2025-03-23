-- SQLite database initialization for Bug Hunter

-- Users table (removed authentication fields)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    role TEXT DEFAULT 'user',
    CONSTRAINT valid_role CHECK (role IN ('admin', 'user', 'viewer'))
);

-- Scan Results table
CREATE TABLE scan_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id TEXT UNIQUE NOT NULL,
    target_url TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    total_findings INTEGER DEFAULT 0,
    scan_duration TEXT,
    scan_type TEXT,
    scan_parameters TEXT,
    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed'))
);

-- Findings table
CREATE TABLE findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER REFERENCES scan_results(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT NOT NULL,
    details TEXT,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified BOOLEAN DEFAULT 0,
    false_positive BOOLEAN DEFAULT 0,
    cvss_score REAL,
    cve_ids TEXT,
    CONSTRAINT valid_severity CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info'))
);

-- Reports table
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT UNIQUE NOT NULL,
    scan_id INTEGER REFERENCES scan_results(id) ON DELETE CASCADE,
    format TEXT NOT NULL,
    file_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    encrypted BOOLEAN DEFAULT 0,
    encryption_key TEXT,
    report_type TEXT,
    metadata TEXT,
    CONSTRAINT valid_format CHECK (format IN ('pdf', 'html', 'json', 'xml'))
);

-- Audit Logs table
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    details TEXT,
    success BOOLEAN DEFAULT 1,
    session_id TEXT
);

-- Scan Schedules table
CREATE TABLE scan_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_url TEXT NOT NULL,
    frequency TEXT NOT NULL,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scan_parameters TEXT,
    notification_email TEXT,
    CONSTRAINT valid_frequency CHECK (frequency IN ('daily', 'weekly', 'monthly', 'custom'))
);

-- API Rate Limits table
CREATE TABLE rate_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    endpoint TEXT NOT NULL,
    requests_count INTEGER DEFAULT 0,
    window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    limit_per_window INTEGER NOT NULL,
    window_size TEXT NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

CREATE INDEX idx_scan_results_timestamp ON scan_results(timestamp);
CREATE INDEX idx_scan_results_target ON scan_results(target_url);
CREATE INDEX idx_findings_severity ON findings(severity);
CREATE INDEX idx_findings_type ON findings(type);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_rate_limits_window ON rate_limits(window_start);
CREATE INDEX idx_rate_limits_user_endpoint ON rate_limits(user_id, endpoint);

-- Create views for common queries
CREATE VIEW high_severity_findings AS
SELECT f.*, s.target_url, s.scan_id
FROM findings f
JOIN scan_results s ON f.scan_id = s.id
WHERE f.severity IN ('critical', 'high')
ORDER BY f.discovered_at DESC;

CREATE VIEW user_scan_summary AS
SELECT
    u.username,
    COUNT(s.id) as total_scans,
    COUNT(f.id) as total_findings,
    MAX(s.timestamp) as last_scan_date,
    COUNT(CASE WHEN f.severity = 'critical' THEN 1 END) as critical_findings,
    COUNT(CASE WHEN f.severity = 'high' THEN 1 END) as high_findings
FROM users u
LEFT JOIN scan_results s ON u.id = s.created_by
LEFT JOIN findings f ON s.id = f.scan_id
GROUP BY u.id, u.username;
