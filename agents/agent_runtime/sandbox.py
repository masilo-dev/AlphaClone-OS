"""
AlphaClone-OS Agent Runtime Sandbox

Provides secure isolation for agents using Linux seccomp and capabilities.
"""

import json
import logging
import os
import pwd
import grp
from pathlib import Path
from typing import List, Optional

try:
    import seccomp
    SECCOMP_AVAILABLE = True
except ImportError:
    SECCOMP_AVAILABLE = False
    
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

class Sandbox:
    """Agent sandbox with seccomp filters and capability controls"""
    
    def __init__(self, agent_id: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.seccomp_enabled = SECCOMP_AVAILABLE
        
    def setup_user(self) -> Optional[int]:
        """Create or get restricted user for agent"""
        username = f"agent_{self.agent_id}"
        try:
            pwd.getpwnam(username)
        except KeyError:
            # Create system user
            os.system(f"useradd -r -s /sbin/nologin {username}")
            
        try:
            return pwd.getpwnam(username).pw_uid
        except:
            logger.error(f"Failed to setup user {username}")
            return None
            
    def _create_seccomp_filter(self) -> Optional[seccomp.SyscallFilter]:
        """Create seccomp filter based on agent capabilities"""
        if not SECCOMP_AVAILABLE:
            return None
            
        try:
            f = seccomp.SyscallFilter(seccomp.KILL)
            
            # Always allow some basic syscalls
            for syscall in ["read", "write", "exit", "exit_group"]:
                f.add_rule(seccomp.ALLOW, syscall)
            
            # Add capability-specific syscalls
            if "network_access" in self.capabilities:
                for syscall in ["socket", "connect", "bind", "accept"]:
                    f.add_rule(seccomp.ALLOW, syscall)
                    
            if "file_access" in self.capabilities:
                for syscall in ["open", "close", "stat", "fstat"]:
                    f.add_rule(seccomp.ALLOW, syscall)
                    
            if "process_control" in self.capabilities:
                for syscall in ["clone", "fork", "kill"]:
                    f.add_rule(seccomp.ALLOW, syscall)
                    
            return f
        except Exception as e:
            logger.error(f"Failed to create seccomp filter: {e}")
            return None
            
    def apply_restrictions(self) -> bool:
        """Apply all sandbox restrictions"""
        success = True
        
        # Drop privileges
        uid = self.setup_user()
        if uid:
            try:
                os.setuid(uid)
            except Exception as e:
                logger.error(f"Failed to drop privileges: {e}")
                success = False
                
        # Apply seccomp filter
        if self.seccomp_enabled:
            f = self._create_seccomp_filter()
            if f:
                try:
                    f.load()
                except Exception as e:
                    logger.error(f"Failed to load seccomp filter: {e}")
                    success = False
                    
        # Set up capability restrictions
        # TODO: Implement Linux capabilities
                    
        return success
        
    def validate_file_access(self, path: str, mode: str) -> bool:
        """Validate if agent can access a file"""
        if "file_access" not in self.capabilities:
            return False
            
        # Check if path is in allowed directories
        allowed_paths = [
            f"/var/lib/alphaclone/agents/{self.agent_id}",
            "/tmp/alphaclone/ipc"
        ]
        
        path = os.path.abspath(path)
        return any(path.startswith(p) for p in allowed_paths)
        
    def validate_network_access(self, host: str, port: int) -> bool:
        """Validate if agent can access network endpoint"""
        if "network_access" not in self.capabilities:
            return False
            
        # Check against allowed endpoints
        if "cloud_sync" in self.capabilities:
            # Allow cloud endpoint
            return True
            
        # Default to localhost only
        return host in ["localhost", "127.0.0.1"]
        
    def cleanup(self):
        """Clean up sandbox resources"""
        # Nothing to clean up yet
        pass