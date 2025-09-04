/**
 * Enhanced Safety Dashboard Component
 * Real-time AI/ML safety monitoring with crime statistics integration
 */

import React, { useEffect, useState } from 'react';
import { Shield, AlertTriangle, TrendingUp, MapPin, Clock, Zap, Wifi, WifiOff } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  useYatriGuardWebSocket, 
  SafetyUtils, 
  useDeviceSensors,
  type SafetyAnalysis,
  type TripStatus,
  type SafetyEvent
} from '@/services/aiSafetyService';

interface SafetyDashboardProps {
  userId: string;
  currentLocation?: {
    lat: number;
    lng: number;
  };
}

export default function SafetyDashboard({ userId, currentLocation }: SafetyDashboardProps) {
  const {
    isConnected,
    safetyAnalysis,
    tripStatus,
    connectionError,
    sendLocationUpdate,
    sendSensorData,
    toggleTripMonitoring,
    acknowledgeSafetyAlert,
    reconnect
  } = useYatriGuardWebSocket(userId);

  const { sensorData, isSupported: sensorSupported, permissionGranted } = useDeviceSensors();
  const [isTripActive, setIsTripActive] = useState(false);

  // Send location updates when available
  useEffect(() => {
    if (currentLocation && isConnected) {
      sendLocationUpdate(currentLocation.lat, currentLocation.lng);
    }
  }, [currentLocation, isConnected, sendLocationUpdate]);

  // Send sensor data for AI/ML processing
  useEffect(() => {
    if (sensorData.accelerometer && sensorData.gyroscope && isConnected) {
      sendSensorData({
        accelerometer: sensorData.accelerometer,
        gyroscope: sensorData.gyroscope,
        magnetometer: sensorData.magnetometer || { x: 0, y: 0, z: 0 }
      });
    }
  }, [sensorData, isConnected, sendSensorData]);

  // Calculate overall safety score
  const safetyScore = safetyAnalysis ? SafetyUtils.calculateOverallSafetyScore(safetyAnalysis) : 50;
  const riskDisplay = safetyAnalysis ? SafetyUtils.getRiskLevelDisplay(safetyAnalysis.risk_level) : null;

  const handleToggleTrip = () => {
    const newState = !isTripActive;
    setIsTripActive(newState);
    toggleTripMonitoring(newState);
  };

  const handleAcknowledgeAlert = (alertId: string) => {
    acknowledgeSafetyAlert(alertId);
  };

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      {connectionError && (
        <Alert className="border-orange-200 bg-orange-50">
          <WifiOff className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <span>{connectionError}</span>
            <Button variant="outline" size="sm" onClick={reconnect}>
              Reconnect
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Real-time Safety Score */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <TrendingUp className={`w-5 h-5 ${SafetyUtils.getScoreColor(safetyScore)}`} />
              <span>AI Safety Score</span>
            </div>
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <Badge variant="default" className="bg-green-100 text-green-800">
                  <Wifi className="w-3 h-3 mr-1" />
                  Live
                </Badge>
              ) : (
                <Badge variant="secondary">
                  <WifiOff className="w-3 h-3 mr-1" />
                  Offline
                </Badge>
              )}
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Safety Score Display */}
            <div className="text-center">
              <div className={`text-4xl font-bold ${SafetyUtils.getScoreColor(safetyScore)}`}>
                {Math.round(safetyScore)}
              </div>
              <div className="text-sm text-muted-foreground">Safety Score (0-100)</div>
              {riskDisplay && (
                <Badge variant={SafetyUtils.getScoreBadgeVariant(safetyScore)} className="mt-2">
                  {riskDisplay.text}
                </Badge>
              )}
            </div>

            {/* Safety Score Progress */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Risk Level</span>
                <span className={riskDisplay?.color || 'text-gray-600'}>
                  {safetyAnalysis?.risk_level.replace('_', ' ').toUpperCase() || 'Unknown'}
                </span>
              </div>
              <Progress value={safetyScore} className="h-2" />
            </div>

            {/* AI Detection Status */}
            {safetyAnalysis && (
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center justify-between">
                  <span>Fall Detection</span>
                  <Badge 
                    variant={safetyAnalysis.detection_results.fall_detection.is_fall ? 'destructive' : 'default'}
                    className="text-xs"
                  >
                    {safetyAnalysis.detection_results.fall_detection.is_fall ? 'Alert' : 'Normal'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Crash Detection</span>
                  <Badge 
                    variant={safetyAnalysis.detection_results.crash_detection.is_crash ? 'destructive' : 'default'}
                    className="text-xs"
                  >
                    {safetyAnalysis.detection_results.crash_detection.is_crash ? 'Alert' : 'Normal'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Red Zone</span>
                  <Badge 
                    variant={safetyAnalysis.detection_results.red_zone_detection.is_red_zone ? 'destructive' : 'default'}
                    className="text-xs"
                  >
                    {safetyAnalysis.detection_results.red_zone_detection.is_red_zone ? 'Breach' : 'Safe'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Distress</span>
                  <Badge 
                    variant={safetyAnalysis.detection_results.distress_detection.is_distressed ? 'destructive' : 'default'}
                    className="text-xs"
                  >
                    {safetyAnalysis.detection_results.distress_detection.is_distressed ? 'Detected' : 'Normal'}
                  </Badge>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Trip Status & Monitoring */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MapPin className="w-5 h-5 text-blue-600" />
              <span>Trip Monitoring</span>
            </div>
            <Button
              onClick={handleToggleTrip}
              variant={isTripActive ? "destructive" : "default"}
              size="sm"
            >
              {isTripActive ? 'Stop Trip' : 'Start Trip'}
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {tripStatus && (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Trip Status</span>
                  <Badge variant={tripStatus.is_active ? 'default' : 'secondary'}>
                    {tripStatus.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Battery Level</span>
                    <div className="flex items-center space-x-2 mt-1">
                      <Zap className="w-4 h-4" />
                      <Progress value={tripStatus.battery_level} className="flex-1 h-2" />
                      <span>{tripStatus.battery_level}%</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Processing Mode</span>
                    <div className="mt-1">
                      <Badge variant="outline" className="capitalize">
                        {tripStatus.processing_mode}
                      </Badge>
                    </div>
                  </div>
                </div>

                {tripStatus.current_location && (
                  <div className="text-sm">
                    <span className="text-muted-foreground">Current Location</span>
                    <div className="font-mono text-xs mt-1">
                      {tripStatus.current_location.lat.toFixed(6)}, {tripStatus.current_location.lng.toFixed(6)}
                    </div>
                    <div className="text-muted-foreground text-xs">
                      Last updated: {new Date(tripStatus.current_location.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                )}
              </>
            )}

            {!tripStatus && isTripActive && (
              <div className="text-center text-muted-foreground">
                <Clock className="w-8 h-8 mx-auto mb-2" />
                <p>Initializing trip monitoring...</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Enhanced Analysis Tabs */}
      {safetyAnalysis?.enhanced_analysis && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="w-5 h-5 text-purple-600" />
              <span>Crime Statistics & Area Analysis</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="area-info" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="area-info">Area Info</TabsTrigger>
                <TabsTrigger value="risk-factors">Risk Factors</TabsTrigger>
                <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
              </TabsList>

              <TabsContent value="area-info" className="space-y-4">
                {safetyAnalysis.enhanced_analysis.nearest_area && (
                  <div className="space-y-3">
                    <div>
                      <span className="text-sm font-medium">Nearest Tourist Area</span>
                      <p className="text-lg font-semibold">
                        {safetyAnalysis.enhanced_analysis.nearest_area.name}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {safetyAnalysis.enhanced_analysis.nearest_area.category} • {' '}
                        {safetyAnalysis.enhanced_analysis.nearest_area.distance_km.toFixed(1)}km away
                      </p>
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="risk-factors" className="space-y-4">
                {safetyAnalysis.enhanced_analysis.crime_breakdown && (
                  <div className="space-y-3">
                    <div className="text-sm font-medium">Crime Risk Breakdown</div>
                    <div className="space-y-2">
                      {Object.entries(safetyAnalysis.enhanced_analysis.crime_breakdown).map(([factor, value]) => (
                        <div key={factor} className="flex items-center justify-between">
                          <span className="text-sm capitalize">{factor.replace('_', ' ')}</span>
                          <div className="flex items-center space-x-2">
                            <Progress value={(value / 10) * 100} className="w-20 h-2" />
                            <span className="text-sm font-mono w-8">{value.toFixed(1)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="recommendations" className="space-y-4">
                <div className="space-y-3">
                  <div className="text-sm font-medium">Safety Recommendations</div>
                  <ul className="space-y-2">
                    {safetyAnalysis.enhanced_analysis.safety_recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start space-x-2 text-sm">
                        <Shield className="w-4 h-4 mt-0.5 text-blue-600 flex-shrink-0" />
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {safetyAnalysis.enhanced_analysis.area_alerts.length > 0 && (
                  <div className="space-y-2">
                    <div className="text-sm font-medium">Active Alerts</div>
                    {safetyAnalysis.enhanced_analysis.area_alerts.map((alert, index) => (
                      <Alert key={index} className="border-orange-200 bg-orange-50">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>{alert}</AlertDescription>
                      </Alert>
                    ))}
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}

      {/* Safety Events & Alerts */}
      {tripStatus?.safety_events && tripStatus.safety_events.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              <span>Safety Events</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {tripStatus.safety_events
                .filter(event => !event.acknowledged)
                .slice(0, 5)
                .map((event) => (
                  <div key={event.id} className="flex items-start justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <Badge 
                          variant={
                            event.severity === 'critical' ? 'destructive' :
                            event.severity === 'high' ? 'destructive' :
                            event.severity === 'medium' ? 'secondary' : 'default'
                          }
                          className="text-xs"
                        >
                          {event.severity}
                        </Badge>
                        <span className="text-sm font-medium capitalize">{event.type.replace('_', ' ')}</span>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">{event.message}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(event.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleAcknowledgeAlert(event.id)}
                    >
                      Acknowledge
                    </Button>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Sensor Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-green-600" />
            <span>Device Sensors</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Motion Sensors</span>
              <div className="mt-1">
                <Badge variant={sensorSupported && permissionGranted ? 'default' : 'secondary'}>
                  {sensorSupported && permissionGranted ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            </div>
            <div>
              <span className="text-muted-foreground">AI Processing</span>
              <div className="mt-1">
                <Badge variant={isConnected ? 'default' : 'secondary'}>
                  {isConnected ? 'Online' : 'Offline'}
                </Badge>
              </div>
            </div>
          </div>
          
          {sensorData.accelerometer && (
            <div className="mt-4 text-xs font-mono">
              <div>Accel: X:{sensorData.accelerometer.x.toFixed(2)} Y:{sensorData.accelerometer.y.toFixed(2)} Z:{sensorData.accelerometer.z.toFixed(2)}</div>
              {sensorData.gyroscope && (
                <div>Gyro: X:{sensorData.gyroscope.x.toFixed(2)} Y:{sensorData.gyroscope.y.toFixed(2)} Z:{sensorData.gyroscope.z.toFixed(2)}</div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
