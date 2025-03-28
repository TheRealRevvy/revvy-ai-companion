"""
Revvy AI Companion - Configuration Module
Centralizes all configuration settings for the Revvy AI system.
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger("RevvyConfig")

class RevvyConfig:
    """Configuration class for Revvy AI Companion"""
    
    def __init__(self, config_path=None):
        # Set default config file path
        if config_path is None:
            self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
        else:
            self.config_path = config_path
        
        # Default configuration
        self.DEFAULT_CONFIG = {
            # System settings
            "system": {
                "name": "Revvy",
                "version": "1.0.0",
                "debug_mode": False,
                "auto_boot": True,
                "auto_shutdown": True
            },
            
            # Network settings
            "network": {
                "api_port": 5000,
                "api_host": "0.0.0.0",
                "enable_bluetooth": True,
                "enable_wifi": True
            },
            
            # OBD settings
            "obd": {
                "port": "/dev/rfcomm0",
                "baudrate": 38400,
                "timeout": 30,
                "reconnect_attempts": 5,
                "polling_interval": 1.0,  # seconds
                "dtc_check_interval": 300  # seconds
            },
            
            # Voice settings
            "voice": {
                "wake_word": "hey revvy",
                "wake_word_sensitivity": 0.7,
                "volume": 80,
                "enable_voice": True,
                "mic_index": 0,
                "speaker_device": "default"
            },
            
            # AI settings
            "ai": {
                "model_path": "./ai/models/mistral-7b-instruct-q4_k_m.gguf",
                "max_tokens": 256,
                "temperature": 0.7,
                "contextual_memory": True,
                "memory_limit": 10  # Number of conversations to remember
            },
            
            # GPS settings
            "gps": {
                "port": "/dev/ttyAMA0",
                "baudrate": 9600,
                "update_interval": 1.0,  # seconds
                "default_latitude": 37.7749,
                "default_longitude": -122.4194
            },
            
            # Display settings
            "display": {
                "unit_system": "metric",  # Options: "metric" or "imperial"
                "temperature_unit": "celsius",  # Options: "celsius" or "fahrenheit"
                "pressure_unit": "kpa",  # Options: "kpa" or "psi"
                "distance_unit": "km",  # Options: "km" or "mi"
                "speed_unit": "kph"  # Options: "kph" or "mph"
            },
            
            # Modes configuration
            "modes": {
                "default_mode": "Standard",
                "age_restricted_modes": ["Unhinged"],
                "rotation_interval": "daily"  # Options: "daily", "startup", "random"
            },
            
            # Achievement settings
            "achievements": {
                "enabled": True,
                "sync_to_cloud": True
            }
        }
        
        # Mode definitions
        self.AVAILABLE_MODES = [
            "Standard", "Performance", "Kiko", "Mechanic", "Zen", 
            "JDM Street", "Anime", "Toretto", "Unhinged", "Mystery", "Parent", "Voice Off"
        ]
        
        self.MODE_PERSONALITIES = {
            "Standard": "Revvy OG",
            "Performance": "Turbo Revvy",
            "Kiko": "Kiko",
            "Mechanic": "Mechanix",
            "Zen": "Sage",
            "JDM Street": "Shinji Revvy",
            "Anime": "Kaizen Revvy",
            "Toretto": "Revvy Toretto",
            "Unhinged": "Gizmo Gremlin",
            "Mystery": "Random",
            "Parent": "Safety Revvy",
            "Voice Off": "Silent"
        }
        
        # Achievements
        self.ACHIEVEMENTS = {
            "safety": [
                {"id": "smooth_operator", "name": "Smooth Operator", "description": "Clean acceleration/braking (10x)", "completed": False},
                {"id": "signal_champ", "name": "Signal Champ", "description": "Proper turn signal usage (20x)", "completed": False},
                {"id": "code_buster", "name": "Code Buster", "description": "Clear 5 DTCs responsibly", "completed": False},
                {"id": "zen_master", "name": "Zen Master", "description": "Complete 5+ calm trips in Zen Mode", "completed": False},
                {"id": "family_first", "name": "Family First", "description": "Consistent seatbelt use in Toretto Mode", "completed": False},
                {"id": "eco_rider", "name": "Eco Rider", "description": "Maintain efficient throttle control", "completed": False},
                {"id": "maintenance_champ", "name": "Maintenance Champ", "description": "Track regular vehicle checks", "completed": False},
                {"id": "cruise_control", "name": "Cruise Control", "description": "Drive consistently for 10 minutes without rapid changes", "completed": False},
                {"id": "steady_hands", "name": "Steady Hands", "description": "Hold a clean lane for 10 minutes", "completed": False}
            ],
            "turbo_vehicles": [
                {"id": "boost_baby_boost", "name": "Boost Baby Boost", "description": "Engage turbo boost during normal driving", "completed": False},
                {"id": "turbo_whistle_warrior", "name": "Turbo Whistle Warrior", "description": "Build boost 10x across separate drives", "completed": False}
            ],
            "na_vehicles": [
                {"id": "pedal_to_metal", "name": "Pedal to the Metal", "description": "90%+ throttle without excessive speed", "completed": False},
                {"id": "naturally_savage", "name": "Naturally Savage", "description": "Reach redline safely", "completed": False},
                {"id": "torque_time", "name": "Torque Time", "description": "High-gear acceleration within speed limits", "completed": False}
            ],
            "easter_eggs": [
                {"id": "danger_to_manifold", "name": "Danger to Manifold", "description": "Triggers in Toretto Mode during high engine stress", "completed": False},
                {"id": "quarter_mile", "name": "Quarter Mile at a Time", "description": "Activates during short performance bursts", "completed": False},
                {"id": "your_responsibility", "name": "Your Responsibility", "description": "Parent Mode startup message", "completed": False},
                {"id": "about_the_driver", "name": "It's About the Driver", "description": "Mystery Mode surprise quote", "completed": False},
                {"id": "almost_had_me", "name": "Almost Had Me", "description": "Appears when clearing one code but another appears", "completed": False}
            ]
        }
        
        # Load user configuration
        self.config = self.load_config()
        
        # Set API port
        self.API_PORT = self.config["network"]["api_port"]
        self.API_HOST = self.config["network"]["api_host"]
        
    def load_config(self):
        """Load configuration from file or create default if not exists"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    logger.info(f"Configuration loaded from {self.config_path}")
                    return config
            else:
                # Create default config
                logger.info(f"No configuration found, creating default at {self.config_path}")
                self.save_config(self.DEFAULT_CONFIG)
                return self.DEFAULT_CONFIG
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self.DEFAULT_CONFIG
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
                logger.info(f"Configuration saved to {self.config_path}")
                
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get(self, section, key, default=None):
        """Get a configuration value"""
        try:
            return self.config[section][key]
        except KeyError:
            return default
    
    def set(self, section, key, value):
        """Set a configuration value"""
        try:
            # Create section if it doesn't exist
            if section not in self.config:
                self.config[section] = {}
                
            self.config[section][key] = value
            self.save_config()
            return True
        except Exception as e:
            logger.error(f"Error setting configuration value: {e}")
            return False