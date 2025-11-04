#!/usr/bin/env python3
"""
AlphaClone-OS Agent Launcher

Manages agent lifecycle and provides supervisor interface.
"""

import argparse
import json
import logging
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

from agent_runtime.auth import get_device_identity
from agent_runtime.runtime import AgentRuntime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message_s}"
)
logger = logging.getLogger(__name__)

class AgentLauncher:
    """Manages agent processes and provides supervisor interface"""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.runtime = AgentRuntime(config_path)
        self.agent_procs: Dict[str, subprocess.Popen] = {}
        self.device_id, self.tpm_available = get_device_identity()
        
    def _load_config(self, path: str) -> dict:
        """Load launcher configuration"""
        try:
            with open(path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {path}: {e}")
            return {}
            
    def start_agent(self, agent_id: str) -> bool:
        """Start an agent process"""
        if agent_id in self.agent_procs:
            logger.warning(f"Agent {agent_id} already running")
            return False
            
        agent_path = Path(__file__).parent / "agents" / agent_id / "main.py"
        if not agent_path.exists():
            logger.error(f"Agent {agent_id} not found at {agent_path}")
            return False
            
        try:
            proc = subprocess.Popen([
                sys.executable,
                str(agent_path),
                self.config_path
            ])
            self.agent_procs[agent_id] = proc
            logger.info(f"Started agent {agent_id} (PID {proc.pid})")
            return True
        except Exception as e:
            logger.error(f"Failed to start agent {agent_id}: {e}")
            return False
            
    def stop_agent(self, agent_id: str) -> bool:
        """Stop an agent process"""
        if agent_id not in self.agent_procs:
            return False
            
        proc = self.agent_procs[agent_id]
        try:
            proc.terminate()
            proc.wait(timeout=5)
            del self.agent_procs[agent_id]
            logger.info(f"Stopped agent {agent_id}")
            return True
        except subprocess.TimeoutExpired:
            proc.kill()
            logger.warning(f"Had to force kill agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Error stopping agent {agent_id}: {e}")
            return False
            
    def get_status(self) -> dict:
        """Get status of all agents"""
        status = {
            "device_id": self.device_id,
            "tpm_available": self.tpm_available,
            "agents": {}
        }
        
        for agent_id, proc in self.agent_procs.items():
            if proc.poll() is None:
                state = "running"
            else:
                state = f"exited ({proc.returncode})"
                
            status["agents"][agent_id] = {
                "pid": proc.pid,
                "state": state
            }
            
        return status
        
    def start_all(self) -> bool:
        """Start all configured agents"""
        success = True
        for agent_id in ["security_agent", "aiops_agent", "network_agent"]:
            if not self.start_agent(agent_id):
                success = False
        return success
        
    def stop_all(self) -> bool:
        """Stop all running agents"""
        success = True
        for agent_id in list(self.agent_procs.keys()):
            if not self.stop_agent(agent_id):
                success = False
        return success
        
    def cleanup(self):
        """Clean up resources on shutdown"""
        self.stop_all()

def main():
    """Launcher entry point"""
    parser = argparse.ArgumentParser(description="AlphaClone-OS Agent Launcher")
    parser.add_argument("command", choices=["start", "stop", "status", "debug"])
    parser.add_argument("--agent", help="Specific agent to target")
    parser.add_argument("--config", default="/etc/alphaclone/agent_config.json",
                      help="Path to config file")
    args = parser.parse_args()
    
    launcher = AgentLauncher(args.config)
    
    try:
        if args.command == "start":
            if args.agent:
                success = launcher.start_agent(args.agent)
            else:
                success = launcher.start_all()
        elif args.command == "stop":
            if args.agent:
                success = launcher.stop_agent(args.agent)
            else:
                success = launcher.stop_all()
        elif args.command == "status":
            status = launcher.get_status()
            print(json.dumps(status, indent=2))
            success = True
        elif args.command == "debug":
            if not args.agent:
                print("Must specify --agent for debug mode")
                sys.exit(1)
            # Start agent in debug mode
            success = launcher.start_agent(args.agent)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        launcher.cleanup()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        launcher.cleanup()
        sys.exit(1)
        
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()