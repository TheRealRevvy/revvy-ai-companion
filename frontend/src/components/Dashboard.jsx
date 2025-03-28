import React, { useState, useEffect } from 'react';
import GaugeCluster from './GaugeCluster';
import Notifications from './Notifications';
import VehicleStatus from './VehicleStatus';
import ModeIndicator from './ModeIndicator';
import SystemStatusBar from './SystemStatusBar';
import QuickUnitToggle from './QuickUnitToggle';
import API from '../services/API';
import '../styles/Dashboard.css';

const Dashboard = ({ vehicleData, currentMode, personality, notifications, unitSystem }) => {
  const [animationPlaying, setAnimationPlaying] = useState(false);
  const [redlineAnimation, setRedlineAnimation] = useState(false);
  const [unitToggleLoading, setUnitToggleLoading] = useState(false);
  
  // Check for redline animation
  useEffect(() => {
    // For Performance mode, trigger redline animation when RPM nears redline
    if (currentMode === 'Performance' && vehicleData && vehicleData.rpm > 6500) {
      if (!redlineAnimation) {
        setRedlineAnimation(true);
        // Reset after animation duration
        setTimeout(() => setRedlineAnimation(false), 3000);
      }
    }
  }, [vehicleData, currentMode, redlineAnimation]);
  
  // Handle missing vehicle data
  const safeVehicleData = vehicleData || {
    rpm: 0,
    speed: 0,
    coolant_temp: 0,
    throttle_pos: 0,
    fuel_level: 0,
    battery_voltage: 12.0,
    boost_pressure: 0,
    oil_temp: 0,
    dtc_codes: []
  };
  
  // Format speed with units
  const formatSpeed = (speed) => {
    if (speed === undefined || speed === null) {
      return unitSystem === 'metric' ? '-- km/h' : '-- mph';
    }
    
    return `${Math.round(speed)} ${unitSystem === 'metric' ? 'km/h' : 'mph'}`;
  };
  
  // Format RPM with padding and handle missing data
  const formatRPM = (rpm) => {
    if (rpm === undefined || rpm === null) return "--";
    return Math.round(rpm).toLocaleString();
  };
  
  // Format temperature with units
  const formatTemperature = (temp) => {
    if (temp === undefined || temp === null) {
      return unitSystem === 'metric' ? '--°C' : '--°F';
    }
    
    return `${Math.round(temp)}°${unitSystem === 'metric' ? 'C' : 'F'}`;
  };
  
  // Get theme class based on current mode
  const getThemeClass = () => {
    return `dashboard-${currentMode.toLowerCase().replace(/\s+/g, '-')}`;
  };
  
  // Get background for current mode
  const getDashboardBackground = () => {
    switch (currentMode) {
      case 'Performance':
        return redlineAnimation ? 'dashboard-bg-redline' : 'dashboard-bg-performance';
      case 'Kiko':
        return 'dashboard-bg-kiko';
      case 'Mechanic':
        return 'dashboard-bg-blueprint';
      case 'Zen':
        return 'dashboard-bg-zen';
      case 'JDM Street':
        return 'dashboard-bg-jdm';
      case 'Anime':
        return 'dashboard-bg-anime';
      case 'Toretto':
        return 'dashboard-bg-toretto';
      case 'Unhinged':
        return 'dashboard-bg-unhinged';
      case 'Parent':
        return 'dashboard-bg-parent';
      default:
        return 'dashboard-bg-standard';
    }
  };
  
  // Handle unit toggle
  const handleToggleUnits = async () => {
    if (unitToggleLoading) return;
    
    setUnitToggleLoading(true);
    
    try {
      const newSystem = unitSystem === 'metric' ? 'imperial' : 'metric';
      await API.toggleUnitSystem(newSystem);
    } catch (error) {
      console.error('Error toggling unit system:', error);
    } finally {
      setUnitToggleLoading(false);
    }
  };
  
  return (
    <div className={`dashboard-container ${getThemeClass()} ${getDashboardBackground()}`}>
      <SystemStatusBar />
      
      <div className="dashboard-header">
        <ModeIndicator mode={currentMode} personality={personality} />
      </div>
      
      <div className="dashboard-main">
        <div className="speed-display">
          <h2>SPEED</h2>
          <div className="speed-value">{formatSpeed(safeVehicleData.speed)}</div>
        </div>
        
        <div className="rpm-display">
          <h2>RPM</h2>
          <div className="rpm-value">{formatRPM(safeVehicleData.rpm)}</div>
        </div>
        
        <GaugeCluster 
          data={safeVehicleData}
          mode={currentMode}
          redlineAnimation={redlineAnimation}
          unitSystem={unitSystem}
        />
      </div>
      
      <div className="dashboard-footer">
        <VehicleStatus 
          data={safeVehicleData} 
          unitSystem={unitSystem}
        />
        <Notifications notifications={notifications} />
      </div>
      
      {/* Add quick unit toggle */}
      <QuickUnitToggle 
        unitSystem={unitSystem}
        onToggle={handleToggleUnits}
        loading={unitToggleLoading}
      />
    </div>
  );
};

export default Dashboard;