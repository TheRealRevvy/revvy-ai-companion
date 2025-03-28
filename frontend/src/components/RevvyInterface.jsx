import React, { useState, useEffect, useRef } from 'react';
import '../styles/RevvyInterface.css';
import API from '../services/API';

const RevvyInterface = ({ personality, currentMode, connected }) => {
  const [message, setMessage] = useState('');
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [animation, setAnimation] = useState('idle');
  const characterRef = useRef(null);
  
  // Get character based on personality
  const getCharacterImage = () => {
    switch (personality) {
      case 'Turbo Revvy':
        return speaking ? '/characters/turbo_speaking.gif' : '/characters/turbo_idle.gif';
      case 'Kiko':
        return speaking ? '/characters/kiko_speaking.gif' : '/characters/kiko_idle.gif';
      case 'Mechanix':
        return speaking ? '/characters/mechanix_speaking.gif' : '/characters/mechanix_idle.gif';
      case 'Sage':
        return speaking ? '/characters/sage_speaking.gif' : '/characters/sage_idle.gif';
      case 'Shinji Revvy':
        return speaking ? '/characters/shinji_speaking.gif' : '/characters/shinji_idle.gif';
      case 'Kaizen Revvy':
        return speaking ? '/characters/kaizen_speaking.gif' : '/characters/kaizen_idle.gif';
      case 'Revvy Toretto':
        return speaking ? '/characters/toretto_speaking.gif' : '/characters/toretto_idle.gif';
      case 'Gizmo Gremlin':
        return speaking ? '/characters/gizmo_speaking.gif' : '/characters/gizmo_idle.gif';
      case 'Safety Revvy':
        return speaking ? '/characters/safety_speaking.gif' : '/characters/safety_idle.gif';
      default:
        return speaking ? '/characters/revvy_speaking.gif' : '/characters/revvy_idle.gif';
    }
  };
  
  // Simulate wake word detection
  const handleWakeWord = () => {
    if (!listening && connected) {
      setListening(true);
      setAnimation('listening');
      setMessage('I\'m listening...');
      
      // Simulate listening for 3 seconds then getting a response
      setTimeout(() => {
        setListening(false);
        setSpeaking(true);
        setAnimation('speaking');
        
        // Get a response from the AI
        API.sendVoiceCommand("What's my current speed?").then(response => {
          setMessage(response.text);
          
          // After speaking duration proportional to message length
          setTimeout(() => {
            setSpeaking(false);
            setAnimation('idle');
            
            // Clear message after a few seconds
            setTimeout(() => {
              setMessage('');
            }, 3000);
          }, Math.max(2000, response.text.length * 50));
        });
      }, 3000);
    }
  };
  
  // Play animations based on events
  useEffect(() => {
    if (characterRef.current) {
      // Add animation classes
      characterRef.current.className = `revvy-character ${animation} ${personality.toLowerCase().replace(/\s+/g, '-')}`;
    }
  }, [animation, personality]);
  
  return (
    <div className={`revvy-interface mode-${currentMode.toLowerCase()}`}>
      <div className="revvy-container">
        <div 
          ref={characterRef}
          className={`revvy-character ${animation} ${personality.toLowerCase().replace(/\s+/g, '-')}`}
          style={{ backgroundImage: `url(${getCharacterImage()})` }}
          onClick={handleWakeWord}
        ></div>
        
        {message && (
          <div className="speech-bubble">
            <p>{message}</p>
          </div>
        )}
        
        {listening && (
          <div className="listening-indicator">
            <div className="listening-wave"></div>
            <div className="listening-wave"></div>
            <div className="listening-wave"></div>
            <div className="listening-wave"></div>
          </div>
        )}
      </div>
      
      {currentMode === 'DJ Mode' && (
        <div className="dj-visualizer">
          <div className="equalizer-bar"></div>
          <div className="equalizer-bar"></div>
          <div className="equalizer-bar"></div>
          <div className="equalizer-bar"></div>
          <div className="equalizer-bar"></div>
          <div className="equalizer-bar"></div>
          <div className="equalizer-bar"></div>
        </div>
      )}
    </div>
  );
};

export default RevvyInterface;