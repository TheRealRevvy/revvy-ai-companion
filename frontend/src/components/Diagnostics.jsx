import React, { useState, useEffect } from 'react';
import API from '../services/API';
import '../styles/Diagnostics.css';

const Diagnostics = ({ dtcCodes }) => {
  const [dtcExplanations, setDtcExplanations] = useState({});
  const [loading, setLoading] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [confirmClear, setConfirmClear] = useState(false);

  // Load explanations when DTC codes change
  useEffect(() => {
    const loadExplanations = async () => {
      if (dtcCodes && dtcCodes.length > 0) {
        setLoading(true);
        
        const explanations = {};
        for (const code of dtcCodes) {
          if (!dtcExplanations[code]) {
            try {
              const response = await API.getDTCExplanation(code);
              explanations[code] = response;
            } catch (error) {
              explanations[code] = {
                description: 'Error getting explanation',
                severity: 'Unknown',
                possibleCauses: ['Unknown'],
                possibleFixes: ['Check vehicle service manual']
              };
            }
          }
        }
        
        setDtcExplanations(prev => ({ ...prev, ...explanations }));
        setLoading(false);
      }
    };
    
    loadExplanations();
  }, [dtcCodes]);

  // Handle clearing DTC codes
  const handleClearDTC = async () => {
    if (!confirmClear) {
      setConfirmClear(true);
      return;
    }
    
    setClearing(true);
    try {
      const result = await API.clearDTCCodes();
      if (result.success) {
        alert('DTC codes have been cleared successfully.');
      } else {
        alert('Failed to clear DTC codes: ' + result.error);
      }
    } catch (error) {
      alert('Error clearing DTC codes: ' + error.message);
    }
    setClearing(false);
    setConfirmClear(false);
  };

  // Get severity color
  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'severity-critical';
      case 'high':
        return 'severity-high';
      case 'medium':
        return 'severity-medium';
      case 'low':
        return 'severity-low';
      default:
        return 'severity-unknown';
    }
  };

  return (
    <div className="diagnostics-container">
      <div className="diagnostics-header">
        <h1>Vehicle Diagnostics</h1>
        {dtcCodes && dtcCodes.length > 0 && (
          <button 
            className={`clear-button ${confirmClear ? 'confirm' : ''}`}
            onClick={handleClearDTC}
            disabled={clearing}
          >
            {clearing ? 'Clearing...' : confirmClear ? 'Confirm Clear' : 'Clear Codes'}
          </button>
        )}
      </div>
      
      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Analyzing DTC Codes...</p>
        </div>
      ) : dtcCodes && dtcCodes.length > 0 ? (
        <div className="dtc-list">
          {dtcCodes.map(code => (
            <div key={code} className="dtc-card">
              <div className="dtc-header">
                <h2 className="dtc-code">{code}</h2>
                {dtcExplanations[code] && (
                  <span className={`severity-badge ${getSeverityColor(dtcExplanations[code].severity)}`}>
                    {dtcExplanations[code].severity}
                  </span>
                )}
              </div>
              
              {dtcExplanations[code] ? (
                <>
                  <p className="dtc-description">{dtcExplanations[code].description}</p>
                  
                  <h3>Possible Causes</h3>
                  <ul className="dtc-causes">
                    {dtcExplanations[code].possibleCauses.map((cause, index) => (
                      <li key={index}>{cause}</li>
                    ))}
                  </ul>
                  
                  <h3>Recommended Fixes</h3>
                  <ul className="dtc-fixes">
                    {dtcExplanations[code].possibleFixes.map((fix, index) => (
                      <li key={index}>{fix}</li>
                    ))}
                  </ul>
                </>
              ) : (
                <p className="dtc-loading">Loading code information...</p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="no-dtc">
          <div className="check-engine-icon">✓</div>
          <h2>No fault codes detected</h2>
          <p>Your vehicle is not reporting any diagnostic trouble codes.</p>
        </div>
      )}
    </div>
  );
};

export default Diagnostics;