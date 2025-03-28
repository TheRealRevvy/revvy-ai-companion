"""
Revvy AI Companion - Mock Components
Provides fallback implementations when real hardware is unavailable
"""

import logging
import time
import random
import threading

logger = logging.getLogger("MockComponents")

class MockOBDManager:
    """Mock OBD Manager for when no real OBD connection is available"""
    
    def __init__(self, config):
        self.config = config
        self.connected = False
        self.running = False
        self.thread = None
        
        # Simulated vehicle data
        self.vehicle_data = {
            "rpm": 0,
            "speed": 0,
            "coolant_temp": 80,
            "intake_temp": 30,
            "throttle_pos": 0,
            "engine_load": 0,
            "fuel_level": 75,
            "battery_voltage": 14.0,
            "boost_pressure": 0,
            "oil_temp": 90,
            "dtc_codes": [],
            "is_check_engine_on": False,
            "has_turbo": False,
            "last_updated": time.time()
        }
        
        logger.info("Mock OBD Manager initialized")
    
    def start(self):
        """Start mock OBD"""
        self.running = True
        self.thread = threading.Thread(target=self._simulate_data)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Mock OBD Manager started")
    
    def stop(self):
        """Stop mock OBD"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        logger.info("Mock OBD Manager stopped")
    
    def connect(self):
        """Simulate connection"""
        self.connected = True
        logger.info("Mock OBD connected")
        return True
    
    def _simulate_data(self):
        """Simulate vehicle data"""
        while self.running:
            # Simulate some basic vehicle data
            if self.connected:
                self.vehicle_data["rpm"] = 800 + random.randint(-50, 50)
                self.vehicle_data["speed"] = 0
                self.vehicle_data["throttle_pos"] = 5 + random.randint(-2, 2)
                self.vehicle_data["coolant_temp"] = 80 + random.randint(-5, 5)
                self.vehicle_data["last_updated"] = time.time()
            
            time.sleep(1.0)
    
    def get_vehicle_data(self):
        """Get simulated vehicle data"""
        return self.vehicle_data.copy()
    
    def get_metric(self, metric_name):
        """Get a specific metric"""
        return self.vehicle_data.get(metric_name)
    
    def get_rpm(self):
        """Get simulated RPM"""
        return self.vehicle_data.get("rpm")
    
    def get_speed(self):
        """Get simulated speed"""
        return self.vehicle_data.get("speed")
    
    def get_coolant_temp(self):
        """Get simulated coolant temperature"""
        return self.vehicle_data.get("coolant_temp")
    
    def get_throttle_pos(self):
        """Get simulated throttle position"""
        return self.vehicle_data.get("throttle_pos")
    
    def get_battery_voltage(self):
        """Get simulated battery voltage"""
        return self.vehicle_data.get("battery_voltage")
    
    def get_boost_pressure(self):
        """Get simulated boost pressure"""
        return self.vehicle_data.get("boost_pressure")
    
    def get_dtc_codes(self):
        """Get simulated DTC codes"""
        return self.vehicle_data.get("dtc_codes")
    
    def clear_dtc_codes(self):
        """Clear simulated DTC codes"""
        self.vehicle_data["dtc_codes"] = []
        self.vehicle_data["is_check_engine_on"] = False
        return True
    
    def is_connected(self):
        """Check if mock OBD is connected"""
        return self.connected
    
    def has_turbo(self):
        """Check if mock vehicle has turbo"""
        return self.vehicle_data.get("has_turbo")


class MockGPSTracker:
    """Mock GPS Tracker for when no real GPS connection is available"""
    
    def __init__(self, config):
        self.config = config
        self.running = False
        self.thread = None
        self.active = False
        
        # Default location (can be set in config)
        self.default_lat = self.config.get("gps", "default_latitude", 37.7749)
        self.default_lon = self.config.get("gps", "default_longitude", -122.4194)
        
        # Simulated GPS data
        self.gps_data = {
            "latitude": self.default_lat,
            "longitude": self.default_lon,
            "altitude": 10.0,
            "speed": 0.0,
            "heading": 0.0,
            "satellites": 0,
            "fix": False,
            "last_updated": time.time()
        }
        
        logger.info("Mock GPS Tracker initialized")
    
    def start(self):
        """Start mock GPS"""
        self.running = True
        self.active = True
        self.thread = threading.Thread(target=self._simulate_data)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Mock GPS Tracker started")
    
    def stop(self):
        """Stop mock GPS"""
        self.running = False
        self.active = False
        if self.thread:
            self.thread.join(timeout=1.0)
        logger.info("Mock GPS Tracker stopped")
    
    def restart(self):
        """Restart mock GPS"""
        self.stop()
        self.start()
    
    def _simulate_data(self):
        """Simulate GPS data"""
        while self.running:
            # Just update the timestamp, keep position fixed
            self.gps_data["last_updated"] = time.time()
            self.gps_data["satellites"] = 8  # Fake a good satellite count
            self.gps_data["fix"] = True      # Fake having a position fix
            
            time.sleep(1.0)
    
    def get_location(self):
        """Get simulated location"""
        return {
            "latitude": self.gps_data["latitude"],
            "longitude": self.gps_data["longitude"]
        }
    
    def get_gps_data(self):
        """Get all simulated GPS data"""
        return self.gps_data.copy()
    
    def has_fix(self):
        """Check if mock GPS has a fix"""
        return self.gps_data["fix"]
    
    def is_active(self):
        """Check if mock GPS is active"""
        return self.active


class MockAIEngine:
    """Mock AI Engine for when no real AI is available"""
    
    def __init__(self, config):
        self.config = config
        self.running = False
        
        # Fallback responses for common queries
        self.fallback_responses = {
            "hello": "Hello! I'm running in fallback mode, but I'm still here to help.",
            "how are you": "I'm operating in fallback mode, but doing my best!",
            "help": "I can provide basic information about your vehicle, even in fallback mode.",
            "speed": "I can't access real speed data in fallback mode.",
            "temperature": "Engine temperature information isn't available in fallback mode.",
            "diagnostic": "Vehicle diagnostics aren't available in fallback mode.",
            "default": "I'm running in fallback mode with limited capabilities. I can't process complex requests right now."
        }
        
        logger.info("Mock AI Engine initialized")
    
    def start(self):
        """Start mock AI"""
        self.running = True
        logger.info("Mock AI Engine started")
    
    def stop(self):
        """Stop mock AI"""
        self.running = False
        logger.info("Mock AI Engine stopped")
    
    def query(self, query_text, context=None, callback=None):
        """Handle a query with fallback responses"""
        query_id = f"q{int(time.time() * 1000)}"
        
        # Simple keyword matching for fallback responses
        response = self.fallback_responses.get("default")
        for keyword, resp in self.fallback_responses.items():
            if keyword in query_text.lower():
                response = resp
                break
        
        # Call callback if provided
        if callback:
            callback(query_id, response)
        
        return query_id
    
    def update_vehicle_context(self, vehicle_data):
        """Mock update vehicle context"""
        pass
    
    def set_personality(self, personality):
        """Mock set personality"""
        return True
    
    def interpret_dtc(self, dtc_code):
        """Mock interpret DTC"""
        return f"Fallback mode: DTC code interpretation for {dtc_code} is unavailable."


class MockVoiceSystem:
    """Mock Voice System for when no real voice hardware is available"""
    
    def __init__(self, config):
        self.config = config
        self.running = False
        self.voice_enabled = self.config.get("voice", "enable_voice", True)
        self.active = False
        
        logger.info("Mock Voice System initialized")
    
    def start(self):
        """Start mock voice system"""
        self.running = True
        self.active = True
        logger.info("Mock Voice System started")
    
    def stop(self):
        """Stop mock voice system"""
        self.running = False
        self.active = False
        logger.info("Mock Voice System stopped")
    
    def restart(self):
        """Restart mock voice system"""
        self.stop()
        self.start()
    
    def speak(self, text, interrupt=False):
        """Mock speaking text"""
        if self.voice_enabled:
            logger.info(f"MOCK SPEAK: {text}")
    
    def set_voice(self, voice_name):
        """Mock set voice"""
        return True
    
    def set_volume(self, volume):
        """Mock set volume"""
        return True
    
    def enable_voice(self, enabled):
        """Enable or disable mock voice"""
        self.voice_enabled = enabled
        return True
    
    def is_active(self):
        """Check if mock voice system is active"""
        return self.active


class MockAPIServer:
    """Mock API Server for when no real API server can be started"""
    
    def __init__(self, config, revvy_core):
        self.config = config
        self.revvy_core = revvy_core
        self.running = False
        
        logger.info("Mock API Server initialized")
    
    def start(self):
        """Start mock API server"""
        self.running = True
        logger.info("Mock API Server started")
    
    def stop(self):
        """Stop mock API server"""
        self.running = False
        logger.info("Mock API Server stopped")
    
    def broadcast_event(self, event_type, data):
        """Mock broadcast event"""
        logger.debug(f"MOCK BROADCAST: {event_type} - {data}")