"""
YatriGuard Frontend-Backend Integration Test
Tests WebSocket connection and AI/ML safety features
"""

import asyncio
import websockets
import json
import time
from datetime import datetime

async def test_yatriguard_integration():
    """Test the complete YatriGuard AI safety integration"""
    
    print("🧪 Testing YatriGuard AI Safety Integration")
    print("=" * 50)
    
    # WebSocket URL
    ws_url = "ws://localhost:8000/ws/test_user_123"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ Connected to YatriGuard WebSocket")
            
            # Send initial connection message
            await websocket.send(json.dumps({
                "type": "connect",
                "user_id": "test_user_123",
                "timestamp": datetime.utcnow().isoformat()
            }))
            
            # Test 1: Start trip monitoring
            print("\n📍 Test 1: Starting trip monitoring")
            await websocket.send(json.dumps({
                "type": "start_trip",
                "timestamp": datetime.utcnow().isoformat()
            }))
            
            # Test 2: Send location data (Jaipur - Pink City Market)
            print("\n🌍 Test 2: Sending location data (High crime area)")
            await websocket.send(json.dumps({
                "type": "location_update",
                "payload": {
                    "latitude": 26.9239,  # Jaipur Pink City Market
                    "longitude": 75.8267,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }))
            
            # Test 3: Send sensor data for AI detection
            print("\n📱 Test 3: Sending sensor data for AI analysis")
            await websocket.send(json.dumps({
                "type": "sensor_data",
                "payload": {
                    "accelerometer": {"x": 0.5, "y": -2.3, "z": 9.8},
                    "gyroscope": {"x": 0.1, "y": 0.2, "z": 0.05},
                    "magnetometer": {"x": 25.0, "y": -15.0, "z": 45.0},
                    "timestamp": datetime.utcnow().isoformat()
                }
            }))
            
            # Test 4: Test different location (Safer area)
            print("\n🏛️ Test 4: Testing safer location (City Palace)")
            await websocket.send(json.dumps({
                "type": "location_update",
                "payload": {
                    "latitude": 26.9255,  # City Palace (Safer)
                    "longitude": 75.8235,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }))
            
            # Listen for responses
            print("\n📨 Listening for responses...")
            timeout_count = 0
            max_timeouts = 10
            
            while timeout_count < max_timeouts:
                try:
                    # Wait for response with timeout
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    
                    message_type = data.get('type')
                    payload = data.get('payload', {})
                    
                    if message_type == 'safety_analysis':
                        print(f"\n🛡️ Safety Analysis Received:")
                        print(f"   Risk Score: {payload.get('overall_risk_score', 'N/A')}/10")
                        print(f"   Risk Level: {payload.get('risk_level', 'N/A').upper()}")
                        print(f"   Is Safe: {payload.get('is_safe', 'N/A')}")
                        
                        # Enhanced analysis
                        enhanced = payload.get('enhanced_analysis')
                        if enhanced:
                            nearest_area = enhanced.get('nearest_area', {})
                            if nearest_area:
                                print(f"   Nearest Area: {nearest_area.get('name', 'Unknown')}")
                                print(f"   Distance: {nearest_area.get('distance_km', 0):.1f}km")
                            
                            recommendations = enhanced.get('safety_recommendations', [])
                            if recommendations:
                                print(f"   Recommendations:")
                                for rec in recommendations[:3]:
                                    print(f"     • {rec}")
                    
                    elif message_type == 'trip_status':
                        print(f"\n🗺️ Trip Status Update:")
                        print(f"   Active: {payload.get('is_active', False)}")
                        print(f"   Battery: {payload.get('battery_level', 'N/A')}%")
                        print(f"   Processing Mode: {payload.get('processing_mode', 'N/A')}")
                        
                        location = payload.get('current_location')
                        if location:
                            print(f"   Location: {location.get('lat', 0):.4f}, {location.get('lng', 0):.4f}")
                    
                    elif message_type == 'safety_alert':
                        print(f"\n🚨 Safety Alert:")
                        print(f"   Type: {payload.get('type', 'Unknown').upper()}")
                        print(f"   Severity: {payload.get('severity', 'Unknown').upper()}")
                        print(f"   Message: {payload.get('message', 'No message')}")
                    
                    else:
                        print(f"\n📬 Received {message_type}: {json.dumps(payload, indent=2)}")
                    
                    timeout_count = 0  # Reset timeout count on successful receive
                    
                except asyncio.TimeoutError:
                    timeout_count += 1
                    if timeout_count == 1:
                        print("   ⏳ Waiting for more responses...")
                    elif timeout_count >= max_timeouts:
                        print("   ⏰ No more responses, ending test")
                        break
            
            # Test 5: Stop trip monitoring
            print("\n⏹️ Test 5: Stopping trip monitoring")
            await websocket.send(json.dumps({
                "type": "stop_trip",
                "timestamp": datetime.utcnow().isoformat()
            }))
            
            # Wait for final response
            try:
                final_response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                final_data = json.loads(final_response)
                if final_data.get('type') == 'trip_status':
                    print(f"   Trip Status: {'Active' if final_data.get('payload', {}).get('is_active') else 'Stopped'}")
            except asyncio.TimeoutError:
                pass
            
            print("\n✅ Integration test completed successfully!")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ Could not connect to WebSocket server")
        print("   Make sure the YatriGuard backend is running on http://localhost:8000")
        print("   Start with: cd backend && python main.py")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

def test_frontend_service():
    """Test the frontend service integration"""
    print("\n🌐 Frontend Service Integration Test")
    print("-" * 40)
    
    # Simulate how the React frontend would use the service
    frontend_usage = """
    // In React component:
    import { useYatriGuardWebSocket, SafetyUtils } from '@/services/aiSafetyService';
    
    function SafetyDashboard({ userId }) {
        const { 
            isConnected, 
            safetyAnalysis, 
            tripStatus 
        } = useYatriGuardWebSocket(userId);
        
        const safetyScore = SafetyUtils.calculateOverallSafetyScore(safetyAnalysis);
        const riskDisplay = SafetyUtils.getRiskLevelDisplay(safetyAnalysis?.risk_level);
        
        return (
            <div>
                <h2>Safety Score: {safetyScore}/100</h2>
                <p>Risk Level: {riskDisplay?.text}</p>
                <p>Connection: {isConnected ? 'Connected' : 'Disconnected'}</p>
            </div>
        );
    }
    """
    
    print("📝 Frontend Integration Code:")
    print(frontend_usage)
    
    print("\n📊 Expected Data Flow:")
    print("1. User opens YatriGuard dashboard")
    print("2. WebSocket connects to backend")
    print("3. Location data sent to AI/ML backend")
    print("4. Crime statistics analysis performed")
    print("5. Safety score calculated and displayed")
    print("6. Real-time updates sent via WebSocket")

if __name__ == "__main__":
    print("🚀 YatriGuard Frontend-Backend Integration Test")
    print("Make sure to start the backend first:")
    print("cd backend && python main.py")
    print("\nPress Enter to start WebSocket test...")
    input()
    
    # Run WebSocket integration test
    asyncio.run(test_yatriguard_integration())
    
    # Show frontend integration info
    test_frontend_service()
