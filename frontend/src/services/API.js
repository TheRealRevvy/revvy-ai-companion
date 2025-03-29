/**
 * Revvy AI Companion - API Service
 * Handles communication with the Revvy backend API
 */

class API {
  constructor() {
    // API endpoint
    this.baseUrl = 'http://localhost:5000/api';
    
    // WebSocket connection
    this.ws = null;
    this.wsUrl = 'ws://localhost:5001';
    
    // Event listeners
    this.eventListeners = {};
    
    // Connection status
    this.connected = false;
    
    // Auto reconnect
    this.reconnectTimer = null;
    this.reconnectInterval = 5000; // 5 seconds
  }
  
  /**
   * Connect to Revvy backend API and WebSocket
   */
  async connect(retryAttempts = 3) {
    for (let attempt = 1; attempt <= retryAttempts; attempt++) {
      try {
        // Test API connection
        const status = await this.getStatus();
        
        if (status) {
          console.log('Connected to Revvy API:', status);
          
          // Connect WebSocket
          this.connectWebSocket();
          
          return true;
        }
      } catch (error) {
        console.error(`Connection attempt ${attempt}/${retryAttempts} failed:`, error);
        
        if (attempt < retryAttempts) {
          // Wait before retry (exponential backoff)
          const delay = Math.min(1000 * Math.pow(2, attempt - 1), 10000);
          console.log(`Retrying in ${delay/1000} seconds...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        } else {
          throw error;
        }
      }
    }
    
    return false;
  }
  
  /**
   * Disconnect from Revvy backend
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    this.connected = false;
  }
  
  /**
   * Connect to WebSocket for real-time updates
   */
  connectWebSocket() {
    if (this.ws) {
      // Already connected
      return;
    }
    
    try {
      this.ws = new WebSocket(this.wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.connected = true;
        
        // Clear reconnect timer
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer);
          this.reconnectTimer = null;
        }
        
        // Subscribe to events
        this.ws.send(JSON.stringify({
          type: 'subscribe',
          events: ['vehicle_data', 'mode_changed', 'notification', 'achievement_unlocked', 'unit_system_changed']
        }));
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.connected = false;
        this.ws = null;
        
        // Attempt to reconnect
        if (!this.reconnectTimer) {
          this.reconnectTimer = setTimeout(() => {
            console.log('Attempting to reconnect WebSocket...');
            this.connectWebSocket();
          }, this.reconnectInterval);
        }
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      
      // Attempt to reconnect
      if (!this.reconnectTimer) {
        this.reconnectTimer = setTimeout(() => {
          console.log('Attempting to reconnect WebSocket...');
          this.connectWebSocket();
        }, this.reconnectInterval);
      }
    }
  }
  
  /**
   * Handle WebSocket messages
   */
  handleWebSocketMessage(data) {
    const messageType = data.type;
    
    // Call event listeners
    if (messageType && this.eventListeners[messageType]) {
      this.eventListeners[messageType].forEach(callback => {
        callback(data);
      });
    }
  }
  
  /**
   * Register event listener
   */
  onMessage(eventType, callback) {
    if (!this.eventListeners[eventType]) {
      this.eventListeners[eventType] = [];
    }
    
    this.eventListeners[eventType].push(callback);
  }
  
  /**
   * Remove event listener
   */
  offMessage(eventType, callback) {
    if (this.eventListeners[eventType]) {
      if (callback) {
        this.eventListeners[eventType] = this.eventListeners[eventType].filter(cb => cb !== callback);
      } else {
        delete this.eventListeners[eventType];
      }
    }
  }
  
  /**
   * Send message via WebSocket
   */
  sendWebSocketMessage(message) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return false;
    }
    
    try {
      this.ws.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      return false;
    }
  }
  
  /**
   * Get API status
   */
  async getStatus() {
    try {
      const response = await fetch(`${this.baseUrl}/status`);
      return await response.json();
    } catch (error) {
      console.error('Error getting API status:', error);
      throw error;
    }
  }
  
  /**
   * Get detailed system status
   */
  async getSystemStatus() {
    try {
      const response = await fetch(`${this.baseUrl}/system/status`);
      return await response.json();
    } catch (error) {
      console.error('Error getting system status:', error);
      throw error;
    }
  }
  
  /**
   * Attempt to reconnect components
   */
  async reconnectComponents() {
    try {
      const response = await fetch(`${this.baseUrl}/system/reconnect`, {
        method: 'POST'
      });
      
      return await response.json();
    } catch (error) {
      console.error('Error reconnecting components:', error);
      throw error;
    }
  }
  
  /**
   * Get vehicle data
   */
  async getVehicleData() {
    try {
      const response = await fetch(`${this.baseUrl}/vehicle`);
      return await response.json();
    } catch (error) {
      console.error('Error getting vehicle data:', error);
      throw error;
    }
  }
  
  /**
   * Get current mode
   */
  async getCurrentMode() {
    try {
      const response = await fetch(`${this.baseUrl}/mode`);
      return await response.json();
    } catch (error) {
      console.error('Error getting current mode:', error);
      throw error;
    }
  }
  
  /**
   * Change dashboard mode
   */
  async changeMode(mode) {
    try {
      const response = await fetch(`${this.baseUrl}/mode`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ mode })
      });
      
      return await response.json();
    } catch (error) {
      console.error('Error changing mode:', error);
      throw error;
    }
  }
  
  /**
   * Send voice command
   */
  async sendVoiceCommand(command) {
    // Try WebSocket first for faster response
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const sent = this.sendWebSocketMessage({
        type: 'voice_command',
        command: command
      });
      
      if (sent) {
        // Return a promise that will be resolved when we get the response
        return new Promise((resolve) => {
          const listener = (data) => {
            if (data.type === 'ai_response') {
              // Remove the listener
              this.offMessage('ai_response', listener);
              
              // Resolve with the response
              resolve({
                success: true,
                text: data.text
              });
            }
          };
          
          // Add listener for response
          this.onMessage('ai_response', listener);
          
          // Timeout after 10 seconds
          setTimeout(() => {
            this.offMessage('ai_response', listener);
            resolve({
              success: false,
              text: "I'm having trouble processing that right now."
            });
          }, 10000);
        });
      }
    }
    
    // Fall back to REST API
    try {
      const response = await fetch(`${this.baseUrl}/voice/command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command })
      });
      
      return await response.json();
    } catch (error) {
      console.error('Error sending voice command:', error);
      throw error;
    }
  }
  
  /**
   * Get achievements
   */
  async getAchievements() {
    try {
      const response = await fetch(`${this.baseUrl}/achievements`);
      return await response.json();
    } catch (error) {
      console.error('Error getting achievements:', error);
      throw error;
    }
  }
  
  /**
   * Clear DTC codes
   */
  async clearDTCCodes() {
    try {
      const response = await fetch(`${this.baseUrl}/dtc/clear`, {
        method: 'POST'
      });
      
      return await response.json();
    } catch (error) {
      console.error('Error clearing DTC codes:', error);
      throw error;
    }
  }
  
  /**
   * Get DTC explanation
   */
  async getDTCExplanation(code) {
    try {
      const response = await fetch(`${this.baseUrl}/dtc/explanation/${code}`);
      return await response.json();
    } catch (error) {
      console.error(`Error getting explanation for DTC ${code}:`, error);
      throw error;
    }
  }
  
  /**
   * Get unit settings
   */
  async getUnitSettings() {
    try {
      const response = await fetch(`${this.baseUrl}/settings/units`);
      return await response.json();
    } catch (error) {
      console.error('Error getting unit settings:', error);
      throw error;
    }
  }
  
  /**
   * Toggle unit system (metric/imperial)
   */
  async toggleUnitSystem(unitSystem) {
    try {
      const response = await fetch(`${this.baseUrl}/settings/units/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ unit_system: unitSystem })
      });
      
      return await response.json();
    } catch (error) {
      console.error('Error toggling unit system:', error);
      throw error;
    }
  }
  
  /**
   * Get list of available personalities
   */
  async getPersonalities() {
    try {
      const response = await fetch(`${this.baseUrl}/personalities`);
      return await response.json();
    } catch (error) {
      console.error('Error getting personalities:', error);
      throw error;
    }
  }
  
  /**
   * Change AI personality
   */
  async changePersonality(personality) {
    try {
      const response = await fetch(`${this.baseUrl}/personality`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ personality })
      });
      
      return await response.json();
    } catch (error) {
      console.error('Error changing personality:', error);
      throw error;
    }
  }
  
  /**
   * Get GPS location data
   */
  async getLocation() {
    try {
      const response = await fetch(`${this.baseUrl}/gps/location`);
      return await response.json();
    } catch (error) {
      console.error('Error getting location data:', error);
      throw error;
    }
  }
  
  /**
   * Get voice settings
   */
  async getVoiceSettings() {
    try {
      const response = await fetch(`${this.baseUrl}/voice/settings`);
      return await response.json();
    } catch (error) {
      console.error('Error getting voice settings:', error);
      throw error;
    }
  }
  
  /**
   * Update voice settings
   */
  async updateVoiceSettings(settings) {
    try {
      const response = await fetch(`${this.baseUrl}/voice/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
      });
      
      return await response.json();
    } catch (error) {
      console.error('Error updating voice settings:', error);
      throw error;
    }
  }
  
  /**
   * Get system logs
   */
  async getLogs(level = 'info', limit = 100) {
    try {
      const response = await fetch(`${this.baseUrl}/system/logs?level=${level}&limit=${limit}`);
      return await response.json();
    } catch (error) {
      console.error('Error getting system logs:', error);
      throw error;
    }
  }
  
  /**
   * Restart system
   */
  async restartSystem() {
    try {
      const response = await fetch(`${this.baseUrl}/system/restart`, {
        method: 'POST'
      });
      
      return await response.json();
    } catch (error) {
      console.error('Error restarting system:', error);
      throw error;
    }
  }
  
  /**
   * Shutdown system
   */
  async shutdownSystem() {
    try {
      const response = await fetch(`${this.baseUrl}/system/shutdown`, {
        method: 'POST'
      });
      
      return await response.json();
    } catch (error) {
      console.error('Error shutting down system:', error);
      throw error;
    }
  }
  
  /**
   * Get system configuration
   */
  async getSystemConfig() {
    try {
      const response = await fetch(`${this.baseUrl}/system/config`);
      return await response.json();
    } catch (error) {
      console.error('Error getting system config:', error);
      throw error;
    }
  }
  
  /**
   * Update system configuration
   */
  async updateSystemConfig(config) {
    try {
      const response = await fetch(`${this.baseUrl}/system/config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
      });
      
      return await response.json();
    } catch (error) {
      console.error('Error updating system config:', error);
      throw error;
    }
  }
  
  /**
   * Get trip history
   */
  async getTripHistory(limit = 10) {
    try {
      const response = await fetch(`${this.baseUrl}/trips?limit=${limit}`);
      return await response.json();
    } catch (error) {
      console.error('Error getting trip history:', error);
      throw error;
    }
  }
  
  /**
   * Get detailed trip data
   */
  async getTripDetails(tripId) {
    try {
      const response = await fetch(`${this.baseUrl}/trips/${tripId}`);
      return await response.json();
    } catch (error) {
      console.error(`Error getting details for trip ${tripId}:`, error);
      throw error;
    }
  }
  
  /**
   * Get maintenance information
   */
  async getMaintenanceInfo() {
    try {
      const response = await fetch(`${this.baseUrl}/maintenance`);
      return await response.json();
    } catch (error) {
      console.error('Error getting maintenance info:', error);
      throw error;
    }
  }
  
  /**
   * Update maintenance item
   */
  async updateMaintenanceItem(itemId, status) {
    try {
      const response = await fetch(`${this.baseUrl}/maintenance/${itemId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status })
      });
      
      return await response.json();
    } catch (error) {
      console.error(`Error updating maintenance item ${itemId}:`, error);
      throw error;
    }
  }
  
  /**
   * Is connected to backend?
   */
  isConnected() {
    return this.connected;
  }
}

// Create and export a singleton instance
const api = new API();
export default api;