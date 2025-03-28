import React, { useState, useEffect } from 'react';
import API from '../services/API';
import '../styles/UnitToggle.css';

const UnitToggle = ({ onUnitSystemChange }) => {
  const [unitSystem, setUnitSystem] = useState('metric');
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // Get current unit settings on mount
    const fetchUnitSettings = async () => {
      try {
        const settings = await API.getUnitSettings();
        setUnitSystem(settings.unit_system);
      } catch (error) {
        console.error('Error fetching unit settings:', error);
      }
    };
    
    fetchUnitSettings();
    
    // Listen for unit system changes
    API.onMessage('unit_system_changed', (data) => {
      setUnitSystem(data.unit_system);
      if (onUnitSystemChange) {
        onUnitSystemChange(data.unit_system);
      }
    });
    
    return () => {
      API.offMessage('unit_system_changed');
    };
  }, [onUnitSystemChange]);
  
  const handleToggle = async () => {
    if (loading) return;
    
    setLoading(true);
    
    try {
      // Toggle between metric and imperial
      const newSystem = unitSystem === 'metric' ? 'imperial' : 'metric';
      
      const result = await API.toggleUnitSystem(newSystem);
      
      if (result.success) {
        setUnitSystem(result.unit_system);
        if (onUnitSystemChange) {
          onUnitSystemChange(result.unit_system);
        }
      }
    } catch (error) {
      console.error('Error toggling unit system:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="unit-toggle">
      <button 
        className={`unit-toggle-button ${loading ? 'loading' : ''}`} 
        onClick={handleToggle}
        disabled={loading}
      >
        {loading ? 'Changing...' : unitSystem === 'metric' ? 'Metric (km/h, °C)' : 'Imperial (mph, °F)'}
      </button>
      
      <div className="unit-indicator">
        <div className={`unit-badge ${unitSystem === 'metric' ? 'active' : ''}`}>
          Metric
        </div>
        <div className={`unit-badge ${unitSystem === 'imperial' ? 'active' : ''}`}>
          Imperial
        </div>
      </div>
    </div>
  );
};

export default UnitToggle;