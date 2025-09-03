import React from "react";
import { Outlet, useLocation } from "react-router-dom";
import { SOSButton } from "./SOSButton";
import { Navigation } from "./Navigation";

interface YatriGuardLayoutProps {
  children?: React.ReactNode;
}

export const YatriGuardLayout: React.FC<YatriGuardLayoutProps> = ({ children }) => {
  const { pathname } = useLocation();
  const showBottomNav = pathname === "/dashboard"; // show nav only on Dashboard

  return (
    <div className="min-h-screen bg-background relative">
      {/* Main Content */}
      <main className={showBottomNav ? "pb-20" : "pb-0"}>
        {children || <Outlet />}
      </main>

      {/* Bottom Navigation (Dashboard only) */}
      {showBottomNav && <Navigation />}

      {/* Always Visible SOS Button */}
      <SOSButton />
    </div>
  );
};