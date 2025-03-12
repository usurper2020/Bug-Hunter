CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    scan_type TEXT NOT NULL,
                    status TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    results TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                );