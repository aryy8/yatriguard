import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm, useFieldArray, type FieldValues } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { CalendarIcon, Plus, Trash2, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { useI18n } from "@/i18n/I18nProvider";

const step1Schema = z.object({
  fullName: z.string().min(2, "Full name is required"),
  dob: z.date({ required_error: "Date of birth is required" }),
  gender: z.enum(["male", "female", "other"], { required_error: "Select gender" }),
  nationality: z.string().min(2, "Nationality is required"),
  aadhaarNumber: z
    .string()
    .regex(/^\d{12}$/i, "Enter valid 12-digit Aadhaar number"),
  idDoc: z.instanceof(File).optional(),
  selfie: z.instanceof(File).optional(),
  mobile: z
    .string()
    .min(10, "Enter valid mobile number")
    .regex(/^\+?[0-9\s-]{10,15}$/i, "Enter valid mobile number"),
  otp: z.string().min(4, "Enter OTP").max(8, "OTP too long").optional(),
  email: z.string().email("Enter valid email"),
});

const step2Schema = z
  .object({
  arrival: z.date({ required_error: "Arrival date is required" }),
  departure: z.date({ required_error: "Departure date is required" }),
  destinations: z.array(z.string().min(2, "Destination required")).min(1, "Add at least one destination"),
  itinerary: z.string().optional(),
  travelMode: z.enum(["flight", "train", "road"], { required_error: "Select mode of travel" }),
  accommodationName: z.string().min(2, "Accommodation name required"),
  accommodationAddress: z.string().min(5, "Address required"),
  bookingRef: z.string().optional(),
  })
  .refine((data) =>
    !data.arrival || !data.departure || (data.departure as Date).getTime() >= (data.arrival as Date).getTime(),
    { message: "Departure must be on or after arrival", path: ["departure"] }
  );

const step3Schema = z.object({
  emergencyPrimaryName: z.string().min(2, "Name required"),
  emergencyPrimaryRelation: z.string().min(2, "Relation required"),
  emergencyPrimaryPhone: z
    .string()
    .min(10, "Enter valid phone")
    .regex(/^\+?[0-9\s-]{10,15}$/i, "Enter valid phone"),
  emergencySecondaryName: z.string().optional(),
  emergencySecondaryRelation: z.string().optional(),
  emergencySecondaryPhone: z.string().optional(),
  bloodGroup: z
    .enum(["A+","A-","B+","B-","AB+","AB-","O+","O-"], { required_error: "Select blood group" })
    .optional(),
  allergies: z.string().optional(),
  locationConsent: z.enum(["family", "authorities", "none"], { required_error: "Choose one" }),
});

const allSchema = step1Schema
  .and(step2Schema)
  .and(step3Schema)
  .and(z.object({ consent: z.literal(true, { errorMap: () => ({ message: "You must agree to continue" }) }) }))
  ;

// Explicitly type the form values to avoid intersection type issues with react-hook-form's FieldArrayPath
export interface FormValues extends FieldValues {
  fullName: string;
  dob?: Date;
  gender?: "male" | "female" | "other";
  nationality: string;
  aadhaarNumber?: string;
  idDoc?: File;
  selfie?: File;
  mobile: string;
  otp?: string;
  email: string;

  arrival?: Date;
  departure?: Date;
  destinations: string[];
  itinerary?: string;
  travelMode?: "flight" | "train" | "road";
  accommodationName: string;
  accommodationAddress: string;
  bookingRef?: string;

  emergencyPrimaryName: string;
  emergencyPrimaryRelation: string;
  emergencyPrimaryPhone: string;
  emergencySecondaryName?: string;
  emergencySecondaryRelation?: string;
  emergencySecondaryPhone?: string;
  bloodGroup?: "A+"|"A-"|"B+"|"B-"|"AB+"|"AB-"|"O+"|"O-";
  allergies?: string;
  locationConsent?: "family"|"authorities"|"none";
  consent?: boolean;
}

function DateField({ value, onChange, placeholder }: { value?: Date; onChange: (d: Date | undefined) => void; placeholder: string }) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !value && "text-muted-foreground")}> 
          <CalendarIcon className="mr-2 h-4 w-4" />
          {value ? format(value, "PPP") : <span>{placeholder}</span>}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="p-0" align="start">
        <Calendar mode="single" selected={value} onSelect={onChange} initialFocus />
      </PopoverContent>
    </Popover>
  );
}

