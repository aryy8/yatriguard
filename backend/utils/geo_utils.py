"""
Geographic Utility Functions
Handles geographic calculations and spatial operations
"""

import math
import logging
from typing import List, Tuple, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class GeoUtils:
    """Utility class for geographic operations"""
    
    def __init__(self):
        self.EARTH_RADIUS_KM = 6371.0
        self.METERS_PER_DEGREE = 111320.0  # Approximate meters per degree at equator
    
    def calculate_distance(self, lat1: float, lon1: float, 
                         lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        Returns distance in kilometers
        """
        try:
            # Convert to radians
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)
            
            # Haversine formula
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
            
            a = (math.sin(dlat/2)**2 + 
                 math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
            
            c = 2 * math.asin(math.sqrt(a))
            distance = self.EARTH_RADIUS_KM * c
            
            return distance
            
        except Exception as e:
            logger.error(f"Error calculating distance: {str(e)}")
            return 0.0
    
    def calculate_bearing(self, lat1: float, lon1: float,
                         lat2: float, lon2: float) -> float:
        """
        Calculate bearing from point 1 to point 2
        Returns bearing in degrees (0-360)
        """
        try:
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            dlon_rad = math.radians(lon2 - lon1)
            
            y = math.sin(dlon_rad) * math.cos(lat2_rad)
            x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
                 math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))
            
            bearing_rad = math.atan2(y, x)
            bearing_deg = math.degrees(bearing_rad)
            
            # Normalize to 0-360 degrees
            bearing_deg = (bearing_deg + 360) % 360
            
            return bearing_deg
            
        except Exception as e:
            logger.error(f"Error calculating bearing: {str(e)}")
            return 0.0
    
    def point_in_polygon(self, lat: float, lon: float, 
                        polygon: List[Dict[str, float]]) -> bool:
        """
        Determine if a point is inside a polygon using ray casting algorithm
        
        Args:
            lat, lon: Point coordinates
            polygon: List of polygon vertices [{'lat': float, 'lng': float}, ...]
        
        Returns:
            True if point is inside polygon
        """
        try:
            if len(polygon) < 3:
                return False
            
            x, y = lon, lat
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
            
        except Exception as e:
            logger.error(f"Error in point-in-polygon test: {str(e)}")
            return False
    
    def get_bounding_box(self, points: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Get bounding box for a list of points
        
        Returns:
            Dictionary with min_lat, max_lat, min_lng, max_lng
        """
        try:
            if not points:
                return {'min_lat': 0, 'max_lat': 0, 'min_lng': 0, 'max_lng': 0}
            
            lats = [p['lat'] for p in points]
            lngs = [p['lng'] for p in points]
            
            return {
                'min_lat': min(lats),
                'max_lat': max(lats),
                'min_lng': min(lngs),
                'max_lng': max(lngs)
            }
            
        except Exception as e:
            logger.error(f"Error calculating bounding box: {str(e)}")
            return {'min_lat': 0, 'max_lat': 0, 'min_lng': 0, 'max_lng': 0}
    
    def expand_bounding_box(self, bbox: Dict[str, float], 
                           expansion_km: float) -> Dict[str, float]:
        """
        Expand bounding box by specified distance in kilometers
        """
        try:
            # Convert km to degrees (approximate)
            lat_expansion = expansion_km / 111.32  # degrees latitude
            
            # Longitude expansion varies by latitude
            avg_lat = (bbox['min_lat'] + bbox['max_lat']) / 2
            lng_expansion = expansion_km / (111.32 * math.cos(math.radians(avg_lat)))
            
            return {
                'min_lat': bbox['min_lat'] - lat_expansion,
                'max_lat': bbox['max_lat'] + lat_expansion,
                'min_lng': bbox['min_lng'] - lng_expansion,
                'max_lng': bbox['max_lng'] + lng_expansion
            }
            
        except Exception as e:
            logger.error(f"Error expanding bounding box: {str(e)}")
            return bbox
    
    def calculate_polygon_area(self, polygon: List[Dict[str, float]]) -> float:
        """
        Calculate area of polygon in square kilometers
        Uses shoelace formula
        """
        try:
            if len(polygon) < 3:
                return 0.0
            
            # Convert to projected coordinates for better accuracy
            n = len(polygon)
            area = 0.0
            
            for i in range(n):
                j = (i + 1) % n
                area += polygon[i]['lng'] * polygon[j]['lat']
                area -= polygon[j]['lng'] * polygon[i]['lat']
            
            area = abs(area) / 2.0
            
            # Convert from degrees to square kilometers (approximate)
            area_km2 = area * (self.METERS_PER_DEGREE / 1000)**2
            
            return area_km2
            
        except Exception as e:
            logger.error(f"Error calculating polygon area: {str(e)}")
            return 0.0
    
    def get_polygon_center(self, polygon: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Calculate centroid of polygon
        """
        try:
            if not polygon:
                return {'lat': 0, 'lng': 0}
            
            lat_sum = sum(p['lat'] for p in polygon)
            lng_sum = sum(p['lng'] for p in polygon)
            
            return {
                'lat': lat_sum / len(polygon),
                'lng': lng_sum / len(polygon)
            }
            
        except Exception as e:
            logger.error(f"Error calculating polygon center: {str(e)}")
            return {'lat': 0, 'lng': 0}
    
    def is_within_radius(self, center_lat: float, center_lng: float,
                        point_lat: float, point_lng: float,
                        radius_km: float) -> bool:
        """
        Check if point is within specified radius from center
        """
        distance = self.calculate_distance(center_lat, center_lng, point_lat, point_lng)
        return distance <= radius_km
    
    def calculate_speed(self, lat1: float, lon1: float, time1: datetime,
                       lat2: float, lon2: float, time2: datetime) -> float:
        """
        Calculate speed between two points
        Returns speed in km/h
        """
        try:
            distance_km = self.calculate_distance(lat1, lon1, lat2, lon2)
            time_diff_seconds = (time2 - time1).total_seconds()
            
            if time_diff_seconds <= 0:
                return 0.0
            
            speed_kmh = (distance_km / time_diff_seconds) * 3600
            return speed_kmh
            
        except Exception as e:
            logger.error(f"Error calculating speed: {str(e)}")
            return 0.0
    
    def get_nearby_zones(self, lat: float, lng: float, 
                        zones: List[Dict], max_distance_km: float = 10.0) -> List[Dict]:
        """
        Get zones within specified distance from point
        """
        nearby_zones = []
        
        try:
            for zone in zones:
                # Calculate distance to zone center
                zone_center = self.get_polygon_center(zone.get('coordinates', []))
                
                if not zone_center or (zone_center['lat'] == 0 and zone_center['lng'] == 0):
                    continue
                
                distance = self.calculate_distance(
                    lat, lng, zone_center['lat'], zone_center['lng']
                )
                
                if distance <= max_distance_km:
                    zone_with_distance = zone.copy()
                    zone_with_distance['distance_km'] = distance
                    nearby_zones.append(zone_with_distance)
            
            # Sort by distance
            nearby_zones.sort(key=lambda x: x['distance_km'])
            
            return nearby_zones
            
        except Exception as e:
            logger.error(f"Error finding nearby zones: {str(e)}")
            return []
    
    def validate_coordinates(self, lat: float, lng: float) -> bool:
        """
        Validate geographic coordinates
        """
        try:
            return (-90 <= lat <= 90) and (-180 <= lng <= 180)
        except:
            return False
    
    def normalize_bearing(self, bearing: float) -> float:
        """
        Normalize bearing to 0-360 degrees
        """
        return bearing % 360
    
    def get_rajasthan_bounds(self) -> Dict[str, float]:
        """
        Get approximate bounding box for Rajasthan state
        """
        return {
            'min_lat': 23.03,    # Southern boundary
            'max_lat': 30.12,    # Northern boundary  
            'min_lng': 69.30,    # Western boundary
            'max_lng': 78.17     # Eastern boundary
        }
    
    def is_in_rajasthan(self, lat: float, lng: float) -> bool:
        """
        Quick check if coordinates are within Rajasthan
        """
        bounds = self.get_rajasthan_bounds()
        return (bounds['min_lat'] <= lat <= bounds['max_lat'] and
                bounds['min_lng'] <= lng <= bounds['max_lng'])
    
    def get_nearest_major_city(self, lat: float, lng: float) -> Dict[str, any]:
        """
        Get nearest major city in Rajasthan
        """
        major_cities = [
            {'name': 'Jaipur', 'lat': 26.9124, 'lng': 75.7873},
            {'name': 'Jodhpur', 'lat': 26.2389, 'lng': 73.0243},
            {'name': 'Udaipur', 'lat': 24.5854, 'lng': 73.7125},
            {'name': 'Kota', 'lat': 25.2138, 'lng': 75.8648},
            {'name': 'Ajmer', 'lat': 26.4499, 'lng': 74.6399},
            {'name': 'Bikaner', 'lat': 28.0229, 'lng': 73.3119},
            {'name': 'Pushkar', 'lat': 26.4900, 'lng': 74.5500},
            {'name': 'Mount Abu', 'lat': 24.5925, 'lng': 72.7156}
        ]
        
        nearest_city = None
        min_distance = float('inf')
        
        for city in major_cities:
            distance = self.calculate_distance(lat, lng, city['lat'], city['lng'])
            if distance < min_distance:
                min_distance = distance
                nearest_city = city.copy()
                nearest_city['distance_km'] = distance
        
        return nearest_city or {'name': 'Unknown', 'distance_km': 0}
