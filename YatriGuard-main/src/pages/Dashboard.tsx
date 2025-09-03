import React, { useEffect, useMemo, useState } from "react";
import { Shield, QrCode, MapPin, AlertTriangle, Clock, Users, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

interface Alert {
  id: string;
  type: "warning" | "info" | "danger";
  message: string;
  location: string;
  time: string;
}

const mockAlerts: Alert[] = [
  {
    id: "1",
    type: "warning",
    message: "Heavy rainfall expected in Goa region",
    location: "Goa",
    time: "2 hours ago",
  },
  {
    id: "2",
    type: "info",
    message: "New help post added near Red Fort",
    location: "Delhi",
    time: "5 hours ago",
  },
];

type SavedId = {
  idNumber: string;
  docHash?: string;
  fullName?: string;
  arrival?: string; // ISO
  departure?: string; // ISO
  destinations?: string[];
  travelMode?: string;
  accommodationName?: string;
  accommodationAddress?: string;
  bookingRef?: string;
  emergencyPrimaryName?: string;
  emergencyPrimaryPhone?: string;
  locationConsent?: string;
};

type Profile = {
  fullName?: string;
  email?: string;
};

export const Dashboard: React.FC = () => {
  const [safetyScore] = useState(92);
  const [saved, setSaved] = useState<SavedId | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem("yg_digital_id");
      if (raw) setSaved(JSON.parse(raw));
    } catch {
      // ignore
    }
    try {
      const p = localStorage.getItem("yg_profile");
      if (p) setProfile(JSON.parse(p));
    } catch {
      // ignore
    }
  }, []);

  const activeTrip = useMemo(() => {
    const arrival = saved?.arrival ? new Date(saved.arrival) : undefined;
    const departure = saved?.departure ? new Date(saved.departure) : undefined;
    let duration = "--";
    if (arrival && departure) {
      const ms = Math.max(0, departure.getTime() - arrival.getTime());
      const days = Math.max(1, Math.ceil(ms / (1000 * 60 * 60 * 24)));
      duration = `${days} day${days > 1 ? "s" : ""}`;
    }
    const destination = (saved?.destinations && saved.destinations.length > 0)
      ? saved.destinations.join(", ")
      : "No trip set";
    return {
      destination,
      duration,
      progress: 50,
    };
  }, [saved]);

  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Welcome back{(saved?.fullName || profile?.fullName) ? `, ${saved?.fullName ?? profile?.fullName}` : ""}!</h1>
          <p className="text-muted-foreground">Your safety is secured by blockchain</p>
        </div>
        <Button variant="outline" size="sm" className="border-success text-success">
          <Shield className="w-4 h-4 mr-2" />
          Verified
        </Button>
      </div>

      {/* Digital ID Card */}
      <Card className="bg-gradient-hero text-white shadow-primary">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8" />
              <div>
                <CardTitle className="text-white">Digital Tourist ID</CardTitle>
                <p className="text-white/80 text-sm">Blockchain Verified</p>
              </div>
            </div>
            <QrCode className="w-8 h-8 text-white/80" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-white/80 text-sm">ID Number</p>
              <p className="font-mono text-lg">{saved?.idNumber ?? "—"}</p>
            </div>
            <div>
              <p className="text-white/80 text-sm">Valid Until</p>
              <p className="font-semibold">{saved?.departure ? new Date(saved.departure).toLocaleDateString() : "—"}</p>
            </div>
            <div>
              <p className="text-white/80 text-sm">Document Hash</p>
              <p className="font-mono text-xs">{saved?.docHash ?? "—"}</p>
            </div>
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-success" />
              <span className="text-sm">Tamper-Proof</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Safety Score & Active Trip */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Safety Score */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-success" />
              <span>Safety Score</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-4xl font-bold text-success mb-2">{safetyScore}/100</div>
                <p className="text-sm text-muted-foreground">Excellent Safety Rating</p>
              </div>
              <Progress value={safetyScore} className="h-3" />
              <div className="text-xs text-muted-foreground space-y-1">
                <div className="flex justify-between">
                  <span>• ID Verification</span>
                  <span className="text-success">✓ Complete</span>
                </div>
                <div className="flex justify-between">
                  <span>• Emergency Contacts</span>
                  <span className="text-success">✓ 3 Added</span>
                </div>
                <div className="flex justify-between">
                  <span>• Location Sharing</span>
                  <span className="text-success">✓ Active</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Active Trip */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MapPin className="w-5 h-5 text-primary" />
              <span>Current Trip</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-lg">{activeTrip.destination}</h3>
                <p className="text-muted-foreground">{activeTrip.duration}</p>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Trip Progress</span>
                  <span>{activeTrip.progress}%</span>
                </div>
                <Progress value={activeTrip.progress} className="h-2" />
              </div>
              <div className="flex space-x-2">
                <Button size="sm" variant="outline" className="flex-1">
                  <MapPin className="w-4 h-4 mr-2" />
                  View Map
                </Button>
                <Button size="sm" variant="outline" className="flex-1">
                  <Users className="w-4 h-4 mr-2" />
                  Share
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Alerts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-warning" />
            <span>Safety Alerts</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mockAlerts.map((alert) => (
              <div key={alert.id} className="flex items-start space-x-3 p-3 rounded-lg border border-border">
                <div className={`w-2 h-2 rounded-full mt-2 ${
                  alert.type === "danger" ? "bg-destructive" :
                  alert.type === "warning" ? "bg-warning" : "bg-primary"
                }`} />
                <div className="flex-1">
                  <p className="font-medium">{alert.message}</p>
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground mt-1">
                    <span className="flex items-center space-x-1">
                      <MapPin className="w-3 h-3" />
                      <span>{alert.location}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{alert.time}</span>
                    </span>
                  </div>
                </div>
                <Badge variant={alert.type === "danger" ? "destructive" : "secondary"}>
                  {alert.type}
                </Badge>
              </div>
            ))}
            <Button variant="outline" className="w-full">
              View All Alerts
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Button variant="outline" className="h-20 flex-col space-y-2">
          <MapPin className="w-6 h-6" />
          <span className="text-sm">View Map</span>
        </Button>
        <Button variant="outline" className="h-20 flex-col space-y-2">
          <Users className="w-6 h-6" />
          <span className="text-sm">Family Share</span>
        </Button>
        <Button variant="outline" className="h-20 flex-col space-y-2">
          <AlertTriangle className="w-6 h-6" />
          <span className="text-sm">Report Issue</span>
        </Button>
        <Button variant="outline" className="h-20 flex-col space-y-2">
          <Shield className="w-6 h-6" />
          <span className="text-sm">Help</span>
        </Button>
      </div>
    </div>
  );
};

export default Dashboard;