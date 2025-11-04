#!/usr/bin/env python3
"""
AlphaClone-OS Agent Runtime

This module provides the core agent runtime environment that integrates with
the kernel simulator's VFS and process management facilities.
"""

import json
import logging
import os
import socket
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AgentInfo:
    """Information about a registered agent"""
    agent_id: str
    capabilities: List[str]
    socket_path: str
    pid: int

class AgentRuntime:
    """Core agent runtime that manages agent lifecycle and communication"""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.agents: Dict[str, AgentInfo] = {}
        self.ipc_dir = Path("/tmp/alphaclone/ipc")
        self.ipc_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize SQLite storage (uses kernel VFS)
        db_path = Path(self.config["database"]["path"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(db_path))
        self._init_db()
        
    def _load_config(self, path: str) -> dict:
        """Load runtime configuration"""
        try:
            with open(path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {path}: {e}")
            return {}

    def _init_db(self):
        """Initialize SQLite tables for agent memory"""
        cur = self.db.cursor()
        
        # Create tables if they don't exist
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS objects (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                key TEXT NOT NULL,
                json_payload TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS embeddings (
                id TEXT PRIMARY KEY,
                object_id TEXT NOT NULL,
                vector BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (object_id) REFERENCES objects(id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_objects_agent_key 
            ON objects(agent_id, key);
        """)
        self.db.commit()

    def register_agent(self, agent_id: str, capabilities: List[str]) -> bool:
        """Register a new agent with the runtime"""
        if agent_id in self.agents:
            logger.error(f"Agent {agent_id} already registered")
            return False
            
        # Create Unix domain socket for agent IPC
        socket_path = self.ipc_dir / f"{agent_id}.sock"
        if socket_path.exists():
            socket_path.unlink()
            
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(str(socket_path))
        
        # Store agent info
        self.agents[agent_id] = AgentInfo(
            agent_id=agent_id,
            capabilities=capabilities,
            socket_path=str(socket_path),
            pid=os.getpid()
        )
        
        logger.info(f"Registered agent {agent_id} with capabilities: {capabilities}")
        return True

    def store_memory(self, agent_id: str, key: str, payload: dict) -> bool:
        """Store an object in agent's persistent memory"""
        if agent_id not in self.agents:
            logger.error(f"Unknown agent {agent_id}")
            return False
            
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO objects (id, agent_id, key, json_payload)
                VALUES (?, ?, ?, ?)
            """, (
                os.urandom(16).hex(),  # Random ID
                agent_id,
                key,
                json.dumps(payload)
            ))
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return False

    def retrieve_memory(self, agent_id: str, key: str) -> Optional[dict]:
        """Retrieve an object from agent's persistent memory"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT json_payload FROM objects
                WHERE agent_id = ? AND key = ?
                ORDER BY updated_at DESC LIMIT 1
            """, (agent_id, key))
            row = cur.fetchone()
            return json.loads(row[0]) if row else None
        except Exception as e:
            logger.error(f"Failed to retrieve memory: {e}")
            return None

    def send_message(self, from_agent: str, to_agent: str, msg: dict) -> bool:
        """Send a message from one agent to another"""
        if from_agent not in self.agents or to_agent not in self.agents:
            logger.error(f"Unknown agent in message {from_agent} -> {to_agent}")
            return False
            
        # TODO: Implement actual message passing
        logger.info(f"Would send: {from_agent} -> {to_agent}: {msg}")
        return True

def main():
    """Runtime entry point"""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config.json>")
        sys.exit(1)
        
    runtime = AgentRuntime(sys.argv[1])
    
    # TODO: Start message processing loop
    
if __name__ == "__main__":
    main()