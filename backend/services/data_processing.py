"""
Data Processing Service - Handles sensor data preprocessing and feature extraction
"""

import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)

class SensorDataProcessor:
    """Service for processing and analyzing sensor data"""
    
    def __init__(self):
        self.data_buffers = {}  # Store recent data for each user
        self.buffer_size = 1000  # Maximum samples to keep in buffer
        
    def process_imu_sequence(self, imu_data: List[Dict]) -> List[Dict]:
        """
        Process IMU data sequence for AI model input
        Applies filtering, normalization, and feature extraction
        """
        try:
            if not imu_data:
                return []
            
            # Apply noise filtering
            filtered_data = self._apply_noise_filter(imu_data)
            
            # Normalize data
            normalized_data = self._normalize_imu_data(filtered_data)
            
            # Extract rolling features
            feature_data = self._extract_rolling_features(normalized_data)
            
            return feature_data
            
        except Exception as e:
            logger.error(f"Error processing IMU sequence: {str(e)}")
            return imu_data  # Return original data as fallback
    
    def _apply_noise_filter(self, imu_data: List[Dict]) -> List[Dict]:
        """Apply simple moving average filter to reduce noise"""
        window_size = 3
        if len(imu_data) < window_size:
            return imu_data
        
        filtered_data = []
        
        for i in range(len(imu_data)):
            if i < window_size - 1:
                filtered_data.append(imu_data[i])
                continue
            
            # Calculate moving average
            avg_sample = {
                'timestamp': imu_data[i]['timestamp'],
                'acceleration_x': 0,
                'acceleration_y': 0,
                'acceleration_z': 0,
                'gyroscope_x': 0,
                'gyroscope_y': 0,
                'gyroscope_z': 0
            }
            
            for j in range(window_size):
                sample = imu_data[i - j]
                avg_sample['acceleration_x'] += sample['acceleration_x']
                avg_sample['acceleration_y'] += sample['acceleration_y']
                avg_sample['acceleration_z'] += sample['acceleration_z']
                avg_sample['gyroscope_x'] += sample['gyroscope_x']
                avg_sample['gyroscope_y'] += sample['gyroscope_y']
                avg_sample['gyroscope_z'] += sample['gyroscope_z']
            
            # Divide by window size
            for key in ['acceleration_x', 'acceleration_y', 'acceleration_z',
                       'gyroscope_x', 'gyroscope_y', 'gyroscope_z']:
                avg_sample[key] /= window_size
            
            filtered_data.append(avg_sample)
        
        return filtered_data
    
    def _normalize_imu_data(self, imu_data: List[Dict]) -> List[Dict]:
        """Normalize IMU data to standard ranges"""
        if not imu_data:
            return []
        
        normalized_data = []
        
        for sample in imu_data:
            normalized_sample = sample.copy()
            
            # Calculate magnitude for normalization reference
            acc_magnitude = np.sqrt(
                sample['acceleration_x']**2 + 
                sample['acceleration_y']**2 + 
                sample['acceleration_z']**2
            )
            
            gyro_magnitude = np.sqrt(
                sample['gyroscope_x']**2 + 
                sample['gyroscope_y']**2 + 
                sample['gyroscope_z']**2
            )
            
            # Add computed features
            normalized_sample['acc_magnitude'] = acc_magnitude
            normalized_sample['gyro_magnitude'] = gyro_magnitude
            
            # Normalize individual components (z-score style)
            # In a real implementation, these would use learned statistics
            normalized_sample['acc_x_norm'] = sample['acceleration_x'] / max(acc_magnitude, 1.0)
            normalized_sample['acc_y_norm'] = sample['acceleration_y'] / max(acc_magnitude, 1.0)
            normalized_sample['acc_z_norm'] = sample['acceleration_z'] / max(acc_magnitude, 1.0)
            
            normalized_data.append(normalized_sample)
        
        return normalized_data
    
    def _extract_rolling_features(self, imu_data: List[Dict]) -> List[Dict]:
        """Extract rolling statistical features from IMU data"""
        feature_window = 10
        feature_data = []
        
        for i, sample in enumerate(imu_data):
            enhanced_sample = sample.copy()
            
            # Extract features from recent window
            if i >= feature_window - 1:
                window_data = imu_data[i - feature_window + 1:i + 1]
                
                # Statistical features
                acc_magnitudes = [s['acc_magnitude'] for s in window_data]
                enhanced_sample.update({
                    'acc_mean': np.mean(acc_magnitudes),
                    'acc_std': np.std(acc_magnitudes),
                    'acc_min': np.min(acc_magnitudes),
                    'acc_max': np.max(acc_magnitudes),
                    'acc_range': np.max(acc_magnitudes) - np.min(acc_magnitudes)
                })
                
                # Frequency domain features (simplified)
                enhanced_sample['acc_energy'] = np.sum(np.array(acc_magnitudes)**2)
            
            feature_data.append(enhanced_sample)
        
        return feature_data
    
    def update_user_buffer(self, user_id: str, sensor_data: Dict):
        """Update user's sensor data buffer"""
        if user_id not in self.data_buffers:
            self.data_buffers[user_id] = {
                'imu': deque(maxlen=self.buffer_size),
                'location': deque(maxlen=100),  # Smaller buffer for location
                'last_update': datetime.utcnow()
            }
        
        buffer = self.data_buffers[user_id]
        
        # Add IMU data
        if sensor_data.get('imu_data'):
            for imu_sample in sensor_data['imu_data']:
                buffer['imu'].append(imu_sample)
        
        # Add location data
        if sensor_data.get('location'):
            buffer['location'].append(sensor_data['location'])
        
        buffer['last_update'] = datetime.utcnow()
    
    def get_recent_data(self, user_id: str, data_type: str, count: int = 100) -> List[Dict]:
        """Get recent sensor data for a user"""
        if user_id not in self.data_buffers:
            return []
        
        buffer = self.data_buffers[user_id]
        
        if data_type not in buffer:
            return []
        
        # Convert deque to list and return recent samples
        data_list = list(buffer[data_type])
        return data_list[-count:] if len(data_list) > count else data_list
    
    def calculate_movement_metrics(self, user_id: str) -> Dict[str, float]:
        """Calculate movement-related metrics for behavioral analysis"""
        try:
            location_data = self.get_recent_data(user_id, 'location', 50)
            
            if len(location_data) < 2:
                return {'total_distance': 0.0, 'average_speed': 0.0, 'movement_variance': 0.0}
            
            # Calculate total distance traveled
            total_distance = 0.0
            speeds = []
            
            for i in range(1, len(location_data)):
                prev_loc = location_data[i-1]
                curr_loc = location_data[i]
                
                # Calculate distance between points
                distance = self._calculate_distance(
                    prev_loc['latitude'], prev_loc['longitude'],
                    curr_loc['latitude'], curr_loc['longitude']
                )
                
                total_distance += distance
                
                # Calculate speed if time difference is available
                if 'timestamp' in prev_loc and 'timestamp' in curr_loc:
                    time_diff = (
                        datetime.fromisoformat(curr_loc['timestamp']) - 
                        datetime.fromisoformat(prev_loc['timestamp'])
                    ).total_seconds()
                    
                    if time_diff > 0:
                        speed = (distance * 1000) / time_diff  # m/s
                        speeds.append(speed)
            
            # Calculate metrics
            average_speed = np.mean(speeds) if speeds else 0.0
            movement_variance = np.var(speeds) if speeds else 0.0
            
            return {
                'total_distance': total_distance,  # km
                'average_speed': average_speed * 3.6,  # Convert to km/h
                'movement_variance': movement_variance,
                'sample_count': len(location_data)
            }
            
        except Exception as e:
            logger.error(f"Error calculating movement metrics: {str(e)}")
            return {'total_distance': 0.0, 'average_speed': 0.0, 'movement_variance': 0.0}
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two geographic points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = np.radians(lat1)
        lon1_rad = np.radians(lon1)
        lat2_rad = np.radians(lat2)
        lon2_rad = np.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (np.sin(dlat/2)**2 + 
             np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2)
        
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def detect_activity_patterns(self, user_id: str) -> Dict[str, any]:
        """Detect activity patterns for behavioral analysis"""
        try:
            imu_data = self.get_recent_data(user_id, 'imu', 500)
            
            if not imu_data:
                return {'activity_level': 'unknown', 'pattern_confidence': 0.0}
            
            # Calculate activity metrics
            activity_levels = []
            for sample in imu_data:
                activity_level = sample.get('acc_magnitude', 0)
                activity_levels.append(activity_level)
            
            avg_activity = np.mean(activity_levels)
            activity_variance = np.var(activity_levels)
            
            # Classify activity level
            if avg_activity < 2.0:
                activity_type = 'stationary'
            elif avg_activity < 5.0:
                activity_type = 'walking'
            elif avg_activity < 10.0:
                activity_type = 'active'
            else:
                activity_type = 'very_active'
            
            return {
                'activity_level': activity_type,
                'average_magnitude': avg_activity,
                'variance': activity_variance,
                'pattern_confidence': min(len(imu_data) / 100.0, 1.0),
                'sample_count': len(imu_data)
            }
            
        except Exception as e:
            logger.error(f"Error detecting activity patterns: {str(e)}")
            return {'activity_level': 'unknown', 'pattern_confidence': 0.0}
