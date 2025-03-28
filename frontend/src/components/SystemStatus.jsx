import React, { useState, useEffect } from 'react';
import API from '../services/API';
import '../styles/SystemStatus.css';

const SystemStatus = () => {
  const [systemStatus, setSystemStatus] = useState({
    status: 'unknown',
    obd_connected: false,
    voice_enabled: true,
    current_mode: 'Unknown',
    current_personality: 'Unknown',
    system_ready: false,
    timestamp: '',
    cpu_usage: 0,
    memory_usage: 0,
    temperature: 0,
    storage_free: 0,
    uptime: 0
  });
  
  const [expanded, setExpanded] = useState(false);
  
  useEffect(() => {
    // Get initial status
    fetchSystemStatus();
    
    // Poll for updates
    const interval = setInterval(fetchSystemStatus, 10000);
    
    return () => clearInterval(interval);
  }, []);
  
  const fetchSystemStatus = async () => {
    try {
      const status = await API.getStatus();
      
      // Add additional system metrics
      const metrics = await API.getSystemMetrics();
      
      setSystemStatus({
        ...status,
        ...metrics
      });
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };
  
  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / (3600 * 24));
    const hours = Math.floor((seconds % (3600 * 24)) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    let result = '';
    if (days > 0) result += `${days}d `;
    if (hours > 0) result += `${hours}h `;
    result += `${minutes}m`;
    
    return result;
  };
  
  const toggleExpanded = () => {
    setExpanded(!expanded);
  };
  
  const getStatusIndicatorClass = () => {
    if (systemStatus.status === 'online' && systemStatus.system_ready) {
      return 'status-indicator status-good';
    } else if (systemStatus.status === 'online' && !systemStatus.system_ready) {
      return 'status-indicator status-warning';
    } else {
      return 'status-indicator status-error';
    }
  };
  
  return (
    <div className={`system-status ${expanded ? 'expanded' : ''}`}>
      <div className="status-header" onClick={toggleExpanded}>
        <div className={getStatusIndicatorClass()}></div>
        <h3>System Status {expanded ? '▼' : '▶'}</h3>
      </div>
      
      {expanded && (
        <div className="status-details">
          <div className="status-group">
            <div className="status-item">
              <span className="status-label">OBD Connection:</span>
              <span className={`status-value ${systemStatus.obd_connected ? 'status-good' : 'status-error'}`}>
                {systemStatus.obd_connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            
            <div className="status-item">
              <span className="status-label">Voice System:</span>
              <span className={`status-value ${systemStatus.voice_enabled ? 'status-good' : 'status-warning'}`}>
                {systemStatus.voice_enabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>
            
            <div className="status-item">
              <span className="status-label">Current Mode:</span>
              <span className="status-value">{systemStatus.current_mode}</span>
            </div>
            
            <div className="status-item">
              <span className="status-label">Personality:</span>
              <span className="status-value">{systemStatus.current_personality}</span>
            </div>
          </div>
          
          <div className