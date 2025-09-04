"""
Rule-based Fallback System
Provides rule-based detection when AI models are unavailable or low-confidence
"""

import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)

class RuleBasedSystemFallback:
    """
    Rule-based fallback system for all detection types
    Provides reliable detection when AI models are unavailable
    """
    
    def __init__(self):
        self.is_initialized = False
        self.detection_thresholds = {}
        self.user_data_buffer = {}  # Store recent data for pattern analysis
        
    async def initialize(self):
        """Initialize rule-based detection thresholds"""
        try:
            # Fall detection thresholds
            self.detection_thresholds['fall'] = {
                'freefall_g_min': 0.5,      # Minimum G-force for freefall
                'freefall_g_max': 2.0,      # Maximum G-force for freefall
                'impact_g_threshold': 15.0,  # Impact G-force threshold
                'freefall_duration_min': 0.3,  # Minimum freefall duration (seconds)
                'stillness_threshold': 2.0,  # Post-impact stillness threshold
                'stillness_duration': 3.0    # Required stillness duration
            }
            
            # Crash detection thresholds
            self.detection_thresholds['crash'] = {
                'min_vehicle_speed': 25.0,    # km/h - minimum speed for crash context
                'deceleration_threshold': -8.0,  # m/s² - sudden deceleration
                'impact_g_threshold': 20.0,   # G-force threshold for crash
                'speed_drop_percentage': 0.8,  # 80% speed drop
                'time_window': 3.0            # seconds
            }
            
            # Distress detection thresholds
            self.detection_thresholds['distress'] = {
                'stationary_duration': 4.0,     # hours
                'erratic_movement_threshold': 5,  # number of direction changes per minute
                'unusual_location_radius': 2.0,  # km from usual areas
                'signal_loss_duration': 2.0     # hours
            }
            
            # Red zone detection (basic distance-based)
            self.detection_thresholds['red_zone'] = {
                'buffer_distance': 0.1,  # km buffer around zones
                'warning_distance': 0.5   # km for early warning
            }
            
            self.is_initialized = True
            logger.info("Rule-based fallback system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize rule-based fallback: {str(e)}")
            raise
    
    def is_ready(self) -> bool:
        """Check if fallback system is ready"""
        return self.is_initialized
    
    async def process_data(self, user_id: str, sensor_data: Dict):
        """Process sensor data through rule-based detection"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Update user data buffer
            self._update_user_buffer(user_id, sensor_data)
            
            alerts = []
            
            # Fall detection
            if sensor_data.get('imu_data'):
                fall_alert = await self._detect_fall_rule_based(user_id, sensor_data['imu_data'])
                if fall_alert:
                    alerts.append(fall_alert)
            
            # Crash detection (needs both IMU and GPS data)
            if sensor_data.get('imu_data') and sensor_data.get('location'):
                crash_alert = await self._detect_crash_rule_based(user_id, sensor_data)
                if crash_alert:
                    alerts.append(crash_alert)
            
            # Distress detection
            distress_alert = await self._detect_distress_rule_based(user_id, sensor_data)
            if distress_alert:
                alerts.append(distress_alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error in rule-based processing: {str(e)}")
            return []
    
    async def _detect_fall_rule_based(self, user_id: str, imu_data: List[Dict]) -> Optional[Dict]:
        """Rule-based fall detection using three-phase approach"""
        try:
            if len(imu_data) < 10:  # Need sufficient data
                return None
            
            thresholds = self.detection_thresholds['fall']
            
            # Analyze recent IMU sequence for fall pattern
            fall_detected = False
            confidence = 0.0
            
            # Calculate G-force magnitudes
            magnitudes = []
            for sample in imu_data:
                magnitude = math.sqrt(
                    sample['acceleration_x']**2 + 
                    sample['acceleration_y']**2 + 
                    sample['acceleration_z']**2
                )
                magnitudes.append(magnitude)
            
            # Look for freefall-impact pattern
            for i in range(len(magnitudes) - 5):
                # Phase 1: Check for freefall (low G-force)
                freefall_window = magnitudes[i:i+3]
                if all(g < thresholds['freefall_g_max'] for g in freefall_window):
                    
                    # Phase 2: Check for impact (high G-force) shortly after
                    impact_window = magnitudes[i+3:i+5]
                    if any(g > thresholds['impact_g_threshold'] for g in impact_window):
                        
                        # Phase 3: Check for stillness after impact
                        if i+10 < len(magnitudes):
                            stillness_window = magnitudes[i+5:i+10]
                            if all(g < thresholds['stillness_threshold'] for g in stillness_window):
                                fall_detected = True
                                confidence = 0.75  # High confidence for rule-based
                                break
            
            if fall_detected:
                return {
                    'user_id': user_id,
                    'alert_type': 'fall_detected',
                    'priority': 'critical',
                    'confidence': confidence,
                    'message': 'Fall detected using rule-based system',
                    'detection_method': 'rule_based',
                    'timestamp': datetime.utcnow(),
                    'details': {
                        'max_impact_g': max(magnitudes),
                        'min_freefall_g': min(magnitudes),
                        'pattern_detected': 'freefall_impact_stillness'
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in rule-based fall detection: {str(e)}")
            return None
    
    async def _detect_crash_rule_based(self, user_id: str, sensor_data: Dict) -> Optional[Dict]:
        """Rule-based crash detection using sensor fusion"""
        try:
            thresholds = self.detection_thresholds['crash']
            
            # Get recent data for context
            recent_data = self._get_recent_user_data(user_id, 30)  # Last 30 seconds
            
            if len(recent_data) < 5:  # Need sufficient data
                return None
            
            # Check for vehicle context (speed > threshold)
            speeds = [data.get('location', {}).get('speed', 0) for data in recent_data[-5:]]
            max_recent_speed = max(speeds) if speeds else 0
            
            if max_recent_speed < thresholds['min_vehicle_speed']:
                return None  # Not in vehicle context
            
            # Check for extreme deceleration
            if len(speeds) >= 2:
                speed_change = speeds[-1] - speeds[0]
                time_diff = 5.0  # Approximate time window
                deceleration = speed_change / time_diff * 3.6  # Convert to m/s²
                
                if deceleration < thresholds['deceleration_threshold']:
                    
                    # Check for extreme G-force
                    imu_data = sensor_data.get('imu_data', [])
                    max_g_force = 0
                    
                    for sample in imu_data[-10:]:  # Check recent samples
                        g_force = math.sqrt(
                            sample['acceleration_x']**2 + 
                            sample['acceleration_y']**2 + 
                            sample['acceleration_z']**2
                        )
                        max_g_force = max(max_g_force, g_force)
                    
                    if max_g_force > thresholds['impact_g_threshold']:
                        return {
                            'user_id': user_id,
                            'alert_type': 'crash_detected',
                            'priority': 'critical',
                            'confidence': 0.8,
                            'message': 'Vehicle crash detected using rule-based system',
                            'detection_method': 'rule_based',
                            'timestamp': datetime.utcnow(),
                            'details': {
                                'max_g_force': max_g_force,
                                'deceleration': deceleration,
                                'speed_before': speeds[0],
                                'speed_after': speeds[-1]
                            }
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in rule-based crash detection: {str(e)}")
            return None
    
    async def _detect_distress_rule_based(self, user_id: str, sensor_data: Dict) -> Optional[Dict]:
        """Rule-based distress detection using behavioral patterns"""
        try:
            thresholds = self.detection_thresholds['distress']
            
            # Get historical data for this user
            user_history = self._get_user_history(user_id)
            
            distress_indicators = []
            confidence = 0.0
            
            # Check for prolonged inactivity
            if self._check_prolonged_inactivity(user_id, thresholds['stationary_duration']):
                distress_indicators.append('prolonged_inactivity')
                confidence += 0.3
            
            # Check for erratic movement
            if self._check_erratic_movement(user_id):
                distress_indicators.append('erratic_movement')
                confidence += 0.2
            
            # Check for unusual location
            if sensor_data.get('location'):
                if self._check_unusual_location(user_id, sensor_data['location']):
                    distress_indicators.append('unusual_location')
                    confidence += 0.3
            
            # Check for signal loss patterns
            if self._check_signal_loss_pattern(user_id):
                distress_indicators.append('signal_loss_pattern')
                confidence += 0.2
            
            # Trigger alert if multiple indicators or high confidence
            if len(distress_indicators) >= 2 or confidence > 0.5:
                return {
                    'user_id': user_id,
                    'alert_type': 'distress_detected',
                    'priority': 'medium',
                    'confidence': min(confidence, 0.9),
                    'message': f'Distress indicators detected: {", ".join(distress_indicators)}',
                    'detection_method': 'rule_based',
                    'timestamp': datetime.utcnow(),
                    'details': {
                        'indicators': distress_indicators,
                        'requires_verification': True
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in rule-based distress detection: {str(e)}")
            return None
    
    def _update_user_buffer(self, user_id: str, sensor_data: Dict):
        """Update user's data buffer"""
        if user_id not in self.user_data_buffer:
            self.user_data_buffer[user_id] = {
                'data_history': [],
                'locations': [],
                'last_activity': datetime.utcnow()
            }
        
        # Add current data to buffer
        buffer = self.user_data_buffer[user_id]
        buffer['data_history'].append({
            'timestamp': datetime.utcnow(),
            'sensor_data': sensor_data
        })
        
        # Keep only recent data (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        buffer['data_history'] = [
            item for item in buffer['data_history'] 
            if item['timestamp'] > cutoff_time
        ]
        
        # Update location history
        if sensor_data.get('location'):
            buffer['locations'].append({
                'timestamp': datetime.utcnow(),
                'location': sensor_data['location']
            })
            buffer['locations'] = buffer['locations'][-100:]  # Keep last 100 locations
        
        buffer['last_activity'] = datetime.utcnow()
    
    def _get_recent_user_data(self, user_id: str, seconds: int) -> List[Dict]:
        """Get user data from recent time window"""
        if user_id not in self.user_data_buffer:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(seconds=seconds)
        recent_data = []
        
        for item in self.user_data_buffer[user_id]['data_history']:
            if item['timestamp'] > cutoff_time:
                recent_data.append(item['sensor_data'])
        
        return recent_data
    
    def _get_user_history(self, user_id: str) -> Dict:
        """Get user's historical data"""
        if user_id not in self.user_data_buffer:
            return {'data_history': [], 'locations': []}
        
        return self.user_data_buffer[user_id]
    
    def _check_prolonged_inactivity(self, user_id: str, threshold_hours: float) -> bool:
        """Check for prolonged inactivity"""
        try:
            history = self._get_user_history(user_id)
            if not history['locations']:
                return False
            
            # Check if user has been in same location for too long
            recent_locations = history['locations'][-20:]  # Check recent locations
            
            if len(recent_locations) < 2:
                return False
            
            # Calculate if user has moved significantly
            first_location = recent_locations[0]['location']
            last_location = recent_locations[-1]['location']
            
            distance = self._calculate_distance(
                first_location['latitude'], first_location['longitude'],
                last_location['latitude'], last_location['longitude']
            )
            
            time_diff = (recent_locations[-1]['timestamp'] - recent_locations[0]['timestamp']).total_seconds() / 3600
            
            # If very little movement over long period
            return distance < 0.1 and time_diff > threshold_hours  # Less than 100m movement
            
        except Exception as e:
            logger.error(f"Error checking prolonged inactivity: {str(e)}")
            return False
    
    def _check_erratic_movement(self, user_id: str) -> bool:
        """Check for erratic movement patterns"""
        try:
            history = self._get_user_history(user_id)
            locations = history['locations'][-10:]  # Check recent locations
            
            if len(locations) < 5:
                return False
            
            # Calculate direction changes
            direction_changes = 0
            
            for i in range(2, len(locations)):
                # Calculate bearings
                bearing1 = self._calculate_bearing(
                    locations[i-2]['location'], locations[i-1]['location']
                )
                bearing2 = self._calculate_bearing(
                    locations[i-1]['location'], locations[i]['location']
                )
                
                # Check for significant direction change
                bearing_diff = abs(bearing2 - bearing1)
                if bearing_diff > 180:
                    bearing_diff = 360 - bearing_diff
                
                if bearing_diff > 45:  # More than 45-degree change
                    direction_changes += 1
            
            # Erratic if too many direction changes
            return direction_changes > len(locations) * 0.6
            
        except Exception as e:
            logger.error(f"Error checking erratic movement: {str(e)}")
            return False
    
    def _check_unusual_location(self, user_id: str, current_location: Dict) -> bool:
        """Check if current location is unusual for user"""
        try:
            history = self._get_user_history(user_id)
            locations = [item['location'] for item in history['locations']]
            
            if len(locations) < 10:  # Need sufficient history
                return False
            
            # Calculate average location (simplified approach)
            avg_lat = sum(loc['latitude'] for loc in locations) / len(locations)
            avg_lng = sum(loc['longitude'] for loc in locations) / len(locations)
            
            # Calculate distance from typical area
            distance = self._calculate_distance(
                current_location['latitude'], current_location['longitude'],
                avg_lat, avg_lng
            )
            
            # Unusual if far from typical locations
            return distance > 10.0  # More than 10km from usual area
            
        except Exception as e:
            logger.error(f"Error checking unusual location: {str(e)}")
            return False
    
    def _check_signal_loss_pattern(self, user_id: str) -> bool:
        """Check for suspicious signal loss patterns"""
        try:
            history = self._get_user_history(user_id)
            
            # Check gaps in data
            if len(history['data_history']) < 5:
                return False
            
            # Look for recent data gaps
            recent_data = history['data_history'][-10:]
            
            for i in range(1, len(recent_data)):
                time_gap = (recent_data[i]['timestamp'] - recent_data[i-1]['timestamp']).total_seconds()
                
                # Suspicious if gap is too long (more than 30 minutes)
                if time_gap > 1800:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking signal loss pattern: {str(e)}")
            return False
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def _calculate_bearing(self, location1: Dict, location2: Dict) -> float:
        """Calculate bearing between two locations"""
        lat1 = math.radians(location1['latitude'])
        lat2 = math.radians(location2['latitude'])
        dlng = math.radians(location2['longitude'] - location1['longitude'])
        
        y = math.sin(dlng) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlng)
        
        bearing = math.atan2(y, x)
        return (math.degrees(bearing) + 360) % 360
