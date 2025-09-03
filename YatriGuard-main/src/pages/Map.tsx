import React, { useState } from "react";
import { MapPin, Shield, AlertTriangle, Phone, Navigation, Home } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface LocationPin {
  id: string;
  type: "help" | "danger" | "safe" | "itinerary";
  name: string;
  description: string;
  coordinates: [number, number];
  distance?: string;
}

const mockLocations: LocationPin[] = [
  {
    id: "1",
    type: "help",
    name: "Tourist Help Desk",
    description: "24/7 assistance available",
    coordinates: [77.2090, 28.6139],
    distance: "0.2 km",
  },
  {
    id: "2", 
    type: "danger",
    name: "Construction Zone",
    description: "Avoid after 8 PM",
    coordinates: [77.2100, 28.6140],
    distance: "0.5 km",
  },
  {
    id: "3",
    type: "itinerary",
    name: "Red Fort",
    description: "Next destination",
    coordinates: [77.2410, 28.6562],
    distance: "2.1 km",
  },
  {
    id: "4",
    type: "safe",
    name: "Safe Zone - Police Station",
    description: "Well-patrolled area",
    coordinates: [77.2080, 28.6130],
    distance: "0.3 km",
  },
];

export const Map: React.FC = () => {
  const [selectedLocation, setSelectedLocation] = useState<LocationPin | null>(null);
  const [trackingEnabled, setTrackingEnabled] = useState(true);

  const getLocationIcon = (type: string) => {
    switch (type) {
      case "help": return Phone;
      case "danger": return AlertTriangle;
      case "safe": return Shield;
      case "itinerary": return Navigation;
      default: return MapPin;
    }
  };

  const getLocationColor = (type: string) => {
    switch (type) {
      case "help": return "text-primary";
      case "danger": return "text-destructive";
      case "safe": return "text-success";
      case "itinerary": return "text-warning";
      default: return "text-muted-foreground";
    }
  };

  const getBadgeVariant = (type: string) => {
    switch (type) {
      case "help": return "default";
      case "danger": return "destructive";
      case "safe": return "secondary";
      case "itinerary": return "secondary";
      default: return "secondary";
    }
  };

  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Safety Map</h1>
          <p className="text-muted-foreground">Real-time location tracking and safety zones</p>
        </div>
        <Button
          variant={trackingEnabled ? "verified" : "outline"}
          size="sm"
          onClick={() => setTrackingEnabled(!trackingEnabled)}
        >
          <MapPin className="w-4 h-4 mr-2" />
          {trackingEnabled ? "Tracking On" : "Tracking Off"}
        </Button>
      </div>

      {/* Map Placeholder - In a real app, this would be an actual map component */}
      <Card className="relative overflow-hidden">
        <div className="h-96 bg-gradient-to-br from-primary/5 to-accent/5 relative">
          {/* Mock Map Background */}
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJoc2woMjIwIDEzJSA5MSUpIiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-20" />
          
          {/* Current Location */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <div className="w-6 h-6 bg-primary rounded-full border-4 border-white shadow-lg relative">
              <div className="absolute inset-0 bg-primary rounded-full animate-ping opacity-75" />
            </div>
            <div className="absolute top-8 left-1/2 transform -translate-x-1/2">
              <Badge variant="default" className="text-xs">You are here</Badge>
            </div>
          </div>

          {/* Location Pins */}
          {mockLocations.map((location, index) => {
            const Icon = getLocationIcon(location.type);
            const positions = [
              { top: "25%", left: "30%" },
              { top: "60%", left: "70%" },
              { top: "30%", left: "80%" },
              { top: "70%", left: "20%" },
            ];
            
            return (
              <div
                key={location.id}
                className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer"
                style={positions[index]}
                onClick={() => setSelectedLocation(location)}
              >
                <div className={`w-8 h-8 ${getLocationColor(location.type)} bg-white rounded-full border-2 flex items-center justify-center shadow-lg hover:scale-110 transition-transform`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
            );
          })}
        </div>

        {/* Map Legend */}
        <div className="absolute top-4 right-4 bg-white/95 backdrop-blur rounded-lg p-3 shadow-lg">
          <h4 className="font-semibold text-sm mb-2">Legend</h4>
          <div className="space-y-1 text-xs">
            <div className="flex items-center space-x-2">
              <Shield className="w-3 h-3 text-success" />
              <span>Safe Zone</span>
            </div>
            <div className="flex items-center space-x-2">
              <Phone className="w-3 h-3 text-primary" />
              <span>Help Desk</span>
            </div>
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-3 h-3 text-destructive" />
              <span>Caution Area</span>
            </div>
            <div className="flex items-center space-x-2">
              <Navigation className="w-3 h-3 text-warning" />
              <span>Itinerary</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Location Details */}
      {selectedLocation && (
        <Card className="border-2 border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {React.createElement(getLocationIcon(selectedLocation.type), {
                  className: `w-5 h-5 ${getLocationColor(selectedLocation.type)}`
                })}
                <span>{selectedLocation.name}</span>
              </div>
              <Badge variant={getBadgeVariant(selectedLocation.type)}>
                {selectedLocation.type}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">{selectedLocation.description}</p>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-sm">
                <MapPin className="w-4 h-4" />
                <span>{selectedLocation.distance} away</span>
              </div>
              <div className="flex space-x-2">
                <Button size="sm" variant="outline">
                  Directions
                </Button>
                {selectedLocation.type === "help" && (
                  <Button size="sm" variant="default">
                    <Phone className="w-4 h-4 mr-2" />
                    Call
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-4">
        <Button variant="outline" className="h-16 flex-col space-y-2">
          <Home className="w-6 h-6" />
          <span className="text-sm">Navigate Home</span>
        </Button>
        <Button variant="outline" className="h-16 flex-col space-y-2">
          <Shield className="w-6 h-6" />
          <span className="text-sm">Find Safe Zone</span>
        </Button>
      </div>

      {/* Location Status */}
      <Card className="bg-success/5 border-success/20">
        <CardContent className="p-4">
          <div className="flex items-center space-x-3">
            <Shield className="w-6 h-6 text-success" />
            <div>
              <p className="font-semibold">Location Secure</p>
              <p className="text-sm text-muted-foreground">
                You're in a well-monitored area with help posts nearby
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Map;