import re
import logging
import threading
import time
from datetime import datetime

# Set up logger
logger = logging.getLogger("CommandHandler")

class CommandHandler:
    """Handles voice and text commands for the Revvy AI Companion"""
    
    def __init__(self, revvy_core):
        self.revvy_core = revvy_core
        self.command_patterns = {
            # Mode commands
            r'(switch|change) (to )?(.*?) mode': self._handle_mode_change,
            r'(enable|activate|turn on) (.*?) mode': self._handle_mode_change,
            
            # Personality commands
            r'(switch|change) (to )?(.*?) personality': self._handle_personality_change,
            
            # Unit system commands
            r'(switch|change) (to )?(metric|imperial) (units|system)': self._handle_unit_toggle,
            r'use (metric|imperial) (units|system)': self._handle_unit_toggle,
            
            # Information commands
            r'(what\'?s|what is|tell me|how\'?s|how is) (my |the )?(current )?(vehicle |car )?(status|condition)': self._handle_vehicle_status,
            r'(what\'?s|what is|tell me|how fast) (my |the |am i |are we )?(current )?(speed|going|driving)': self._handle_speed_request,
            r'(what\'?s|what is|tell me|how\'?s|how is) (my |the )?(current )?(engine|motor|rpm)': self._handle_engine_info,
            r'(what\'?s|what is|tell me|do i have|are there) (any |some )?(check engine|warning|trouble|diagnostic|dtc|error) (light|code|codes|issues|problems)': self._handle_diagnostic_codes,
            
            # Control commands
            r'(turn|switch) (on|off) (the )?(voice|speech|talking)': self._handle_voice_toggle,
            r'(mute|unmute) (yourself|revvy|assistant)': self._handle_voice_toggle,
            
            # System commands
            r'(restart|reboot) (yourself|system|revvy|assistant)': self._handle_system_restart,
            r'(shutdown|power off|turn off) (yourself|system|revvy|assistant)': self._handle_system_shutdown,
            
            # GPS commands
            r'(what\'?s|what is|tell me|where is|where am i|what\'?s my) (my |the |our )?(current )?(location|position|gps)': self._handle_location_request,
            
            # Help commands
            r'(help|what can you do|what commands|list commands|available commands)': self._handle_help_request,
            
            # Volume commands
            r'(increase|decrease|raise|lower|turn up|turn down) (the )?(volume|sound)': self._handle_volume_change,
            r'(set|change) (the )?volume (to|at) (\d+)( percent)?': self._handle_volume_set,
            
            # Diagnostic clear commands
            r'(clear|reset) (the )?(check engine|warning|trouble|diagnostic|dtc|error) (light|code|codes|issues|problems)': self._handle_clear_dtc
        }
        
        logger.info("Command Handler initialized")
    
    def process_command(self, command, context=None):
        """Process a user command using pattern matching and AI fallback"""
        logger.info(f"Processing command: {command}")
        
        # Check for direct pattern matches first
        for pattern, handler in self.command_patterns.items():
            match = re.search(pattern, command.lower())
            if match:
                logger.debug(f"Command matched pattern: {pattern}")
                
                # Extract the parameters from the match
                if "mode" in pattern:
                    mode = match.group(3)
                    return handler(mode)
                elif "personality" in pattern:
                    personality = match.group(3)
                    return handler(personality)
                elif "metric|imperial" in pattern:
                    unit_system = match.group(3)
                    return handler(unit_system)
                elif "volume (to|at)" in pattern:
                    volume = int(match.group(4))
                    return handler(volume)
                elif "volume|sound" in pattern:
                    direction = match.group(1)
                    return handler(direction)
                else:
                    # No parameters needed for this command
                    return handler()
        
        # No direct pattern match, use AI to interpret the command
        if self.revvy_core.ai and self.revvy_core.component_status['ai']['available']:
            # Build context for AI
            ai_context = {}
            
            # Add vehicle data if available
            if self.revvy_core.obd and self.revvy_core.obd.is_connected():
                ai_context['vehicle_data'] = self.revvy_core.obd.get_vehicle_data_with_units()
            
            # Add GPS data if available
            if self.revvy_core.gps and self.revvy_core.gps.is_active():
                ai_context['gps_data'] = self.revvy_core.gps.get_gps_data()
            
            # Add system status
            ai_context['system_status'] = {
                'mode': self.revvy_core.current_mode,
                'personality': self.revvy_core.current_personality,
                'voice_enabled': self.revvy_core.voice_enabled
            }
            
            # Process with AI and return response
            query_id = self.revvy_core.ai.query(command, ai_context)
            
            # This would normally be handled through a callback mechanism
            # For synchronous response, we'd need to implement a wait mechanism
            return f"I'm thinking about your request: '{command}'"
        else:
            return "I'm sorry, I couldn't understand that command and my AI processing is not available."
    
    def _handle_mode_change(self, mode):
        """Handle changing the operating mode"""
        available_modes = self.revvy_core.config.AVAILABLE_MODES
        
        # Try to find a matching mode
        matching_mode = None
        for available_mode in available_modes:
            if mode.lower() in available_mode.lower():
                matching_mode = available_mode
                break
        
        if matching_mode:
            # Check if mode requires age verification
            if matching_mode in self.revvy_core.config.get("modes", "age_restricted_modes", []):
                return f"The {matching_mode} Mode requires age verification. Please confirm in the app."
            
            # Change the mode
            success = self.revvy_core.set_mode(matching_mode)
            if success:
                return f"Switching to {matching_mode} Mode with {self.revvy_core.current_personality} personality."
            else:
                return f"I couldn't switch to {matching_mode} Mode. Please try again."
        else:
            return f"I couldn't find a mode matching '{mode}'. Available modes include Standard, Performance, and others."
    
    def _handle_personality_change(self, personality):
        """Handle changing the personality"""
        available_personalities = list(set(self.revvy_core.config.MODE_PERSONALITIES.values()))
        
        # Try to find a matching personality
        matching_personality = None
        for available_personality in available_personalities:
            if personality.lower() in available_personality.lower():
                matching_personality = available_personality
                break
        
        if matching_personality:
            # Change the personality
            success = self.revvy_core.set_personality(matching_personality)
            if success:
                return f"Switching to {matching_personality} personality."
            else:
                return f"I couldn't switch to {matching_personality} personality. Please try again."
        else:
            return f"I couldn't find a personality matching '{personality}'. Available personalities include Revvy OG, Turbo Revvy, and others."
    
    def _handle_voice_toggle(self, command=None):
        """Handle toggling voice on/off"""
        # Figure out the requested state
        voice_on = True
        if command and any(term in command.lower() for term in ["off", "mute"]):
            voice_on = False
        
        # Toggle voice state
        current_state = self.revvy_core.voice_enabled
        if voice_on != current_state:
            self.revvy_core.toggle_voice()
            
        if voice_on:
            return "Voice output enabled."
        else:
            return "Voice output disabled. I'll continue to respond via text."
    
    def _handle_system_restart(self):
        """Handle system restart request"""
        # Start a thread to restart the system after sending response
        threading.Thread(
            target=self._delayed_restart,
            daemon=True
        ).start()
        
        return "Preparing to restart. I'll be back in a moment."
    
    def _delayed_restart(self):
        """Restart the system after a short delay"""
        time.sleep(3.0)  # Give time for response to be delivered
        try:
            self.revvy_core.restart()
        except Exception as e:
            logger.error(f"Error during system restart: {e}")
    
    def _handle_system_shutdown(self):
        """Handle system shutdown request"""
        # Start a thread to shut down the system after sending response
        threading.Thread(
            target=self._delayed_shutdown,
            daemon=True
        ).start()
        
        return "Preparing to shut down. Goodbye!"
    
    def _delayed_shutdown(self):
        """Shut down the system after a short delay"""
        time.sleep(3.0)  # Give time for response to be delivered
        try:
            self.revvy_core.prepare_shutdown()
        except Exception as e:
            logger.error(f"Error during system shutdown: {e}")
    
    def _handle_location_request(self):
        """Handle request for current location"""
        if not self.revvy_core.gps or not self.revvy_core.gps.is_active():
            return "I can't access location information at the moment."
        
        # Check if we have a GPS fix
        gps_data = self.revvy_core.gps.get_gps_data()
        if not gps_data.get("fix", False):
            return "I don't have a GPS fix at the moment. Make sure you have a clear view of the sky."
        
        # Get coordinates
        lat = gps_data.get("latitude")
        lon = gps_data.get("longitude")
        
        # Basic response with coordinates
        response = f"Your current location is approximately {lat:.6f}, {lon:.6f}."
        
        # Add altitude if available
        altitude = gps_data.get("altitude")
        if altitude is not None:
            unit_system = self.revvy_core.config.get("display", "unit_system")
            if unit_system == "imperial":
                # Convert meters to feet
                altitude = altitude * 3.28084
                response += f" Altitude is {round(altitude)} feet above sea level."
            else:
                response += f" Altitude is {round(altitude)} meters above sea level."
        
        return response
    
    def _handle_help_request(self):
        """Handle request for help and available commands"""
        current_personality = self.revvy_core.current_personality
        
        help_text = f"Hi! I'm {current_personality}, your vehicle AI assistant. Here are some things you can ask me:\n\n"
        help_text += "• Vehicle information: Ask about speed, engine status, or general vehicle status\n"
        help_text += "• Diagnostics: Check for trouble codes or clear the check engine light\n"
        help_text += "• Location: Ask about your current location\n"
        help_text += "• Units: Switch between metric and imperial units\n"
        help_text += "• Modes: Change to different modes like Standard, Performance, or Mechanic\n"
        help_text += "• Personalities: Change my personality\n"
        help_text += "• Voice controls: Mute or unmute me, adjust volume\n\n"
        help_text += "You can also ask me questions, and I'll do my best to help!"
        
        return help_text
    
    def _handle_volume_change(self, direction=None):
        """Handle volume increase/decrease"""
        if not self.revvy_core.voice or not self.revvy_core.component_status['voice']['available']:
            return "I can't control the volume at the moment."
        
        # Get current volume
        current_volume = self.revvy_core.config.get("voice", "volume", 80)
        
        # Calculate new volume
        if direction and any(term in direction.lower() for term in ["increase", "raise", "up"]):
            new_volume = min(100, current_volume + 10)
            action = "increased"
        else:
            new_volume = max(0, current_volume - 10)
            action = "decreased"
        
        # Set new volume
        self.revvy_core.config.set("voice", "volume", new_volume)
        self.revvy_core.voice.set_volume(new_volume)
        
        return f"Volume {action} to {new_volume}%."
    
    def _handle_volume_set(self, volume):
        """Handle setting specific volume level"""
        if not self.revvy_core.voice or not self.revvy_core.component_status['voice']['available']:
            return "I can't control the volume at the moment."
        
        # Ensure volume is within valid range
        volume = max(0, min(100, volume))
        
        # Set volume
        self.revvy_core.config.set("voice", "volume", volume)
        self.revvy_core.voice.set_volume(volume)
        
        return f"Volume set to {volume}%."
    
    def _handle_clear_dtc(self):
        """Handle clearing diagnostic trouble codes"""
        if not self.revvy_core.obd or not self.revvy_core.obd.is_connected():
            return "I can't access the vehicle diagnostic system at the moment."
        
        # Check if there are any DTC codes to clear
        dtc_codes = self.revvy_core.obd.get_dtc_codes()
        if not dtc_codes:
            return "There are no diagnostic trouble codes to clear."
        
        # Attempt to clear DTC codes
        success = self.revvy_core.obd.clear_dtc_codes()
        if success:
            return f"I've cleared {len(dtc_codes)} diagnostic trouble codes. The check engine light should turn off soon if the issue has been resolved."
        else:
            return "I couldn't clear the diagnostic trouble codes. Please try again or consult a mechanic."