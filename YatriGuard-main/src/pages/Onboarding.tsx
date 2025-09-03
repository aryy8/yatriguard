import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, Upload, Users, CheckCircle, ArrowRight, FileText, Smartphone, User, Calendar, Heart, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";

type OnboardingStep = "identity-verification" | "trip-details" | "emergency-safety" | "review-generate";

interface PersonalDetails {
  fullName: string;
  dateOfBirth: string;
  gender: string;
  nationality: string;
  email: string;
  mobile: string;
  otpVerified: boolean;
}

interface TripDetails {
  arrivalDate: string;
  departureDate: string;
  destinations: string;
  accommodations: string;
  modeOfTravel: string;
}

interface EmergencyContact {
  name: string;
  phone: string;
  relation: string;
}

interface SafetyInfo {
  primaryContact: EmergencyContact;
  secondaryContact: EmergencyContact;
  bloodGroup: string;
  allergies: string;
  locationSharingConsent: "family" | "authorities" | "none";
}

export const Onboarding: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [currentStep, setCurrentStep] = useState<OnboardingStep>("identity-verification");
  
  // Personal Details State
  const [personalDetails, setPersonalDetails] = useState<PersonalDetails>({
    fullName: "",
    dateOfBirth: "",
    gender: "",
    nationality: "",
    email: "",
    mobile: "",
    otpVerified: false,
  });
  
  // Trip Details State
  const [tripDetails, setTripDetails] = useState<TripDetails>({
    arrivalDate: "",
    departureDate: "",
    destinations: "",
    accommodations: "",
    modeOfTravel: "",
  });
  
  // Safety Info State
  const [safetyInfo, setSafetyInfo] = useState<SafetyInfo>({
    primaryContact: { name: "", phone: "", relation: "" },
    secondaryContact: { name: "", phone: "", relation: "" },
    bloodGroup: "",
    allergies: "",
    locationSharingConsent: "none",
  });
  
  // Documents State
  const [idDocument, setIdDocument] = useState<File | null>(null);
  const [selfieDocument, setSelfieDocument] = useState<File | null>(null);
  const [finalConsent, setFinalConsent] = useState(false);
  const [isGeneratingId, setIsGeneratingId] = useState(false);

  const stepProgress = {
    "identity-verification": 25,
    "trip-details": 50,
    "emergency-safety": 75,
    "review-generate": 100,
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>, type: "id" | "selfie") => {
    const file = event.target.files?.[0];
    if (file) {
      if (type === "id") {
        setIdDocument(file);
        toast({
          title: "ID Document Uploaded",
          description: "Your ID document has been securely uploaded",
        });
      } else {
        setSelfieDocument(file);
        toast({
          title: "Selfie Uploaded",
          description: "Your verification selfie has been uploaded",
        });
      }
    }
  };

  const sendOTP = () => {
    toast({
      title: "OTP Sent",
      description: `Verification code sent to ${personalDetails.mobile}`,
    });
  };

  const verifyOTP = () => {
    setPersonalDetails(prev => ({ ...prev, otpVerified: true }));
    toast({
      title: "Mobile Verified",
      description: "Your mobile number has been successfully verified",
    });
  };

  const generateBlockchainId = async () => {
    setIsGeneratingId(true);
    
    // Simulate blockchain ID generation
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    const blockchainId = `YG-${Date.now()}-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;
    
    toast({
      title: "🔒 Digital Tourist ID Generated!",
      description: `Your secure ID: ${blockchainId}`,
      duration: 5000,
    });
    
    setIsGeneratingId(false);
    
    // Navigate to dashboard after ID generation
    setTimeout(() => {
      navigate("/dashboard");
    }, 2000);
  };

  const nextStep = () => {
    const steps: OnboardingStep[] = ["identity-verification", "trip-details", "emergency-safety", "review-generate"];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1]);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case "identity-verification":
        return personalDetails.fullName && personalDetails.dateOfBirth && personalDetails.gender && 
               personalDetails.nationality && personalDetails.email && personalDetails.mobile && 
               personalDetails.otpVerified && idDocument && selfieDocument;
      case "trip-details":
        return tripDetails.arrivalDate && tripDetails.departureDate && tripDetails.destinations && 
               tripDetails.accommodations && tripDetails.modeOfTravel;
      case "emergency-safety":
        return safetyInfo.primaryContact.name && safetyInfo.primaryContact.phone && 
               safetyInfo.primaryContact.relation && safetyInfo.locationSharingConsent !== "none";
      case "review-generate":
        return finalConsent;
      default:
        return true;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-gradient-hero text-primary-foreground p-6">
        <div className="container mx-auto">
          <div className="flex items-center space-x-3 mb-4">
            <Shield className="w-8 h-8" />
            <h1 className="text-2xl font-bold">YatriGuard Setup</h1>
          </div>
          <p className="text-primary-foreground/90">
            Create your blockchain-secured Digital Tourist ID
          </p>
          <div className="mt-4">
            <Progress value={stepProgress[currentStep]} className="bg-white/20" />
            <p className="text-sm mt-2 text-primary-foreground/80">
              Step {Object.keys(stepProgress).indexOf(currentStep) + 1} of 4
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Step 1: Identity Verification */}
        {currentStep === "identity-verification" && (
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <User className="w-6 h-6" />
                <span>Identity & Verification</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4">
                <div>
                  <Label htmlFor="fullName">Full Name</Label>
                  <Input
                    id="fullName"
                    value={personalDetails.fullName}
                    onChange={(e) => setPersonalDetails(prev => ({ ...prev, fullName: e.target.value }))}
                    placeholder="Enter your full name"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="dateOfBirth">Date of Birth</Label>
                    <Input
                      id="dateOfBirth"
                      type="date"
                      value={personalDetails.dateOfBirth}
                      onChange={(e) => setPersonalDetails(prev => ({ ...prev, dateOfBirth: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label>Gender</Label>
                    <Select value={personalDetails.gender} onValueChange={(value) => setPersonalDetails(prev => ({ ...prev, gender: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select gender" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="male">Male</SelectItem>
                        <SelectItem value="female">Female</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label>Nationality</Label>
                  <Select value={personalDetails.nationality} onValueChange={(value) => setPersonalDetails(prev => ({ ...prev, nationality: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select nationality" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="indian">Indian</SelectItem>
                      <SelectItem value="us">United States</SelectItem>
                      <SelectItem value="uk">United Kingdom</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={personalDetails.email}
                    onChange={(e) => setPersonalDetails(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="your@email.com"
                  />
                </div>

                <div>
                  <Label htmlFor="mobile">Mobile Number</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="mobile"
                      value={personalDetails.mobile}
                      onChange={(e) => setPersonalDetails(prev => ({ ...prev, mobile: e.target.value }))}
                      placeholder="+91 9876543210"
                      className="flex-1"
                    />
                    {!personalDetails.otpVerified ? (
                      <Button onClick={sendOTP} variant="outline" disabled={!personalDetails.mobile}>
                        Send OTP
                      </Button>
                    ) : (
                      <Button variant="outline" disabled className="text-success">
                        ✓ Verified
                      </Button>
                    )}
                  </div>
                  {personalDetails.mobile && !personalDetails.otpVerified && (
                    <div className="flex space-x-2 mt-2">
                      <Input placeholder="Enter OTP" className="flex-1" />
                      <Button onClick={verifyOTP} size="sm">Verify</Button>
                    </div>
                  )}
                </div>
              </div>

              {/* Document Upload */}
              <div className="space-y-4">
                <h3 className="font-semibold">Upload Documents</h3>
                
                {/* ID Document */}
                <div className="border-2 border-dashed border-border rounded-lg p-4">
                  <div className="text-center space-y-3">
                    {idDocument ? (
                      <div className="space-y-2">
                        <CheckCircle className="w-8 h-8 text-success mx-auto" />
                        <p className="font-medium">{idDocument.name}</p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <FileText className="w-8 h-8 text-muted-foreground mx-auto" />
                        <p className="font-medium">Aadhaar Card / Passport</p>
                      </div>
                    )}
                    <Input
                      type="file"
                      accept=".jpg,.jpeg,.png,.pdf"
                      onChange={(e) => handleFileUpload(e, "id")}
                      className="hidden"
                      id="id-doc"
                    />
                    <Label htmlFor="id-doc">
                      <Button variant="outline" size="sm">
                        {idDocument ? "Change" : "Upload ID"}
                      </Button>
                    </Label>
                  </div>
                </div>

                {/* Selfie */}
                <div className="border-2 border-dashed border-border rounded-lg p-4">
                  <div className="text-center space-y-3">
                    {selfieDocument ? (
                      <div className="space-y-2">
                        <CheckCircle className="w-8 h-8 text-success mx-auto" />
                        <p className="font-medium">Selfie uploaded</p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <User className="w-8 h-8 text-muted-foreground mx-auto" />
                        <p className="font-medium">Verification Selfie</p>
                      </div>
                    )}
                    <Input
                      type="file"
                      accept=".jpg,.jpeg,.png"
                      onChange={(e) => handleFileUpload(e, "selfie")}
                      className="hidden"
                      id="selfie"
                    />
                    <Label htmlFor="selfie">
                      <Button variant="outline" size="sm">
                        {selfieDocument ? "Retake" : "Take Selfie"}
                      </Button>
                    </Label>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Trip Details */}
        {currentStep === "trip-details" && (
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calendar className="w-6 h-6" />
                <span>Trip Details</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="arrivalDate">Arrival Date</Label>
                    <Input
                      id="arrivalDate"
                      type="date"
                      value={tripDetails.arrivalDate}
                      onChange={(e) => setTripDetails(prev => ({ ...prev, arrivalDate: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="departureDate">Departure Date</Label>
                    <Input
                      id="departureDate"
                      type="date"
                      value={tripDetails.departureDate}
                      onChange={(e) => setTripDetails(prev => ({ ...prev, departureDate: e.target.value }))}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="destinations">Planned Destinations</Label>
                  <Textarea
                    id="destinations"
                    value={tripDetails.destinations}
                    onChange={(e) => setTripDetails(prev => ({ ...prev, destinations: e.target.value }))}
                    placeholder="e.g., Mumbai, Goa, Kerala (include cities, attractions, hotels)"
                    rows={3}
                  />
                </div>

                <div>
                  <Label>Mode of Travel</Label>
                  <Select value={tripDetails.modeOfTravel} onValueChange={(value) => setTripDetails(prev => ({ ...prev, modeOfTravel: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select mode of travel" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="flight">Flight</SelectItem>
                      <SelectItem value="train">Train</SelectItem>
                      <SelectItem value="road">Road/Car</SelectItem>
                      <SelectItem value="mixed">Mixed (Flight + Road/Train)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="accommodations">Accommodation Details</Label>
                  <Textarea
                    id="accommodations"
                    value={tripDetails.accommodations}
                    onChange={(e) => setTripDetails(prev => ({ ...prev, accommodations: e.target.value }))}
                    placeholder="Hotel names, addresses, booking confirmations"
                    rows={3}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Emergency & Safety Info */}
        {currentStep === "emergency-safety" && (
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Heart className="w-6 h-6" />
                <span>Emergency & Safety Info</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-6">
                {/* Primary Contact */}
                <div className="border border-border rounded-lg p-4 space-y-4">
                  <h3 className="font-semibold text-emergency">Primary Emergency Contact</h3>
                  <div className="grid gap-4">
                    <Input
                      placeholder="Full Name"
                      value={safetyInfo.primaryContact.name}
                      onChange={(e) => setSafetyInfo(prev => ({ 
                        ...prev, 
                        primaryContact: { ...prev.primaryContact, name: e.target.value }
                      }))}
                    />
                    <Input
                      placeholder="Phone Number"
                      value={safetyInfo.primaryContact.phone}
                      onChange={(e) => setSafetyInfo(prev => ({ 
                        ...prev, 
                        primaryContact: { ...prev.primaryContact, phone: e.target.value }
                      }))}
                    />
                    <Input
                      placeholder="Relationship (e.g., Parent, Spouse)"
                      value={safetyInfo.primaryContact.relation}
                      onChange={(e) => setSafetyInfo(prev => ({ 
                        ...prev, 
                        primaryContact: { ...prev.primaryContact, relation: e.target.value }
                      }))}
                    />
                  </div>
                </div>

                {/* Secondary Contact */}
                <div className="border border-border rounded-lg p-4 space-y-4">
                  <h3 className="font-semibold">Secondary Contact (Optional)</h3>
                  <div className="grid gap-4">
                    <Input
                      placeholder="Full Name"
                      value={safetyInfo.secondaryContact.name}
                      onChange={(e) => setSafetyInfo(prev => ({ 
                        ...prev, 
                        secondaryContact: { ...prev.secondaryContact, name: e.target.value }
                      }))}
                    />
                    <Input
                      placeholder="Phone Number"
                      value={safetyInfo.secondaryContact.phone}
                      onChange={(e) => setSafetyInfo(prev => ({ 
                        ...prev, 
                        secondaryContact: { ...prev.secondaryContact, phone: e.target.value }
                      }))}
                    />
                    <Input
                      placeholder="Relationship"
                      value={safetyInfo.secondaryContact.relation}
                      onChange={(e) => setSafetyInfo(prev => ({ 
                        ...prev, 
                        secondaryContact: { ...prev.secondaryContact, relation: e.target.value }
                      }))}
                    />
                  </div>
                </div>

                {/* Health Info */}
                <div className="space-y-4">
                  <h3 className="font-semibold">Health Information (Optional)</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Blood Group</Label>
                      <Select value={safetyInfo.bloodGroup} onValueChange={(value) => setSafetyInfo(prev => ({ ...prev, bloodGroup: value }))}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="A+">A+</SelectItem>
                          <SelectItem value="A-">A-</SelectItem>
                          <SelectItem value="B+">B+</SelectItem>
                          <SelectItem value="B-">B-</SelectItem>
                          <SelectItem value="AB+">AB+</SelectItem>
                          <SelectItem value="AB-">AB-</SelectItem>
                          <SelectItem value="O+">O+</SelectItem>
                          <SelectItem value="O-">O-</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="allergies">Allergies</Label>
                      <Input
                        id="allergies"
                        value={safetyInfo.allergies}
                        onChange={(e) => setSafetyInfo(prev => ({ ...prev, allergies: e.target.value }))}
                        placeholder="e.g., Peanuts, Shellfish"
                      />
                    </div>
                  </div>
                </div>

                {/* Location Sharing */}
                <div className="space-y-4">
                  <h3 className="font-semibold">Location Sharing Consent</h3>
                  <div className="space-y-3">
                    {[
                      { value: "family" as const, label: "Family Members Only", desc: "Share location with emergency contacts" },
                      { value: "authorities" as const, label: "Authorities & Family", desc: "Share with police, tourism dept, and contacts" },
                      { value: "none" as const, label: "Emergency Only", desc: "Share only during active SOS situations" },
                    ].map(option => (
                      <div key={option.value} className="flex items-start space-x-3 p-3 border border-border rounded-lg">
                        <input
                          type="radio"
                          id={option.value}
                          name="locationConsent"
                          checked={safetyInfo.locationSharingConsent === option.value}
                          onChange={() => setSafetyInfo(prev => ({ ...prev, locationSharingConsent: option.value }))}
                          className="mt-1"
                        />
                        <div>
                          <Label htmlFor={option.value} className="font-medium cursor-pointer">
                            {option.label}
                          </Label>
                          <p className="text-sm text-muted-foreground">{option.desc}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 4: Review & Generate */}
        {currentStep === "review-generate" && (
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Eye className="w-6 h-6" />
                <span>Review & Generate ID</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Review Summary */}
              <div className="space-y-4">
                <div className="bg-muted p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">Personal Details</h3>
                  <div className="text-sm space-y-1">
                    <p><strong>Name:</strong> {personalDetails.fullName}</p>
                    <p><strong>DOB:</strong> {personalDetails.dateOfBirth}</p>
                    <p><strong>Nationality:</strong> {personalDetails.nationality}</p>
                    <p><strong>Email:</strong> {personalDetails.email}</p>
                    <p><strong>Mobile:</strong> {personalDetails.mobile} ✓</p>
                  </div>
                </div>

                <div className="bg-muted p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">Trip Information</h3>
                  <div className="text-sm space-y-1">
                    <p><strong>Duration:</strong> {tripDetails.arrivalDate} to {tripDetails.departureDate}</p>
                    <p><strong>Destinations:</strong> {tripDetails.destinations}</p>
                    <p><strong>Travel Mode:</strong> {tripDetails.modeOfTravel}</p>
                  </div>
                </div>

                <div className="bg-muted p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">Emergency Contact</h3>
                  <div className="text-sm space-y-1">
                    <p><strong>Primary:</strong> {safetyInfo.primaryContact.name} ({safetyInfo.primaryContact.relation})</p>
                    <p><strong>Phone:</strong> {safetyInfo.primaryContact.phone}</p>
                    <p><strong>Location Sharing:</strong> {safetyInfo.locationSharingConsent}</p>
                  </div>
                </div>
              </div>

              {/* Consent */}
              <div className="border border-border rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <Checkbox
                    id="finalConsent"
                    checked={finalConsent}
                    onCheckedChange={(checked) => setFinalConsent(checked === true)}
                  />
                  <div>
                    <Label htmlFor="finalConsent" className="font-medium cursor-pointer">
                      I agree to secure storage on blockchain for trip duration
                    </Label>
                    <p className="text-sm text-muted-foreground mt-1">
                      Your Digital Tourist ID will be stored securely on blockchain and is valid until your departure date. 
                      You can revoke access anytime.
                    </p>
                  </div>
                </div>
              </div>

              {/* Generate Button */}
              {!isGeneratingId ? (
                <Button
                  onClick={generateBlockchainId}
                  disabled={!finalConsent}
                  size="lg"
                  className="w-full bg-gradient-primary hover:shadow-primary"
                >
                  <Shield className="w-5 h-5 mr-2" />
                  Generate My Digital Tourist ID
                </Button>
              ) : (
                <div className="text-center space-y-4">
                  <div className="w-16 h-16 bg-gradient-primary rounded-full flex items-center justify-center mx-auto animate-pulse">
                    <Shield className="w-8 h-8 text-white animate-spin" />
                  </div>
                  <div>
                    <h3 className="font-bold">Generating Your Digital ID...</h3>
                    <p className="text-sm text-muted-foreground">Creating blockchain-secured tourist identity</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Navigation */}
        {currentStep !== "review-generate" && (
          <div className="max-w-2xl mx-auto mt-8 text-center">
            <Button
              onClick={nextStep}
              disabled={!canProceed()}
              size="lg"
              className="w-full sm:w-auto"
            >
              Continue
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Onboarding;