export default function DigitalID() {
  const { t } = useI18n();
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [generated, setGenerated] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [generatedOtp, setGeneratedOtp] = useState<string | null>(null);
  const [mobileVerified, setMobileVerified] = useState(false);
  const [aadhaarVerified, setAadhaarVerified] = useState(false);
  const [processing, setProcessing] = useState(false);
  const navigate = useNavigate();

  const form = useForm<FormValues>({
    resolver: zodResolver(allSchema), // full schema; per-step gating handled manually below
    defaultValues: {
      gender: undefined,
      travelMode: undefined,
      locationConsent: undefined,
      consent: undefined as unknown as true,
      destinations: [""],
      aadhaarNumber: "",
      otp: "",
      accommodationName: "",
      accommodationAddress: "",
      bookingRef: "",
      itinerary: "",
    },
    mode: "onSubmit",
  });

  const { fields: destinationFields, append: addDestination, remove: removeDestination } = useFieldArray<FormValues, "destinations">({
    control: form.control,
    name: "destinations",
  });

  const progress = useMemo(() => (step / 4) * 100, [step]);
  const stepLabels = [
    t('digital.steps.identity'),
    t('digital.steps.trip'),
    t('digital.steps.emergency'),
    t('digital.steps.review'),
  ] as const;

  // Popular Indian destinations
  const DESTINATIONS = useMemo(
    () => [
      "Agra",
      "Jaipur",
      "Udaipur",
      "Goa",
      "Mumbai",
      "Delhi",
      "Varanasi",
      "Rishikesh",
      "Manali",
      "Leh",
      "Mysuru",
      "Bengaluru",
      "Hyderabad",
      "Chennai",
      "Kolkata",
      "Kochi",
      "Munnar",
      "Andaman",
    ],
    []
  );

  // Trip length calculation
  const tripLengthDays = useMemo(() => {
    const a = form.getValues("arrival");
    const d = form.getValues("departure");
    if (!a || !d) return null;
    const diff = Math.ceil(((d as Date).getTime() - (a as Date).getTime()) / (1000 * 60 * 60 * 24));
    return diff >= 0 ? diff : null;
  }, [form.watch("arrival"), form.watch("departure")]);

  // Verhoeff algorithm for Aadhaar checksum validation
  const verhoeffValidate = (num: string) => {
    const d = [
      [0,1,2,3,4,5,6,7,8,9],
      [1,2,3,4,0,6,7,8,9,5],
      [2,3,4,0,1,7,8,9,5,6],
      [3,4,0,1,2,8,9,5,6,7],
      [4,0,1,2,3,9,5,6,7,8],
      [5,9,8,7,6,0,4,3,2,1],
      [6,5,9,8,7,1,0,4,3,2],
      [7,6,5,9,8,2,1,0,4,3],
      [8,7,6,5,9,3,2,1,0,4],
      [9,8,7,6,5,4,3,2,1,0],
    ];
    const p = [
      [0,1,2,3,4,5,6,7,8,9],
      [1,5,7,6,2,8,3,0,9,4],
      [5,8,0,3,7,9,6,1,4,2],
      [8,9,1,6,0,4,3,5,2,7],
      [9,4,5,3,1,2,6,8,7,0],
      [4,2,8,6,5,7,3,9,0,1],
      [2,7,9,3,8,0,6,4,1,5],
      [7,0,4,6,9,1,3,2,5,8],
    ];
    const inv = [0,4,3,2,1,5,6,7,8,9];
    let c = 0;
    const reversed = num.replace(/\D/g, "").split("").reverse().map(Number);
    for (let i = 0; i < reversed.length; i++) {
      c = d[c][p[(i % 8)][reversed[i]]];
    }
    return c === 0;
  };

  const sendOtp = () => {
    const code = (Math.floor(100000 + Math.random() * 900000)).toString();
    setGeneratedOtp(code);
    setOtpSent(true);
    setMobileVerified(false);
    // In a real app, send via SMS. For demo, log to console.
    console.info("[Demo] OTP sent:", code);
  };

  const verifyOtp = () => {
    const entered = form.getValues("otp") || "";
    const ok = generatedOtp && entered === generatedOtp;
    setMobileVerified(!!ok);
  };

  const verifyAadhaar = () => {
    const num = (form.getValues("aadhaarNumber") || "").replace(/\s/g, "");
    if (/^\d{12}$/.test(num) && verhoeffValidate(num)) {
      setAadhaarVerified(true);
    } else {
      setAadhaarVerified(false);
      form.setError("aadhaarNumber" as any, { type: "manual", message: t('val.aadhaar.invalidManual') });
    }
  };

  const validateCurrentStep = async () => {
    const values = form.getValues();
    try {
      if (step === 1) await step1Schema.parseAsync(values);
      if (step === 2) await step2Schema.parseAsync(values);
      if (step === 3) await step3Schema.parseAsync(values);
      if (step === 4) await allSchema.parseAsync(values);
      if (step === 1) {
        if (!mobileVerified) {
          form.setError("otp" as any, { type: "manual", message: t('val.verify.mobile') });
          return false;
        }
        if (!aadhaarVerified) {
          form.setError("aadhaarNumber" as any, { type: "manual", message: t('val.verify.aadhaar') });
          return false;
        }
      }
      return true;
    } catch (e) {
      form.trigger();
      return false;
    }
  };

  const onNext = async () => {
    const ok = await validateCurrentStep();
    if (ok) setStep((s) => (s < 4 ? ((s + 1) as 1 | 2 | 3 | 4) : s));
  };

  const onPrev = () => setStep((s) => (s > 1 ? ((s - 1) as 1 | 2 | 3 | 4) : s));

  const onGenerate = async () => {
    const ok = await validateCurrentStep();
    if (!ok) return;
    const values = form.getValues();
    const idNumber = `YG-${new Date().getFullYear()}-${Math.floor(100000 + Math.random() * 900000)}`;
    const docHash = `0x${Math.random().toString(16).substring(2, 6)}...${Math.random().toString(16).substring(2, 6)}`;
    const payload = {
      idNumber,
      docHash,
      fullName: values.fullName,
      arrival: values.arrival ? (values.arrival as Date).toISOString() : undefined,
      departure: values.departure ? (values.departure as Date).toISOString() : undefined,
      destinations: values.destinations,
      travelMode: values.travelMode,
      accommodationName: values.accommodationName,
      accommodationAddress: values.accommodationAddress,
      bookingRef: values.bookingRef,
      emergencyPrimaryName: values.emergencyPrimaryName,
      emergencyPrimaryPhone: values.emergencyPrimaryPhone,
      locationConsent: values.locationConsent,
    };
    try {
      localStorage.setItem("yg_digital_id", JSON.stringify(payload));
    } catch {}
    // Simulate blockchain write buffer before navigating
    setProcessing(true);
    setTimeout(() => {
      setProcessing(false);
      navigate("/dashboard");
    }, 2000);
  };

  return (
    <div className="container mx-auto max-w-4xl px-4 py-8">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">{t('digital.title')}</CardTitle>
          <p className="text-muted-foreground mt-1 text-sm">{t('digital.subtitle')}</p>
          <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-muted">
            <div className="h-2 rounded-full bg-primary transition-all" style={{ width: `${progress}%` }} />
          </div>
          <div className="mt-3 grid grid-cols-4 gap-2">
            {stepLabels.map((label, i) => {
              const n = (i + 1) as 1 | 2 | 3 | 4;
              const active = n === step;
              const done = n < step;
              return (
                <div key={label} className="flex items-center gap-2">
                  <span
                    className={
                      "inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-semibold " +
                      (done ? "bg-primary text-primary-foreground" : active ? "bg-primary/80 text-white" : "bg-muted text-muted-foreground")
                    }
                  >
                    {n}
                  </span>
                  <span className={"text-xs " + (active ? "text-foreground" : "text-muted-foreground")}>{label}</span>
                </div>
              );
            })}
          </div>
          <p className="mt-2 text-sm text-muted-foreground">{t('digital.step.hint')} {step} of 4</p>
        </CardHeader>
        <Form {...form}>
          <form onSubmit={(e)=>{ e.preventDefault(); step < 4 ? onNext() : onGenerate(); }}>
            <CardContent className="space-y-6">
              {step === 1 && (
                <div className="space-y-4 rounded-xl border bg-muted/30 p-5">
                  <h3 className="font-semibold">{t('digital.step1.title')}</h3>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <FormField control={form.control} name="fullName" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Full Name</FormLabel>
                        <FormControl>
                          <Input placeholder="Your full name" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="dob" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Date of Birth</FormLabel>
                        <FormControl>
                          <DateField value={field.value} onChange={field.onChange} placeholder="Pick a date" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="gender" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Gender</FormLabel>
                        <FormControl>
                          <Select value={field.value} onValueChange={field.onChange}>
                            <SelectTrigger><SelectValue placeholder={t('generic.select')} /></SelectTrigger>
                            <SelectContent>
                              <SelectItem value="male">Male</SelectItem>
                              <SelectItem value="female">Female</SelectItem>
                              <SelectItem value="other">Other</SelectItem>
                            </SelectContent>
                          </Select>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="nationality" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Nationality</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g., Indian" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <FormField control={form.control} name="aadhaarNumber" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Aadhaar Number</FormLabel>
                        <FormControl>
                          <div className="flex gap-2">
                            <Input placeholder="12-digit Aadhaar" inputMode="numeric" maxLength={12} {...field} />
                            <Button type="button" variant="secondary" onClick={verifyAadhaar}>Verify</Button>
                          </div>
                        </FormControl>
                        {aadhaarVerified ? (
                          <p className="text-green-600 flex items-center gap-1 text-xs"><CheckCircle className="h-3 w-3" /> Verified</p>
                        ) : (
                          <FormMessage />
                        )}
                      </FormItem>
                    )} />
                    <div />
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <FormItem>
                      <FormLabel>Upload Aadhaar/Passport</FormLabel>
                      <Input type="file" accept="image/*,application/pdf" onChange={(e)=>{
                        const f = e.target.files?.[0];
                        form.setValue("idDoc", f as any, { shouldValidate: false });
                      }} />
                      <p className="text-xs text-muted-foreground">Image or PDF</p>
                    </FormItem>
                    <FormItem>
                      <FormLabel>Upload Selfie</FormLabel>
                      <Input type="file" accept="image/*" onChange={(e)=>{
                        const f = e.target.files?.[0];
                        form.setValue("selfie", f as any, { shouldValidate: false });
                      }} />
                      <p className="text-xs text-muted-foreground">Clear face photo</p>
                    </FormItem>
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <FormField control={form.control} name="mobile" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Mobile (OTP)</FormLabel>
                        <FormControl>
                          <div className="flex gap-2">
                            <Input placeholder="+91 98765 43210" {...field} />
                            <Button type="button" variant="secondary" onClick={sendOtp}>{otpSent ? "Resend" : "Send OTP"}</Button>
                          </div>
                        </FormControl>
                        <FormMessage />
                        {otpSent && generatedOtp && !mobileVerified && (
                          <p className="text-xs text-amber-600 mt-1">Demo OTP: <span className="font-semibold">{generatedOtp}</span></p>
                        )}
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="otp" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Enter OTP</FormLabel>
                        <FormControl>
                          <div className="flex gap-2">
                            <Input placeholder="123456" inputMode="numeric" maxLength={6} {...field} />
                            <Button type="button" onClick={verifyOtp} variant="secondary">Verify</Button>
                          </div>
                        </FormControl>
                        {mobileVerified ? (
                          <p className="text-green-600 flex items-center gap-1 text-xs"><CheckCircle className="h-3 w-3" /> Mobile verified</p>
                        ) : (
                          <FormMessage />
                        )}
                      </FormItem>
                    )} />
                  </div>

                  <FormField control={form.control} name="email" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input placeholder="you@example.com" type="email" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                </div>
              )}

              {step === 2 && (
                <div className="space-y-4 rounded-xl border bg-muted/30 p-5">
                  <h3 className="font-semibold">{t('digital.step2.title')}</h3>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <FormField control={form.control} name="arrival" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Arrival Date</FormLabel>
                        <FormControl>
                          <DateField value={field.value} onChange={field.onChange} placeholder="Select arrival" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="departure" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Departure Date</FormLabel>
                        <FormControl>
                          <DateField value={field.value} onChange={field.onChange} placeholder="Select departure" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                  </div>

                  {tripLengthDays !== null && (
                    <div className="text-sm text-muted-foreground">{t('digital.trip.length')}: <span className="font-medium text-foreground">{tripLengthDays} day(s)</span></div>
                  )}

                  <div className="space-y-2">
                    <FormLabel>Destinations</FormLabel>
                    <div className="space-y-2">
                      {destinationFields.map((field, idx) => (
                        <div key={field.id} className="flex gap-2">
                          <FormField
                            control={form.control}
                            name={`destinations.${idx}`}
                            render={({ field }) => (
                              <FormItem className="flex-1">
                                <FormControl>
                                  <Select value={field.value} onValueChange={field.onChange}>
                                    <SelectTrigger>
                                      <SelectValue placeholder={`Destination ${idx + 1}`} />
                                    </SelectTrigger>
                                    <SelectContent>
                                      {DESTINATIONS.map((d) => (
                                        <SelectItem key={d} value={d}>{d}</SelectItem>
                                      ))}
                                    </SelectContent>
                                  </Select>
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            onClick={() => removeDestination(idx)}
                            aria-label="Remove destination"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                      <Button type="button" variant="outline" onClick={() => addDestination("")}>
                        <Plus className="mr-2 h-4 w-4" /> {t('digital.add.destination')}
                      </Button>
                    </div>
                  </div>

                  <FormField control={form.control} name="itinerary" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Itinerary Details (optional)</FormLabel>
                      <FormControl>
                        <Textarea rows={4} placeholder="Activities, notes, references" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <FormField control={form.control} name="travelMode" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Mode of Travel</FormLabel>
                        <FormControl>
                          <Select value={field.value} onValueChange={field.onChange}>
                            <SelectTrigger><SelectValue placeholder={t('generic.select')} /></SelectTrigger>
                            <SelectContent>
                              <SelectItem value="flight">Flight</SelectItem>
                              <SelectItem value="train">Train</SelectItem>
                              <SelectItem value="road">Road</SelectItem>
                            </SelectContent>
                          </Select>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="accommodationName" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Accommodation Name</FormLabel>
                        <FormControl>
                          <Input placeholder="Hotel/Hostel name" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <FormField control={form.control} name="accommodationAddress" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Accommodation Address</FormLabel>
                        <FormControl>
                          <Input placeholder="Street, City, PIN" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="bookingRef" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Booking Reference (optional)</FormLabel>
                        <FormControl>
                          <Input placeholder="#ABC123" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                  </div>
                </div>
              )}

              {step === 3 && (
                <div className="space-y-4 rounded-xl border bg-muted/30 p-5">
                  <h3 className="font-semibold">{t('digital.step3.title')}</h3>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                    <FormField control={form.control} name="emergencyPrimaryName" render={({ field }) => (
                      <FormItem className="sm:col-span-1">
                        <FormLabel>Primary Contact Name</FormLabel>
                        <FormControl><Input placeholder="Name" {...field} /></FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="emergencyPrimaryRelation" render={({ field }) => (
                      <FormItem className="sm:col-span-1">
                        <FormLabel>Relation</FormLabel>
                        <FormControl><Input placeholder="e.g., Parent" {...field} /></FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="emergencyPrimaryPhone" render={({ field }) => (
                      <FormItem className="sm:col-span-1">
                        <FormLabel>Phone</FormLabel>
                        <FormControl><Input placeholder="+91 ..." {...field} /></FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                    <FormField control={form.control} name="emergencySecondaryName" render={({ field }) => (
                      <FormItem className="sm:col-span-1">
                        <FormLabel>Secondary Contact (optional)</FormLabel>
                        <FormControl><Input placeholder="Name" {...field} /></FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="emergencySecondaryRelation" render={({ field }) => (
                      <FormItem className="sm:col-span-1">
                        <FormLabel>Relation</FormLabel>
                        <FormControl><Input placeholder="Relation" {...field} /></FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="emergencySecondaryPhone" render={({ field }) => (
                      <FormItem className="sm:col-span-1">
                        <FormLabel>Phone</FormLabel>
                        <FormControl><Input placeholder="+91 ..." {...field} /></FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <FormField control={form.control} name="bloodGroup" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Blood Group (optional)</FormLabel>
                        <FormControl>
                          <Select value={field.value} onValueChange={field.onChange}>
                            <SelectTrigger><SelectValue placeholder={t('generic.select')} /></SelectTrigger>
                            <SelectContent>
                              {(["A+","A-","B+","B-","AB+","AB-","O+","O-"] as const).map(bg => (
                                <SelectItem key={bg} value={bg}>{bg}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                    <FormField control={form.control} name="allergies" render={({ field }) => (
                      <FormItem>
                        <FormLabel>Allergies (optional)</FormLabel>
                        <FormControl><Input placeholder="e.g., Penicillin" {...field} /></FormControl>
                        <FormMessage />
                      </FormItem>
                    )} />
                  </div>

                  <FormField control={form.control} name="locationConsent" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Location sharing consent</FormLabel>
                      <FormControl>
                        <RadioGroup value={field.value} onValueChange={field.onChange} className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="family" id="consent-family" />
                            <label htmlFor="consent-family">Family</label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="authorities" id="consent-authorities" />
                            <label htmlFor="consent-authorities">Authorities</label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="none" id="consent-none" />
                            <label htmlFor="consent-none">None</label>
                          </div>
                        </RadioGroup>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                </div>
              )}

              {step === 4 && (
                <div className="space-y-4 rounded-xl border bg-muted/30 p-5">
                  <h3 className="font-semibold">{t('digital.step4.title')}</h3>
                  <div className="space-y-2 text-sm">
                    <p className="text-muted-foreground">{t('digital.preview')}</p>
                    <pre className="whitespace-pre-wrap rounded-md bg-muted p-4 text-xs">
{JSON.stringify(form.getValues(), (key, val) => (val instanceof File ? { name: val.name, size: val.size } : val), 2)}
                    </pre>
                  </div>
                  <FormField control={form.control} name="consent" render={({ field }) => (
                    <FormItem className="flex items-start space-x-2 space-y-0">
                      <Checkbox id="consent" checked={!!field.value} onCheckedChange={(v)=> field.onChange(Boolean(v))} />
                      <div className="grid gap-1.5 leading-none">
                        <FormLabel htmlFor="consent" className="font-normal">
                          {t('digital.consent')}
                        </FormLabel>
                        <FormMessage />
                      </div>
                    </FormItem>
                  )} />

                  {generated && null}
                </div>
              )}
            </CardContent>

            <CardFooter className="flex items-center justify-between border-t pt-4">
              <div className="text-sm text-muted-foreground">{t('digital.hint.navigate')}</div>
              <div className="flex gap-2">
                <Button size="lg" type="button" variant="outline" onClick={onPrev} disabled={step === 1}>{t('digital.btn.back')}</Button>
                {step < 4 ? (
                  <Button size="lg" type="submit">{t('digital.btn.next')}</Button>
                ) : (
                  <Button size="lg" type="submit" onClick={onGenerate}>{t('digital.btn.generate')}</Button>
                )}
              </div>
            </CardFooter>
          </form>
        </Form>
      </Card>
      {processing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-3 rounded-lg border bg-card p-6 text-center shadow-lg">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
            <p className="text-sm font-medium">Securing Digital ID on blockchain…</p>
            <p className="text-xs text-muted-foreground">This may take a few seconds.</p>
          </div>
        </div>
      )}
    </div>
  );
}
