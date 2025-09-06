"""
Alert Service - Handles alert creation, storage, and notification
"""

import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import uuid

logger = logging.getLogger(__name__)

class AlertService:
    """Service for managing alerts and notifications"""
    
    def __init__(self):
        self.alert_storage = []  # In-memory storage for demo
        self.authorities_endpoints = [
            "http://police-dashboard:8001/alerts",
            "http://emergency-services:8002/alerts"
        ]
        
    async def store_alert(self, alert_data) -> str:
        """Store alert in database"""
        try:
            alert_dict = {
                'id': str(uuid.uuid4()),
                'user_id': alert_data.user_id,
                'alert_type': alert_data.alert_type,
                'priority': alert_data.priority,
                'message': alert_data.message,
                'confidence': alert_data.confidence,
                'timestamp': alert_data.timestamp.isoformat(),
                'location': alert_data.location.dict() if alert_data.location else None,
                'acknowledged': False,
                'authorities_notified': False
            }
            
            self.alert_storage.append(alert_dict)
            
            logger.info(f"Alert stored: {alert_dict['id']} for user {alert_data.user_id}")
            return alert_dict['id']
            
        except Exception as e:
            logger.error(f"Failed to store alert: {str(e)}")
            raise
    
    async def get_user_alerts(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get recent alerts for a user"""
        try:
            user_alerts = [
                alert for alert in self.alert_storage 
                if alert['user_id'] == user_id
            ]
            
            # Sort by timestamp (most recent first)
            user_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return user_alerts[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get user alerts: {str(e)}")
            return []
    
    async def notify_authorities(self, alert_data):
        """Notify authorities about the alert"""
        try:
            notification_data = {
                'alert_id': getattr(alert_data, 'id', None),
                'user_id': alert_data.user_id,
                'alert_type': alert_data.alert_type,
                'priority': alert_data.priority,
                'message': alert_data.message,
                'location': alert_data.location.dict() if alert_data.location else None,
                'timestamp': alert_data.timestamp.isoformat(),
                'confidence': alert_data.confidence
            }
            
            # In a real implementation, this would send HTTP requests to authorities
            logger.info(f"Notifying authorities about alert: {alert_data.alert_type}")
            
            # Simulate different notification strategies based on priority
            if alert_data.priority == "critical":
                await self._send_immediate_notification(notification_data)
            elif alert_data.priority == "high":
                await self._send_priority_notification(notification_data)
            else:
                await self._send_standard_notification(notification_data)
                
        except Exception as e:
            logger.error(f"Failed to notify authorities: {str(e)}")
    
    async def _send_immediate_notification(self, data: Dict):
        """Send immediate notification for critical alerts"""
        # Multiple channels for critical alerts
        logger.critical(f"CRITICAL ALERT: {data['alert_type']} for user {data['user_id']}")
        # Would integrate with: SMS, Push notifications, Phone calls, Radio dispatch
    
    async def _send_priority_notification(self, data: Dict):
        """Send priority notification for high alerts"""
        logger.warning(f"HIGH PRIORITY ALERT: {data['alert_type']} for user {data['user_id']}")
        # Would integrate with: Push notifications, Dashboard alerts
    
    async def _send_standard_notification(self, data: Dict):
        """Send standard notification for medium/low alerts"""
        logger.info(f"ALERT: {data['alert_type']} for user {data['user_id']}")
        # Would integrate with: Dashboard notifications
    
    async def send_sms_alert(self, alert_data):
        """Send SMS alert as fallback communication"""
        try:
            # In a real implementation, integrate with SMS service (Twilio, AWS SNS, etc.)
            sms_message = self._format_sms_message(alert_data)
            
            # Simulate SMS sending
            logger.info(f"SMS ALERT sent for user {alert_data.user_id}: {sms_message}")
            
            # Update alert status
            await self._update_alert_status(alert_data.user_id, {
                'sms_sent': True,
                'sms_sent_at': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to send SMS alert: {str(e)}")
    
    def _format_sms_message(self, alert_data) -> str:
        """Format alert message for SMS"""
        location_text = ""
        if alert_data.location:
            location_text = f" at {alert_data.location.latitude:.4f},{alert_data.location.longitude:.4f}"
        
        message = f"YatriGuard ALERT: {alert_data.message}{location_text}. Time: {datetime.now().strftime('%H:%M')}"
        
        # SMS character limit
        return message[:160]
    
    async def _update_alert_status(self, user_id: str, status_update: Dict):
        """Update alert status"""
        for alert in self.alert_storage:
            if alert['user_id'] == user_id:
                alert.update(status_update)
                break
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Mark alert as acknowledged"""
        try:
            for alert in self.alert_storage:
                if alert['id'] == alert_id:
                    alert.update({
                        'acknowledged': True,
                        'acknowledged_by': acknowledged_by,
                        'acknowledged_at': datetime.utcnow().isoformat()
                    })
                    logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {str(e)}")
            return False
