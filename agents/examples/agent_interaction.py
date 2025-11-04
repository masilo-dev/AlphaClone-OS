#!/usr/bin/env python3
"""
AlphaClone-OS Agent Integration Example

Demonstrates agent interactions in a real-world scenario:
1. UI agent detects new USB device
2. Device agent handles hardware
3. Security agent verifies device
4. AIops agent analyzes behavior
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

from agent_runtime.runtime import AgentRuntime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

def simulate_usb_scenario(runtime: AgentRuntime):
    """Simulate USB device insertion scenario"""
    
    # 1. UI Agent detects device
    logger.info("UI Agent: New device detected")
    runtime.send_message(
        from_agent="ui_agent",
        to_agent="device_agent",
        msg={
            "type": "device_connected",
            "device": {
                "vendor_id": "0x0483",
                "product_id": "0x5740",
                "serial": "TEST001"
            }
        }
    )
    
    time.sleep(1)  # Simulate processing time
    
    # 2. Device Agent handles hardware
    logger.info("Device Agent: Loading driver")
    runtime.send_message(
        from_agent="device_agent",
        to_agent="security_agent",
        msg={
            "type": "verify_device",
            "device": {
                "vendor_id": "0x0483",
                "product_id": "0x5740",
                "driver": "usb-storage",
                "mount_point": "/media/usb0"
            }
        }
    )
    
    time.sleep(1)
    
    # 3. Security Agent checks device
    logger.info("Security Agent: Verifying device")
    runtime.send_message(
        from_agent="security_agent",
        to_agent="aiops_agent",
        msg={
            "type": "analyze_device",
            "context": {
                "device_type": "usb-storage",
                "history": ["First time seen"],
                "user_authorized": False
            }
        }
    )
    
    time.sleep(1)
    
    # 4. AI Agent analyzes
    logger.info("AI Agent: Analyzing device behavior")
    runtime.send_message(
        from_agent="aiops_agent",
        to_agent="security_agent",
        msg={
            "type": "device_analysis",
            "result": {
                "risk_level": "medium",
                "recommendations": [
                    "Prompt user for authorization",
                    "Mount read-only initially",
                    "Scan for malware before full access"
                ]
            }
        }
    )
    
    time.sleep(1)
    
    # 5. Security Agent applies policy
    logger.info("Security Agent: Applying security policy")
    runtime.send_message(
        from_agent="security_agent",
        to_agent="device_agent",
        msg={
            "type": "apply_device_policy",
            "policy": {
                "mount_options": ["ro", "noexec", "nosuid"],
                "require_auth": True
            }
        }
    )
    
    time.sleep(1)
    
    # 6. Device Agent confirms
    logger.info("Device Agent: Policy applied")
    runtime.send_message(
        from_agent="device_agent",
        to_agent="ui_agent",
        msg={
            "type": "show_device_prompt",
            "prompt": {
                "title": "New USB Device",
                "message": "Allow access to USB storage device?",
                "options": ["Allow", "Deny"]
            }
        }
    )

def main():
    """Example entry point"""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config.json>")
        sys.exit(1)
        
    # Initialize runtime
    runtime = AgentRuntime(sys.argv[1])
    
    try:
        # Run example scenario
        simulate_usb_scenario(runtime)
    except KeyboardInterrupt:
        logger.info("Example terminated by user")
    except Exception as e:
        logger.error(f"Example failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()