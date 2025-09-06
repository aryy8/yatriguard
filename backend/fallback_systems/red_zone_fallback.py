"""
Enhanced Red Zone Fallback System with Crime Statistics
Integrates with existing red-zone-python.py logic and adds comprehensive risk analysis
"""

import asyncio
import logging
from typing import List, Dict, Tuple, Optional
import sys
import os
from datetime import datetime

# Add the backend directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the enhanced red zone system
try:
    from models.enhanced_red_zone import EnhancedRedZoneSystem
except ImportError:
    EnhancedRedZoneSystem = None

logger = logging.getLogger(__name__)

class RedZoneSystemFallback:
    """
    Enhanced fallback system using rule-based red zone detection with crime statistics
    Integrates with existing red-zone-python.py logic and enhanced risk assessment
    """
    
    def __init__(self):
        self.red_zones = []
        self.is_initialized = False
        # Initialize enhanced system if available
        self.enhanced_system = EnhancedRedZoneSystem() if EnhancedRedZoneSystem else None
        self.crime_aware = self.enhanced_system is not None
        
    async def initialize(self):
        """Initialize the enhanced fallback system with predefined zones and crime data"""
        try:
            # Initialize enhanced system first if available
            if self.enhanced_system:
                await self.enhanced_system.initialize()
                logger.info("Enhanced crime statistics system initialized")
            
            # Load red zones data (similar to original red-zone-python.py)
            self.red_zones = [
                {
                    'id': 1,
                    'name': 'Military Zone Alpha',
                    'type': 'Military',
                    'coordinates': [
                        {'lat': 26.9124, 'lng': 75.7873},
                        {'lat': 26.9150, 'lng': 75.7900},
                        {'lat': 26.9100, 'lng': 75.7950},
                        {'lat': 26.9080, 'lng': 75.7920}
                    ],
                    'risk_level': 5
                },
                {
                    'id': 2,
                    'name': 'Wildlife Sanctuary - Restricted Area',
                    'type': 'Wildlife',
                    'coordinates': [
                        {'lat': 26.9200, 'lng': 75.8000},
                        {'lat': 26.9250, 'lng': 75.8050},
                        {'lat': 26.9200, 'lng': 75.8100},
                        {'lat': 26.9150, 'lng': 75.8050}
                    ],
                    'risk_level': 3
                },
                {
                    'id': 3,
                    'name': 'Border Security Zone',
                    'type': 'Border',
                    'coordinates': [
                        {'lat': 28.0000, 'lng': 70.5000},
                        {'lat': 28.0200, 'lng': 70.5200},
                        {'lat': 28.0100, 'lng': 70.5400},
                        {'lat': 27.9900, 'lng': 70.5200}
                    ],
                    'risk_level': 4
                },
                {
                    'id': 4,
                    'name': 'Mining Area - Dangerous',
                    'type': 'Industrial',
                    'coordinates': [
                        {'lat': 25.5000, 'lng': 74.5000},
                        {'lat': 25.5100, 'lng': 74.5100},
                        {'lat': 25.5050, 'lng': 74.5200},
                        {'lat': 25.4950, 'lng': 74.5100}
                    ],
                    'risk_level': 3
                }
            ]
            
            self.is_initialized = True
            logger.info("Red zone fallback system initialized with {} zones".format(len(self.red_zones)))
            
        except Exception as e:
            logger.error(f"Failed to initialize red zone fallback: {str(e)}")
            raise
    
    def is_ready(self) -> bool:
        """Check if fallback system is ready"""
        return self.is_initialized
    
    def check_point_in_polygon(self, lat: float, lng: float) -> bool:
        """
        Check if point is inside any red zone polygon
        Uses the same algorithm as the original red-zone-python.py
        """
        try:
            for zone in self.red_zones:
                if self._point_in_polygon_ray_casting(lat, lng, zone['coordinates']):
                    logger.warning(f"RED ZONE BREACH DETECTED: {zone['name']} (Type: {zone['type']})")
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Error in point-in-polygon check: {str(e)}")
            return False
    
    def _point_in_polygon_ray_casting(self, lat: float, lng: float, 
                                    polygon: List[Dict[str, float]]) -> bool:
        """
        Ray casting algorithm for point-in-polygon test
        Same implementation as red-zone-python.py
        """
        x, y = lng, lat
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]['lng'], polygon[0]['lat']
        
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]['lng'], polygon[i % n]['lat']
            
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            
            p1x, p1y = p2x, p2y
        
        return inside
    
    def get_zone_info(self, lat: float, lng: float) -> Optional[Dict]:
        """Get information about the zone containing the point"""
        try:
            for zone in self.red_zones:
                if self._point_in_polygon_ray_casting(lat, lng, zone['coordinates']):
                    return {
                        'zone_id': zone['id'],
                        'zone_name': zone['name'],
                        'zone_type': zone['type'],
                        'risk_level': zone['risk_level'],
                        'breach_detected': True
                    }
            
            return {
                'zone_id': None,
                'zone_name': 'Safe Area',
                'zone_type': 'Safe',
                'risk_level': 0,
                'breach_detected': False
            }
            
        except Exception as e:
            logger.error(f"Error getting zone info: {str(e)}")
            return None
    
    def get_nearby_zones(self, lat: float, lng: float, radius_km: float = 5.0) -> List[Dict]:
        """Get zones within specified radius"""
        try:
            nearby_zones = []
            
            for zone in self.red_zones:
                # Calculate distance to zone center
                zone_center = self._calculate_polygon_center(zone['coordinates'])
                distance = self._calculate_distance(
                    lat, lng, zone_center['lat'], zone_center['lng']
                )
                
                if distance <= radius_km:
                    nearby_zones.append({
                        'zone_id': zone['id'],
                        'zone_name': zone['name'],
                        'zone_type': zone['type'],
                        'risk_level': zone['risk_level'],
                        'distance_km': distance,
                        'coordinates': zone['coordinates']
                    })
            
            # Sort by distance
            nearby_zones.sort(key=lambda x: x['distance_km'])
            return nearby_zones
            
        except Exception as e:
            logger.error(f"Error finding nearby zones: {str(e)}")
            return []
    
    def _calculate_polygon_center(self, polygon: List[Dict[str, float]]) -> Dict[str, float]:
        """Calculate centroid of polygon"""
        if not polygon:
            return {'lat': 0, 'lng': 0}
        
        lat_sum = sum(p['lat'] for p in polygon)
        lng_sum = sum(p['lng'] for p in polygon)
        
        return {
            'lat': lat_sum / len(polygon),
            'lng': lng_sum / len(polygon)
        }
    
    def _calculate_distance(self, lat1: float, lng1: float, 
                          lat2: float, lng2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        import math
        
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
        distance = R * c
        
        return distance
    
    def add_zone(self, zone_data: Dict) -> bool:
        """Add a new red zone"""
        try:
            new_zone = {
                'id': len(self.red_zones) + 1,
                'name': zone_data.get('name', 'New Zone'),
                'type': zone_data.get('type', 'Custom'),
                'coordinates': zone_data.get('coordinates', []),
                'risk_level': zone_data.get('risk_level', 3)
            }
            
            # Validate coordinates
            if len(new_zone['coordinates']) < 3:
                logger.error("Zone must have at least 3 coordinates")
                return False
            
            self.red_zones.append(new_zone)
            logger.info(f"Added new red zone: {new_zone['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding zone: {str(e)}")
            return False
    
    def remove_zone(self, zone_id: int) -> bool:
        """Remove a red zone"""
        try:
            self.red_zones = [zone for zone in self.red_zones if zone['id'] != zone_id]
            logger.info(f"Removed red zone with ID: {zone_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing zone: {str(e)}")
            return False
    
    def get_all_zones(self) -> List[Dict]:
        """Get all red zones"""
        return self.red_zones
    
    def validate_location(self, lat: float, lng: float) -> Dict[str, any]:
        """
        Comprehensive location validation
        Returns detailed information about location safety
        """
        try:
            result = {
                'coordinates': {'lat': lat, 'lng': lng},
                'is_safe': True,
                'risk_level': 0,
                'zone_info': None,
                'nearby_zones': [],
                'warnings': [],
                'recommendations': []
            }
            
            # Check for direct breach
            zone_info = self.get_zone_info(lat, lng)
            if zone_info and zone_info['breach_detected']:
                result['is_safe'] = False
                result['risk_level'] = zone_info['risk_level']
                result['zone_info'] = zone_info
                result['warnings'].append(f"You are in a restricted {zone_info['zone_type']} zone")
                result['recommendations'].append("Exit the area immediately and contact authorities")
            
            # Check nearby zones
            nearby_zones = self.get_nearby_zones(lat, lng, 2.0)  # 2km radius
            if nearby_zones:
                result['nearby_zones'] = nearby_zones
                
                closest_zone = nearby_zones[0]
                if closest_zone['distance_km'] < 1.0:  # Within 1km
                    result['warnings'].append(f"Warning: {closest_zone['zone_name']} is {closest_zone['distance_km']:.1f}km away")
                    result['recommendations'].append("Avoid moving towards the restricted area")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in location validation: {str(e)}")
            return {
                'coordinates': {'lat': lat, 'lng': lng},
                'is_safe': True,
                'risk_level': 0,
                'error': str(e)
            }
    
    async def check_location_with_crime_analysis(self, lat: float, lng: float) -> Dict[str, any]:
        """
        Enhanced location check with crime statistics and risk assessment
        Combines rule-based red zone detection with crime density analysis
        """
        try:
            # Start with basic fallback validation
            basic_result = self.validate_location(lat, lng)
            
            # If enhanced system is available, add crime analysis
            if self.enhanced_system and self.enhanced_system.is_ready():
                try:
                    crime_analysis = self.enhanced_system.calculate_area_risk_score(
                        lat, lng, datetime.utcnow()
                    )
                    
                    # Combine results
                    enhanced_result = {
                        **basic_result,
                        'enhanced_analysis': True,
                        'crime_risk_score': crime_analysis.get('overall_risk_score', 5.0),
                        'crime_risk_level': crime_analysis.get('risk_level', 'medium'),
                        'nearest_tourist_area': crime_analysis.get('nearest_area', {}),
                        'crime_breakdown': crime_analysis.get('risk_breakdown', {}),
                        'safety_recommendations': crime_analysis.get('recommendations', []),
                        'area_alerts': crime_analysis.get('alerts', [])
                    }
                    
                    # Update overall risk level considering both rule-based and crime data
                    rule_based_risk = basic_result.get('risk_level', 0)
                    crime_risk = crime_analysis.get('overall_risk_score', 5.0)
                    
                    # Weighted combination: rule-based zones have priority
                    if rule_based_risk > 0:  # In restricted zone
                        enhanced_result['combined_risk_level'] = max(rule_based_risk, crime_risk)
                        enhanced_result['is_safe'] = False
                    else:  # Safe from restricted zones, use crime risk
                        enhanced_result['combined_risk_level'] = crime_risk
                        enhanced_result['is_safe'] = crime_risk <= 4.0
                    
                    # Combine warnings and recommendations
                    all_warnings = basic_result.get('warnings', []) + crime_analysis.get('alerts', [])
                    all_recommendations = basic_result.get('recommendations', []) + crime_analysis.get('recommendations', [])
                    
                    enhanced_result['warnings'] = list(set(all_warnings))  # Remove duplicates
                    enhanced_result['recommendations'] = list(set(all_recommendations))[:8]  # Limit to 8
                    
                    return enhanced_result
                    
                except Exception as crime_error:
                    logger.warning(f"Crime analysis failed, using fallback: {str(crime_error)}")
                    # Return basic result with error note
                    return {
                        **basic_result,
                        'enhanced_analysis': False,
                        'crime_analysis_error': str(crime_error)
                    }
            else:
                # Enhanced system not available, return basic result
                return {
                    **basic_result,
                    'enhanced_analysis': False,
                    'note': 'Crime statistics not available, using rule-based detection only'
                }
                
        except Exception as e:
            logger.error(f"Error in enhanced location check: {str(e)}")
            return {
                'coordinates': {'lat': lat, 'lng': lng},
                'is_safe': True,
                'risk_level': 5,
                'error': str(e),
                'enhanced_analysis': False
            }
    
    async def get_tourist_area_crime_stats(self, area_name: str) -> Dict[str, any]:
        """Get crime statistics for a specific tourist area"""
        try:
            if not self.enhanced_system or not self.enhanced_system.is_ready():
                return {
                    'area_name': area_name,
                    'error': 'Enhanced crime statistics not available',
                    'fallback': True
                }
            
            return await self.enhanced_system.get_tourist_area_insights(area_name)
            
        except Exception as e:
            logger.error(f"Error getting tourist area stats: {str(e)}")
            return {
                'area_name': area_name,
                'error': str(e),
                'fallback': True
            }
    
    def get_system_status(self) -> Dict[str, any]:
        """Get status of both fallback and enhanced systems"""
        return {
            'fallback_system': {
                'initialized': self.is_initialized,
                'total_zones': len(self.red_zones),
                'system_type': 'rule_based'
            },
            'enhanced_system': {
                'available': self.enhanced_system is not None,
                'initialized': self.enhanced_system.is_ready() if self.enhanced_system else False,
                'crime_aware': self.crime_aware,
                'features': [
                    'crime_density_analysis',
                    'tourist_area_insights',
                    'time_based_risk_assessment',
                    'crowd_density_analysis'
                ] if self.crime_aware else []
            },
            'integration_status': 'full' if (self.is_initialized and self.crime_aware and 
                                           self.enhanced_system and self.enhanced_system.is_ready()) else 'basic'
        }
