import React from 'react';
import '../styles/VehicleStatus.css';

const VehicleStatus = ({ data, unitSystem }) => {
  // Format values with proper units
  const formatTemperature = (temp) => {
    if (temp === undefined || temp === null) {
      return unitSystem === 'metric' ? '--°C' : '--°F';
    }
    return `${Math.round(temp)}°${unitSystem === 'metric' ? 'C' : 'F'}`;
  };
  
  const formatSpeed = (speed) => {
    if (speed === undefined || speed === null) {
      return unitSystem === 'metric' ? '-- km/h' : '-- mph';
    }
    return `${Math.round(speed)} ${unitSystem === 'metric' ? 'km/h' : 'mph'}`;
  };
  
  const formatPressure = (pressure) => {
    if (pressure === undefined || pressure === null) {
      return unitSystem === 'metric' ? '-- kPa' : '-- psi';
    }
    if (unitSystem === 'metric') {
      return `${Math.round(pressure)} kPa`;
    } else {
      return `${pressure.toFixed(1)} psi`;
    }
  };
  
  const formatDistance = (distance) => {
    if (distance === undefined || distance === null) {
      return unitSystem === 'metric' ? '-- km' : '-- mi';
    }
    if (unitSystem === 'metric') {
      return `${distance.toFixed(1)} km`;
    } else {
      return `${(distance * 0.621371).toFixed(1)} mi`;
    }
  };
  
  // Get temperature status class
  const getTempStatusClass = (temp) => {
    if (temp === undefined || temp === null) return '';
    
    const highTemp = unitSystem === 'metric' ? 110 : 230; // °C or °F
    const lowTemp = unitSystem === 'metric' ? 40 : 104;   // °C or °F
    
    if (temp > highTemp) return 'status-warning';
    if (temp < lowTemp && data.rpm > 1000) return 'status-cold';
    return 'status-normal';
  };
  
  // Get fuel status class
  const getFuelStatusClass = (level) => {
    if (level === undefined || level === null) return '';
    
    if (level < 15) return 'status-warning';
    if (level < 30) return 'status-low';
    return 'status-normal';
  };
  
  return (
    <div className="vehicle-status">
      <div className="status-group">
        <div className="status-item">
          <span className="status-label">Coolant:</span>
          <span className={`status-value ${getTempStatusClass(data.coolant_temp)}`}>
            {formatTemperature(data.coolant_temp)}
          </span>
        </div>
        
        {data.oil_temp && (
          <div className="status-item">
            <span className="status-label">Oil:</span>
            <span className="status-value">
              {formatTemperature(data.oil_temp)}
            </span>
          </div>
        )}
        
        <div className="status-item">
          <span className="status-label">Fuel:</span>
          <span className={`status-value ${getFuelStatusClass(data.fuel_level)}`}>
            {data.fuel_level !== undefined ? `${Math.round(data.fuel_level)}%` : '--'}
          </span>
        </div>
      </div>
      
      <div className="status-group">
        {data.has_turbo && (
          <div className="status-item">
            <span className="status-label">Boost:</span>
            <span className="status-value">
              {formatPressure(data.boost_pressure)}
            </span>
          </div>
        )}
        
        <div className="status-item">
          <span className="status-label">Battery:</span>
          <span className={`status-value ${data.battery_voltage < 12.0 ? 'status-warning' : 'status-normal'}`}>
            {data.battery_voltage !== undefined ? `${data.battery_voltage.toFixed(1)}V` : '--V'}
          </span>
        </div>
        
        {data.dtc_codes && data.dtc_codes.length > 0 && (
          <div className="status-item">
            <span className="status-label">DTCs:</span>
            <span className="status-value status-warning">
              {data.dtc_codes.length}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default VehicleStatus;