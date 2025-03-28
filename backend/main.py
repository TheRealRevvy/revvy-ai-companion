# Add to the imports
import traceback
from functools import wraps

# Add this function to the top of the file
def component_safe(default_return=None):
    """Decorator to make component methods fault-tolerant"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                component_name = func.__module__.split('.')[-1]
                logger.error(f"Error in {component_name}.{func.__name__}: {e}")
                logger.debug(traceback.format_exc())
                return default_return
        return wrapper
    return decorator

# Update the RevvyCore.__init__ method:
def __init__(self):
    self.running = False
    self.config = RevvyConfig()
    
    # Component status tracking
    self.component_status = {
        'obd': {'available': False, 'error': None},
        'ai': {'available': False, 'error': None},
        'voice': {'available': False, 'error': None},
        'gps': {'available': False, 'error': None},
        'api': {'available': False, 'error': None}
    }
    
    # Initialize all subsystems with error handling
    logger.info("Initializing Revvy AI Companion...")
    
    try:
        self.obd = OBDManager(self.config)
        self.component_status['obd']['available'] = True
    except Exception as e:
        logger.error(f"Failed to initialize OBD Manager: {e}")
        self.component_status['obd']['error'] = str(e)
        self.obd = MockOBDManager(self.config)  # Use mock OBD
    
    try:
        self.ai = AIEngine(self.config)
        self.component_status['ai']['available'] = True
    except Exception as e:
        logger.error(f"Failed to initialize AI Engine: {e}")
        self.component_status['ai']['error'] = str(e)
        self.ai = MockAIEngine(self.config)  # Use mock AI
    
    try:
        self.voice = VoiceSystem(self.config, self.ai)
        self.component_status['voice']['available'] = True
    except Exception as e:
        logger.error(f"Failed to initialize Voice System: {e}")
        self.component_status['voice']['error'] = str(e)
        self.voice = MockVoiceSystem(self.config)  # Use mock voice
    
    try:
        self.gps = GPSTracker(self.config)
        self.component_status['gps']['available'] = True
    except Exception as e:
        logger.error(f"Failed to initialize GPS Tracker: {e}")
        self.component_status['gps']['error'] = str(e)
        self.gps = MockGPSTracker(self.config)  # Use mock GPS
    
    try:
        self.api = APIServer(self.config, self)
        self.component_status['api']['available'] = True
    except Exception as e:
        logger.error(f"Failed to initialize API Server: {e}")
        self.component_status['api']['error'] = str(e)
        self.api = MockAPIServer(self.config, self)  # Use mock API
    
    # State variables
    self.current_mode = "Standard"
    self.current_personality = "Revvy OG"
    self.voice_enabled = True
    self.system_ready = False
    
    # Add command handler
    self.command_handler = CommandHandler(self)
    
    # Load personality profiles
    self.personality_profiles = self._load_personality_profiles()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, self.handle_shutdown)
    signal.signal(signal.SIGTERM, self.handle_shutdown)

# Update main_loop with better error handling
def main_loop(self):
    """Main application loop with enhanced error handling"""
    logger.info("Revvy is now ready!")
    
    # Welcome message based on component availability
    self._announce_system_status()
    
    # Main event loop with error recovery
    while self.running:
        try:
            # Check vehicle status
            self._safe_check_vehicle_status()
            
            # Process any pending events
            self._safe_process_events()
            
            # Check component health periodically
            self._check_component_health()
            
            # Sleep to prevent CPU hogging
            time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            logger.debug(traceback.format_exc())
            # Continue running despite errors
            time.sleep(1)  # Delay before retry

# Add these methods to RevvyCore:
def _announce_system_status(self):
    """Announce system status on startup"""
    messages = ["Revvy AI Companion is ready."]
    
    if not self.component_status['obd']['available']:
        messages.append("Vehicle connection is unavailable. Diagnostic features are limited.")
    
    if not self.component_status['gps']['available']:
        messages.append("GPS is unavailable. Location features are limited.")
    
    if not self.component_status['voice']['available']:
        messages.append("Voice system is unavailable. Using text-only mode.")
    
    message = " ".join(messages)
    if self.voice.voice_enabled and self.component_status['voice']['available']:
        self.voice.speak(message)
    logger.info(message)

@component_safe()
def _safe_check_vehicle_status(self):
    """Safe wrapper for check_vehicle_status"""
    if self.obd and self.obd.is_connected():
        battery_voltage = self.obd.get_battery_voltage()
        
        # Detect if engine is off (voltage typically drops below 13V when engine is off)
        if battery_voltage and battery_voltage < 12.5 and self.running:
            logger.info(f"Low voltage detected ({battery_voltage}V), preparing for shutdown")
            self.prepare_shutdown()

@component_safe()
def _safe_process_events(self):
    """Safe wrapper for process_events"""
    # Check for mode change requests
    pass

def _check_component_health(self):
    """Periodically check health of all components and attempt recovery"""
    # This method runs less frequently
    if random.random() > 0.01:  # ~1% chance each cycle (every ~10 seconds)
        return
    
    # Check OBD connection and try to recover if needed
    if self.component_status['obd']['available'] and not self.obd.is_connected():
        logger.info("OBD disconnected, attempting to reconnect")
        try:
            self.obd.connect()
        except Exception as e:
            logger.error(f"Failed to reconnect OBD: {e}")
    
    # Check GPS connection and try to recover if needed
    if self.component_status['gps']['available'] and not self.gps.is_active():
        logger.info("GPS inactive, attempting to restart")
        try:
            self.gps.restart()
        except Exception as e:
            logger.error(f"Failed to restart GPS: {e}")
    
    # Check voice system and try to recover if needed
    if self.component_status['voice']['available'] and not self.voice.is_active():
        logger.info("Voice system inactive, attempting to restart")
        try:
            self.voice.restart()
        except Exception as e:
            logger.error(f"Failed to restart Voice system: {e}")