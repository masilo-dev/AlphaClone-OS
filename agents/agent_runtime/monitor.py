"""
AlphaClone-OS System Monitor

Provides system-wide monitoring, metrics collection, and logging.
"""

import json
import logging
import os
import psutil
import socket
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_used: int
    memory_total: int
    disk_used: int
    disk_total: int
    network_sent: int
    network_recv: int
    timestamp: float

@dataclass
class AgentMetrics:
    """Per-agent metrics"""
    agent_id: str
    cpu_percent: float
    memory_rss: int
    fds_open: int
    threads: int
    timestamp: float

class MetricsDB:
    """Persistent storage for system metrics"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize metrics database"""
        db = sqlite3.connect(self.db_path)
        cur = db.cursor()
        
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                timestamp REAL PRIMARY KEY,
                cpu_percent REAL,
                memory_used INTEGER,
                memory_total INTEGER,
                disk_used INTEGER,
                disk_total INTEGER,
                network_sent INTEGER,
                network_recv INTEGER
            );
            
            CREATE TABLE IF NOT EXISTS agent_metrics (
                timestamp REAL,
                agent_id TEXT,
                cpu_percent REAL,
                memory_rss INTEGER,
                fds_open INTEGER,
                threads INTEGER,
                PRIMARY KEY (timestamp, agent_id)
            );
            
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                timestamp REAL,
                agent_id TEXT,
                level TEXT,
                message TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_system_metrics_time 
            ON system_metrics(timestamp);
            
            CREATE INDEX IF NOT EXISTS idx_agent_metrics_time 
            ON agent_metrics(timestamp);
            
            CREATE INDEX IF NOT EXISTS idx_events_time 
            ON events(timestamp);
        """)
        
        db.commit()
        db.close()
        
    def store_system_metrics(self, metrics: SystemMetrics):
        """Store system metrics"""
        db = sqlite3.connect(self.db_path)
        cur = db.cursor()
        
        cur.execute("""
            INSERT INTO system_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metrics.timestamp,
            metrics.cpu_percent,
            metrics.memory_used,
            metrics.memory_total,
            metrics.disk_used,
            metrics.disk_total,
            metrics.network_sent,
            metrics.network_recv
        ))
        
        db.commit()
        db.close()
        
    def store_agent_metrics(self, metrics: AgentMetrics):
        """Store agent metrics"""
        db = sqlite3.connect(self.db_path)
        cur = db.cursor()
        
        cur.execute("""
            INSERT INTO agent_metrics VALUES (?, ?, ?, ?, ?, ?)
        """, (
            metrics.timestamp,
            metrics.agent_id,
            metrics.cpu_percent,
            metrics.memory_rss,
            metrics.fds_open,
            metrics.threads
        ))
        
        db.commit()
        db.close()
        
    def store_event(self, agent_id: str, level: str, message: str):
        """Store an event"""
        db = sqlite3.connect(self.db_path)
        cur = db.cursor()
        
        cur.execute("""
            INSERT INTO events (timestamp, agent_id, level, message)
            VALUES (?, ?, ?, ?)
        """, (
            time.time(),
            agent_id,
            level,
            message
        ))
        
        db.commit()
        db.close()
        
    def get_system_metrics(
        self,
        start_time: float,
        end_time: float
    ) -> List[SystemMetrics]:
        """Get system metrics for a time range"""
        db = sqlite3.connect(self.db_path)
        cur = db.cursor()
        
        cur.execute("""
            SELECT * FROM system_metrics
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        """, (start_time, end_time))
        
        metrics = []
        for row in cur.fetchall():
            metrics.append(SystemMetrics(
                timestamp=row[0],
                cpu_percent=row[1],
                memory_used=row[2],
                memory_total=row[3],
                disk_used=row[4],
                disk_total=row[5],
                network_sent=row[6],
                network_recv=row[7]
            ))
            
        db.close()
        return metrics
        
    def get_agent_metrics(
        self,
        agent_id: str,
        start_time: float,
        end_time: float
    ) -> List[AgentMetrics]:
        """Get agent metrics for a time range"""
        db = sqlite3.connect(self.db_path)
        cur = db.cursor()
        
        cur.execute("""
            SELECT * FROM agent_metrics
            WHERE agent_id = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        """, (agent_id, start_time, end_time))
        
        metrics = []
        for row in cur.fetchall():
            metrics.append(AgentMetrics(
                timestamp=row[0],
                agent_id=row[1],
                cpu_percent=row[2],
                memory_rss=row[3],
                fds_open=row[4],
                threads=row[5]
            ))
            
        db.close()
        return metrics
        
    def get_events(
        self,
        start_time: float,
        end_time: float,
        agent_id: Optional[str] = None,
        level: Optional[str] = None
    ) -> List[dict]:
        """Get events for a time range"""
        db = sqlite3.connect(self.db_path)
        cur = db.cursor()
        
        query = """
            SELECT * FROM events
            WHERE timestamp BETWEEN ? AND ?
        """
        params = [start_time, end_time]
        
        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)
        if level:
            query += " AND level = ?"
            params.append(level)
            
        query += " ORDER BY timestamp"
        
        cur.execute(query, params)
        
        events = []
        for row in cur.fetchall():
            events.append({
                "id": row[0],
                "timestamp": row[1],
                "agent_id": row[2],
                "level": row[3],
                "message": row[4]
            })
            
        db.close()
        return events

