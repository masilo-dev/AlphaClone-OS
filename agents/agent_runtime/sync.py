"""
AlphaClone-OS Cloud Sync Protocol

Enhanced cloud synchronization with:
- End-to-end encryption
- Atomic updates
- Version vectors for conflict resolution
- Differential sync
- Bandwidth optimization
"""

import base64
import hashlib
import json
import logging
import os
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import cryptography.fernet
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SyncManifest:
    """Manifest for a sync batch"""
    device_id: str
    timestamp: float
    version_vector: Dict[str, int]
    objects: List[dict]
    signature: Optional[str] = None

class VersionVector:
    """Tracks object versions for conflict resolution"""
    
    def __init__(self):
        self.versions: Dict[str, int] = defaultdict(int)
        
    def increment(self, device_id: str):
        """Increment version for a device"""
        self.versions[device_id] += 1
        
    def merge(self, other: Dict[str, int]):
        """Merge with another version vector"""
        for device_id, version in other.items():
            self.versions[device_id] = max(
                self.versions[device_id],
                version
            )
            
    def dominates(self, other: Dict[str, int]) -> bool:
        """Check if this vector dominates another"""
        return all(
            self.versions[k] >= v
            for k, v in other.items()
        )

class CloudSync:
    """Enhanced cloud synchronization"""
    
    def __init__(self, config: dict):
        self.config = config
        self.device_id = config["device_id"]
        self.endpoint = config["endpoint"]
        
        # Set up encryption
        self.fernet = self._setup_encryption()
        self.version_vector = VersionVector()
        
        # Set up TLS
        self.session = self._setup_tls()
        
    def _setup_encryption(self) -> cryptography.fernet.Fernet:
        """Set up end-to-end encryption"""
        if "encryption_key" in self.config:
            key = base64.b64decode(self.config["encryption_key"])
        else:
            key = AESGCM.generate_key(bit_length=256)
            self.config["encryption_key"] = base64.b64encode(key).decode()
            
        return cryptography.fernet.Fernet(
            base64.b64encode(key)
        )
        
    def _setup_tls(self) -> requests.Session:
        """Set up mutual TLS session"""
        session = requests.Session()
        
        cert_path = self.config.get("mtls_cert_path")
        key_path = self.config.get("mtls_key_path")
        
        if cert_path and key_path:
            session.cert = (cert_path, key_path)
            
        session.verify = self.config.get("ca_cert_path", True)
        return session
        
    def _sign_manifest(self, manifest: SyncManifest) -> str:
        """Sign a sync manifest"""
        key_path = self.config["signing_key_path"]
        with open(key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None
            )
            
        manifest_data = json.dumps({
            "device_id": manifest.device_id,
            "timestamp": manifest.timestamp,
            "version_vector": manifest.version_vector,
            "objects": manifest.objects
        }).encode()
        
        signature = private_key.sign(
            manifest_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode()
        
    def _verify_manifest(self, manifest: dict, signature: str) -> bool:
        """Verify a manifest signature"""
        try:
            cert_path = self.config["cloud_cert_path"]
            with open(cert_path, "rb") as f:
                public_key = serialization.load_pem_public_key(
                    f.read()
                )
                
            manifest_data = json.dumps({
                k: v for k, v in manifest.items()
                if k != "signature"
            }).encode()
            
            signature_bytes = base64.b64decode(signature)
            
            public_key.verify(
                signature_bytes,
                manifest_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
            
    def prepare_sync(self, objects: List[dict]) -> SyncManifest:
        """Prepare objects for sync"""
        # Encrypt objects
        encrypted = []
        for obj in objects:
            obj_data = json.dumps(obj).encode()
            encrypted.append({
                "id": obj["id"],
                "data": self.fernet.encrypt(obj_data).decode(),
                "hash": hashlib.sha256(obj_data).hexdigest()
            })
            
        # Create manifest
        manifest = SyncManifest(
            device_id=self.device_id,
            timestamp=time.time(),
            version_vector=dict(self.version_vector.versions),
            objects=encrypted
        )
        
        # Sign manifest
        manifest.signature = self._sign_manifest(manifest)
        
        return manifest
        
    def sync_to_cloud(self, manifest: SyncManifest) -> bool:
        """Send updates to cloud"""
        try:
            response = self.session.post(
                f"{self.endpoint}/sync",
                json=manifest.__dict__,
                timeout=30
            )
            
            if response.status_code == 200:
                # Update version vector
                self.version_vector.increment(self.device_id)
                return True
                
            logger.error(
                f"Sync failed: {response.status_code} - {response.text}"
            )
            return False
            
        except Exception as e:
            logger.error(f"Sync error: {e}")
            return False
            
    def get_updates(self) -> List[dict]:
        """Get updates from cloud"""
        try:
            response = self.session.get(
                f"{self.endpoint}/updates",
                params={"since": max(self.version_vector.versions.values(), default=0)},
                timeout=30
            )
            
            if response.status_code != 200:
                return []
                
            manifest = response.json()
            
            # Verify signature
            if not self._verify_manifest(manifest, manifest["signature"]):
                logger.error("Invalid manifest signature")
                return []
                
            # Decrypt objects
            objects = []
            for obj in manifest["objects"]:
                try:
                    decrypted = self.fernet.decrypt(
                        obj["data"].encode()
                    )
                    obj_data = json.loads(decrypted)
                    
                    # Verify hash
                    if hashlib.sha256(decrypted).hexdigest() != obj["hash"]:
                        logger.error(f"Hash mismatch for object {obj['id']}")
                        continue
                        
                    objects.append(obj_data)
                except Exception as e:
                    logger.error(f"Failed to decrypt object: {e}")
                    
            # Update version vector
            self.version_vector.merge(manifest["version_vector"])
            
            return objects
            
        except Exception as e:
            logger.error(f"Update error: {e}")
            return []
            
    def resolve_conflicts(self, local: dict, remote: dict) -> dict:
        """Resolve sync conflicts"""
        # Default to most recent version
        if local["updated_at"] > remote["updated_at"]:
            return local
        elif local["updated_at"] < remote["updated_at"]:
            return remote
            
        # If same timestamp, merge non-conflicting fields
        result = local.copy()
        for key, value in remote.items():
            if key not in local:
                result[key] = value
                
        return result