#!/usr/bin/env python3
"""
Revvy AI Companion - Setup Wizard
Guides the user through initial setup process
"""

import os
import sys
import json
import time
import subprocess
import re

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the setup wizard header"""
    clear_screen()
    print("=" * 50)
    print("       REVVY AI COMPANION - SETUP WIZARD")
    print("=" * 50)
    print("")

def get_user_input(prompt, default=None):
    """Get user input with a default value"""
    if default:
        user_input = input(f"{prompt} [{default}]: ")
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ")

def scan_bluetooth_devices():
    """Scan for Bluetooth devices"""
    print("\nScanning for Bluetooth devices (this may take a few seconds)...")
    
    try:
        # Run Bluetooth scan
        result = subprocess.run(
            ['hcitool', 'scan'], 
            capture_output=True, 
            text=True
        )
        
        # Parse output
        output = result.stdout
        devices = []
        
        for line in output.strip().split('\n')[1:]:  # Skip the first line (header)
            if line.strip():
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    mac_address = parts[1]
                    name = parts[2] if len(parts) > 2 else "Unknown"
                    devices.append({
                        'address': mac_address,
                        'name': name
                    })
        
        return devices
        
    except Exception as e:
        print(f"Error scanning for Bluetooth devices: {e}")
        return []

def setup_obd():
    """Set up OBD connection"""
    print_header()
    print("OBD CONFIGURATION")
    print("-----------------")
    print("Let's configure your OBD connection.")
    print("Make sure your OBD adapter is powered on and in range.\n")
    
    # Scan for Bluetooth devices
    devices = scan_bluetooth_devices()
    
    if not devices:
        print("No Bluetooth devices found. Please make sure your OBD adapter is powered on.")
        print("You can enter the MAC address manually.")
        
        mac_address = get_user_input("Enter OBD adapter MAC address (xx:xx:xx:xx:xx:xx)")
        if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac_address):
            print("Invalid MAC address format. Using default.")
            mac_address = "00:00:00:00:00:00"
    else:
        print("\nAvailable Bluetooth devices:")
        for i, device in enumerate(devices):
            print(f"{i+1}. {device['name']} ({device['address']})")
        
        selection = get_user_input("Select your OBD adapter (or enter 0 to input manually)", "1")
        
        try:
            selection = int(selection)
            if selection == 0:
                mac_address = get_user_input("Enter OBD adapter MAC address (xx:xx:xx:xx:xx:xx)")
            else:
                mac_address = devices[selection-1]['address']
        except (ValueError, IndexError):
            print("Invalid selection. Using the first device.")
            mac_address = devices[0]['address']
    
    # Update OBD connection script
    print(f"\nSetting OBD adapter MAC address to: {mac_address}")
    
    try:
        # Update the MAC address in the connection script
        script_path = '/opt/revvy/scripts/obd_connect.sh'
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        content = re.sub(
            r'OBD_MAC="[0-9A-Fa-f:]*"', 
            f'OBD_MAC="{mac_address}"', 
            content
        )
        
        with open(script_path, 'w') as f:
            f.write(content)
        
        print("OBD configuration updated successfully.")
        
    except Exception as e:
        print(f"Error updating OBD configuration: {e}")
    
    input("\nPress Enter to continue...")

def setup_voice():
    """Set up voice settings"""
    print_header()
    print("VOICE CONFIGURATION")
    print("-------------------")
    print("Let's configure the voice settings.")
    
    # Test microphone
    print("\nTesting microphone...")
    try:
        subprocess.run(['arecord', '-d', '1', '-f', 'cd', '/dev/null'])
        print("Microphone detected.")
    except Exception as e:
        print(f"Error testing microphone: {e}")
    
    # Test speaker
    print("\nTesting speaker...")
    try:
        subprocess.run(['speaker-test', '-t', 'sine', '-f', '1000', '-l', '1', '-c', '2'])
        print("Speaker test complete.")
    except Exception as e:
        print(f"Error testing speaker: {e}")
    
    # Configure voice settings
    enable_voice = get_user_input("Enable voice interaction (yes/no)", "yes").lower() == "yes"
    volume = get_user_input("Set volume (0-100)", "80")
    
    try:
        volume = int(volume)
        volume = max(0, min(100, volume))
    except ValueError:
        print("Invalid volume. Using default (80).")
        volume = 80
    
    # Update configuration
    config_path = '/opt/revvy/config.json'
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if 'voice' not in config:
                config['voice'] = {}
            
            config['voice']['enable_voice'] = enable_voice
            config['voice']['volume'] = volume
            
            with open(config_path, 'w') as f:
                json