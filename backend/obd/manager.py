"""
Revvy AI Companion - OBD Manager
Handles communication with the vehicle through the OBD-II interface.
"""

import time
import logging
import threading
import traceback
import obd
from obd import OBDStatus
from utils.unit_converter import UnitConverter

logger = logging.getLogger("OBDManager")

class OBDManager:
    """Manages OBD connection and vehicle data"""
    
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.connected = False
        self.running = False
        self.thread = None
        self.data_lock = threading.Lock()
        
        # Vehicle data cache
        self.vehicle_data = {
            "rpm": 0,
            "speed": 0,
            "coolant_temp": 0,
            "intake_temp": 0,
            "throttle_pos": 0,
            "engine_load": 0,
            "fuel_level": 0,
            "battery_voltage": 12.0,
            "boost_pressure": 0,
            "oil_temp": 0,
            "dtc_codes": [],
            "is_check_engine_on": False,
            "has_turbo": False,
            "last_updated": time.time()
        }
        
        # Command mappings
        self.commands = {
            "rpm": obd.commands.RPM,
            "speed": obd.commands.SPEED,
            "coolant_temp": obd.commands.COOLANT_TEMP,
            "intake_temp": obd.commands.INTAKE_TEMP,
            "throttle_pos": obd.commands.THROTTLE_POS,
            "engine_load": obd.commands.ENGINE_LOAD,
            "fuel_level": obd.commands.FUEL_LEVEL,
            "battery_voltage": obd.commands.CONTROL_MODULE_VOLTAGE,
            "boost_pressure": obd.commands.INTAKE_PRESSURE,
            "oil_temp": obd.commands.OIL_TEMP,
            "status": obd.commands.STATUS,
            "dtc": obd.commands.GET_DTC
        }
        
        # Available commands for this vehicle
        self.available_commands = []
        
    def start(self):
        """Start OBD connection and monitoring thread"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("OBD Manager started")
        
    def stop(self):
        """Stop OBD connection and monitoring thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        
        if self.connection:
            self.connection.close()
            self.connected = False
            
        logger.info("OBD Manager stopped")
    
    def is_active(self):
        """Check if OBD manager is active"""
        return self.running and self.thread and self.thread.is_alive()

    def restart(self):
        """Attempt to restart the OBD manager"""
        logger.info("Attempting to restart OBD manager")
        self.stop()
        time.sleep(1)
        self.start()
    
    def connect(self):
        """Establish connection to the OBD adapter"""
        port = self.config.get("obd", "port")
        baudrate = self.config.get("obd", "baudrate")
        timeout = self.config.get("obd", "timeout")
        
        try:
            logger.info(f"Connecting to OBD on {port} at {baudrate} baud")
            
            # Create connection
            self.connection = obd.OBD(
                portstr=port,
                baudrate=baudrate,
                timeout=timeout,
                fast=False
            )
            
            # Check connection status
            if self.connection.status() == OBDStatus.CAR_CONNECTED:
                logger.info("Successfully connected to vehicle")
                self.connected = True
                
                # Get available commands
                self._discover_available_commands()
                
                # Check if vehicle has turbo
                self._detect_turbo()
                
                return True
            else:
                logger.warning(f"OBD connection failed: {self.connection.status()}")
                self.connected = False
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to OBD: {e}")
            self.connected = False
            return False
    
    def _discover_available_commands(self):
        """Discover available OBD commands for this vehicle"""
        if not self.connection:
            return
            
        self.available_commands = []
        
        for name, cmd in self.commands.items():
            if cmd in self.connection.supported_commands:
                self.available_commands.append(name)
                logger.debug(f"Command available: {name}")
            else:
                logger.debug(f"Command not supported: {name}")
                
        logger.info(f"Discovered {len(self.available_commands)} available OBD commands")
    
    def _detect_turbo(self):
        """Detect if vehicle has a turbo/supercharger by checking for boost pressure"""
        if "boost_pressure" in self.available_commands:
            try:
                response = self.connection.query(self.commands["boost_pressure"])
                if response.is_null():
                    self.vehicle_data["has_turbo"] = False
                else:
                    # If the sensor is present, assume it may have a turbo
                    self.vehicle_data["has_turbo"] = True
                    logger.info("Turbo/supercharger detected (boost pressure sensor present)")
            except Exception as e:
                logger.error(f"Error detecting turbo: {e}")
        else:
            logger.info("No boost pressure sensor detected, assuming naturally aspirated")
            self.vehicle_data["has_turbo"] = False
    
    def _monitor_loop(self):
        """Main monitoring loop that continuously polls vehicle data"""
        reconnect_attempts = 0
        max_reconnect_attempts = self.config.get("obd", "reconnect_attempts")
        polling_interval = self.config.get("obd", "polling_interval")
        dtc_check_interval = self.config.get("obd", "dtc_check_interval")
        last_dtc_check = 0
        
        while self.running:
            try:
                # Try to connect if not connected
                if not self.connected:
                    if reconnect_attempts < max_reconnect_attempts:
                        reconnect_attempts += 1
                        logger.info(f"Attempting to connect to OBD ({reconnect_attempts}/{max_reconnect_attempts})")
                        
                        if self.connect():
                            reconnect_attempts = 0
                        else:
                            time.sleep(2)  # Wait before retry
                    else:
                        logger.error("Max reconnection attempts reached, will retry later")
                        # Don't exit, just wait a longer time before trying again
                        time.sleep(30)
                        reconnect_attempts = 0
                        
                # If connected, poll data
                if self.connected:
                    try:
                        # Update standard metrics
                        self._update_metrics()
                        
                        # Check DTCs periodically (not on every cycle to reduce overhead)
                        current_time = time.time()
                        if current_time - last_dtc_check > dtc_check_interval:
                            self._check_dtc_codes()
                            last_dtc_check = current_time
                        
                        # Reset reconnect counter on successful poll
                        reconnect_attempts = 0
                        
                    except Exception as e:
                        logger.error(f"Error polling OBD data: {e}")
                        # Don't immediately mark as disconnected, maybe it's just a temporary error
                        # Only mark as disconnected after repeated failures
                        if reconnect_attempts > 3:
                            logger.error("Multiple polling failures, marking OBD as disconnected")
                            self.connected = False
                        reconnect_attempts += 1
                
                # Sleep for polling interval
                time.sleep(polling_interval)
                
            except Exception as e:
                logger.error(f"Unexpected error in OBD monitor loop: {e}")
                logger.debug(traceback.format_exc())
                # Don't exit the loop, just sleep and continue
                time.sleep(5)
    
    def _update_metrics(self):
        """Update vehicle metrics from OBD"""
        if not self.connection or not self.connected:
            return
            
        with self.data_lock:
            # Update each available metric
            for name in self.available_commands:
                try:
                    if name in ["dtc", "status"]:  # Skip special commands
                        continue
                        
                    cmd = self.commands[name]
                    response = self.connection.query(cmd)
                    
                    if not response.is_null():
                        # Store the value
                        self.vehicle_data[name] = response.value.magnitude
                    
                except Exception as e:
                    logger.debug(f"Error updating {name}: {e}")
            
            # Update timestamp
            self.vehicle_data["last_updated"] = time.time()
    
    def _check_dtc_codes(self):
        """Check for Diagnostic Trouble Codes"""
        if not self.connection or not self.connected:
            return
            
        try:
            # Check engine status
            status_response = self.connection.query(self.commands["status"])
            if not status_response.is_null():
                self.vehicle_data["is_check_engine_on"] = status_response.value.MIL
            
            # Get DTCs if check engine light is on
            if self.vehicle_data["is_check_engine_on"]:
                dtc_response = self.connection.query(self.commands["dtc"])
                if not dtc_response.is_null():
                    with self.data_lock:
                        self.vehicle_data["dtc_codes"] = dtc_response.value
                    
                    # Log DTCs
                    if dtc_response.value:
                        logger.warning(f"DTCs detected: {dtc_response.value}")
            else:
                with self.data_lock:
                    self.vehicle_data["dtc_codes"] = []
                
        except Exception as e:
            logger.error(f"Error checking DTCs: {e}")
    
    def get_vehicle_data(self):
        """Get all vehicle data"""
        with self.data_lock:
            return self.vehicle_data.copy()
    
    def get_vehicle_data_with_units(self):
        """Get vehicle data converted to user's preferred units"""
        data = self.get_vehicle_data()
        unit_system = self.config.get("display", "unit_system")
        
        if unit_system == "imperial":
            # Convert speed from kph to mph
            if "speed" in data:
                data["speed"] = UnitConverter.kph_to_mph(data["speed"])
                data["speed_unit"] = "mph"
            
            # Convert temperatures from C to F
            for temp_field in ["coolant_temp", "intake_temp", "oil_temp"]:
                if temp_field in data:
                    data[temp_field] = UnitConverter.celsius_to_fahrenheit(data[temp_field])
                    data[f"{temp_field}_unit"] = "F"
            
            # Convert pressure from kPa to PSI
            if "boost_pressure" in data:
                data["boost_pressure"] = UnitConverter.kpa_to_psi(data["boost_pressure"])
                data["boost_pressure_unit"] = "psi"
        else:
            # Add unit labels for metric
            if "speed" in data:
                data["speed_unit"] = "km/h"
            
            for temp_field in ["coolant_temp", "intake_temp", "oil_temp"]:
                if temp_field in data:
                    data[f"{temp_field}_unit"] = "C"
            
            if "boost_pressure" in data:
                data["boost_pressure_unit"] = "kPa"
        
        return data
    
    def get_metric(self, metric_name):
        """Get a specific vehicle metric"""
        with self.data_lock:
            return self.vehicle_data.get(metric_name)
    
    def get_speed_with_unit(self):
        """Get speed in user's preferred unit with unit label"""
        speed = self.get_metric("speed")
        unit_system = self.config.get("display", "unit_system")
        
        if unit_system == "imperial":
            speed = UnitConverter.kph_to_mph(speed)
            return {"value": speed, "unit": "mph"}
        else:
            return {"value": speed, "unit": "km/h"}
    
    def get_rpm(self):
        """Get engine RPM"""
        return self.get_metric("rpm")
    
    def get_speed(self):
        """Get vehicle speed in km/h"""
        return self.get_metric("speed")
    
    def get_coolant_temp(self):
        """Get engine coolant temperature in Celsius"""
        return self.get_metric("coolant_temp")
    
    def get_throttle_pos(self):
        """Get throttle position as percentage"""
        return self.get_metric("throttle_pos")
    
    def get_battery_voltage(self):
        """Get battery voltage"""
        return self.get_metric("battery_voltage")
    
    def get_boost_pressure(self):
        """Get boost/intake pressure in kPa"""
        return self.get_metric("boost_pressure")
    
    def get_dtc_codes(self):
        """Get current DTC codes"""
        return self.get_metric("dtc_codes")
    
    def clear_dtc_codes(self):
        """Clear DTC codes"""
        if not self.connection or not self.connected:
            return False
            
        try:
            self.connection.query(obd.commands.CLEAR_DTC)
            logger.info("DTC codes cleared")
            
            # Recheck DTCs after clearing
            self._check_dtc_codes()
            return True
            
        except Exception as e:
            logger.error(f"Error clearing DTCs: {e}")
            return False
    
    def is_connected(self):
        """Check if connected to vehicle"""
        return self.connected
    
    def has_turbo(self):
        """Check if vehicle has turbo/supercharger"""
        return self.get_metric("has_turbo")