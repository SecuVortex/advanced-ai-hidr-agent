"""SQLite Database - Phase 2 Task 2.5"""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger('HIDR.Database')

class Database:
    def __init__(self, db_path='hidr.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS threats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            process_name TEXT,
            pid INTEGER,
            path TEXT,
            threat_level INTEGER,
            yara_matches TEXT,
            mitre_techniques TEXT,
            action_taken TEXT,
            quarantine_path TEXT
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_processes INTEGER,
            threats_found INTEGER,
            scan_duration REAL
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metric_name TEXT,
            value REAL
        )''')
        
        # Phase 6: Add indexes for performance
        c.execute('CREATE INDEX IF NOT EXISTS idx_threats_timestamp ON threats(timestamp)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_threats_level ON threats(threat_level)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_scans_timestamp ON scans(timestamp)')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized with indexes: {self.db_path}")
    
    def add_threat(self, process_name, pid, path, threat_level, yara_matches, mitre_techniques, action_taken, quarantine_path=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO threats (process_name, pid, path, threat_level, yara_matches, mitre_techniques, action_taken, quarantine_path)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (process_name, pid, path, threat_level, str(yara_matches), str(mitre_techniques), action_taken, quarantine_path))
        conn.commit()
        conn.close()
    
    def add_scan(self, total_processes, threats_found, scan_duration):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO scans (total_processes, threats_found, scan_duration) VALUES (?, ?, ?)',
                  (total_processes, threats_found, scan_duration))
        conn.commit()
        conn.close()
    
    def get_threats_24h(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT timestamp, threat_level FROM threats 
                     WHERE timestamp >= datetime('now', '-24 hours')
                     ORDER BY timestamp''')
        results = c.fetchall()
        conn.close()
        return results
    
    def get_stats(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM threats')
        total_threats = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM scans')
        total_scans = c.fetchone()[0]
        c.execute('SELECT AVG(threat_level) FROM threats')
        avg_threat = c.fetchone()[0] or 0
        conn.close()
        return {'total_threats': total_threats, 'total_scans': total_scans, 'avg_threat': round(avg_threat, 1)}
