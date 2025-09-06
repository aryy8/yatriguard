"""
YatriGuard API Demo Client
Demonstrates the AI/ML safety features
"""

import asyncio
import json
import time
import random
from datetime import datetime, timedelta
import websockets
import requests
from typing import Dict, List

class YatriGuardDemoClient:
    """Demo client for testing YatriGuard API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.ws_url = base_url.replace("http", "ws")
        self.user_id = f"demo_user_{int(time.time())}"
        
    async def demo_red_zone_detection(self):
        """Demonstrate red zone detection"""
        print("\n🛡️  RED ZONE DETECTION DEMO")
        print("=" * 50)
        
        # Test locations - some safe, some in red zones
        test_locations = [
            {"lat": 26.9000, "lng": 75.7800, "name": "Safe Area - Market"},
            {"lat": 26.9124, "lng": 75.7873, "name": "DANGER - Military Zone"},
            {"lat": 26.9200, "lng": 75.8000, "name": "RESTRICTED - Wildlife Area"},
            {"lat": 26.9300, "lng": 75.8100, "name": "Safe Area - Hotel District"},
        ]
        
        for location in test_locations:
            sensor_data = self._create_sensor_data(location=location)
            
            print(f"\n📍 Testing location: {location['name']}")
            print(f"   Coordinates: {location['lat']:.4f}, {location['lng']:.4f}")
            
            try:
                response = requests.post(
                    f"{self.api_url}/sensor-data/{self.user_id}",
                    json=sensor_data
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Data sent successfully")
                else:
                    print(f"   ❌ Error: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
            
            # Wait a bit between tests
            await asyncio.sleep(2)
    
    async def demo_fall_detection(self):
        """Demonstrate fall detection"""
        print("\n🤸 FALL DETECTION DEMO")
        print("=" * 50)
        
        # Simulate normal walking
        print("\n📱 Simulating normal walking...")
        normal_imu = self._generate_normal_walking_imu()
        sensor_data = self._create_sensor_data(imu_data=normal_imu)
        await self._send_sensor_data(sensor_data)
        
        await asyncio.sleep(2)
        
        # Simulate a fall
        print("\n💥 Simulating a fall event...")
        fall_imu = self._generate_fall_imu()
        sensor_data = self._create_sensor_data(imu_data=fall_imu)
        await self._send_sensor_data(sensor_data)
        
        await asyncio.sleep(2)
    
    async def demo_crash_detection(self):
        """Demonstrate crash detection"""
        print("\n🚗 CRASH DETECTION DEMO")
        print("=" * 50)
        
        # Simulate driving at high speed
        print("\n🏎️  Simulating vehicle driving at 80 km/h...")
        driving_data = self._create_sensor_data(
            location={"lat": 26.9000, "lng": 75.7800, "speed": 80.0},
            imu_data=self._generate_driving_imu()
        )
        await self._send_sensor_data(driving_data)
        
        await asyncio.sleep(1)
        
        # Simulate crash
        print("\n💥 Simulating vehicle crash...")
        crash_data = self._create_sensor_data(
            location={"lat": 26.9001, "lng": 75.7801, "speed": 0.0},
            imu_data=self._generate_crash_imu()
        )
        await self._send_sensor_data(crash_data)
        
        await asyncio.sleep(2)
    
    async def demo_distress_detection(self):
        """Demonstrate distress detection"""
        print("\n😟 DISTRESS DETECTION DEMO")
        print("=" * 50)
        
        # Simulate staying in one place for too long
        print("\n⏰ Simulating prolonged inactivity...")
        
        same_location = {"lat": 26.8500, "lng": 75.7000}  # Remote location
        
        for i in range(5):
            sensor_data = self._create_sensor_data(
                location=same_location,
                battery_level=max(20, 50 - i * 5)  # Declining battery
            )
            await self._send_sensor_data(sensor_data)
            await asyncio.sleep(1)
        
        print("   📊 Behavioral pattern analysis in progress...")
    
    async def demo_websocket_monitoring(self):
        """Demonstrate real-time WebSocket monitoring"""
        print("\n🔗 WEBSOCKET REAL-TIME MONITORING DEMO")
        print("=" * 50)
        
        ws_uri = f"{self.ws_url}/ws/{self.user_id}"
        
        try:
            async with websockets.connect(ws_uri) as websocket:
                print(f"   ✅ Connected to WebSocket: {ws_uri}")
                
                # Send some test data
                test_data = self._create_sensor_data(
                    location={"lat": 26.9124, "lng": 75.7873},  # Military zone
                    imu_data=self._generate_fall_imu()
                )
                
                await websocket.send(json.dumps(test_data))
                print("   📤 Sent sensor data via WebSocket")
                
                # Listen for alerts
                print("   👂 Listening for real-time alerts...")
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    alert = json.loads(response)
                    print(f"   🚨 ALERT RECEIVED: {alert.get('alert_type', 'Unknown')}")
                    print(f"      Message: {alert.get('message', 'No message')}")
                except asyncio.TimeoutError:
                    print("   ⏰ No alerts received within timeout period")
                    
        except Exception as e:
            print(f"   ❌ WebSocket error: {str(e)}")
    
    async def demo_panic_button(self):
        """Demonstrate panic button functionality"""
        print("\n🆘 PANIC BUTTON DEMO")
        print("=" * 50)
        
        location = {"lat": 26.9500, "lng": 75.8200}
        
        try:
            response = requests.post(
                f"{self.api_url}/user/{self.user_id}/panic",
                json={
                    "location": {
                        "latitude": location["lat"],
                        "longitude": location["lng"],
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   🚨 PANIC ALERT SENT!")
                print(f"   📧 {result.get('message', 'Emergency services notified')}")
            else:
                print(f"   ❌ Error sending panic alert: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    async def check_system_health(self):
        """Check system health and status"""
        print("\n💊 SYSTEM HEALTH CHECK")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.api_url}/health")
            
            if response.status_code == 200:
                health = response.json()
                print(f"   ✅ System Status: {health.get('status', 'Unknown')}")
                
                ai_models = health.get('ai_models', {})
                print("\n   🤖 AI Models Status:")
                for model, status in ai_models.items():
                    status_icon = "✅" if status else "❌"
                    print(f"      {status_icon} {model}: {'Ready' if status else 'Not Ready'}")
                
                fallback_systems = health.get('fallback_systems', {})
                print("\n   🛡️  Fallback Systems Status:")
                for system, status in fallback_systems.items():
                    status_icon = "✅" if status else "❌"
                    print(f"      {status_icon} {system}: {'Ready' if status else 'Not Ready'}")
                    
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    async def view_user_alerts(self):
        """View user's alert history"""
        print(f"\n📋 USER ALERTS HISTORY ({self.user_id})")
        print("=" * 70)
        
        try:
            response = requests.get(f"{self.api_url}/user/{self.user_id}/alerts")
            
            if response.status_code == 200:
                data = response.json()
                alerts = data.get('alerts', [])
                
                if alerts:
                    for alert in alerts[:5]:  # Show last 5 alerts
                        print(f"   🚨 {alert.get('alert_type', 'Unknown')} - {alert.get('priority', 'medium').upper()}")
                        print(f"      📝 {alert.get('message', 'No message')}")
                        print(f"      🕐 {alert.get('timestamp', 'Unknown time')}")
                        print()
                else:
                    print("   📭 No alerts found for this user")
                    
            else:
                print(f"   ❌ Error fetching alerts: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    async def _send_sensor_data(self, sensor_data: Dict):
        """Send sensor data to API"""
        try:
            response = requests.post(
                f"{self.api_url}/sensor-data/{self.user_id}",
                json=sensor_data
            )
            
            if response.status_code == 200:
                print("   ✅ Sensor data processed")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    def _create_sensor_data(self, location: Dict = None, imu_data: List = None, battery_level: float = 75.0) -> Dict:
        """Create sensor data payload"""
        data = {
            "user_id": self.user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "battery_level": battery_level
        }
        
        if location:
            data["location"] = {
                "latitude": location["lat"],
                "longitude": location["lng"],
                "speed": location.get("speed", 0.0),
                "accuracy": 5.0,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        if imu_data:
            data["imu_data"] = imu_data
        
        return data
    
    def _generate_normal_walking_imu(self) -> List[Dict]:
        """Generate normal walking IMU data"""
        imu_data = []
        base_time = datetime.utcnow()
        
        for i in range(50):
            imu_data.append({
                "acceleration_x": random.uniform(-2, 2),
                "acceleration_y": random.uniform(-2, 2),
                "acceleration_z": random.uniform(8, 12),  # Normal gravity + movement
                "gyroscope_x": random.uniform(-0.5, 0.5),
                "gyroscope_y": random.uniform(-0.5, 0.5),
                "gyroscope_z": random.uniform(-0.5, 0.5),
                "timestamp": (base_time + timedelta(milliseconds=i*20)).isoformat()
            })
        
        return imu_data
    
    def _generate_fall_imu(self) -> List[Dict]:
        """Generate fall pattern IMU data"""
        imu_data = []
        base_time = datetime.utcnow()
        
        # Phase 1: Freefall (low G)
        for i in range(10):
            imu_data.append({
                "acceleration_x": random.uniform(-0.5, 0.5),
                "acceleration_y": random.uniform(-0.5, 0.5),
                "acceleration_z": random.uniform(-1, 1),  # Near zero G
                "gyroscope_x": random.uniform(-2, 2),
                "gyroscope_y": random.uniform(-2, 2),
                "gyroscope_z": random.uniform(-2, 2),
                "timestamp": (base_time + timedelta(milliseconds=i*20)).isoformat()
            })
        
        # Phase 2: Impact (high G)
        for i in range(10, 15):
            imu_data.append({
                "acceleration_x": random.uniform(-25, 25),
                "acceleration_y": random.uniform(-25, 25),
                "acceleration_z": random.uniform(15, 30),  # High impact
                "gyroscope_x": random.uniform(-10, 10),
                "gyroscope_y": random.uniform(-10, 10),
                "gyroscope_z": random.uniform(-10, 10),
                "timestamp": (base_time + timedelta(milliseconds=i*20)).isoformat()
            })
        
        # Phase 3: Stillness (low movement)
        for i in range(15, 30):
            imu_data.append({
                "acceleration_x": random.uniform(-0.2, 0.2),
                "acceleration_y": random.uniform(-0.2, 0.2),
                "acceleration_z": random.uniform(9.5, 10.5),  # Resting on ground
                "gyroscope_x": random.uniform(-0.1, 0.1),
                "gyroscope_y": random.uniform(-0.1, 0.1),
                "gyroscope_z": random.uniform(-0.1, 0.1),
                "timestamp": (base_time + timedelta(milliseconds=i*20)).isoformat()
            })
        
        return imu_data
    
    def _generate_driving_imu(self) -> List[Dict]:
        """Generate normal driving IMU data"""
        imu_data = []
        base_time = datetime.utcnow()
        
        for i in range(30):
            imu_data.append({
                "acceleration_x": random.uniform(-1, 1),
                "acceleration_y": random.uniform(-1, 1),
                "acceleration_z": random.uniform(9, 11),  # Mostly gravity
                "gyroscope_x": random.uniform(-0.3, 0.3),
                "gyroscope_y": random.uniform(-0.3, 0.3),
                "gyroscope_z": random.uniform(-0.3, 0.3),
                "timestamp": (base_time + timedelta(milliseconds=i*20)).isoformat()
            })
        
        return imu_data
    
    def _generate_crash_imu(self) -> List[Dict]:
        """Generate crash impact IMU data"""
        imu_data = []
        base_time = datetime.utcnow()
        
        for i in range(20):
            if i < 5:  # Normal driving
                imu_data.append({
                    "acceleration_x": random.uniform(-1, 1),
                    "acceleration_y": random.uniform(-1, 1),
                    "acceleration_z": random.uniform(9, 11),
                    "gyroscope_x": random.uniform(-0.3, 0.3),
                    "gyroscope_y": random.uniform(-0.3, 0.3),
                    "gyroscope_z": random.uniform(-0.3, 0.3),
                    "timestamp": (base_time + timedelta(milliseconds=i*20)).isoformat()
                })
            else:  # Crash impact
                imu_data.append({
                    "acceleration_x": random.uniform(-30, 30),
                    "acceleration_y": random.uniform(-30, 30),
                    "acceleration_z": random.uniform(20, 40),  # Extreme G-force
                    "gyroscope_x": random.uniform(-15, 15),
                    "gyroscope_y": random.uniform(-15, 15),
                    "gyroscope_z": random.uniform(-15, 15),
                    "timestamp": (base_time + timedelta(milliseconds=i*20)).isoformat()
                })
        
        return imu_data

async def main():
    """Run the demo"""
    print("🚀 YatriGuard AI Safety System Demo")
    print("=" * 60)
    print("This demo showcases the AI/ML safety features")
    print("with rule-based fallback systems for tourists.")
    print("=" * 60)
    
    client = YatriGuardDemoClient()
    
    try:
        # Check if server is running
        await client.check_system_health()
        
        # Run all demos
        await client.demo_red_zone_detection()
        await client.demo_fall_detection()
        await client.demo_crash_detection()
        await client.demo_distress_detection()
        await client.demo_panic_button()
        
        # Try WebSocket demo (may fail if WebSocket not available)
        try:
            await client.demo_websocket_monitoring()
        except:
            print("   ⚠️  WebSocket demo skipped (connection not available)")
        
        # View alerts generated
        await asyncio.sleep(2)  # Wait for processing
        await client.view_user_alerts()
        
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("Check the server logs for detailed AI processing information.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        print("Make sure the YatriGuard server is running on http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(main())
