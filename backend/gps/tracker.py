"""
Revvy AI Companion - GPS Tracker
Handles GPS location services
"""

import os
import time
import logging
import threading
import json
import serial
import pynmea2
import traceback

logger = logging.getLogger("GPSTracker")

class GPSTracker:
    """Tracks vehicle location using GPS"""
    
    def __init__(self, config):
        self.config = config
        self.running = False
        self.thread = None
        self.serial = None
        self.active = False
        
        # GPS settings
        self.port = self.config.get("gps", "port")
        self.baudrate = self.config.get("gps", "baudrate")
        self.update_interval = self.config.get("gps", "update_interval")
        
        # Default location (used when GPS is unavailable)
        self.default_lat = self.config.get("gps", "default_latitude", 37.7749)
        self.default_lon = self.config.get("gps", "default_longitude", -122.4194)
        
        # GPS data
        self.gps_data = {
            "latitude": self.default_lat,
            "longitude": self.default_lon,
            "altitude": 0.0,
            "speed": 0.0,
            "heading": 0.0,
            "satellites": 0,
            "fix": False,
            "last_updated": 0
        }
        
        # Trip data
        self.trip_start_time = 0
        self.trip_distance = 0.0
        self.last_location = None
        
    def start(self):
        """Start GPS tracking"""
        self.running = True
        self.thread = threading.Thread(target=self._gps_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("GPS Tracker started")
        
    def stop(self):
        """Stop GPS tracking"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        
        if self.serial:
            try:
                self.serial.close()
            except:
                pass
            self.serial = None
            
        self.active = False
        logger.info("GPS Tracker stopped")
    
    def restart(self):
        """Restart GPS tracking"""
        logger.info("Restarting GPS tracker")
        self.stop()
        time.sleep(1)
        self.start()
    
    def _connect_gps(self):
        """Connect to GPS device"""
        try:
            if self.serial and self.serial.is_open:
                self.serial.close()
                
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            logger.info(f"Connected to GPS on {self.port}")
            self.active = True
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to GPS: {e}")
            self.active = False
            self.serial = None
            return False
    
    def _gps_loop(self):
        """Main GPS reading loop"""
        connect_attempts = 0
        reconnect_interval = 10  # seconds
        
        while self.running:
            try:
                # Try to connect if not already connected
                if not self.serial:
                    if connect_attempts > 0 and connect_attempts % 6 == 0:
                        logger.info(f"Multiple GPS connection failures, will keep trying")
                    
                    if not self._connect_gps():
                        connect_attempts += 1
                        time.sleep(reconnect_interval)
                        continue
                    else:
                        connect_attempts = 0
                
                # Read GPS data
                if self.serial:
                    try:
                        line = self.serial.readline().decode('ascii', errors='replace').strip()
                        
                        if line.startswith('$'):
                            try:
                                msg = pynmea2.parse(line)
                                self._process_nmea_message(msg)
                            except pynmea2.ParseError:
                                pass  # Ignore parse errors, they're common
                    except (serial.SerialException, UnicodeDecodeError) as e:
                        logger.error(f"Error reading GPS data: {e}")
                        # Close and reopen on error
                        try:
                            if self.serial:
                                self.serial.close()
                        except:
                            pass
                        self.serial = None
                        self.active = False
                        time.sleep(1)
                
            except Exception as e:
                logger.error(f"Unexpected error in GPS loop: {e}")
                logger.debug(traceback.format_exc())
                # Don't exit the loop, just sleep and continue
                time.sleep(5)
    
    def _process_nmea_message(self, msg):
        """Process NMEA message and update GPS data"""
        try:
            # Process GGA message (fix data)
            if isinstance(msg, pynmea2.GGA):
                if msg.latitude and msg.longitude:
                    self.gps_data["latitude"] = msg.latitude
                    self.gps_data["longitude"] = msg.longitude
                    self.gps_data["altitude"] = msg.altitude if msg.altitude else 0.0
                    self.gps_data["satellites"] = msg.num_sats if msg.num_sats else 0
                    self.gps_data["fix"] = msg.gps_qual > 0
                    self.gps_data["last_updated"] = time.time()
                    
                    # Update trip data
                    self._update_trip_data()
            
            # Process RMC message (recommended minimum data)
            elif isinstance(msg, pynmea2.RMC):
                if msg.status == 'A':  # A=active, V=void
                    self.gps_data["speed"] = msg.spd_over_grnd * 1.852 if msg.spd_over_grnd else 0.0  # Convert knots to km/h
                    self.gps_data["heading"] = msg.true_course if msg.true_course else 0.0
                
        except Exception as e:
            logger.error(f"Error processing NMEA message: {e}")
    
    def _update_trip_data(self):
        """Update trip data with new location"""
        current_location = (self.gps_data["latitude"], self.gps_data["longitude"])
        
        # Initialize trip if needed
        if self.trip_start_time == 0:
            self.trip_start_time = time.time()
            self.last_location = current_location
            return
        
        # Update trip distance if we have a previous location
        if self.last_location:
            try:
                distance = self._calculate_distance(self.last_location, current_location)
                
                # Only add distance if it's reasonable (avoid GPS jumps)
                if distance < 0.5:  # Less than 500m between readings
                    self.trip_distance += distance
                
                self.last_location = current_location
                
            except Exception as e:
                logger.error(f"Error calculating trip distance: {e}")
    
    def _calculate_distance(self, loc1, loc2):
        """Calculate distance between two coordinates in kilometers"""
        import math
        
        lat1, lon1 = loc1
        lat2, lon2 = loc2
        
        # Convert to radians
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Radius of earth in kilometers
        
        return c * r
    
    def get_location(self):
        """Get current location"""
        if self.gps_data["fix"]:
            return {
                "latitude": self.gps_data["latitude"],
                "longitude": self.gps_data["longitude"]
            }
        else:
            return {
                "latitude": self.default_lat,
                "longitude": self.default_lon,
                "is_default": True
            }
    
    def get_speed(self):
        """Get current speed in km/h"""
        return self.gps_data["speed"] if self.gps_data["fix"] else 0.0
    
    def get_trip_data(self):
        """Get trip data"""
        current_time = time.time()
        trip_duration = current_time - self.trip_start_time if self.trip_start_time > 0 else 0
        
        return {
            "distance": self.trip_distance,  # km
            "duration": trip_duration,       # seconds
            "avg_speed": self.trip_distance / (trip_duration / 3600) if trip_duration > 0 else 0  # km/h
        }
    
    def reset_trip(self):
        """Reset trip data"""
        self.trip_start_time = time.time()
        self.trip_distance = 0.0
        self.last_location = None
        logger.info("Trip data reset")
    
    def get_gps_data(self):
        """Get all GPS data"""
        return self.gps_data.copy()
    
    def has_fix(self):
        """Check if GPS has a fix"""
        return self.gps_data["fix"]
    
    def is_active(self):
        """Check if GPS tracker is active"""
        return self.active and self.running and self.thread and self.thread.is_alive()