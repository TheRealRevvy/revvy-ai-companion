import React, { useState, useEffect } from 'react';
import API from '../services/API';
import '../styles/SystemStatusBar.css';

const SystemStatusBar = () => {
  const [status, setStatus] = useState({
    obd: false,
    gps: false,
    voice: true,
    ai: true,
    serverConnection: false
  });
  
  const [expanded, setExpanded] = useState(false);
  const [retrying, setRetrying] = useState(false);
  
  useEffect(() => {
    // Initial fetch
    fetchSystemStatus();
    
    // Set up periodic status check
    const interval = setInterval(fetchSystemStatus, 10000);
    
    return () => clearInterval(interval);
  }, []);
  
  const fetchSystemStatus = async () => {
    try {
      const systemStatus = await API.getSystemStatus();
      
      setStatus({
        obd: systemStatus.obd_connected,
        gps: systemStatus.gps_active,
        voice: systemStatus.voice_enabled,
        ai: systemStatus.ai_available,
        serverConnection: true
      });
    } catch (error) {
      console.error('Error fetching system status:', error);
      setStatus(prev => ({
        ...prev,
        serverConnection: false
      }));
    }
  };
  
  const handleRetry = async () => {
    setRetrying(true);
    
    try {
      await API.reconnectComponents();
      await fetchSystemStatus();
    } catch (error) {
      console.error('Error reconnecting components:', error);
    }
    
    setRetrying(false);
  };
  
  const toggleExpanded = () => {
    setExpanded(!expanded);
  };
  
  return (
    <div className={`system-status-bar ${expanded ? 'expanded' : ''}`}>
      <div className="status-bar-content" onClick={toggleExpanded}>
        <div className="status-indicators">
          <div className={`status-indicator ${status.serverConnection ? 'active' : 'error'}`} title="Server Connection">
            <i className="icon-server"></i>
          </div>
          <div className={`status-indicator ${status.obd ? 'active' : 'warning'}`} title="OBD Connection">
            <i className="icon-car"></i>
          </div>
          <div className={`status-indicator ${status.gps ? 'active' : 'warning'}`} title="GPS Signal">
            <i className="icon-location"></i>
          </div>
          <div className={`status-indicator ${status.voice ? 'active' : 'warning'}`} title="Voice System">
            <i className="icon-microphone"></i>
          </div>
          <div className={`status-indicator ${status.ai ? 'active' : 'warning'}`} title="AI System">
            <i className="icon-brain"></i>
          </div>
        </div>
        
        <div className="status-summary">
          {!status.serverConnection && <span className="status-error">Server connection lost</span>}
          {status.serverConnection && !status.obd && <span className="status-warning">OBD not connected</span>}
          {status.serverConnection && !status.gps && <span className="status-warning">GPS not available</span>}
        </div>
      </div>
      
      {expanded && (
        <div className="status-details">
          <h3>System Status</h3>
          
          <div className="status-detail-item">
            <span className="status-label">Server Connection:</span>
            <span className={`status-value ${status.serverConnection ? 'ok' : 'error'}`}>
              {status.serverConnection ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          
          <div className="status-detail-item">
            <span className="status-label">OBD Connection:</span>
            <span className={`status-value ${status.obd ? 'ok' : 'warning'}`}>
              {status.obd ? 'Connected' : 'Not Connected'}
            </span>
            {!status.obd && <span className="status-note">Vehicle data unavailable</span>}
          </div>
          
          <div className="status-detail-item">
            <span className="status-label">GPS Signal:</span>
            <span className={`status-value ${status.gps ? 'ok' : 'warning'}`}>
              {status.gps ? 'Available' : 'Not Available'}
            </span>
            {!status.gps && <span className="status-note">Location features limited</span>}
          </div>
          
          <div className="status-detail-item">
            <span className="status-label">Voice System:</span>
            <span className={`status-value ${status.voice ? 'ok' : 'warning'}`}>
              {status.voice ? 'Enabled' : 'Disabled'}
            </span>
          </div>
          
          <div className="status-detail-item">
            <span className="status-label">AI System:</span>
            <span className={`status-value ${status.ai ? 'ok' : 'warning'}`}>
              {status.ai ? 'Available' : 'Limited Mode'}
            </span>
            {!status.ai && <span className="status-note">Using basic responses</span>}
          </div>
          
          <div className="status-actions">
            <button 
              className={`retry-button ${retrying ? 'retrying' : ''}`} 
              onClick={handleRetry}
              disabled={retrying}
            >
              {retrying ? 'Reconnecting...' : 'Retry Connections'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemStatusBar;