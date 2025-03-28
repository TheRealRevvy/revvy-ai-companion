"""
Revvy AI Companion - Voice System
Handles voice activation, speech recognition, and text-to-speech functionality.
"""

import os
import time
import logging
import threading
import queue
import json
from collections import deque
import numpy as np
import sounddevice as sd
import soundfile as sf
import pvporcupine
from pvrecorder import PvRecorder
import pyttsx3
import speech_recognition as sr

logger = logging.getLogger("VoiceSystem")

class VoiceSystem:
    """Handles voice interactions with wake word detection and TTS"""
    
    def __init__(self, config, ai_engine):
        self.config = config
        self.ai_engine = ai_engine
        self.running = False
        self.thread = None
        self.wake_word_thread = None
        self.tts_queue = queue.Queue()
        
        # Voice settings
        self.wake_word = self.config.get("voice", "wake_word")
        self.wake_word_sensitivity = self.config.get("voice", "wake_word_sensitivity")
        self.volume = self.config.get("voice", "volume")
        self.voice_enabled = self.config.get("voice", "enable_voice")
        self.mic_index = self.config.get("voice", "mic_index")
        self.speaker_device = self.config.get("voice", "speaker_device")
        
        # Porcupine wake word engine
        self.porcupine = None
        self.recorder = None
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        
        # Text-to-speech engine
        self.tts_engine = None
        
        # Current voice (based on personality)
        self.current_voice = "default"
        
        # Cache for audio samples
        self.audio_cache = {}
        
    def start(self):
        """Start voice system"""
        if not self.voice_enabled:
            logger.info("Voice system is disabled in config")
            return
        
        self.running = True
        
        # Initialize wake word detection
        self._init_wake_word()
        
        # Initialize TTS engine
        self._init_tts()
        
        # Start TTS processing thread
        self.thread = threading.Thread(target=self._process_tts_queue)
        self.thread.daemon = True
        self.thread.start()
        
        # Start wake word detection thread
        if self.porcupine and self.recorder:
            self.wake_word_thread = threading.Thread(target=self._wake_word_detection)
            self.wake_word_thread.daemon = True
            self.wake_word_thread.start()
        
        logger.info("Voice System started")
    
    def stop(self):
        """Stop voice system"""
        self.running = False
        
        # Stop threads
        if self.thread:
            self.thread.join(timeout=2.0)
        
        if self.wake_word_thread:
            self.wake_word_thread.join(timeout=2.0)
        
        # Cleanup resources
        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None
        
        if self.recorder:
            self.recorder.delete()
            self.recorder = None
        
        logger.info("Voice System stopped")
    
    def _init_wake_word(self):
        """Initialize wake word detection engine"""
        try:
            # Initialize Porcupine with "Hey Revvy" wake word
            self.porcupine = pvporcupine.create(
                keywords=["hey google"],  # Use "hey google" as proxy for "hey revvy"
                sensitivities=[self.wake_word_sensitivity]
            )
            
            # Initialize recorder
            self.recorder = PvRecorder(
                device_index=self.mic_index,
                frame_length=self.porcupine.frame_length
            )
            
            logger.info("Wake word detection initialized")
            
        except Exception as e:
            logger.error(f"Error initializing wake word detection: {e}")
            self.porcupine = None
            self.recorder = None
    
    def _init_tts(self):
        """Initialize text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Set properties
            self.tts_engine.setProperty('rate', 175)  # Speed of speech
            self.tts_engine.setProperty('volume', self.volume / 100)  # Volume (0 to 1)
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            
            # Set default voice
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)
            
            logger.info("TTS engine initialized")
            
        except Exception as e:
            logger.error(f"Error initializing TTS engine: {e}")
            self.tts_engine = None
    
    def _wake_word_detection(self):
        """Wake word detection loop"""
        if not self.porcupine or not self.recorder:
            logger.error("Wake word detection not initialized")
            return
        
        try:
            self.recorder.start()
            logger.info("Wake word detection started")
            
            while self.running:
                pcm = self.recorder.read()
                
                # Process audio frame
                result = self.porcupine.process(pcm)
                
                # Wake word detected
                if result >= 0:
                    logger.info("Wake word detected!")
                    
                    # Temporarily pause wake word detection
                    self.recorder.stop()
                    
                    # Handle the voice command
                    self._handle_voice_command()
                    
                    # Resume wake word detection
                    self.recorder.start()
            
            self.recorder.stop()
            
        except Exception as e:
            logger.error(f"Error in wake word detection: {e}")
            
            # Try to restart
            if self.running:
                logger.info("Attempting to restart wake word detection")
                if self.recorder:
                    try:
                        self.recorder.stop()
                    except:
                        pass
                
                time.sleep(1)
                self._wake_word_detection()
    
    def _handle_voice_command(self):
        """Handle voice command after wake word detection"""
        try:
            # Speak activation confirmation
            self.speak("Yes?", interrupt=True)
            
            # Record audio for command
            command = self._recognize_speech()
            
            if command:
                logger.info(f"Recognized command: {command}")
                
                # Process command with AI
                self.ai_engine.query(command, callback=self._handle_ai_response)
            else:
                logger.info("No speech recognized")
                self.speak("I didn't catch that.")
                
        except Exception as e:
            logger.error(f"Error handling voice command: {e}")
            self.speak("Sorry, I encountered an error.")
    
    def _recognize_speech(self):
        """Record and recognize speech"""
        try:
            with sr.Microphone(device_index=self.mic_index) as source:
                logger.info("Listening for command...")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for speech
                audio = self.recognizer.listen(source, timeout=5.0, phrase_time_limit=10.0)
                
                logger.info("Processing speech...")
                
                # Recognize speech using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                return text
                
        except sr.WaitTimeoutError:
            logger.info("Timeout waiting for speech")
            return None
            
        except sr.UnknownValueError:
            logger.info("Speech not understood")
            return None
            
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Error recognizing speech: {e}")
            return None
    
    def _handle_ai_response(self, query_id, response_text):
        """Handle AI response to voice command"""
        if response_text:
            # Speak the response
            self.speak(response_text)
    
    def _process_tts_queue(self):
        """Process text-to-speech queue"""
        while self.running:
            try:
                # Get next text to speak
                try:
                    text, interrupt = self.tts_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                # Speak the text
                if self.tts_engine:
                    # Check cache for pre-generated audio
                    cache_key = f"{self.current_voice}:{text}"
                    
                    if cache_key in self.audio_cache:
                        # Play from cache
                        audio_data = self.audio_cache[cache_key]
                        sd.play(audio_data, 22050)
                        sd.wait()
                    else:
                        # Generate and speak
                        self.tts_engine.say(text)
                        self.tts_engine.runAndWait()
                    
                self.tts_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing TTS: {e}")
    
    def speak(self, text, interrupt=False):
        """Speak text using TTS"""
        if not self.voice_enabled:
            logger.debug(f"Voice disabled, not speaking: {text}")
            return
        
        try:
            # Add to TTS queue
            self.tts_queue.put((text, interrupt))
            
        except Exception as e:
            logger.error(f"Error queuing TTS: {e}")
    
    def set_voice(self, voice_name):
        """Set the voice based on personality"""
        if not self.tts_engine:
            return False
        
        try:
            voices = self.tts_engine.getProperty('voices')
            
            # Map personality to voice index
            voice_map = {
                "Revvy OG": 0,       # Default voice
                "Turbo Revvy": 1,     # More enthusiastic voice
                "Kiko": 2,           # Higher pitched voice
                "Mechanix": 3,       # Technical sounding voice
                "Sage": 4,           # Calm voice
                "Shinji Revvy": 5,   # Japanese accent
                "Kaizen Revvy": 6,   # Dramatic voice
                "Revvy Toretto": 7,  # Deep voice
                "Gizmo Gremlin": 8,  # Mischievous voice
                "Safety Revvy": 9    # Authoritative voice
            }
            
            # If we don't have enough voices, use default
            voice_index = voice_map.get(voice_name, 0)
            
            # Make sure we don't go out of bounds
            if voice_index >= len(voices):
                voice_index = 0
            
            # Set the voice
            self.tts_engine.setProperty('voice', voices[voice_index].id)
            self.current_voice = voice_name
            
            logger.info(f"Voice set to {voice_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False
    
    def set_volume(self, volume):
        """Set TTS volume"""
        if not self.tts_engine:
            return False
        
        try:
            # Ensure volume is between 0 and 100
            volume = max(0, min(100, volume))
            
            # Set volume (0 to 1)
            self.tts_engine.setProperty('volume', volume / 100)
            self.volume = volume
            
            logger.info(f"Volume set to {volume}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return False
    
    def enable_voice(self, enabled):
        """Enable or disable voice"""
        self.voice_enabled = enabled
        self.config.set("voice", "enable_voice", enabled)
        
        logger.info(f"Voice {'enabled' if enabled else 'disabled'}")
        return True