class SystemMonitor:
    """System-wide monitoring service"""
    
    def __init__(self, metrics_path: str):
        self.metrics_db = MetricsDB(metrics_path)
        self.last_net_io = psutil.net_io_counters()
        self.last_check = time.time()
        
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        current_time = time.time()
        
        # CPU & Memory
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        # Disk
        disk = psutil.disk_usage('/')
        
        # Network (calculate rates)
        net_io = psutil.net_io_counters()
        elapsed = current_time - self.last_check
        
        net_sent = (
            net_io.bytes_sent - self.last_net_io.bytes_sent
        ) / elapsed
        net_recv = (
            net_io.bytes_recv - self.last_net_io.bytes_recv
        ) / elapsed
        
        self.last_net_io = net_io
        self.last_check = current_time
        
        metrics = SystemMetrics(
            cpu_percent=cpu_percent,
            memory_used=memory.used,
            memory_total=memory.total,
            disk_used=disk.used,
            disk_total=disk.total,
            network_sent=int(net_sent),
            network_recv=int(net_recv),
            timestamp=current_time
        )
        
        self.metrics_db.store_system_metrics(metrics)
        return metrics
        
    def collect_agent_metrics(self, pid: int, agent_id: str) -> Optional[AgentMetrics]:
        """Collect metrics for an agent process"""
        try:
            proc = psutil.Process(pid)
            
            metrics = AgentMetrics(
                agent_id=agent_id,
                cpu_percent=proc.cpu_percent(),
                memory_rss=proc.memory_info().rss,
                fds_open=proc.num_fds(),
                threads=proc.num_threads(),
                timestamp=time.time()
            )
            
            self.metrics_db.store_agent_metrics(metrics)
            return metrics
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
            
    def log_event(self, agent_id: str, level: str, message: str):
        """Log an event"""
        self.metrics_db.store_event(agent_id, level, message)
        
    def get_system_status(self) -> dict:
        """Get current system status summary"""
        metrics = self.collect_system_metrics()
        
        return {
            "cpu_percent": metrics.cpu_percent,
            "memory_percent": (
                metrics.memory_used / metrics.memory_total * 100
            ),
            "disk_percent": (
                metrics.disk_used / metrics.disk_total * 100
            ),
            "network": {
                "sent_mbps": metrics.network_sent / 1024 / 1024,
                "recv_mbps": metrics.network_recv / 1024 / 1024
            }
        }
        
    def get_agent_status(self, agent_id: str, pid: int) -> Optional[dict]:
        """Get current agent status"""
        metrics = self.collect_agent_metrics(pid, agent_id)
        if not metrics:
            return None
            
        return {
            "cpu_percent": metrics.cpu_percent,
            "memory_mb": metrics.memory_rss / 1024 / 1024,
            "fds": metrics.fds_open,
            "threads": metrics.threads
        }
        
    def get_historical_metrics(
        self,
        hours: int = 24,
        agent_id: Optional[str] = None
    ) -> dict:
        """Get historical metrics"""
        end_time = time.time()
        start_time = end_time - (hours * 3600)
        
        system_metrics = self.metrics_db.get_system_metrics(
            start_time, end_time
        )
        
        result = {
            "system": [m.__dict__ for m in system_metrics]
        }
        
        if agent_id:
            agent_metrics = self.metrics_db.get_agent_metrics(
                agent_id, start_time, end_time
            )
            result["agent"] = [m.__dict__ for m in agent_metrics]
            
        return result
        
    def get_recent_events(
        self,
        hours: int = 24,
        agent_id: Optional[str] = None,
        level: Optional[str] = None
    ) -> List[dict]:
        """Get recent events"""
        end_time = time.time()
        start_time = end_time - (hours * 3600)
        
        return self.metrics_db.get_events(
            start_time, end_time,
            agent_id=agent_id,
            level=level
        )