"""
YatriGuard FastAPI Backend
AI/ML-based safety system for tourists with rule-based fallbacks
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
import asyncio
import json
import numpy as np
import logging
from datetime import datetime, timedelta
from enum import Enum
import uuid

from models.sensor_models import SensorData, LocationData, IMUData, AlertData
from models.detection_models import (
    FallDetectionModel, 
    CrashDetectionModel, 
    DistressDetectionModel,
    RedZoneDetector
)
from services.alert_service import AlertService
from services.data_processing import SensorDataProcessor
from utils.geo_utils import GeoUtils
from utils.battery_optimization import BatteryOptimizer
from fallback_systems.red_zone_fallback import RedZoneSystemFallback
from fallback_systems.rule_based_fallback import RuleBasedSystemFallback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YatriGuard AI Safety API",
    description="AI/ML-powered tourist safety system with rule-based fallbacks",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
alert_service = AlertService()
sensor_processor = SensorDataProcessor()
battery_optimizer = BatteryOptimizer()
geo_utils = GeoUtils()

# AI/ML Models
fall_detector = FallDetectionModel()
crash_detector = CrashDetectionModel()
distress_detector = DistressDetectionModel()
red_zone_detector = RedZoneDetector()

# Fallback systems
red_zone_fallback = RedZoneSystemFallback()
rule_based_fallback = RuleBasedSystemFallback()

# Active connections for real-time monitoring
active_connections: Dict[str, WebSocket] = {}
user_data: Dict[str, Dict] = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_data: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_data[user_id] = {
            'connected_at': datetime.utcnow(),
            'last_location': None,
            'trip_active': False,
            'safety_events': [],
            'battery_level': 100,
            'processing_mode': 'high',
            'last_sensor_data': None
        }
        logger.info(f"User {user_id} connected via WebSocket")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_data:
            del self.user_data[user_id]
        logger.info(f"User {user_id} disconnected")

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {user_id}: {str(e)}")
                self.disconnect(user_id)

manager = ConnectionManager()

class AlertType(str, Enum):
    FALL_DETECTED = "fall_detected"
    CRASH_DETECTED = "crash_detected"
    RED_ZONE_BREACH = "red_zone_breach"
    DISTRESS_DETECTED = "distress_detected"
    BATTERY_CRITICAL = "battery_critical"
    NETWORK_LOSS = "network_loss"

class AlertPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@app.on_event("startup")
async def startup_event():
    """Initialize AI models and load training data"""
    logger.info("Starting YatriGuard AI Safety System...")
    
    # Load and initialize AI models
    await fall_detector.initialize()
    await crash_detector.initialize()
    await distress_detector.initialize()
    await red_zone_detector.initialize()
    
    # Initialize fallback systems
    await red_zone_fallback.initialize()
    await rule_based_fallback.initialize()
    
    logger.info("All systems initialized successfully")

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """Enhanced WebSocket endpoint for real-time AI safety monitoring"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive data from client
            raw_data = await websocket.receive_text()
            message = json.loads(raw_data)
            
            message_type = message.get('type')
            payload = message.get('payload', {})
            
            if message_type == 'location_update':
                await handle_location_update(user_id, payload)
            elif message_type == 'sensor_data':
                await handle_sensor_data(user_id, payload)
            elif message_type == 'start_trip':
                await handle_start_trip(user_id)
            elif message_type == 'stop_trip':
                await handle_stop_trip(user_id)
            elif message_type == 'acknowledge_alert':
                await handle_acknowledge_alert(user_id, payload)
            elif message_type == 'connect':
                # Send initial status
                await send_trip_status(user_id)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
        manager.disconnect(user_id)

async def handle_location_update(user_id: str, location_data: dict):
    """Process location update and run AI safety analysis"""
    try:
        lat = location_data['latitude']
        lng = location_data['longitude']
        timestamp = datetime.fromisoformat(location_data['timestamp'].replace('Z', '+00:00'))
        
        # Update user location
        if user_id in manager.user_data:
            manager.user_data[user_id]['last_location'] = {
                'lat': lat,
                'lng': lng,
                'timestamp': timestamp.isoformat()
            }
        
        # Run AI safety analysis
        safety_analysis = await run_comprehensive_safety_analysis(
            lat, lng, timestamp, user_id
        )
        
        # Send analysis back to client
        await manager.send_personal_message({
            'type': 'safety_analysis',
            'payload': safety_analysis
        }, user_id)
        
        # Update trip status
        await send_trip_status(user_id)
        
    except Exception as e:
        logger.error(f"Error processing location update: {str(e)}")

