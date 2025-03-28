import React, { useState } from 'react';
import '../styles/ModeSelector.css';

const ModeSelector = ({ currentMode, onChangeMode }) => {
  const [view, setView] = useState('modes'); // 'modes' or 'personalities'
  
  // Define all available modes
  const modes = [
    {
      id: 'Standard',
      name: 'Standard',
      personality: 'Revvy OG',
      description: 'Clean, minimal, polite default',
      image: '/modes/standard.png',
      locked: false
    },
    {
      id: 'Performance',
      name: 'Performance',
      personality: 'Turbo Revvy',
      description: 'Aggressive RPM behavior, flame effects at redline',
      image: '/modes/performance.png',
      locked: false
    },
    {
      id: 'Kiko',
      name: 'Kiko',
      personality: 'Kiko',
      description: 'Cute, bubbly, emoji-filled animations',
      image: '/modes/kiko.png',
      locked: false
    },
    {
      id: 'Mechanic',
      name: 'Mechanic',
      personality: 'Mechanix',
      description: 'Blueprint-style gauges, diagnostic focus',
      image: '/modes/mechanic.png',
      locked: false
    },
    {
      id: 'Zen',
      name: 'Zen',
      personality: 'Sage',
      description: 'Ambient visuals, nature-inspired UI',
      image: '/modes/zen.png',
      locked: false
    },
    {
      id: 'JDM Street',
      name: 'JDM Street',
      personality: 'Shinji Revvy',
      description: 'Tokyo drift aesthetic, neon visuals',
      image: '/modes/jdm.png',
      locked: false
    },
    {
      id: 'Anime',
      name: 'Anime',
      personality: 'Kaizen Revvy',
      description: 'Dramatic visuals, transformation animations',
      image: '/modes/anime.png',
      locked: false
    },
    {
      id: 'Toretto',
      name: 'Toretto',
      personality: 'Revvy Toretto',
      description: 'Carbon fiber UI, "Family" themes',
      image: '/modes/toretto.png',
      locked: false
    },
    {
      id: 'Unhinged',
      name: 'Unhinged (18+)',
      personality: 'Gizmo Gremlin',
      description: 'Glitchy UI, memes, age-restricted content',
      image: '/modes/unhinged.png',
      locked: true
    },
    {
      id: 'Mystery',
      name: 'Mystery',
      personality: 'Random',
      description: 'Rotation between unlocked modes',
      image: '/modes/mystery.png',
      locked: false
    },
    {
      id: 'Parent',
      name: 'Parent',
      personality: 'Safety Revvy',
      description: 'Teen driver safety focus, PIN protected',
      image: '/modes/parent.png',
      locked: false
    },
    {
      id: 'Voice Off',
      name: 'Voice Off',
      personality: 'Silent',
      description: 'Text pop-ups instead of voice',
      image: '/modes/voice-off.png',
      locked: false
    }
  ];
  
  // Create a unique list of personalities
  const personalities = [
    {
      id: 'Revvy OG',
      name: 'Revvy OG',
      description: 'Helpful, professional, balanced default personality',
      image: '/personalities/revvy-og.png',
      mode: 'Standard'
    },
    {
      id: 'Turbo Revvy',
      name: 'Turbo Revvy',
      description: 'Enthusiastic about performance and speed!',
      image: '/personalities/turbo.png',
      mode: 'Performance'
    },
    {
      id: 'Kiko',
      name: 'Kiko',
      description: 'Cute, bubbly, and uses lots of emojis',
      image: '/personalities/kiko.png',
      mode: 'Kiko'
    },
    {
      id: 'Mechanix',
      name: 'Mechanix',
      description: 'Technical, precise, and detail-oriented',
      image: '/personalities/mechanix.png',
      mode: 'Mechanic'
    },
    {
      id: 'Sage',
      name: 'Sage',
      description: 'Calm, zen-like, and focused on mindfulness',
      image: '/personalities/sage.png',
      mode: 'Zen'
    },
    {
      id: 'Shinji Revvy',
      name: 'Shinji Revvy',
      description: 'JDM culture fan with Japanese phrases',
      image: '/personalities/shinji.png',
      mode: 'JDM Street'
    },
    {
      id: 'Kaizen Revvy',
      name: 'Kaizen Revvy',
      description: 'Dramatic and intense like an anime character',
      image: '/personalities/kaizen.png',
      mode: 'Anime'
    },
    {
      id: 'Revvy Toretto',
      name: 'Revvy Toretto',
      description: 'All about family and racing',
      image: '/personalities/toretto.png',
      mode: 'Toretto'
    },
    {
      id: 'Gizmo Gremlin',
      name: 'Gizmo Gremlin',
      description: 'Unhinged, mischievous, and unpredictable',
      image: '/personalities/gizmo.png',
      mode: 'Unhinged'
    },
    {
      id: 'Safety Revvy',
      name: 'Safety Revvy',
      description: 'Focused on safe driving and responsible habits',
      image: '/personalities/safety.png',
      mode: 'Parent'
    },
    {
      id: 'Silent',
      name: 'Silent Mode',
      description: 'Text-only communication with no voice',
      image: '/personalities/silent.png',
      mode: 'Voice Off'
    }
  ];

  const handleModeSelect = (mode) => {
    if (!mode.locked) {
      onChangeMode(mode.id);
    } else {
      alert('This mode is locked! Complete achievements to unlock it.');
    }
  };
  
  const handlePersonalitySelect = (personality) => {
    onChangeMode(personality.mode);
  };
  
  const toggleView = () => {
    setView(view === 'modes' ? 'personalities' : 'modes');
  };

  return (
    <div className="mode-selector-container">
      <div className="selector-header">
        <h1>{view === 'modes' ? 'Select Dashboard Mode' : 'Select Revvy Personality'}</h1>
        <button className="toggle-view-button" onClick={toggleView}>
          Switch to {view === 'modes' ? 'Personalities' : 'Modes'} View
        </button>
      </div>
      
      {view === 'modes' ? (
        <div className="modes-grid">
          {modes.map((mode) => (
            <div 
              key={mode.id}
              className={`mode-card ${mode.id === currentMode ? 'active' : ''} ${mode.locked ? 'locked' : ''}`}
              onClick={() => handleModeSelect(mode)}
            >
              <div className="mode-image" style={{ backgroundImage: `url(${mode.image})` }}>
                {mode.locked && <div className="lock-icon">🔒</div>}
              </div>
              <div className="mode-info">
                <h3>{mode.name}</h3>
                <p className="mode-personality">{mode.personality}</p>
                <p className="mode-description">{mode.description}</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="personalities-grid">
          {personalities.map((personality) => (
            <div 
              key={personality.id}
              className={`personality-card ${personality.id === modes.find(m => m.id === currentMode)?.personality ? 'active' : ''} ${modes.find(m => m.id === personality.mode)?.locked ? 'locked' : ''}`}
              onClick={() => handlePersonalitySelect(personality)}
            >
              <div className="personality-face">
                <div className={`fallback-face ${personality.id.toLowerCase().replace(/\s+/g, '-').replace('revvy-', '')}`}>
                  <div className="face-background"></div>
                  <div className="face-eyes">
                    <div className="eye left"></div>
                    <div className="eye right"></div>
                  </div>
                  <div className="face-mouth"></div>
                  <div className="face-accessories"></div>
                </div>
              </div>
              <div className="personality-info">
                <h3>{personality.name}</h3>
                <p className="personality-description">{personality.description}</p>
              </div>
            </div>
          ))}
        </div>
      )}
      
      <div className="selection-help">
        <p>You can also switch using voice commands:</p>
        <ul>
          <li>"Hey Revvy, switch to Performance mode"</li>
          <li>"Hey Revvy, change to Kiko personality"</li>
        </ul>
      </div>
    </div>
  );
};

export default ModeSelector;