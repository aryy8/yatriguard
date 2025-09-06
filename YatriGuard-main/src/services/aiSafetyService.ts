/**
 * YatriGuard AI/ML Safety Service
 * Handles WebSocket connection to backend for real-time safety monitoring
 */

import { useEffect, useState, useCallback, useRef } from 'react';

// Types for AI/ML data structures
export interface SafetyAnalysis {
  overall_risk_score: number;
  risk_level: 'very_low' | 'low' | 'medium' | 'high' | 'very_high';
  is_safe: boolean;
  location: {
    lat: number;
    lng: number;
    timestamp: string;
  };
  detection_results: {
    fall_detection: {
      is_fall: boolean;
      confidence: number;
      phase?: string;
    };
    crash_detection: {
      is_crash: boolean;
      confidence: number;
      impact_severity?: number;
    };
    red_zone_detection: {
      is_red_zone: boolean;
      confidence: number;
      zone_name?: string;
      crime_risk_score?: number;
    };
    distress_detection: {
      is_distressed: boolean;
      confidence: number;
      anomaly_score?: number;
    };
  };
  enhanced_analysis?: {
    nearest_area?: {
      name: string;
      category: string;
      distance_km: number;
    };
    crime_breakdown?: {
      crime_risk: number;
      time_risk: number;
      crowd_risk: number;
      police_impact: number;
    };
    safety_recommendations: string[];
    area_alerts: string[];
  };
}

export interface TripStatus {
  trip_id: string;
  is_active: boolean;
  current_location: {
    lat: number;
    lng: number;
    timestamp: string;
  };
  safety_events: SafetyEvent[];
  battery_level: number;
  processing_mode: 'high' | 'medium' | 'low' | 'critical';
  connection_status: 'connected' | 'reconnecting' | 'disconnected';
}

export interface SafetyEvent {
  id: string;
  type: 'fall' | 'crash' | 'red_zone' | 'distress' | 'low_battery' | 'connection_lost';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  location?: {
    lat: number;
    lng: number;
  };
  timestamp: string;
  acknowledged: boolean;
}

