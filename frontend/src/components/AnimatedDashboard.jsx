import React, { useState, useEffect, useRef } from 'react';
import '../styles/AnimatedDashboard.css';

const AnimatedDashboard = ({ currentMode, vehicleData, personality }) => {
  const [animationLoaded, setAnimationLoaded] = useState(false);
  const [usesFallback, setUsesFallback] = useState(false);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  
  // Animation paths for each mode
  const animationPaths = {
    'Standard': '/animations/standard.json',
    'Performance': '/animations/performance.json',
    'Kiko': '/animations/kiko.json',
    'Mechanic': '/animations/mechanic.json',
    'Zen': '/animations/zen.json',
    'JDM Street': '/animations/jdm.json',
    'Anime': '/animations/anime.json',
    'Toretto': '/animations/toretto.json',
    'Unhinged': '/animations/unhinged.json',
    'Mystery': '/animations/mystery.json',
    'Parent': '/animations/parent.json',
    'Voice Off': '/animations/voice-off.json'
  };
  
  // Initialize animation
  useEffect(() => {
    const loadAnimation = async () => {
      try {
        // Check if custom animation exists for this mode
        const animationPath = animationPaths[currentMode];
        
        // Try to load the animation
        const response = await fetch(animationPath);
        
        if (response.ok) {
          // Animation exists, load it
          const animationData = await response.json();
          
          // Use Lottie or other animation library to play the animation
          if (window.lottie && canvasRef.current) {
            if (animationRef.current) {
              animationRef.current.destroy();
            }
            
            animationRef.current = window.lottie.loadAnimation({
              container: canvasRef.current,
              renderer: 'canvas',
              loop: true,
              autoplay: true,
              animationData: animationData
            });
            
            setAnimationLoaded(true);
            setUsesFallback(false);
          }
        } else {
          // Animation doesn't exist, use fallback
          console.log(`Animation for ${currentMode} not found, using fallback face`);
          setUsesFallback(true);
          setAnimationLoaded(true);
        }
      } catch (error) {
        console.error('Error loading animation:', error);
        setUsesFallback(true);
        setAnimationLoaded(true);
      }
    };
    
    loadAnimation();
    
    // Cleanup animation on unmount
    return () => {
      if (animationRef.current) {
        animationRef.current.destroy();
        animationRef.current = null;
      }
    };
  }, [currentMode]);
  
  // Update animation parameters based on vehicle data
  useEffect(() => {
    if (animationRef.current && vehicleData) {
      // Example: Update animation speed based on RPM
      const speedFactor = Math.min(2, Math.max(0.5, vehicleData.rpm / 3000));
      animationRef.current.setSpeed(speedFactor);
      
      // Other custom animation controls based on vehicle data could go here
    }
  }, [vehicleData]);
  
  // Render fallback face animation based on personality
  const renderFallbackFace = () => {
    const personalityMap = {
      "Revvy OG": "default",
      "Turbo Revvy": "excited",
      "Kiko": "cute",
      "Mechanix": "technical",
      "Sage": "zen",
      "Shinji Revvy": "jdm",
      "Kaizen Revvy": "anime",
      "Revvy Toretto": "serious",
      "Gizmo Gremlin": "mischievous",
      "Safety Revvy": "concerned",
      "Random": "random",
      "Silent": "minimal"
    };
    
    const faceType = personalityMap[personality] || "default";
    
    // Get RPM-based expression for some dynamic behavior
    const getRPMExpression = () => {
      const rpm = vehicleData?.rpm || 0;
      if (rpm > 6000) return "very-excited";
      if (rpm > 4000) return "excited";
      if (rpm > 2000) return "neutral";
      return "relaxed";
    };
    
    // Combine face type with expression
    const expression = getRPMExpression();
    
    return (
      <div className="fallback-face-container">
        <div className={`fallback-face ${faceType} ${expression}`}>
          <div className="face-background"></div>
          <div className="face-eyes">
            <div className="eye left"></div>
            <div className="eye right"></div>
          </div>
          <div className="face-mouth"></div>
          <div className="face-accessories"></div>
        </div>
      </div>
    );
  };
  
  return (
    <div className={`animated-dashboard mode-${currentMode.toLowerCase().replace(/\s+/g, '-')}`}>
      {!animationLoaded && (
        <div className="loading-animation">
          <div className="loading-spinner"></div>
          <p>Loading {currentMode} animations...</p>
        </div>
      )}
      
      {animationLoaded && !usesFallback && (
        <div ref={canvasRef} className="animation-container"></div>
      )}
      
      {animationLoaded && usesFallback && renderFallbackFace()}
    </div>
  );
};

export default AnimatedDashboard;