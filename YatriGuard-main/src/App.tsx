import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { useEffect } from "react";
import { I18nProvider } from "./i18n/I18nProvider";
import { YatriGuardLayout } from "./components/YatriGuardLayout";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Map from "./pages/Map";
import Onboarding from "./pages/Onboarding";
import NotFound from "./pages/NotFound";
import DigitalID from "./pages/DigitalID";
import SignIn from "./pages/SignIn";

const queryClient = new QueryClient();

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    // Use instant scroll on route changes
    window.scrollTo({ top: 0, left: 0, behavior: "instant" as ScrollBehavior });
  }, [pathname]);
  return null;
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <I18nProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <ScrollToTop />
          <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route 
            path="/digital-id"
            element={
              <YatriGuardLayout>
                <DigitalID />
              </YatriGuardLayout>
            }
          />
          <Route 
            path="/signin"
            element={
              <YatriGuardLayout>
                <SignIn />
              </YatriGuardLayout>
            }
          />
          <Route 
            path="/dashboard" 
            element={
              <YatriGuardLayout>
                <Dashboard />
              </YatriGuardLayout>
            } 
          />
          <Route 
            path="/map" 
            element={
              <YatriGuardLayout>
                <Map />
              </YatriGuardLayout>
            } 
          />
          <Route 
            path="/itinerary" 
            element={
              <YatriGuardLayout>
                <div className="container mx-auto px-4 py-6">
                  <h1 className="text-2xl font-bold mb-4">Trip Itinerary</h1>
                  <p className="text-muted-foreground">Coming soon - Plan and manage your travel itinerary</p>
                </div>
              </YatriGuardLayout>
            } 
          />
          <Route 
            path="/settings" 
            element={
              <YatriGuardLayout>
                <div className="container mx-auto px-4 py-6">
                  <h1 className="text-2xl font-bold mb-4">Settings</h1>
                  <p className="text-muted-foreground">Coming soon - Privacy settings and app configuration</p>
                </div>
              </YatriGuardLayout>
            } 
          />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </I18nProvider>
  </QueryClientProvider>
);

export default App;
