import React from 'react';
import UnitToggle from './UnitToggle';
import '../styles/Settings.css';

const Settings = ({ unitSystem, onUnitSystemChange }) => {
  return (
    <div className="settings-container">
      <h1>Settings</h1>
      
      <div className="settings-section">
        <h2>Display</h2>
        
        <div className="setting-item">
          <div className="setting-label">
            <span>Unit System</span>
            <p className="setting-description">
              Choose between metric (km/h, °C) and imperial (mph, °F) units
            </p>
          </div>
          
          <div className="setting-control">
            <UnitToggle 
              onUnitSystemChange={onUnitSystemChange} 
            />
          </div>
        </div>
        
        {/* Other settings can be added here */}
      </div>
      
      <div className="settings-section">
        <h2>Voice Settings</h2>
        
        {/* Voice settings can be added here */}
      </div>
      
      <div className="settings-section">
        <h2>System Information</h2>
        <div className="setting-info">
          <p>Revvy AI Companion</p>
          <p>Version 1.0.0</p>
          <p>© 2025 TheRealRevvy. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default Settings;