async def handle_sensor_data(user_id: str, sensor_data: dict):
    """Process sensor data for AI/ML detection"""
    try:
        # Store sensor data
        if user_id in manager.user_data:
            manager.user_data[user_id]['last_sensor_data'] = {
                **sensor_data,
                'received_at': datetime.utcnow().isoformat()
            }
        
        # Create sensor data model
        processed_data = SensorData(
            accelerometer=IMUData(**sensor_data['accelerometer']),
            gyroscope=IMUData(**sensor_data['gyroscope']),
            magnetometer=IMUData(**sensor_data.get('magnetometer', {'x': 0, 'y': 0, 'z': 0})),
            timestamp=sensor_data['timestamp'],
            user_id=user_id
        )
        
        # Run fall detection
        fall_prob = await fall_detector.predict(processed_data.dict())
        if fall_prob > 0.7:  # High confidence fall
            await create_safety_event(user_id, 'fall', 'high', 'Potential fall detected')
        
        # Run crash detection  
        crash_prob = await crash_detector.predict(processed_data.dict())
        if crash_prob > 0.8:  # High confidence crash
            await create_safety_event(user_id, 'crash', 'critical', 'Potential crash detected')
        
        # Run distress detection
        distress_prob = await distress_detector.predict(processed_data.dict())
        if distress_prob > 0.6:  # Medium confidence distress
            await create_safety_event(user_id, 'distress', 'medium', 'Unusual behavior detected')
        
    except Exception as e:
        logger.error(f"Error processing sensor data: {str(e)}")

async def handle_start_trip(user_id: str):
    """Start trip monitoring for user"""
    if user_id in manager.user_data:
        manager.user_data[user_id]['trip_active'] = True
        manager.user_data[user_id]['trip_start'] = datetime.utcnow().isoformat()
        logger.info(f"Trip monitoring started for user {user_id}")
        await send_trip_status(user_id)

async def handle_stop_trip(user_id: str):
    """Stop trip monitoring for user"""
    if user_id in manager.user_data:
        manager.user_data[user_id]['trip_active'] = False
        manager.user_data[user_id]['trip_end'] = datetime.utcnow().isoformat()
        logger.info(f"Trip monitoring stopped for user {user_id}")
        await send_trip_status(user_id)

async def handle_acknowledge_alert(user_id: str, alert_data: dict):
    """Mark safety alert as acknowledged"""
    alert_id = alert_data.get('alert_id')
    if user_id in manager.user_data:
        events = manager.user_data[user_id]['safety_events']
        for event in events:
            if event['id'] == alert_id:
                event['acknowledged'] = True
                logger.info(f"Alert {alert_id} acknowledged by user {user_id}")
                break

async def run_comprehensive_safety_analysis(lat: float, lng: float, timestamp: datetime, user_id: str):
    """Run comprehensive AI safety analysis including crime statistics"""
    try:
        # Basic location data
        location_data = {
            'latitude': lat,
            'longitude': lng,
            'timestamp': timestamp
        }
        
        # Run red zone detection with enhanced crime statistics
        red_zone_analysis = await red_zone_detector.get_detailed_risk_analysis(location_data)
        
        # Use fallback system for additional analysis
        fallback_analysis = await red_zone_fallback.check_location_with_crime_analysis(lat, lng)
        
        # Combine results
        detection_results = {
            'fall_detection': {'is_fall': False, 'confidence': 0.0},
            'crash_detection': {'is_crash': False, 'confidence': 0.0},
            'red_zone_detection': {
                'is_red_zone': red_zone_analysis.get('overall_risk_score', 0) > 7.0,
                'confidence': 0.9,
                'crime_risk_score': red_zone_analysis.get('overall_risk_score', 0)
            },
            'distress_detection': {'is_distressed': False, 'confidence': 0.0}
        }
        
        # Enhanced analysis from crime statistics
        enhanced_analysis = None
        if fallback_analysis.get('enhanced_analysis'):
            enhanced_analysis = {
                'nearest_area': fallback_analysis.get('nearest_tourist_area'),
                'crime_breakdown': fallback_analysis.get('crime_breakdown'),
                'safety_recommendations': fallback_analysis.get('safety_recommendations', []),
                'area_alerts': fallback_analysis.get('area_alerts', [])
            }
        
        return {
            'overall_risk_score': red_zone_analysis.get('overall_risk_score', 5.0),
            'risk_level': red_zone_analysis.get('risk_level', 'medium'),
            'is_safe': red_zone_analysis.get('overall_risk_score', 5.0) <= 4.0,
            'location': {'lat': lat, 'lng': lng, 'timestamp': timestamp.isoformat()},
            'detection_results': detection_results,
            'enhanced_analysis': enhanced_analysis
        }
        
    except Exception as e:
        logger.error(f"Error in comprehensive safety analysis: {str(e)}")
        return {
            'overall_risk_score': 5.0,
            'risk_level': 'medium',
            'is_safe': True,
            'location': {'lat': lat, 'lng': lng, 'timestamp': timestamp.isoformat()},
            'error': str(e)
        }

