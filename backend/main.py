# Add to the imports at the top of the file
import signal
import time
import random
import logging
import threading
from .config import RevvyConfig
from .ai.engine import AIEngine
from .obd.manager import OBDManager
from .voice.system import VoiceSystem
from .gps.tracker import GPSTracker
from .api.server import APIServer
from .voice.command_handler import CommandHandler
from .mocks import MockOBDManager, MockAIEngine, MockVoiceSystem, MockGPSTracker, MockAPIServer

# Set up logger
logger = logging.getLogger("RevvyCore")

# Add to the RevvyCore class:

def start(self):
    """Start the Revvy AI Companion system"""
    if self.running:
        logger.warning("Revvy AI Companion is already running")
        return False
    
    logger.info("Starting Revvy AI Companion...")
    self.running = True
    
    # Start OBD connection
    if not self.obd.is_connected():
        try:
            self.obd.connect()
        except Exception as e:
            logger.error(f"Failed to connect to OBD: {e}")
    
    # Start each component with error handling
    for component_name, component in [
        ('obd', self.obd), 
        ('gps', self.gps), 
        ('ai', self.ai), 
        ('voice', self.voice), 
        ('api', self.api)
    ]:
        try:
            component.start()
            logger.info(f"Started {component_name} component")
        except Exception as e:
            logger.error(f"Failed to start {component_name} component: {e}")
            logger.debug(traceback.format_exc())
    
    # Start main loop in a separate thread
    self.main_thread = threading.Thread(target=self.main_loop)
    self.main_thread.daemon = True
    self.main_thread.start()
    
    self.system_ready = True
    logger.info("Revvy AI Companion started")
    return True

def stop(self):
    """Stop the Revvy AI Companion system"""
    if not self.running:
        logger.warning("Revvy AI Companion is not running")
        return False
    
    logger.info("Stopping Revvy AI Companion...")
    self.running = False
    
    # Stop each component with error handling
    for component_name, component in [
        ('api', self.api), 
        ('voice', self.voice), 
        ('ai', self.ai), 
        ('gps', self.gps), 
        ('obd', self.obd)
    ]:
        try:
            component.stop()
            logger.info(f"Stopped {component_name} component")
        except Exception as e:
            logger.error(f"Failed to stop {component_name} component: {e}")
            logger.debug(traceback.format_exc())
    
    # Wait for main thread to finish
    if hasattr(self, 'main_thread') and self.main_thread.is_alive():
        self.main_thread.join(timeout=5.0)
    
    self.system_ready = False
    logger.info("Revvy AI Companion stopped")
    return True

def restart(self):
    """Restart the Revvy AI Companion system"""
    logger.info("Restarting Revvy AI Companion...")
    
    if self.stop():
        # Small delay to ensure clean shutdown
        time.sleep(1.0)
        return self.start()
    
    return False

def prepare_shutdown(self):
    """Prepare for system shutdown"""
    logger.info("Preparing for shutdown...")
    
    # Announce shutdown if voice is available
    if self.voice and self.voice.is_active() and self.voice.voice_enabled:
        self.voice.speak("Preparing to shut down. Goodbye!")
    
    # Save any pending data
    self._save_system_state()
    
    # Stop the system
    self.stop()

def handle_shutdown(self, signum, frame):
    """Handle shutdown signals"""
    signal_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
    logger.info(f"Received {signal_name}, shutting down...")
    
    self.prepare_shutdown()
    
    # Exit the application
    import sys
    sys.exit(0)

def _save_system_state(self):
    """Save system state before shutdown"""
    logger.info("Saving system state...")
    
    # Save config changes
    self.config.save_config()
    
    # Any additional state saving operations
    
    logger.info("System state saved")

def _load_personality_profiles(self):
    """Load personality profiles from configuration"""
    logger.info("Loading personality profiles...")
    
    # Get personality profiles from config or use defaults
    personality_profiles = {}
    
    # Map modes to personalities based on configuration
    for mode, personality in self.config.MODE_PERSONALITIES.items():
        personality_profiles[mode] = {
            "name": personality,
            "voice_id": self.config.get("personalities", f"{personality.lower().replace(' ', '_')}_voice_id", "default"),
            "speaking_rate": self.config.get("personalities", f"{personality.lower().replace(' ', '_')}_speaking_rate", 1.0),
            "speaking_pitch": self.config.get("personalities", f"{personality.lower().replace(' ', '_')}_speaking_pitch", 1.0)
        }
    
    logger.info(f"Loaded {len(personality_profiles)} personality profiles")
    return personality_profiles

