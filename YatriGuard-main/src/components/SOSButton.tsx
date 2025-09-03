import React, { useState } from "react";
import { AlertTriangle, Phone, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";

export const SOSButton: React.FC = () => {
  const [isSOSActive, setIsSOSActive] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const { toast } = useToast();

  const handleSOSPress = () => {
    if (isSOSActive) return;
    
    setIsSOSActive(true);
    setCountdown(3);
    
    const countdownInterval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(countdownInterval);
          triggerSOS();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    // Show cancel option
    toast({
      title: "SOS Activating...",
      description: "Tap to cancel emergency alert",
      duration: 3000,
      action: (
        <Button
          variant="secondary"
          size="sm"
          onClick={() => {
            clearInterval(countdownInterval);
            setIsSOSActive(false);
            setCountdown(0);
            toast({
              title: "SOS Cancelled",
              description: "Emergency alert cancelled",
            });
          }}
        >
          Cancel
        </Button>
      ),
    });
  };

  const triggerSOS = () => {
    // Generate incident ID for blockchain logging
    const incidentId = `INC_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    toast({
      title: "🚨 SOS ACTIVATED",
      description: `Emergency alert sent. Incident ID: ${incidentId}`,
      duration: 10000,
    });

    // Here would be the actual SOS logic:
    // - Send location to authorities
    // - Alert emergency contacts
    // - Log incident on blockchain
    // - Send SMS/USSD if offline
    
    setTimeout(() => {
      setIsSOSActive(false);
    }, 2000);
  };

  return (
    <div className="fixed bottom-24 right-4 z-50">
      {/* SOS Button */}
      <Button
        onClick={handleSOSPress}
        disabled={isSOSActive}
        className={`
          w-16 h-16 rounded-full bg-gradient-emergency text-emergency-foreground
          shadow-emergency hover:shadow-lg hover:scale-105 transition-all duration-300
          ${isSOSActive ? 'animate-pulse scale-110' : ''}
          border-2 border-white
        `}
      >
        {countdown > 0 ? (
          <span className="text-2xl font-bold">{countdown}</span>
        ) : isSOSActive ? (
          <Zap className="w-8 h-8 animate-bounce" />
        ) : (
          <AlertTriangle className="w-8 h-8" />
        )}
      </Button>

      {/* Emergency Info Card (shows when SOS is active) */}
      {isSOSActive && countdown === 0 && (
        <Card className="absolute bottom-20 right-0 w-64 shadow-emergency">
          <CardContent className="p-4 space-y-2">
            <div className="flex items-center space-x-2 text-emergency">
              <AlertTriangle className="w-5 h-5" />
              <span className="font-semibold">Emergency Alert Active</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Your location and details have been shared with:
            </p>
            <ul className="text-sm space-y-1">
              <li className="flex items-center space-x-2">
                <Phone className="w-4 h-4" />
                <span>Local Emergency Services</span>
              </li>
              <li className="flex items-center space-x-2">
                <Phone className="w-4 h-4" />
                <span>Emergency Contacts</span>
              </li>
            </ul>
            <div className="pt-2 border-t">
              <p className="text-xs text-muted-foreground">
                🔒 Blockchain-verified incident logged
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};