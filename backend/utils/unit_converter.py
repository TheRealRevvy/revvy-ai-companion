"""
Revvy AI Companion - Unit Converter
Handles conversion between different unit systems
"""

class UnitConverter:
    """Utility class for unit conversions"""
    
    @staticmethod
    def celsius_to_fahrenheit(celsius):
        """Convert Celsius to Fahrenheit"""
        if celsius is None:
            return None
        return (celsius * 9/5) + 32
    
    @staticmethod
    def fahrenheit_to_celsius(fahrenheit):
        """Convert Fahrenheit to Celsius"""
        if fahrenheit is None:
            return None
        return (fahrenheit - 32) * 5/9
    
    @staticmethod
    def kph_to_mph(kph):
        """Convert km/h to mph"""
        if kph is None:
            return None
        return kph * 0.621371
    
    @staticmethod
    def mph_to_kph(mph):
        """Convert mph to km/h"""
        if mph is None:
            return None
        return mph / 0.621371
    
    @staticmethod
    def km_to_miles(km):
        """Convert kilometers to miles"""
        if km is None:
            return None
        return km * 0.621371
    
    @staticmethod
    def miles_to_km(miles):
        """Convert miles to kilometers"""
        if miles is None:
            return None
        return miles / 0.621371
    
    @staticmethod
    def kpa_to_psi(kpa):
        """Convert kPa to PSI"""
        if kpa is None:
            return None
        return kpa * 0.145038
    
    @staticmethod
    def psi_to_kpa(psi):
        """Convert PSI to kPa"""
        if psi is None:
            return None
        return psi / 0.145038
    
    @staticmethod
    def bar_to_psi(bar):
        """Convert BAR to PSI"""
        if bar is None:
            return None
        return bar * 14.5038
    
    @staticmethod
    def convert_temperature(value, from_unit, to_unit):
        """Convert temperature between units"""
        if value is None:
            return None
            
        if from_unit == to_unit:
            return value
            
        if from_unit == "celsius" and to_unit == "fahrenheit":
            return UnitConverter.celsius_to_fahrenheit(value)
            
        if from_unit == "fahrenheit" and to_unit == "celsius":
            return UnitConverter.fahrenheit_to_celsius(value)
            
        return value  # Default fallback
    
    @staticmethod
    def convert_speed(value, from_unit, to_unit):
        """Convert speed between units"""
        if value is None:
            return None
            
        if from_unit == to_unit:
            return value
            
        if from_unit == "kph" and to_unit == "mph":
            return UnitConverter.kph_to_mph(value)
            
        if from_unit == "mph" and to_unit == "kph":
            return UnitConverter.mph_to_kph(value)
            
        return value  # Default fallback
    
    @staticmethod
    def convert_distance(value, from_unit, to_unit):
        """Convert distance between units"""
        if value is None:
            return None
            
        if from_unit == to_unit:
            return value
            
        if from_unit == "km" and to_unit == "mi":
            return UnitConverter.km_to_miles(value)
            
        if from_unit == "mi" and to_unit == "km":
            return UnitConverter.miles_to_km(value)
            
        return value  # Default fallback
    
    @staticmethod
    def convert_pressure(value, from_unit, to_unit):
        """Convert pressure between units"""
        if value is None:
            return None
            
        if from_unit == to_unit:
            return value
            
        if from_unit == "kpa" and to_unit == "psi":
            return UnitConverter.kpa_to_psi(value)
            
        if from_unit == "psi" and to_unit == "kpa":
            return UnitConverter.psi_to_kpa(value)
            
        if from_unit == "bar" and to_unit == "psi":
            return UnitConverter.bar_to_psi(value)
            
        return value  # Default fallback