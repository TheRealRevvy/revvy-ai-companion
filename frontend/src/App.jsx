import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Settings from './components/Settings';
import VehicleData from './components/VehicleData';
import Diagnostics from './components/Diagnostics';
import ModeSelector from './components/ModeSelector';
import RevvyInterface from './components/RevvyInterface';
import AnimatedDashboard from './components/AnimatedDashboard';
import API from './services/API';
import './styles/App.css';

function App() {
  const [vehicleData, setVehicleData] = useState({
    rpm: 0,
    speed: 0,
    coolant_temp: 0,
    throttle_pos: 0,
    fuel_level: 100,
    battery_voltage: 12.5,
    boost_pressure: 0,
    oil_temp: 0,
    dtc_codes: [],
    is_check_engine_on: false,
    has_turbo: false
  });
  
  const [connected, setConnected] = useState(false);
  const [currentMode, setCurrentMode] = useState('Standard');
  const [personality, setPersonality] = useState('Revvy OG');
  const [notifications, setNotifications] = useState([]);
  const [achievements, setAchievements] = useState({});
  const [kioskMode, setKioskMode] = useState(true);
  const [unitSystem, setUnitSystem] = useState('metric');
  
  // Connect to Revvy backend
  useEffect(() => {
    const connectToBackend = async () => {
      try {
        await API.connect();
        setConnected(true);
        console.log('Connected to Revvy backend');
        
        // Get initial data
        const data = await API.getVehicleData();
        setVehicleData(data);
        
        const mode = await API.getCurrentMode();
        setCurrentMode(mode.mode);
        setPersonality(mode.personality);
        
        const achievementData = await API.getAchievements();
        setAchievements(achievementData);
        
        // Get initial unit settings
        const settings = await API.getUnitSettings();
        setUnitSystem(settings.unit_system);
        
      } catch (error) {
        console.error('Failed to connect to Revvy backend:', error);
      }
    };
    
    connectToBackend();
    
    // Set up interval to refresh data
    const dataInterval = setInterval(async () => {
      if (connected) {
        try {
          const data = await API.getVehicleData();
          setVehicleData(data);
        } catch (error) {
          console.error('Error fetching vehicle data:', error);
        }
      }
    }, 1000);
    
    // Set up event listeners
    API.onMessage('mode_changed', (data) => {
      setCurrentMode(data.mode);
      setPersonality(data.personality);
    });
    
    API.onMessage('notification', (data) => {
      addNotification(data);
    });
    
    API.onMessage('achievement_unlocked', (data) => {
      addNotification({
        type: 'achievement',
        title: 'Achievement Unlocked!',
        message: data.name,
        description: data.description
      });
      
      // Update achievements
      setAchievements(prev => {
        const newAchievements = {...prev};
        if (newAchievements[data.category]) {
          const achIndex = newAchievements[data.category].findIndex(a => a.id === data.id);
          if (achIndex >= 0) {
            newAchievements[data.category][achIndex].completed = true;
          }
        }
        return newAchievements;
      });
    });
    
    // Listen for unit system changes
    API.onMessage('unit_system_changed', (data) => {
      setUnitSystem(data.unit_system);
    });
    
    // Set up keyboard traps for kiosk mode
    if (kioskMode) {
      const handleKeyDown = (e) => {
        // Block browser navigation keys and alt+F4
        const blockedKeys = [
          27, // Escape
          112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, // F1-F12
          9 // Tab
        ];
        
        if (
          blockedKeys.includes(e.keyCode) || 
          (e.altKey && e.keyCode === 115) || // Alt+F4
          (e.ctrlKey && (e.keyCode === 78 || e.keyCode === 84)) // Ctrl+N, Ctrl+T
        ) {
          e.preventDefault();
          return false;
        }
      };
      
      window.addEventListener('keydown', handleKeyDown);
      
      return () => {
        window.removeEventListener('keydown', handleKeyDown);
        clearInterval(dataInterval);
        API.disconnect();
      };
    }
    
    return () => {
      clearInterval(dataInterval);
      API.disconnect();
      API.offMessage('unit_system_changed');
    };
  }, [connected, kioskMode]);
  
  // Add a notification
  const addNotification = (notification) => {
    const newNotification = {
      id: Date.now(),
      ...notification,
      timestamp: new Date()
    };
    
    setNotifications(prev => [newNotification, ...prev].slice(0, 10));
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== newNotification.id));
    }, 5000);
  };
  
  // Change dashboard mode
  const changeMode = async (mode) => {
    try {
      const result = await API.changeMode(mode);
      if (result.success) {
        setCurrentMode(result.mode);
        setPersonality(result.personality);
      }
    } catch (error) {
      console.error('Error changing mode:', error);
    }
  };
  
  // Handle unit system change
  const handleUnitSystemChange = (newUnitSystem) => {
    setUnitSystem(newUnitSystem);
  };
  
  return (
    <Router>
      <div className={`app-container mode-${currentMode.toLowerCase().replace(/\s+/g, '-')}`}>
        {/* Animated dashboard background */}
        <AnimatedDashboard 
          currentMode={currentMode} 
          vehicleData={vehicleData}
          personality={personality}
        />
        
        <Routes>
          <Route path="/" element={
            <Dashboard 
              vehicleData={vehicleData}
              currentMode={currentMode}
              personality={personality}
              notifications={notifications}
              unitSystem={unitSystem}
            />
          } />
          <Route path="/settings" element={
            <Settings 
              unitSystem={unitSystem}
              onUnitSystemChange={handleUnitSystemChange}
            />
          } />
          <Route path="/vehicle" element={
            <VehicleData 
              data={vehicleData}
              unitSystem={unitSystem}
            />
          } />
          <Route path="/diagnostics" element={
            <Diagnostics 
              dtcCodes={vehicleData.dtc_codes}
              unitSystem={unitSystem}
            />
          } />
          <Route path="/modes" element={
            <ModeSelector 
              currentMode={currentMode} 
              onChangeMode={changeMode}
            />
          } />
        </Routes>
        
        <RevvyInterface 
          personality={personality}
          currentMode={currentMode}
          connected={connected}
          unitSystem={unitSystem}
        />
      </div>
    </Router>
  );
}

export default App;