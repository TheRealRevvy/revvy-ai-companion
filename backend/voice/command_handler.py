    def _handle_unit_toggle(self, unit_system):
        """Handle toggling of unit system"""
        if unit_system.lower() not in ['metric', 'imperial']:
            return f"I didn't understand which unit system you wanted. You can say 'switch to metric' or 'switch to imperial'."
        
        # Update config
        self.revvy_core.config.set("display", "unit_system", unit_system.lower())
        
        # Update related units
        if unit_system.lower() == 'metric':
            self.revvy_core.config.set("display", "temperature_unit", "celsius")
            self.revvy_core.config.set("display", "pressure_unit", "kpa")
            self.revvy_core.config.set("display", "distance_unit", "km")
            self.revvy_core.config.set("display", "speed_unit", "kph")
            
            return "Switching to metric units. I'll now display speeds in kilometers per hour and temperatures in Celsius."
        else:
            self.revvy_core.config.set("display", "temperature_unit", "fahrenheit")
            self.revvy_core.config.set("display", "pressure_unit", "psi")
            self.revvy_core.config.set("display", "distance_unit", "mi")
            self.revvy_core.config.set("display", "speed_unit", "mph")
            
            return "Switching to imperial units. I'll now display speeds in miles per hour and temperatures in Fahrenheit."
    
    def _handle_vehicle_status(self):
        """Handle request for vehicle status"""
        if not self.revvy_core.obd or not self.revvy_core.obd.is_connected():
            return "I can't access vehicle information at the moment."
        
        unit_system = self.revvy_core.config.get("display", "unit_system")
        vehicle_data = self.revvy_core.obd.get_vehicle_data_with_units()
        
        status = []
        
        # Check speed
        if "speed" in vehicle_data:
            speed = vehicle_data["speed"]
            speed_unit = "mph" if unit_system == "imperial" else "km/h"
            status.append(f"Current speed is {round(speed)} {speed_unit}.")
        
        # Check engine
        if "rpm" in vehicle_data:
            status.append(f"Engine is running at {vehicle_data['rpm']} RPM.")
        
        # Check temperature
        if "coolant_temp" in vehicle_data:
            temp = vehicle_data["coolant_temp"]
            temp_unit = "°F" if unit_system == "imperial" else "°C"
            
            if unit_system == "imperial":
                temp_warning = 230  # °F
                temp_cold = 104     # °F
            else:
                temp_warning = 110  # °C
                temp_cold = 40      # °C
                
            if temp > temp_warning:
                status.append(f"Engine temperature is high at {round(temp)}{temp_unit}. Please check your coolant level.")
            elif temp < temp_cold and vehicle_data.get('rpm', 0) > 1000:
                status.append(f"Engine is still warming up. Temperature is {round(temp)}{temp_unit}.")
            else:
                status.append(f"Engine temperature is normal at {round(temp)}{temp_unit}.")
        
        # Check fuel
        if "fuel_level" in vehicle_data:
            fuel_level = vehicle_data["fuel_level"]
            if fuel_level < 15:
                status.append(f"Fuel level is low at {round(fuel_level)}%. Please refuel soon.")
            else:
                status.append(f"Fuel level is at {round(fuel_level)}%.")
        
        # Check for DTC codes
        dtc_codes = vehicle_data.get('dtc_codes', [])
        if dtc_codes:
            status.append(f"There are {len(dtc_codes)} diagnostic trouble codes present. Would you like me to read them?")
        
        return " ".join(status)
    
    def _handle_speed_request(self):
        """Handle request for current speed"""
        if not self.revvy_core.obd or not self.revvy_core.obd.is_connected():
            return "I can't access speed information at the moment."
        
        unit_system = self.revvy_core.config.get("display", "unit_system")
        speed_data = self.revvy_core.obd.get_speed_with_unit()
        
        if speed_data["value"] is None:
            return f"I can't determine the current speed."
            
        return f"Your current speed is {round(speed_data['value'])} {speed_data['unit']}."
    
    def _handle_engine_info(self):
        """Handle request for engine information"""
        if not self.revvy_core.obd or not self.revvy_core.obd.is_connected():
            return "I can't access engine information at the moment."
        
        unit_system = self.revvy_core.config.get("display", "unit_system")
        vehicle_data = self.revvy_core.obd.get_vehicle_data_with_units()
        
        rpm = vehicle_data.get('rpm')
        coolant_temp = vehicle_data.get('coolant_temp')
        temp_unit = "°F" if unit_system == "imperial" else "°C"
        throttle_pos = vehicle_data.get('throttle_pos')
        
        response = []
        
        if rpm is not None:
            response.append(f"Engine is running at {round(rpm)} RPM")
        
        if coolant_temp is not None:
            response.append(f"coolant temperature at {round(coolant_temp)}{temp_unit}")
        
        if throttle_pos is not None:
            response.append(f"throttle position at {round(throttle_pos)}%")
        
        if not response:
            return "I can't get any engine information at the moment."
        
        response_text = "Engine status: " + ", ".join(response) + "."
        
        if vehicle_data.get('has_turbo', False):
            boost = vehicle_data.get('boost_pressure')
            boost_unit = "psi" if unit_system == "imperial" else "kPa"
            
            if boost is not None and boost > 0:
                response_text += f" Turbo is providing {boost if unit_system == 'imperial' else round(boost)} {boost_unit} of boost pressure."
            else:
                response_text += " Turbo is not currently building boost."
        
        return response_text
    
    def _handle_diagnostic_codes(self):
        """Handle request for diagnostic codes"""
        if not self.revvy_core.obd or not self.revvy_core.obd.is_connected():
            return "I can't access diagnostic information at the moment."
        
        dtc_codes = self.revvy_core.obd.get_dtc_codes()
        
        if not dtc_codes:
            return "Good news! No diagnostic trouble codes found. Your vehicle is running without any reported issues."
        
        response = f"I found {len(dtc_codes)} diagnostic trouble codes: "
        
        # Add each code with a brief explanation
        for code in dtc_codes:
            # Start a thread to get the detailed explanation for the app
            threading.Thread(
                target=self._get_dtc_explanation_async,
                args=(code,),
                daemon=True
            ).start()
            
            # For voice, just mention the code
            response += f"{code}, "
        
        response = response.rstrip(', ')
        response += ". Would you like me to explain what these codes mean?"
        
        return response
    
    def _get_dtc_explanation_async(self, code):
        """Get DTC explanation in background thread"""
        try:
            # Use AI engine to interpret the code
            self.revvy_core.ai.interpret_dtc(code)
        except Exception as e:
            logger.error(f"Error getting DTC explanation: {e}")