def set_mode(self, mode_name):
    """Change the current operating mode"""
    if mode_name not in self.config.AVAILABLE_MODES:
        logger.error(f"Invalid mode: {mode_name}")
        return False
    
    logger.info(f"Changing mode to: {mode_name}")
    self.current_mode = mode_name
    
    # Set corresponding personality
    personality = self.config.MODE_PERSONALITIES.get(mode_name, "Revvy OG")
    self.set_personality(personality)
    
    # Announce mode change if voice is available
    if self.voice and self.voice.is_active() and self.voice.voice_enabled:
        self.voice.speak(f"Switching to {mode_name} mode with {personality} personality.")
    
    return True

def set_personality(self, personality_name):
    """Change the current personality"""
    if personality_name == "Random":
        # Pick a random personality that's not "Silent" or "Random"
        available_personalities = [p for p in self.config.MODE_PERSONALITIES.values() 
                                 if p not in ["Random", "Silent"]]
        personality_name = random.choice(available_personalities)
    
    logger.info(f"Changing personality to: {personality_name}")
    self.current_personality = personality_name
    
    # Update AI engine personality
    if self.ai:
        self.ai.set_personality(personality_name)
    
    # Update voice settings for the personality
    if self.voice and personality_name in [p for mode, p in self.config.MODE_PERSONALITIES.items()]:
        # Get voice settings for this personality
        for mode, personality in self.config.MODE_PERSONALITIES.items():
            if personality == personality_name:
                profile = self.personality_profiles.get(mode, {})
                voice_id = profile.get("voice_id", "default")
                speaking_rate = profile.get("speaking_rate", 1.0)
                speaking_pitch = profile.get("speaking_pitch", 1.0)
                
                # Apply voice settings
                self.voice.set_voice(voice_id)
                self.voice.set_speaking_rate(speaking_rate)
                self.voice.set_speaking_pitch(speaking_pitch)
                
                # Mute voice for Silent personality
                if personality_name == "Silent":
                    self.voice.enable_voice(False)
                else:
                    self.voice.enable_voice(self.voice_enabled)
                
                break
    
    return True

def toggle_voice(self):
    """Toggle voice output on/off"""
    self.voice_enabled = not self.voice_enabled
    
    if self.voice:
        self.voice.enable_voice(self.voice_enabled)
    
    logger.info(f"Voice {'enabled' if self.voice_enabled else 'disabled'}")
    return self.voice_enabled

def get_status(self):
    """Get system status information"""
    status = {
        "system": {
            "running": self.running,
            "ready": self.system_ready,
            "mode": self.current_mode,
            "personality": self.current_personality,
            "voice_enabled": self.voice_enabled,
            "version": self.config.get("system", "version", "1.0.0")
        },
        "components": self.component_status.copy()
    }
    
    # Add vehicle status if available
    if self.obd and self.obd.is_connected():
        status["vehicle"] = self.obd.get_vehicle_data_with_units()
    
    # Add GPS status if available
    if self.gps and self.gps.is_active():
        status["location"] = self.gps.get_gps_data()
    
    return status

def process_command(self, command, context=None):
    """Process voice command using command handler"""
    if not self.command_handler:
        logger.error("Command handler not available")
        return "I'm sorry, I can't process commands right now."
    
    return self.command_handler.process_command(command, context)

def get_vehicle_data(self):
    """Get current vehicle data with unit conversions"""
    if not self.obd or not self.obd.is_connected():
        return None
    
    # Get raw vehicle data
    vehicle_data = self.obd.get_vehicle_data()
    
    # Get unit system preference
    unit_system = self.config.get("display", "unit_system", "metric")
    
    # Convert values based on unit system if needed
    if unit_system == "imperial" and vehicle_data:
        # Convert speed from km/h to mph
        if "speed" in vehicle_data and vehicle_data["speed"] is not None:
            vehicle_data["speed"] = vehicle_data["speed"] * 0.621371
        
        # Convert temperatures from C to F
        for temp_field in ["coolant_temp", "intake_temp", "oil_temp"]:
            if temp_field in vehicle_data and vehicle_data[temp_field] is not None:
                vehicle_data[temp_field] = (vehicle_data[temp_field] * 9/5) + 32
        
        # Convert boost pressure from kPa to PSI
        if "boost_pressure" in vehicle_data and vehicle_data["boost_pressure"] is not None:
            vehicle_data["boost_pressure"] = vehicle_data["boost_pressure"] * 0.145038
    
    return vehicle_data