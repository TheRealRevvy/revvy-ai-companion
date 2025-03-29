# Add unit awareness to the AI Engine
from datetime import datetime

def _build_prompt(self, query, context=None):
    """Build a prompt with context and conversation history"""
    # Get personality traits
    personality_traits = self._get_personality_traits()
    
    # Get unit system
    unit_system = self.config.get("display", "unit_system", "metric")
    
    # Start with system prompt
    prompt = f"""You are {self.current_personality}, an AI assistant for vehicles. 
{personality_traits}

Current Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Using {unit_system.capitalize()} Units
"""
    
    # Add vehicle context if available
    if context and 'vehicle_data' in context:
        vehicle_data = context['vehicle_data']
        
        # Format vehicle data with appropriate units
        vehicle_context = "Current Vehicle Status:\n"
        
        # Speed in appropriate units
        if 'speed' in vehicle_data and vehicle_data['speed'] is not None:
            speed_unit = "mph" if unit_system == "imperial" else "km/h"
            vehicle_context += f"- Speed: {round(vehicle_data['speed'])} {speed_unit}\n"
        
        # Engine RPM
        if 'rpm' in vehicle_data and vehicle_data['rpm'] is not None:
            vehicle_context += f"- Engine RPM: {vehicle_data['rpm']}\n"
        
        # Temperature in appropriate units
        if 'coolant_temp' in vehicle_data and vehicle_data['coolant_temp'] is not None:
            temp_unit = "°F" if unit_system == "imperial" else "°C"
            vehicle_context += f"- Coolant Temperature: {round(vehicle_data['coolant_temp'])} {temp_unit}\n"
        
        # Fuel level
        if 'fuel_level' in vehicle_data and vehicle_data['fuel_level'] is not None:
            vehicle_context += f"- Fuel Level: {round(vehicle_data['fuel_level'])}%\n"
        
        # Throttle position
        if 'throttle_pos' in vehicle_data and vehicle_data['throttle_pos'] is not None:
            vehicle_context += f"- Throttle Position: {round(vehicle_data['throttle_pos'])}%\n"
        
        # Boost pressure if vehicle has turbo
        if 'has_turbo' in vehicle_data and vehicle_data['has_turbo'] and 'boost_pressure' in vehicle_data:
            pressure_unit = "psi" if unit_system == "imperial" else "kPa"
            boost = vehicle_data['boost_pressure']
            if boost is not None:
                vehicle_context += f"- Boost Pressure: {round(boost) if unit_system == 'metric' else boost} {pressure_unit}\n"
        
        # Add diagnostic status
        if 'dtc_codes' in vehicle_data and vehicle_data['dtc_codes']:
            vehicle_context += f"- Check Engine Light: ON\n"
            vehicle_context += f"- DTC Codes: {', '.join(vehicle_data['dtc_codes'])}\n"
        else:
            vehicle_context += f"- Check Engine Light: OFF\n"
        
        # Add vehicle context to prompt
        prompt += f"\n{vehicle_context}\n"
    
    # Add GPS location if available
    if context and 'gps_data' in context:
        gps_data = context['gps_data']
        if gps_data.get('fix', False):
            lat = gps_data.get('latitude')
            lon = gps_data.get('longitude')
            prompt += f"\nCurrent Location: {lat}, {lon}\n"
    
    # Add conversation history
    if hasattr(self, 'conversation_history') and self.conversation_history:
        prompt += "\nConversation History:\n"
        
        # Get the last few conversations based on memory limit
        memory_limit = self.config.get("ai", "memory_limit", 10)
        recent_history = self.conversation_history[-memory_limit:]
        
        for entry in recent_history:
            prompt += f"User: {entry['user']}\n"
            prompt += f"Revvy: {entry['assistant']}\n"
    
    # Add the current query
    prompt += f"\nUser: {query}\nRevvy: "
    
    return prompt