async def send_trip_status(user_id: str):
    """Send current trip status to user"""
    if user_id not in manager.user_data:
        return
        
    user_info = manager.user_data[user_id]
    trip_status = {
        'trip_id': user_id,
        'is_active': user_info.get('trip_active', False),
        'current_location': user_info.get('last_location'),
        'safety_events': user_info.get('safety_events', []),
        'battery_level': user_info.get('battery_level', 100),
        'processing_mode': user_info.get('processing_mode', 'high'),
        'connection_status': 'connected'
    }
    
    await manager.send_personal_message({
        'type': 'trip_status',
        'payload': trip_status
    }, user_id)

async def create_safety_event(user_id: str, event_type: str, severity: str, message: str):
    """Create and broadcast safety event"""
    if user_id not in manager.user_data:
        return
    
    event = {
        'id': str(uuid.uuid4()),
        'type': event_type,
        'severity': severity,
        'message': message,
        'location': manager.user_data[user_id].get('last_location'),
        'timestamp': datetime.utcnow().isoformat(),
        'acknowledged': False
    }
    
    manager.user_data[user_id]['safety_events'].append(event)
    
    # Send alert to user
    await manager.send_personal_message({
        'type': 'safety_alert',
        'payload': event
    }, user_id)
    
    # Log critical events
    if severity in ['high', 'critical']:
        logger.warning(f"Safety event for user {user_id}: {event_type} - {message}")

@app.post("/api/sensor-data/{user_id}")
async def receive_sensor_data(user_id: str, sensor_data: SensorData, background_tasks: BackgroundTasks):
    """Receive and process sensor data from mobile app"""
    
    # Add to background processing queue
    background_tasks.add_task(process_sensor_data_pipeline, user_id, sensor_data)
    
    # Immediate response for app responsiveness
    return {
        "status": "received",
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "message": "Sensor data received and queued for processing"
    }

async def process_sensor_data_pipeline(user_id: str, sensor_data: SensorData):
    """Main AI/ML processing pipeline with fallback systems"""
    try:
        # Battery optimization - adjust processing based on battery level
        processing_level = battery_optimizer.get_processing_level(sensor_data.battery_level)
        
        # Process location data for red zone detection
        if sensor_data.location:
            await process_location_data(user_id, sensor_data.location, processing_level)
        
        # Process IMU data for fall and crash detection
        if sensor_data.imu_data:
            await process_imu_data(user_id, sensor_data.imu_data, processing_level)
        
        # Behavioral anomaly detection for distress
        await process_behavioral_data(user_id, sensor_data, processing_level)
        
    except Exception as e:
        logger.error(f"Error in sensor data pipeline for user {user_id}: {str(e)}")
        # Fallback to rule-based system
        await rule_based_fallback.process_data(user_id, sensor_data)

async def process_location_data(user_id: str, location: LocationData, processing_level: str):
    """Process GPS location data for geo-fence breach detection"""
    
    try:
        # Primary AI-based red zone detection
        if processing_level in ["high", "medium"]:
            breach_probability = await red_zone_detector.predict_breach(location)
            
            if breach_probability > 0.7:  # High confidence threshold
                alert = AlertData(
                    user_id=user_id,
                    alert_type=AlertType.RED_ZONE_BREACH,
                    priority=AlertPriority.CRITICAL,
                    location=location,
                    confidence=breach_probability,
                    message=f"High-risk area detected with {breach_probability:.2%} confidence"
                )
                await send_alert(alert)
                return
        
        # Fallback to rule-based system
        breach_detected = red_zone_fallback.check_point_in_polygon(
            location.latitude, location.longitude
        )
        
        if breach_detected:
            alert = AlertData(
                user_id=user_id,
                alert_type=AlertType.RED_ZONE_BREACH,
                priority=AlertPriority.HIGH,
                location=location,
                confidence=1.0,  # Rule-based is binary
                message="Restricted area detected - Rule-based system"
            )
            await send_alert(alert)
            
    except Exception as e:
        logger.error(f"Error in location processing: {str(e)}")

