"""
Battery Optimization Utilities
Adjusts AI processing intensity based on device battery level and network conditions
"""

import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class ProcessingLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"

class BatteryOptimizer:
    """Optimizes AI processing based on battery and network conditions"""
    
    def __init__(self):
        self.battery_thresholds = {
            'critical': 15,  # Below 15% - minimal processing
            'low': 30,       # Below 30% - reduced processing
            'medium': 60,    # Below 60% - standard processing
            'high': 100      # Above 60% - full processing
        }
        
        self.processing_configs = {
            ProcessingLevel.LOW: {
                'gps_interval': 300,        # 5 minutes
                'imu_batch_size': 50,       # Small batches
                'enable_ai_models': False,  # Rule-based only
                'max_concurrent_tasks': 1
            },
            ProcessingLevel.MEDIUM: {
                'gps_interval': 120,        # 2 minutes
                'imu_batch_size': 100,      # Medium batches
                'enable_ai_models': True,   # Limited AI
                'max_concurrent_tasks': 2
            },
            ProcessingLevel.HIGH: {
                'gps_interval': 30,         # 30 seconds
                'imu_batch_size': 200,      # Large batches
                'enable_ai_models': True,   # Full AI processing
                'max_concurrent_tasks': 4
            }
        }
    
    def get_processing_level(self, battery_level: float, 
                           is_charging: bool = False,
                           network_type: str = "wifi") -> ProcessingLevel:
        """
        Determine optimal processing level based on device conditions
        """
        try:
            # Override for charging devices
            if is_charging and battery_level > 20:
                return ProcessingLevel.HIGH
            
            # Battery-based decision
            if battery_level <= self.battery_thresholds['critical']:
                return ProcessingLevel.LOW
            elif battery_level <= self.battery_thresholds['low']:
                # Consider network type for low battery
                if network_type in ['wifi', '4g']:
                    return ProcessingLevel.MEDIUM
                else:
                    return ProcessingLevel.LOW
            elif battery_level <= self.battery_thresholds['medium']:
                return ProcessingLevel.MEDIUM
            else:
                return ProcessingLevel.HIGH
                
        except Exception as e:
            logger.error(f"Error determining processing level: {str(e)}")
            return ProcessingLevel.MEDIUM  # Safe default
    
    def get_config_for_level(self, level: ProcessingLevel) -> Dict:
        """Get processing configuration for given level"""
        return self.processing_configs.get(level, self.processing_configs[ProcessingLevel.MEDIUM])
    
    def optimize_sampling_rates(self, battery_level: float, 
                              is_charging: bool = False,
                              location_risk: str = "medium") -> Dict[str, int]:
        """
        Optimize sensor sampling rates based on conditions
        """
        level = self.get_processing_level(battery_level, is_charging)
        base_config = self.get_config_for_level(level)
        
        # Adjust based on location risk
        risk_multipliers = {
            "low": 0.5,      # Safe areas - reduce sampling
            "medium": 1.0,   # Normal areas - standard sampling  
            "high": 2.0,     # High-risk areas - increase sampling
            "critical": 3.0  # Critical areas - maximum sampling
        }
        
        multiplier = risk_multipliers.get(location_risk, 1.0)
        
        # Calculate optimized rates
        optimized_config = {
            'gps_interval': max(int(base_config['gps_interval'] / multiplier), 10),
            'imu_batch_size': min(int(base_config['imu_batch_size'] * multiplier), 500),
            'processing_level': level.value,
            'ai_enabled': base_config['enable_ai_models'],
            'max_tasks': base_config['max_concurrent_tasks']
        }
        
        return optimized_config
    
    def should_enable_feature(self, feature_name: str, 
                            battery_level: float,
                            is_charging: bool = False) -> bool:
        """
        Determine if a specific feature should be enabled based on battery
        """
        level = self.get_processing_level(battery_level, is_charging)
        
        feature_requirements = {
            'fall_detection': ProcessingLevel.MEDIUM,
            'crash_detection': ProcessingLevel.MEDIUM,
            'distress_detection': ProcessingLevel.HIGH,
            'behavioral_analysis': ProcessingLevel.HIGH,
            'continuous_monitoring': ProcessingLevel.MEDIUM,
            'advanced_analytics': ProcessingLevel.HIGH
        }
        
        required_level = feature_requirements.get(feature_name, ProcessingLevel.MEDIUM)
        
        # Check if current level meets requirement
        level_hierarchy = {
            ProcessingLevel.LOW: 1,
            ProcessingLevel.MEDIUM: 2,
            ProcessingLevel.HIGH: 3
        }
        
        return level_hierarchy[level] >= level_hierarchy[required_level]
    
    def calculate_estimated_battery_drain(self, processing_level: ProcessingLevel,
                                        duration_hours: float) -> float:
        """
        Estimate battery drain for given processing level and duration
        """
        # Battery drain rates per hour (percentage)
        drain_rates = {
            ProcessingLevel.LOW: 2.0,      # 2% per hour
            ProcessingLevel.MEDIUM: 5.0,   # 5% per hour
            ProcessingLevel.HIGH: 10.0     # 10% per hour
        }
        
        base_drain = drain_rates.get(processing_level, 5.0)
        return base_drain * duration_hours
    
    def get_power_saving_recommendations(self, battery_level: float,
                                       current_config: Dict) -> List[str]:
        """
        Get recommendations for power saving
        """
        recommendations = []
        
        if battery_level < 20:
            recommendations.extend([
                "Switch to emergency mode - GPS tracking only",
                "Disable continuous sensor monitoring",
                "Use rule-based detection instead of AI models",
                "Increase GPS reporting interval to 5 minutes"
            ])
        elif battery_level < 40:
            recommendations.extend([
                "Reduce AI processing frequency",
                "Batch sensor data uploads",
                "Switch to medium processing level"
            ])
        elif battery_level < 60:
            recommendations.extend([
                "Consider enabling power-saving mode",
                "Optimize network usage"
            ])
        
        return recommendations
    
    def adaptive_processing_schedule(self, user_patterns: Dict) -> Dict[str, any]:
        """
        Create adaptive processing schedule based on user patterns
        """
        schedule = {
            'high_activity_hours': [],      # Hours when user is typically active
            'low_activity_hours': [],       # Hours when user is typically inactive
            'travel_hours': [],             # Hours when user typically travels
            'processing_adjustments': {}
        }
        
        # Analyze user patterns (simplified)
        typical_active_hours = user_patterns.get('active_hours', list(range(6, 22)))
        typical_travel_hours = user_patterns.get('travel_hours', [7, 8, 17, 18, 19])
        
        schedule['high_activity_hours'] = typical_active_hours
        schedule['travel_hours'] = typical_travel_hours
        
        # Create processing adjustments
        for hour in range(24):
            if hour in typical_travel_hours:
                # Higher processing during travel hours
                schedule['processing_adjustments'][hour] = ProcessingLevel.HIGH
            elif hour in typical_active_hours:
                # Standard processing during active hours
                schedule['processing_adjustments'][hour] = ProcessingLevel.MEDIUM
            else:
                # Lower processing during inactive hours
                schedule['processing_adjustments'][hour] = ProcessingLevel.LOW
        
        return schedule
    
    def emergency_mode_config(self) -> Dict[str, any]:
        """
        Get configuration for emergency mode (critical battery)
        """
        return {
            'gps_interval': 600,           # 10 minutes
            'imu_processing': False,       # Disable IMU processing
            'ai_models': False,            # Disable all AI models
            'rule_based_only': True,       # Use only rule-based detection
            'network_optimization': True,  # Optimize network usage
            'background_sync': False,      # Disable background sync
            'alert_methods': ['sms'],      # SMS only for alerts
            'max_concurrent_operations': 1
        }
