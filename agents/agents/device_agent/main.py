#!/usr/bin/env python3
"""
AlphaClone-OS Device Agent

Manages hardware devices, drivers, and system resources.
Provides hardware abstraction layer (HAL) for other agents.
"""

import json
import logging
import os
import signal
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import pyudev

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DeviceInfo:
    """Information about a hardware device"""
    device_path: str
    subsystem: str
    driver: str
    vendor_id: str
    product_id: str
    serial: str

class DeviceManager:
    """Hardware device management"""
    
    def __init__(self):
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.devices: Dict[str, DeviceInfo] = {}
        self._scan_devices()
        
    def _scan_devices(self):
        """Scan for connected devices"""
        for device in self.context.list_devices():
            self._add_device(device)
            
    def _add_device(self, device: pyudev.Device):
        """Add a device to tracking"""
        if not device.get('ID_VENDOR_ID'):
            return  # Skip non-hardware devices
            
        dev_info = DeviceInfo(
            device_path=device.device_path,
            subsystem=device.subsystem,
            driver=device.driver or "",
            vendor_id=device.get('ID_VENDOR_ID', ""),
            product_id=device.get('ID_MODEL_ID', ""),
            serial=device.get('ID_SERIAL', "")
        )
        self.devices[device.device_path] = dev_info
        
    def setup_monitor(self, callback):
        """Set up device monitoring"""
        self.monitor.filter_by(subsystem='usb')
        self.monitor.filter_by(subsystem='pci')
        self.monitor.filter_by(subsystem='input')
        
        observer = pyudev.MonitorObserver(self.monitor, callback)
        observer.start()
        
    def get_devices(self) -> List[DeviceInfo]:
        """Get list of tracked devices"""
        return list(self.devices.values())
        
    def find_device(self, vendor_id: str, product_id: str) -> Optional[DeviceInfo]:
        """Find a specific device"""
        for dev in self.devices.values():
            if dev.vendor_id == vendor_id and dev.product_id == product_id:
                return dev
        return None

class PowerManager:
    """System power management"""
    
    def __init__(self):
        self.bus = dbus.SystemBus()
        self._init_dbus()
        
    def _init_dbus(self):
        """Initialize D-Bus power management"""
        try:
            self.power_proxy = self.bus.get_object(
                'org.freedesktop.login1',
                '/org/freedesktop/login1'
            )
        except dbus.exceptions.DBusException as e:
            logger.error(f"Failed to connect to power management: {e}")
            
    def can_suspend(self) -> bool:
        """Check if system can suspend"""
        try:
            return self.power_proxy.CanSuspend(
                dbus_interface='org.freedesktop.login1.Manager'
            ) == 'yes'
        except:
            return False
            
    def suspend(self) -> bool:
        """Suspend the system"""
        try:
            self.power_proxy.Suspend(
                True,  # Interactive
                dbus_interface='org.freedesktop.login1.Manager'
            )
            return True
        except Exception as e:
            logger.error(f"Failed to suspend: {e}")
            return False
            
    def get_power_state(self) -> dict:
        """Get power supply status"""
        try:
            with open('/sys/class/power_supply/BAT0/status') as f:
                status = f.read().strip()
            with open('/sys/class/power_supply/BAT0/capacity') as f:
                capacity = int(f.read().strip())
                
            return {
                "on_battery": status != "Not charging",
                "battery_level": capacity,
                "can_suspend": self.can_suspend()
            }
        except:
            return {
                "on_battery": False,
                "battery_level": 100,
                "can_suspend": False
            }

class DeviceAgent:
    """Hardware management agent"""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.agent_id = "device_agent"
        
        # Initialize managers
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.main_loop = GLib.MainLoop()
        self.device_mgr = DeviceManager()
        self.power_mgr = PowerManager()
        
    def _load_config(self, path: str) -> dict:
        """Load agent configuration"""
        try:
            with open(path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {path}: {e}")
            return {}
            
    def handle_device_event(self, device):
        """Handle device hotplug events"""
        action = device.get('ACTION')
        
        if action == 'add':
            self.device_mgr._add_device(device)
            logger.info(f"New device: {device.get('ID_VENDOR_ID')}:"
                       f"{device.get('ID_MODEL_ID')}")
        elif action == 'remove':
            if device.device_path in self.device_mgr.devices:
                del self.device_mgr.devices[device.device_path]
                logger.info(f"Removed device: {device.device_path}")
                
    def handle_message(self, msg: dict) -> Optional[dict]:
        """Handle incoming messages from other agents"""
        msg_type = msg.get("type")
        
        if msg_type == "device_list":
            return {
                "devices": [d.__dict__ for d in self.device_mgr.get_devices()]
            }
        elif msg_type == "find_device":
            device = self.device_mgr.find_device(
                msg.get("vendor_id"), msg.get("product_id")
            )
            return {
                "device": device.__dict__ if device else None
            }
        elif msg_type == "power_state":
            return self.power_mgr.get_power_state()
        elif msg_type == "suspend":
            return {
                "success": self.power_mgr.suspend()
            }
            
        return {"error": f"Unknown message type: {msg_type}"}
        
    def run(self):
        """Main agent loop"""
        logger.info(f"Starting {self.agent_id}")
        
        # Set up device monitoring
        self.device_mgr.setup_monitor(self.handle_device_event)
        
        def cleanup(signum, frame):
            logger.info("Shutting down device agent...")
            self.main_loop.quit()
            
        signal.signal(signal.SIGTERM, cleanup)
        signal.signal(signal.SIGINT, cleanup)
        
        try:
            # Run main event loop
            self.main_loop.run()
        except Exception as e:
            logger.error(f"Device agent error: {e}")
        finally:
            cleanup(None, None)

def main():
    """Agent entry point"""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config.json>")
        sys.exit(1)
        
    agent = DeviceAgent(sys.argv[1])
    agent.run()

if __name__ == "__main__":
    main()