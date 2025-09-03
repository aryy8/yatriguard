import React from "react";
import { NavLink } from "react-router-dom";
import { Home, MapPin, Calendar, Shield, Settings } from "lucide-react";
import { useI18n } from "@/i18n/I18nProvider";

const navItems = [
  { to: "/", icon: Home, key: "nav.home" },
  { to: "/dashboard", icon: Shield, key: "nav.dashboard" },
  { to: "/map", icon: MapPin, key: "nav.map" },
  { to: "/itinerary", icon: Calendar, key: "nav.trip" },
  { to: "/settings", icon: Settings, key: "nav.settings" },
];

export const Navigation: React.FC = () => {
  const { t } = useI18n();
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-card border-t border-border z-40">
      <div className="flex justify-around items-center py-2">
        {navItems.map(({ to, icon: Icon, key }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex flex-col items-center py-2 px-3 rounded-lg transition-all duration-200 ${
                isActive
                  ? "text-primary bg-primary/10"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
              }`
            }
          >
            <Icon className="w-5 h-5 mb-1" />
            <span className="text-xs font-medium">{t(key)}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
};