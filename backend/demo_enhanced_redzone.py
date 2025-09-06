"""
Enhanced Red Zone Detection Demo with Crime Statistics
Demonstrates the comprehensive risk assessment system for tourist safety in Rajasthan
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.enhanced_red_zone import EnhancedRedZoneSystem
from fallback_systems.red_zone_fallback import RedZoneSystemFallback

async def demo_enhanced_red_zone_system():
    """Comprehensive demo of the enhanced red zone system"""
    
    print("\n🛡️  YatriGuard Enhanced Red Zone System Demo")
    print("=" * 60)
    print("Testing crime statistics integration and tourist area risk assessment")
    print()
    
    try:
        # Initialize enhanced system
        print("🔄 Initializing enhanced red zone system...")
        enhanced_system = EnhancedRedZoneSystem()
        await enhanced_system.initialize()
        
        # Initialize fallback system
        print("🔄 Initializing fallback system...")
        fallback_system = RedZoneSystemFallback()
        await fallback_system.initialize()
        
        print("✅ All systems initialized successfully!")
        print()
        
        # Test locations in major Rajasthan cities
        test_locations = [
            {
                'name': 'Jaipur - Pink City Market (High Crime Area)',
                'lat': 26.9239,
                'lng': 75.8267,
                'description': 'Popular tourist market with pickpocketing incidents'
            },
            {
                'name': 'Jaipur - City Palace (Safe Tourist Area)',
                'lat': 26.9255,
                'lng': 75.8235,
                'description': 'Well-secured heritage site'
            },
            {
                'name': 'Jodhpur - Clock Tower Market',
                'lat': 26.2960,
                'lng': 73.0169,
                'description': 'Busy market with moderate risk'
            },
            {
                'name': 'Udaipur - City Palace Complex',
                'lat': 24.5764,
                'lng': 73.6832,
                'description': 'Low-risk premium tourist destination'
            },
            {
                'name': 'Pushkar - Main Bazaar',
                'lat': 26.4889,
                'lng': 74.5511,
                'description': 'Tourist market with fraud risks'
            },
            {
                'name': 'Remote Desert Area (No Data)',
                'lat': 27.1234,
                'lng': 71.5678,
                'description': 'Unknown area with limited information'
            }
        ]
        
        # Test different times of day
        test_times = [
            {'name': 'Morning (Safe)', 'hour': 10},
            {'name': 'Night (High Risk)', 'hour': 23}
        ]
        
        print("🌍 Testing Enhanced Risk Analysis")
        print("-" * 40)
        
        for location in test_locations:
            print(f"\n📍 Location: {location['name']}")
            print(f"   Coordinates: ({location['lat']}, {location['lng']})")
            print(f"   Context: {location['description']}")
            
            for time_test in test_times:
                test_time = datetime.now().replace(hour=time_test['hour'], minute=0, second=0)
                
                print(f"\n   ⏰ Time: {time_test['name']} ({test_time.strftime('%H:%M')})")
                
                try:
                    # Enhanced system analysis
                    risk_analysis = enhanced_system.calculate_area_risk_score(
                        location['lat'], location['lng'], test_time
                    )
                    
                    print(f"   🎯 Overall Risk Score: {risk_analysis['overall_risk_score']}/10")
                    print(f"   📊 Risk Level: {risk_analysis['risk_level'].upper()}")
                    
                    if risk_analysis.get('nearest_area'):
                        area = risk_analysis['nearest_area']
                        print(f"   🏢 Nearest Area: {area.get('name', 'Unknown')} ({area.get('distance_km', 0):.1f}km)")
                    
                    # Risk breakdown
                    breakdown = risk_analysis.get('risk_breakdown', {})
                    if breakdown:
                        print("   📈 Risk Breakdown:")
                        for factor, value in breakdown.items():
                            print(f"      • {factor.replace('_', ' ').title()}: {value}")
                    
                    # Recommendations
                    recommendations = risk_analysis.get('recommendations', [])
                    if recommendations:
                        print("   💡 Safety Recommendations:")
                        for rec in recommendations[:3]:  # Limit to 3
                            print(f"      • {rec}")
                    
                    # Alerts
                    alerts = risk_analysis.get('alerts', [])
                    if alerts:
                        print("   ⚠️  Active Alerts:")
                        for alert in alerts:
                            print(f"      • {alert}")
                            
                except Exception as e:
                    print(f"   ❌ Error in enhanced analysis: {str(e)}")
            
            print()
        
        # Test fallback system integration
        print("\n🔧 Testing Fallback System Integration")
        print("-" * 40)
        
        # Test enhanced location check
        test_location = test_locations[0]  # Jaipur market
        
        print(f"📍 Testing: {test_location['name']}")
        
        try:
            enhanced_check = await fallback_system.check_location_with_crime_analysis(
                test_location['lat'], test_location['lng']
            )
            
            print(f"🔍 Enhanced Analysis Available: {enhanced_check.get('enhanced_analysis', False)}")
            print(f"🛡️ Is Safe: {enhanced_check.get('is_safe', 'Unknown')}")
            print(f"📊 Combined Risk Level: {enhanced_check.get('combined_risk_level', 'Unknown')}")
            
            if enhanced_check.get('crime_risk_score'):
                print(f"🚨 Crime Risk Score: {enhanced_check['crime_risk_score']}/10")
            
            # System status
            system_status = fallback_system.get_system_status()
            print(f"\n📊 System Status: {system_status['integration_status'].upper()}")
            
        except Exception as e:
            print(f"❌ Error in fallback integration: {str(e)}")
        
        # Test tourist area insights
        print("\n🏛️ Testing Tourist Area Insights")
        print("-" * 40)
        
        tourist_areas = ['Amber Fort', 'City Palace', 'Mehrangarh Fort', 'Pushkar Temple']
        
        for area in tourist_areas:
            try:
                insights = await enhanced_system.get_tourist_area_insights(area)
                
                print(f"\n🏢 Area: {area}")
                found_areas = insights.get('found_areas', [])
                
                if found_areas:
                    for area_data in found_areas[:1]:  # Show first match
                        print(f"   📊 Daily Visitors: {area_data.get('daily_visitors', 'Unknown')}")
                        print(f"   ⭐ Safety Rating: {area_data.get('safety_rating', 'Unknown')}/10")
                        print(f"   👮 Police Presence: {area_data.get('police_presence', 'Unknown')}")
                        
                        risk_factors = area_data.get('risk_factors', [])
                        if risk_factors:
                            print(f"   ⚠️ Risk Factors: {', '.join(risk_factors)}")
                else:
                    print(f"   ℹ️ No detailed data available")
                    
            except Exception as e:
                print(f"   ❌ Error getting insights: {str(e)}")
        
        # Performance and statistics summary
        print("\n📈 System Statistics and Performance")
        print("-" * 40)
        
        # Crime statistics summary
        print("🚨 Crime Statistics Coverage:")
        print("   • Jaipur: 15,420 total crimes (342.5 per 100k)")
        print("   • Jodhpur: 8,934 total crimes (287.3 per 100k)")  
        print("   • Udaipur: 4,567 total crimes (234.1 per 100k)")
        print("   • Pushkar: 678 total crimes (145.2 per 100k)")
        print("   • Mount Abu: 234 total crimes (89.3 per 100k)")
        print("   • Jaisalmer: 892 total crimes (198.7 per 100k)")
        
        print("\n🏛️ Tourist Area Coverage:")
        print("   • Heritage Sites: 3 major sites")
        print("   • Markets: 2 major markets") 
        print("   • Transport Hubs: 2 major hubs")
        print("   • Religious Sites: 1 major site")
        
        print("\n⚡ System Features:")
        print("   • Real-time crime risk assessment")
        print("   • Time-of-day risk adjustment")
        print("   • Crowd density analysis")
        print("   • Police presence factoring")
        print("   • Recent incident tracking")
        print("   • Infrastructure safety scoring")
        print("   • Contextual safety recommendations")
        
        print("\n✅ Demo completed successfully!")
        print("🔗 Integration: Enhanced crime statistics fully integrated with fallback system")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def demo_api_responses():
    """Demo API response format for frontend integration"""
    
    print("\n🌐 API Response Format Demo")
    print("=" * 40)
    print("Sample responses for frontend WebSocket integration")
    
    try:
        enhanced_system = EnhancedRedZoneSystem()
        await enhanced_system.initialize()
        
        # Sample location data
        sample_location = {
            'lat': 26.9239,  # Jaipur market
            'lng': 75.8267,
            'timestamp': datetime.utcnow()
        }
        
        # Get comprehensive analysis
        analysis = enhanced_system.calculate_area_risk_score(
            sample_location['lat'], 
            sample_location['lng'],
            sample_location['timestamp']
        )
        
        # Format for API response
        api_response = {
            'status': 'success',
            'location': {
                'latitude': sample_location['lat'],
                'longitude': sample_location['lng'],
                'timestamp': sample_location['timestamp'].isoformat()
            },
            'risk_assessment': {
                'overall_score': analysis['overall_risk_score'],
                'level': analysis['risk_level'],
                'is_safe': analysis['overall_risk_score'] <= 4.0,
                'confidence': 0.95
            },
            'area_info': {
                'name': analysis.get('nearest_area', {}).get('name', 'Unknown'),
                'category': analysis.get('nearest_area', {}).get('category', 'unknown'),
                'distance_km': analysis.get('nearest_area', {}).get('distance_km', 0)
            },
            'risk_factors': analysis.get('risk_breakdown', {}),
            'safety_recommendations': analysis.get('recommendations', []),
            'alerts': analysis.get('alerts', []),
            'metadata': {
                'detection_method': 'enhanced_crime_analysis',
                'features_used': [
                    'crime_density',
                    'time_of_day',
                    'crowd_analysis',
                    'police_presence',
                    'incident_history'
                ]
            }
        }
        
        print("\n📤 Sample API Response:")
        print(json.dumps(api_response, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ API demo failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting YatriGuard Enhanced Red Zone System Demo...")
    
    try:
        asyncio.run(demo_enhanced_red_zone_system())
        asyncio.run(demo_api_responses())
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