// WebSocket connection hook
export function useYatriGuardWebSocket(userId?: string) {
  const [isConnected, setIsConnected] = useState(false);
  const [safetyAnalysis, setSafetyAnalysis] = useState<SafetyAnalysis | null>(null);
  const [tripStatus, setTripStatus] = useState<TripStatus | null>(null);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const maxRetries = 5;
  const baseRetryDelay = 1000;

  const connect = useCallback(() => {
    if (!userId) return;

    try {
      // WebSocket URL - adjust for your deployment
      const wsUrl = process.env.NODE_ENV === 'production' 
        ? `wss://api.yatriguard.com/ws/${userId}`
        : `ws://localhost:8000/ws/${userId}`;
      
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('YatriGuard WebSocket connected');
        setIsConnected(true);
        setConnectionError(null);
        setRetryCount(0);
        
        // Send initial connection message
        wsRef.current?.send(JSON.stringify({
          type: 'connect',
          user_id: userId,
          timestamp: new Date().toISOString()
        }));
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'safety_analysis':
              setSafetyAnalysis(data.payload);
              break;
              
            case 'trip_status':
              setTripStatus(data.payload);
              break;
              
            case 'safety_alert':
              // Handle real-time safety alerts
              if (tripStatus) {
                setTripStatus(prev => prev ? {
                  ...prev,
                  safety_events: [...prev.safety_events, data.payload]
                } : null);
              }
              break;
              
            case 'battery_update':
              if (tripStatus) {
                setTripStatus(prev => prev ? {
                  ...prev,
                  battery_level: data.payload.level,
                  processing_mode: data.payload.mode
                } : null);
              }
              break;
              
            default:
              console.log('Unknown WebSocket message type:', data.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      wsRef.current.onclose = (event) => {
        setIsConnected(false);
        console.log('YatriGuard WebSocket disconnected:', event.code, event.reason);
        
        // Attempt reconnection if not manually closed
        if (event.code !== 1000 && retryCount < maxRetries) {
          const delay = baseRetryDelay * Math.pow(2, retryCount);
          setConnectionError(`Connection lost. Retrying in ${delay/1000}s...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            setRetryCount(prev => prev + 1);
            connect();
          }, delay);
        } else if (retryCount >= maxRetries) {
          setConnectionError('Connection failed. Please refresh the page.');
        }
      };
      
      wsRef.current.onerror = (error) => {
        console.error('YatriGuard WebSocket error:', error);
        setConnectionError('Connection error occurred.');
      };
      
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      setConnectionError('Failed to establish connection.');
    }
  }, [userId, retryCount]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setSafetyAnalysis(null);
    setTripStatus(null);
  }, []);

  // Send location update to backend
  const sendLocationUpdate = useCallback((lat: number, lng: number) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify({
        type: 'location_update',
        payload: {
          latitude: lat,
          longitude: lng,
          timestamp: new Date().toISOString()
        }
      }));
    }
  }, [isConnected]);

  // Send sensor data for AI/ML processing
  const sendSensorData = useCallback((sensorData: {
    accelerometer: { x: number; y: number; z: number };
    gyroscope: { x: number; y: number; z: number };
    magnetometer?: { x: number; y: number; z: number };
  }) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify({
        type: 'sensor_data',
        payload: {
          ...sensorData,
          timestamp: new Date().toISOString()
        }
      }));
    }
  }, [isConnected]);

  // Start/stop trip monitoring
  const toggleTripMonitoring = useCallback((start: boolean) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify({
        type: start ? 'start_trip' : 'stop_trip',
        timestamp: new Date().toISOString()
      }));
    }
  }, [isConnected]);

  // Acknowledge safety alert
  const acknowledgeSafetyAlert = useCallback((alertId: string) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify({
        type: 'acknowledge_alert',
        payload: { alert_id: alertId }
      }));
    }
  }, [isConnected]);

  useEffect(() => {
    if (userId) {
      connect();
    }
    
    return () => {
      disconnect();
    };
  }, [userId, connect, disconnect]);

  return {
    isConnected,
    safetyAnalysis,
    tripStatus,
    connectionError,
    sendLocationUpdate,
    sendSensorData,
    toggleTripMonitoring,
    acknowledgeSafetyAlert,
    reconnect: connect
  };
}

// Safety score calculation utilities
export const SafetyUtils = {
  calculateOverallSafetyScore: (analysis: SafetyAnalysis): number => {
    if (!analysis) return 50; // Default neutral score
    
    // Convert 0-10 risk score to 0-100 safety score (inverted)
    const baseScore = (10 - analysis.overall_risk_score) * 10;
    
    // Apply detection-specific adjustments
    let adjustments = 0;
    const detections = analysis.detection_results;
    
    if (detections.fall_detection.is_fall) adjustments -= 30;
    if (detections.crash_detection.is_crash) adjustments -= 40;
    if (detections.red_zone_detection.is_red_zone) adjustments -= 25;
    if (detections.distress_detection.is_distressed) adjustments -= 20;
    
    return Math.max(0, Math.min(100, baseScore + adjustments));
  },

  getScoreColor: (score: number): string => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  },

  getScoreBadgeVariant: (score: number): 'default' | 'secondary' | 'destructive' => {
    if (score >= 70) return 'default';
    if (score >= 40) return 'secondary';
    return 'destructive';
  },

  getRiskLevelDisplay: (level: string): { text: string; color: string } => {
    const displays = {
      'very_low': { text: 'Very Safe', color: 'text-green-600' },
      'low': { text: 'Safe', color: 'text-green-500' },
      'medium': { text: 'Moderate', color: 'text-yellow-600' },
      'high': { text: 'High Risk', color: 'text-orange-600' },
      'very_high': { text: 'Critical', color: 'text-red-600' }
    };
    return displays[level as keyof typeof displays] || { text: 'Unknown', color: 'text-gray-600' };
  }
};

// Device sensor data collection hook
export function useDeviceSensors() {
  const [sensorData, setSensorData] = useState<{
    accelerometer: { x: number; y: number; z: number } | null;
    gyroscope: { x: number; y: number; z: number } | null;
    magnetometer: { x: number; y: number; z: number } | null;
  }>({
    accelerometer: null,
    gyroscope: null,
    magnetometer: null
  });

  const [isSupported, setIsSupported] = useState(false);
  const [permissionGranted, setPermissionGranted] = useState(false);

  useEffect(() => {
    // Check for device motion support
    if (typeof DeviceMotionEvent !== 'undefined') {
      setIsSupported(true);
      
      // Request permission on iOS
      if (typeof (DeviceMotionEvent as any).requestPermission === 'function') {
        (DeviceMotionEvent as any).requestPermission()
          .then((permission: string) => {
            setPermissionGranted(permission === 'granted');
          })
          .catch(console.error);
      } else {
        setPermissionGranted(true);
      }
    }
  }, []);

  useEffect(() => {
    if (!isSupported || !permissionGranted) return;

    const handleDeviceMotion = (event: DeviceMotionEvent) => {
      setSensorData({
        accelerometer: event.acceleration ? {
          x: event.acceleration.x || 0,
          y: event.acceleration.y || 0,
          z: event.acceleration.z || 0
        } : null,
        gyroscope: event.rotationRate ? {
          x: event.rotationRate.alpha || 0,
          y: event.rotationRate.beta || 0,
          z: event.rotationRate.gamma || 0
        } : null,
        magnetometer: null // Not directly available via DeviceMotionEvent
      });
    };

    window.addEventListener('devicemotion', handleDeviceMotion);
    
    return () => {
      window.removeEventListener('devicemotion', handleDeviceMotion);
    };
  }, [isSupported, permissionGranted]);

  return {
    sensorData,
    isSupported,
    permissionGranted
  };
}

export default useYatriGuardWebSocket;
