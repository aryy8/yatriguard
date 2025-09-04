"""
Quick test to verify the YatriGuard backend is working
"""

import asyncio
import websockets
import json
import requests
from datetime import datetime

async def test_websocket_connection():
    """Test WebSocket connection to YatriGuard backend"""
    uri = "ws://localhost:8001/ws/test_user_123"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")
            
            # Test location update
            location_data = {
                "type": "location_update",
                "payload": {
                    "latitude": 26.9124,  # Jaipur coordinates
                    "longitude": 75.7873,
                    "timestamp": datetime.now().isoformat() + "Z",
                    "accuracy": 10.0
                }
            }
            
            await websocket.send(json.dumps(location_data))
            print("📍 Location data sent")
            
            # Test sensor data
            sensor_data = {
                "type": "sensor_data", 
                "payload": {
                    "accelerometer": {"x": 0.5, "y": -0.2, "z": 9.8},
                    "gyroscope": {"x": 0.1, "y": 0.0, "z": -0.05},
                    "timestamp": datetime.now().isoformat() + "Z"
                }
            }
            
            await websocket.send(json.dumps(sensor_data))
            print("📱 Sensor data sent")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                print(f"📨 Received response: {response_data.get('type', 'unknown')}")
                
                if response_data.get('type') == 'safety_update':
                    payload = response_data.get('payload', {})
                    print(f"🛡️ Safety Score: {payload.get('safety_score', 'N/A')}")
                    print(f"🔍 AI Status: {payload.get('ai_status', {})}")
                    print(f"🗺️ Red Zone Risk: {payload.get('red_zone_risk', 'N/A')}")
                
            except asyncio.TimeoutError:
                print("⏰ No response received within timeout")
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

def test_rest_endpoints():
    """Test REST API endpoints"""
    base_url = "http://localhost:8001"
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check endpoint working")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test safety analysis endpoint
    try:
        safety_data = {
            "location": {
                "latitude": 26.9124,
                "longitude": 75.7873
            },
            "sensor_data": {
                "accelerometer": {"x": 0.5, "y": -0.2, "z": 9.8},
                "gyroscope": {"x": 0.1, "y": 0.0, "z": -0.05}
            }
        }
        
        response = requests.post(f"{base_url}/api/safety-analysis/test_user", json=safety_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Safety analysis endpoint working")
            print(f"🛡️ Safety Score: {data.get('safety_score', 'N/A')}")
        else:
            print(f"❌ Safety analysis failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Safety analysis error: {e}")

async def main():
    """Run all tests"""
    print("🧪 Testing YatriGuard Backend Integration")
    print("=" * 50)
    
    # Test REST endpoints first
    print("\n1. Testing REST API Endpoints:")
    test_rest_endpoints()
    
    print("\n2. Testing WebSocket Connection:")
    await test_websocket_connection()
    
    print("\n✅ Integration test completed!")

if __name__ == "__main__":
    asyncio.run(main())
