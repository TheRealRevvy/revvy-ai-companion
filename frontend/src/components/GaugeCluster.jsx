import React from 'react';
import '../styles/GaugeCluster.css';

const GaugeCluster = ({ data, mode, redlineAnimation, unitSystem }) => {
  // Safety check for null/undefined data
  const safeData = data || {};
  
  // Calculate gauge values based on data with safety fallbacks
  const calculateRPMAngle = (rpm) => {
    if (rpm === undefined || rpm === null) return -90; // Default to min
    
    // Assuming 8000 RPM is max
    const maxRPM = 8000;
    const angle = (rpm / maxRPM) * 180 - 90; // -90 to 90 degrees
    return Math.min(Math.max(angle, -90), 90); // Clamp between -90 and 90
  };
  
  const calculateSpeedAngle = (speed) => {
    if (speed === undefined || speed === null) return -90; // Default to min
    
    // Adjust max speed based on unit system
    const maxSpeed = unitSystem === 'metric' ? 240 : 150; // km/h or mph
    const angle = (speed / maxSpeed) * 180 - 90; // -90 to 90 degrees
    return Math.min(Math.max(angle, -90), 90); // Clamp between -90 and 90
  };
  
  const calculateTempAngle = (temp) => {
    if (temp === undefined || temp === null) return -90; // Default to min
    
    // Adjust range based on unit system
    if (unitSystem === 'metric') {
      // 0C to 140C range
      const minTemp = 0;
      const maxTemp = 140;
      const angle = ((temp - minTemp) / (maxTemp - minTemp)) * 180 - 90;
      return Math.min(Math.max(angle, -90), 90);
    } else {
      // 32F to 284F range
      const minTemp = 32;
      const maxTemp = 284;
      const angle = ((temp - minTemp) / (maxTemp - minTemp)) * 180 - 90;
      return Math.min(Math.max(angle, -90), 90);
    }
  };
  
  const calculateFuelAngle = (level) => {
    if (level === undefined || level === null) return -90; // Default to min
    
    // 0% to 100% range
    const angle = (level / 100) * 180 - 90;
    return Math.min(Math.max(angle, -90), 90);
  };
  
  const calculateBoostAngle = (boost) => {
    if (boost === undefined || boost === null) return -90; // Default to min
    
    if (unitSystem === 'metric') {
      // -100 to 300 kPa range (vacuum to boost)
      const minBoost = -100;
      const maxBoost = 300;
      const angle = ((boost - minBoost) / (maxBoost - minBoost)) * 180 - 90;
      return Math.min(Math.max(angle, -90), 90);
    } else {
      // -15 to 45 PSI range (vacuum to boost)
      const minBoost = -15;
      const maxBoost = 45;
      const angle = ((boost - minBoost) / (maxBoost - minBoost)) * 180 - 90;
      return Math.min(Math.max(angle, -90), 90);
    }
  };
  
  // Get gauge theme based on current mode
  const getGaugeTheme = () => {
    switch (mode) {
      case 'Performance':
        return 'gauge-theme-performance';
      case 'Kiko':
        return 'gauge-theme-kiko';
      case 'Mechanic':
        return 'gauge-theme-mechanic';
      case 'Zen':
        return 'gauge-theme-zen';
      case 'JDM Street':
        return 'gauge-theme-jdm';
      case 'Anime':
        return 'gauge-theme-anime';
      case 'Toretto':
        return 'gauge-theme-toretto';
      case 'Unhinged':
        return 'gauge-theme-unhinged';
      case 'Parent':
        return 'gauge-theme-parent';
      default:
        return 'gauge-theme-standard';
    }
  };
  
  // Additional animations for performance mode
  const getRedlineClass = () => {
    return redlineAnimation ? 'redline-active' : '';
  };
  
  // Get unit label for gauges
  const getSpeedUnit = () => unitSystem === 'metric' ? 'km/h' : 'mph';
  const getTempUnit = () => unitSystem === 'metric' ? '°C' : '°F';
  const getPressureUnit = () => unitSystem === 'metric' ? 'kPa' : 'psi';
  
  // Get gauge marks based on unit system
  const getSpeedMarks = () => {
    if (unitSystem === 'metric') {
      return (
        <>
          <span>0</span>
          <span>60</span>
          <span>120</span>
          <span>180</span>
          <span>240</span>
        </>
      );
    } else {
      return (
        <>
          <span>0</span>
          <span>40</span>
          <span>80</span>
          <span>120</span>
          <span>150</span>
        </>
      );
    }
  };
  
  const getTempMarks = () => {
    if (unitSystem === 'metric') {
      return (
        <>
          <span>0°C</span>
          <span>50°C</span>
          <span>100°C</span>
          <span>140°C</span>
        </>
      );
    } else {
      return (
        <>
          <span>32°F</span>
          <span>122°F</span>
          <span>212°F</span>
          <span>284°F</span>
        </>
      );
    }
  };
  
  const getPressureMarks = () => {
    if (unitSystem === 'metric') {
      return (
        <>
          <span>-100</span>
          <span>0</span>
          <span>100</span>
          <span>200</span>
          <span>300</span>
        </>
      );
    } else {
      return (
        <>
          <span>-15</span>
          <span>0</span>
          <span>15</span>
          <span>30</span>
          <span>45</span>
        </>
      );
    }
  };
  
  return (
    <div className={`gauge-cluster ${getGaugeTheme()} ${getRedlineClass()}`}>
      {/* Custom gauge layout based on mode */}
      {mode === 'Performance' || mode === 'Standard' ? (
        <>
          <div className="gauge rpm-gauge">
            <div className="gauge-label">RPM</div>
            <div className="gauge-dial">
              <div 
                className="gauge-needle" 
                style={{ transform: `rotate(${calculateRPMAngle(safeData.rpm)}deg)` }}
              ></div>
              <div className="gauge-center"></div>
              <div className="gauge-marks">
                <span>0</span>
                <span>2</span>
                <span>4</span>
                <span>6</span>
                <span>8</span>
              </div>
            </div>
          </div>
          
          <div className="gauge boost-gauge">
            <div className="gauge-label">BOOST {getPressureUnit()}</div>
            <div className="gauge-dial">
              <div 
                className="gauge-needle" 
                style={{ transform: `rotate(${calculateBoostAngle(safeData.boost_pressure)}deg)` }}
              ></div>
              <div className="gauge-center"></div>
              <div className="gauge-marks">
                {getPressureMarks()}
              </div>
            </div>
          </div>
        </>
      ) : mode === 'Mechanic' ? (
        <>
          <div className="gauge temp-gauge">
            <div className="gauge-label">COOLANT {getTempUnit()}</div>
            <div className="gauge-dial blueprint">
              <div 
                className="gauge-needle" 
                style={{ transform: `rotate(${calculateTempAngle(safeData.coolant_temp)}deg)` }}
              ></div>
              <div className="gauge-center"></div>
              <div className="gauge-marks">
                {getTempMarks()}
              </div>
            </div>
          </div>
          
          <div className="gauge oil-gauge">
            <div className="gauge-label">OIL {getTempUnit()}</div>
            <div className="gauge-dial blueprint">
              <div 
                className="gauge-needle" 
                style={{ transform: `rotate(${calculateTempAngle(safeData.oil_temp)}deg)` }}
              ></div>
              <div className="gauge-center"></div>
              <div className="gauge-marks">
                {getTempMarks()}
              </div>
            </div>
          </div>
          
          <div className="gauge throttle-gauge">
            <div className="gauge-label">THROTTLE</div>
            <div className="gauge-dial blueprint">
              <div 
                className="gauge-needle" 
                style={{ transform: `rotate(${calculateFuelAngle(safeData.throttle_pos)}deg)` }}
              ></div>
              <div className="gauge-center"></div>
              <div className="gauge-marks">
                <span>0%</span>
                <span>50%</span>
                <span>100%</span>
              </div>
            </div>
          </div>
        </>
      ) : (
        // Default layout for other modes
        <>
          <div className="gauge speed-gauge">
            <div className="gauge-label">SPEED {getSpeedUnit()}</div>
            <div className="gauge-dial">
              <div 
                className="gauge-needle" 
                style={{ transform: `rotate(${calculateSpeedAngle(safeData.speed)}deg)` }}
              ></div>
              <div className="gauge-center"></div>
              <div className="gauge-marks">
                {getSpeedMarks()}
              </div>
            </div>
          </div>
          
          <div className="gauge temp-gauge">
            <div className="gauge-label">TEMP {getTempUnit()}</div>
            <div className="gauge-dial">
              <div 
                className="gauge-needle" 
                style={{ transform: `rotate(${calculateTempAngle(safeData.coolant_temp)}deg)` }}
              ></div>
              <div className="gauge-center"></div>
              <div className="gauge-marks">
                {getTempMarks()}
              </div>
            </div>
          </div>
          
          <div className="gauge fuel-gauge">
            <div className="gauge-label">FUEL</div>
            <div className="gauge-dial">
              <div 
                className="gauge-needle" 
                style={{ transform: `rotate(${calculateFuelAngle(safeData.fuel_level)}deg)` }}
              ></div>
              <div className="gauge-center"></div>
              <div className="gauge-marks">
                <span>E</span>
                <span>1/2</span>
                <span>F</span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default GaugeCluster;