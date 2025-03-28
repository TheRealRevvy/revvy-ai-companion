import React from 'react';
import '../styles/QuickUnitToggle.css';

const QuickUnitToggle = ({ unitSystem, onToggle, loading }) => {
  return (
    <button 
      className={`quick-unit-toggle ${loading ? 'loading' : ''}`}
      onClick={onToggle}
      disabled={loading}
      title={`Switch to ${unitSystem === 'metric' ? 'imperial' : 'metric'} units`}
    >
      {unitSystem === 'metric' ? 'km/h' : 'mph'}
    </button>
  );
};

export default QuickUnitToggle;