async def process_imu_data(user_id: str, imu_data: List[IMUData], processing_level: str):
    """Process IMU data for fall and crash detection"""
    
    try:
        if processing_level == "low":
            # Basic rule-based detection only
            await rule_based_imu_detection(user_id, imu_data)
            return
        
        # Prepare data for AI models
        processed_data = sensor_processor.process_imu_sequence(imu_data)
        
        # Fall Detection (LSTM-based)
        fall_probability = await fall_detector.predict_fall(processed_data)
        if fall_probability > 0.8:
            alert = AlertData(
                user_id=user_id,
                alert_type=AlertType.FALL_DETECTED,
                priority=AlertPriority.CRITICAL,
                confidence=fall_probability,
                message=f"Fall detected with {fall_probability:.2%} confidence"
            )
            await send_alert(alert)
            return
        
        # Crash Detection (requires GPS context)
        # This will be called if GPS shows vehicle speeds
        
    except Exception as e:
        logger.error(f"Error in IMU processing: {str(e)}")
        # Fallback to rule-based detection
        await rule_based_imu_detection(user_id, imu_data)

async def rule_based_imu_detection(user_id: str, imu_data: List[IMUData]):
    """Rule-based fallback for IMU detection"""
    
    # Simple threshold-based fall detection
    for data_point in imu_data[-10:]:  # Check last 10 readings
        total_acceleration = (
            data_point.acceleration_x**2 + 
            data_point.acceleration_y**2 + 
            data_point.acceleration_z**2
        )**0.5
        
        # Detect free fall (low G) followed by impact (high G)
        if total_acceleration < 2.0:  # Possible free fall
            # Check for impact in next readings
            continue
        elif total_acceleration > 15.0:  # High impact
            alert = AlertData(
                user_id=user_id,
                alert_type=AlertType.FALL_DETECTED,
                priority=AlertPriority.HIGH,
                confidence=0.7,  # Lower confidence for rule-based
                message="Possible fall detected - Rule-based system"
            )
            await send_alert(alert)
            break

async def process_behavioral_data(user_id: str, sensor_data: SensorData, processing_level: str):
    """Process behavioral patterns for distress detection"""
    
    try:
        if processing_level == "high":
            # AI-based anomaly detection
            distress_probability = await distress_detector.analyze_behavior(user_id, sensor_data)
            
            if distress_probability > 0.6:
                alert = AlertData(
                    user_id=user_id,
                    alert_type=AlertType.DISTRESS_DETECTED,
                    priority=AlertPriority.MEDIUM,
                    confidence=distress_probability,
                    message=f"Behavioral anomaly detected - possible distress ({distress_probability:.2%})"
                )
                await send_alert(alert)
        
    except Exception as e:
        logger.error(f"Error in behavioral analysis: {str(e)}")

async def send_alert(alert: AlertData):
    """Send alert to user and authorities"""
    
    # Store alert in database
    await alert_service.store_alert(alert)
    
    # Send real-time notification via WebSocket
    if alert.user_id in active_connections:
        try:
            await active_connections[alert.user_id].send_text(alert.json())
        except:
            pass
    
    # Send to authorities dashboard
    await alert_service.notify_authorities(alert)
    
    # SMS fallback for critical alerts
    if alert.priority == AlertPriority.CRITICAL:
        await alert_service.send_sms_alert(alert)
    
    logger.info(f"Alert sent: {alert.alert_type} for user {alert.user_id}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "ai_models": {
            "fall_detector": fall_detector.is_ready(),
            "crash_detector": crash_detector.is_ready(),
            "distress_detector": distress_detector.is_ready(),
            "red_zone_detector": red_zone_detector.is_ready()
        },
        "fallback_systems": {
            "red_zone_fallback": red_zone_fallback.is_ready(),
            "rule_based_fallback": rule_based_fallback.is_ready()
        }
    }

@app.get("/api/user/{user_id}/alerts")
async def get_user_alerts(user_id: str, limit: int = 50):
    """Get recent alerts for a user"""
    alerts = await alert_service.get_user_alerts(user_id, limit)
    return {"alerts": alerts}

@app.post("/api/user/{user_id}/panic")
async def trigger_panic_button(user_id: str, location: Optional[LocationData] = None):
    """Handle panic button press"""
    
    alert = AlertData(
        user_id=user_id,
        alert_type="panic_button",
        priority=AlertPriority.CRITICAL,
        location=location,
        confidence=1.0,
        message="PANIC BUTTON PRESSED - Immediate assistance required"
    )
    
    await send_alert(alert)
    
    return {
        "status": "panic_alert_sent",
        "message": "Emergency services have been notified"
    }

@app.get("/api/red-zones")
async def get_red_zones():
    """Get all defined red zones"""
    return await red_zone_detector.get_all_zones()

@app.post("/api/red-zones")
async def create_red_zone(zone_data: dict):
    """Create new red zone (admin only)"""
    zone = await red_zone_detector.create_zone(zone_data)
    return {"message": "Red zone created", "zone": zone}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
