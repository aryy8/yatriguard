"""
YatriGuard Configuration
Environment-based configuration for the AI safety system
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for YatriGuard backend"""
    
    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    RELOAD = os.getenv('RELOAD', 'true').lower() == 'true'
    
    # API Configuration
    API_VERSION = "1.0.0"
    API_TITLE = "YatriGuard AI Safety API"
    API_DESCRIPTION = "AI/ML-powered tourist safety system with rule-based fallbacks"
    
    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    
    # AI Model Configuration
    AI_MODELS_ENABLED = os.getenv('AI_MODELS_ENABLED', 'true').lower() == 'true'
    FALLBACK_ONLY = os.getenv('FALLBACK_ONLY', 'false').lower() == 'true'
    
    # Detection Thresholds
    FALL_DETECTION_THRESHOLD = float(os.getenv('FALL_DETECTION_THRESHOLD', '0.8'))
    CRASH_DETECTION_THRESHOLD = float(os.getenv('CRASH_DETECTION_THRESHOLD', '0.85'))
    DISTRESS_DETECTION_THRESHOLD = float(os.getenv('DISTRESS_DETECTION_THRESHOLD', '0.6'))
    
    # Battery Optimization
    BATTERY_OPTIMIZATION_ENABLED = True
    LOW_BATTERY_THRESHOLD = 30  # Percentage
    CRITICAL_BATTERY_THRESHOLD = 15  # Percentage
    
    # Data Processing
    MAX_DATA_BUFFER_SIZE = 1000
    DATA_RETENTION_HOURS = 24
    PROCESSING_BATCH_SIZE = 100
    
    # Alert Configuration
    ENABLE_SMS_ALERTS = os.getenv('ENABLE_SMS_ALERTS', 'false').lower() == 'true'
    ENABLE_EMAIL_ALERTS = os.getenv('ENABLE_EMAIL_ALERTS', 'false').lower() == 'true'
    ALERT_COOLDOWN_MINUTES = 5  # Prevent spam alerts
    
    # Geographic Configuration - Rajasthan Focus
    RAJASTHAN_BOUNDS = {
        'min_lat': 23.03,
        'max_lat': 30.12,
        'min_lng': 69.30,
        'max_lng': 78.17
    }
    
    # Red Zone Configuration
    RED_ZONE_BUFFER_KM = 0.1  # Buffer distance for red zones
    RED_ZONE_WARNING_KM = 0.5  # Warning distance
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'yatriguard.log')
    
    # Database Configuration (if using database)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./yatriguard.db')
    
    # External Services
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # WebSocket Configuration
    WEBSOCKET_HEARTBEAT_INTERVAL = 30  # seconds
    MAX_WEBSOCKET_CONNECTIONS = 1000
    
    @classmethod
    def get_detection_config(cls) -> Dict[str, Any]:
        """Get detection configuration"""
        return {
            'fall_threshold': cls.FALL_DETECTION_THRESHOLD,
            'crash_threshold': cls.CRASH_DETECTION_THRESHOLD,
            'distress_threshold': cls.DISTRESS_DETECTION_THRESHOLD,
            'ai_enabled': cls.AI_MODELS_ENABLED,
            'fallback_only': cls.FALLBACK_ONLY
        }
    
    @classmethod
    def get_battery_config(cls) -> Dict[str, Any]:
        """Get battery optimization configuration"""
        return {
            'optimization_enabled': cls.BATTERY_OPTIMIZATION_ENABLED,
            'low_battery_threshold': cls.LOW_BATTERY_THRESHOLD,
            'critical_battery_threshold': cls.CRITICAL_BATTERY_THRESHOLD
        }
    
    @classmethod
    def get_geographic_config(cls) -> Dict[str, Any]:
        """Get geographic configuration"""
        return {
            'rajasthan_bounds': cls.RAJASTHAN_BOUNDS,
            'red_zone_buffer_km': cls.RED_ZONE_BUFFER_KM,
            'red_zone_warning_km': cls.RED_ZONE_WARNING_KM
        }

# Development Configuration
class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    RELOAD = True
    AI_MODELS_ENABLED = False  # Use fallback systems for faster development
    FALLBACK_ONLY = True

# Production Configuration  
class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG = False
    RELOAD = False
    AI_MODELS_ENABLED = True
    FALLBACK_ONLY = False
    LOG_LEVEL = 'WARNING'

# Get configuration based on environment
def get_config():
    """Get configuration based on environment"""
    env = os.getenv('ENVIRONMENT', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()

# Global config instance
config = get_config()
