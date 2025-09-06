import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading
import time
from datetime import datetime
import math
import requests
from typing import List, Dict, Tuple, Optional

class RedZoneDetectionSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Red Zone & Geo-Fence Breach Detection System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f8ff')
        
        # System state
        self.current_location = None
        self.is_monitoring = False
        self.monitoring_thread = None
        self.alerts = []
        self.red_zones = [
            {
                'id': 1,
                'name': 'Military Zone Alpha',
                'type': 'Military',
                'coordinates': [
                    {'lat': 26.9124, 'lng': 75.7873},
                    {'lat': 26.9150, 'lng': 75.7900},
                    {'lat': 26.9100, 'lng': 75.7950},
                    {'lat': 26.9080, 'lng': 75.7920}
                ]
            },
            {
                'id': 2,
                'name': 'Wildlife Sanctuary - Restricted Area',
                'type': 'Wildlife',
                'coordinates': [
                    {'lat': 26.9200, 'lng': 75.8000},
                    {'lat': 26.9250, 'lng': 75.8050},
                    {'lat': 26.9200, 'lng': 75.8100},
                    {'lat': 26.9150, 'lng': 75.8050}
                ]
            }
        ]
        
        # For demo/simulation
        self.demo_mode = False
        self.demo_locations = [
            {'lat': 26.9124, 'lng': 75.7873},  # Inside Military Zone
            {'lat': 26.9200, 'lng': 75.8000},  # Inside Wildlife Zone
            {'lat': 26.9000, 'lng': 75.7800},  # Outside zones
        ]
        self.demo_index = 0
        
        self.setup_gui()
        
    def setup_gui(self):
        """Initialize the GUI components"""
        # Main title
        title_frame = tk.Frame(self.root, bg='#f0f8ff')
        title_frame.pack(fill='x', padx=20, pady=10)
        
        title_label = tk.Label(
            title_frame, 
            text="🛡️ Red Zone Detection System",
            font=('Arial', 20, 'bold'),
            bg='#f0f8ff',
            fg='#1e3a8a'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="GPS-based geo-fence breach monitoring",
            font=('Arial', 12),
            bg='#f0f8ff',
            fg='#6b7280'
        )
        subtitle_label.pack()
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#f0f8ff')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create three columns
        self.setup_gps_panel(main_frame)
        self.setup_zones_panel(main_frame)
        self.setup_alerts_panel(main_frame)
        
        # Status bar
        self.setup_status_bar()
        
    def setup_gps_panel(self, parent):
        """Setup GPS control panel"""
        gps_frame = tk.LabelFrame(
            parent,
            text="📍 GPS Control",
            font=('Arial', 12, 'bold'),
            bg='white',
            padx=10,
            pady=10
        )
        gps_frame.grid(row=0, column=0, sticky='nsew', padx=5)
        
        # GPS status
        self.gps_status_label = tk.Label(
            gps_frame,
            text="GPS Status: Not Connected",
            font=('Arial', 10),
            bg='white'
        )
        self.gps_status_label.pack(pady=5)
        
        # Location display
        location_frame = tk.Frame(gps_frame, bg='white')
        location_frame.pack(fill='x', pady=5)
        
        tk.Label(location_frame, text="Current Location:", bg='white', font=('Arial', 9, 'bold')).pack()
        self.location_text = scrolledtext.ScrolledText(
            location_frame,
            height=3,
            width=30,
            font=('Arial', 8)
        )
        self.location_text.pack(fill='x', pady=2)
        
        # Control buttons
        button_frame = tk.Frame(gps_frame, bg='white')
        button_frame.pack(fill='x', pady=10)
        
        self.gps_button = tk.Button(
            button_frame,
            text="🎭 Enable Demo Mode",
            command=self.enable_demo_mode,
            bg='#10b981',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        self.gps_button.pack(fill='x', pady=2)
        
        self.monitor_button = tk.Button(
            button_frame,
            text="▶️ Start Monitoring",
            command=self.toggle_monitoring,
            bg='#059669',
            fg='white',
            font=('Arial', 10, 'bold'),
            state='disabled'
        )
        self.monitor_button.pack(fill='x', pady=2)
        
        # Simulate movement button (for demo)
        self.move_button = tk.Button(
            button_frame,
            text="🚶 Simulate Movement",
            command=self.simulate_movement,
            bg='#3b82f6',
            fg='white',
            font=('Arial', 9),
            state='disabled'
        )
        self.move_button.pack(fill='x', pady=2)
        
    def setup_zones_panel(self, parent):
        """Setup red zones management panel"""
        zones_frame = tk.LabelFrame(
            parent,
            text="⚙️ Red Zones Management",
            font=('Arial', 12, 'bold'),
            bg='white',
            padx=10,
            pady=10
        )
        zones_frame.grid(row=0, column=1, sticky='nsew', padx=5)
        
        # Add new zone section
        add_frame = tk.LabelFrame(zones_frame, text="Add New Zone", bg='#f9fafb', padx=5, pady=5)
        add_frame.pack(fill='x', pady=5)
        
        tk.Label(add_frame, text="Zone Name:", bg='#f9fafb').pack(anchor='w')
        self.zone_name_entry = tk.Entry(add_frame, width=30)
        self.zone_name_entry.pack(fill='x', pady=2)
        
        tk.Label(add_frame, text="Zone Type:", bg='#f9fafb').pack(anchor='w')
        self.zone_type_var = tk.StringVar()
        zone_type_combo = ttk.Combobox(
            add_frame,
            textvariable=self.zone_type_var,
            values=['Military', 'Wildlife', 'Border', 'Crime'],
            state='readonly'
        )
        zone_type_combo.pack(fill='x', pady=2)
        
        tk.Button(
            add_frame,
            text="➕ Add Sample Zone",
            command=self.add_sample_zone,
            bg='#8b5cf6',
            fg='white',
            font=('Arial', 9)
        ).pack(fill='x', pady=5)
        
        # Existing zones list
        tk.Label(zones_frame, text="Existing Zones:", bg='white', font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10,5))
        
        self.zones_listbox = tk.Listbox(zones_frame, height=8)
        self.zones_listbox.pack(fill='both', expand=True, pady=2)
        
        zones_button_frame = tk.Frame(zones_frame, bg='white')
        zones_button_frame.pack(fill='x', pady=5)
        
        tk.Button(
            zones_button_frame,
            text="🗑️ Delete Selected",
            command=self.delete_zone,
            bg='#ef4444',
            fg='white',
            font=('Arial', 9)
        ).pack(side='left', padx=2)
        
        tk.Button(
            zones_button_frame,
            text="🔄 Refresh List",
            command=self.refresh_zones_list,
            bg='#6b7280',
            fg='white',
            font=('Arial', 9)
        ).pack(side='right', padx=2)
        
        self.refresh_zones_list()
        
    def setup_alerts_panel(self, parent):
        """Setup alerts panel"""
        alerts_frame = tk.LabelFrame(
            parent,
            text="⚠️ Recent Alerts",
            font=('Arial', 12, 'bold'),
            bg='white',
            padx=10,
            pady=10
        )
        alerts_frame.grid(row=0, column=2, sticky='nsew', padx=5)
        
        # Alert counter
        self.alert_count_label = tk.Label(
            alerts_frame,
            text="Total Alerts: 0",
            bg='white',
            font=('Arial', 10, 'bold')
        )
        self.alert_count_label.pack(pady=5)
        
        # Alerts display
        self.alerts_text = scrolledtext.ScrolledText(
            alerts_frame,
            height=15,
            width=40,
            font=('Arial', 9)
        )
        self.alerts_text.pack(fill='both', expand=True, pady=5)
        
        # Clear alerts button
        tk.Button(
            alerts_frame,
            text="🧹 Clear All Alerts",
            command=self.clear_alerts,
            bg='#6b7280',
            fg='white',
            font=('Arial', 9)
        ).pack(fill='x', pady=5)
        
        # Configure grid weights
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=1)
        
    def setup_status_bar(self):
        """Setup status bar at bottom"""
        status_frame = tk.Frame(self.root, bg='#e5e7eb', relief='sunken', bd=1)
        status_frame.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(
            status_frame,
            text="System Status: Standby | GPS: Inactive | Zones: 2 | Alerts: 0",
            bg='#e5e7eb',
            font=('Arial', 9)
        )
        self.status_label.pack(side='left', padx=10, pady=5)
        
        self.monitoring_indicator = tk.Label(
            status_frame,
            text="🔴 Standby",
            bg='#e5e7eb',
            font=('Arial', 9, 'bold')
        )
        self.monitoring_indicator.pack(side='right', padx=10, pady=5)
        
    def is_point_in_polygon(self, point: Dict, polygon: List[Dict]) -> bool:
        """Point-in-polygon algorithm implementation"""
        lat, lng = point['lat'], point['lng']
        inside = False
        
        j = len(polygon) - 1
        for i in range(len(polygon)):
            xi, yi = polygon[i]['lng'], polygon[i]['lat']
            xj, yj = polygon[j]['lng'], polygon[j]['lat']
            
            if ((yi > lat) != (yj > lat)) and (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
            
        return inside
        
    def check_zone_breaches(self, location: Dict) -> List[Dict]:
        """Check if current location breaches any red zones"""
        breached_zones = []
        
        for zone in self.red_zones:
            if self.is_point_in_polygon(location, zone['coordinates']):
                breached_zones.append(zone)
                
        return breached_zones
        
    def create_alert(self, zone: Dict, location: Dict):
        """Create and display an alert"""
        alert = {
            'id': len(self.alerts) + 1,
            'timestamp': datetime.now(),
            'zone_name': zone['name'],
            'zone_type': zone['type'],
            'location': location,
            'severity': 'HIGH'
        }
        
        self.alerts.insert(0, alert)
        self.update_alerts_display()
        
        # Show popup alert
        messagebox.showwarning(
            "🚨 RED ZONE ALERT",
            f"BREACH DETECTED!\n\n"
            f"Zone: {zone['name']}\n"
            f"Type: {zone['type']}\n"
            f"Time: {alert['timestamp'].strftime('%H:%M:%S')}\n"
            f"Location: {location['lat']:.6f}, {location['lng']:.6f}\n\n"
            f"You have entered a restricted area!"
        )
        
    def enable_demo_mode(self):
        """Enable demo mode with simulated GPS"""
        self.demo_mode = True
        self.current_location = self.demo_locations[0].copy()
        
        self.gps_status_label.config(text="GPS Status: Demo Mode Active", fg='green')
        self.gps_button.config(text="✅ Demo Mode Enabled", state='disabled')
        self.monitor_button.config(state='normal')
        self.move_button.config(state='normal')
        
        self.update_location_display()
        self.update_status_bar()
        
    def simulate_movement(self):
        """Simulate movement to different locations"""
        if not self.demo_mode:
            return
            
        self.demo_index = (self.demo_index + 1) % len(self.demo_locations)
        self.current_location = self.demo_locations[self.demo_index].copy()
        
        self.update_location_display()
        
        if self.is_monitoring:
            breached_zones = self.check_zone_breaches(self.current_location)
            for zone in breached_zones:
                self.create_alert(zone, self.current_location)
                
    def toggle_monitoring(self):
        """Start/Stop monitoring"""
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        """Start monitoring for zone breaches"""
        self.is_monitoring = True
        self.monitor_button.config(text="⏹️ Stop Monitoring", bg='#ef4444')
        self.monitoring_indicator.config(text="🟢 Active", fg='green')
        
        def monitoring_loop():
            while self.is_monitoring:
                if self.current_location:
                    breached_zones = self.check_zone_breaches(self.current_location)
                    for zone in breached_zones:
                        self.create_alert(zone, self.current_location)
                time.sleep(2)  # Check every 2 seconds
                
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.update_status_bar()
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        self.monitor_button.config(text="▶️ Start Monitoring", bg='#059669')
        self.monitoring_indicator.config(text="🔴 Standby", fg='red')
        self.update_status_bar()
        
    def add_sample_zone(self):
        """Add a sample red zone"""
        name = self.zone_name_entry.get().strip()
        zone_type = self.zone_type_var.get()
        
        if not name or not zone_type:
            messagebox.showerror("Error", "Please enter zone name and select type")
            return
            
        # Create sample coordinates around current location or default area
        base_lat = self.current_location['lat'] if self.current_location else 26.9200
        base_lng = self.current_location['lng'] if self.current_location else 75.8000
        
        new_zone = {
            'id': len(self.red_zones) + 1,
            'name': name,
            'type': zone_type,
            'coordinates': [
                {'lat': base_lat, 'lng': base_lng},
                {'lat': base_lat + 0.005, 'lng': base_lng + 0.005},
                {'lat': base_lat + 0.005, 'lng': base_lng - 0.005},
                {'lat': base_lat - 0.005, 'lng': base_lng}
            ]
        }
        
        self.red_zones.append(new_zone)
        self.refresh_zones_list()
        self.zone_name_entry.delete(0, tk.END)
        self.zone_type_var.set('')
        self.update_status_bar()
        
    def delete_zone(self):
        """Delete selected zone"""
        selection = self.zones_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a zone to delete")
            return
            
        index = selection[0]
        if messagebox.askyesno("Confirm Delete", f"Delete zone: {self.red_zones[index]['name']}?"):
            del self.red_zones[index]
            self.refresh_zones_list()
            self.update_status_bar()
            
    def refresh_zones_list(self):
        """Refresh the zones listbox"""
        self.zones_listbox.delete(0, tk.END)
        for zone in self.red_zones:
            self.zones_listbox.insert(
                tk.END,
                f"🚫 {zone['name']} ({zone['type']}) - {len(zone['coordinates'])} points"
            )
            
    def update_location_display(self):
        """Update location display"""
        if self.current_location:
            location_info = (
                f"Latitude: {self.current_location['lat']:.6f}\n"
                f"Longitude: {self.current_location['lng']:.6f}\n"
                f"Mode: {'Demo' if self.demo_mode else 'Real GPS'}\n"
                f"Updated: {datetime.now().strftime('%H:%M:%S')}"
            )
            self.location_text.delete(1.0, tk.END)
            self.location_text.insert(1.0, location_info)
            
    def update_alerts_display(self):
        """Update alerts display"""
        self.alerts_text.delete(1.0, tk.END)
        
        if not self.alerts:
            self.alerts_text.insert(tk.END, "🟢 No alerts - All zones clear\n\n")
        else:
            for alert in self.alerts:
                alert_text = (
                    f"🚨 ALERT #{alert['id']} - {alert['severity']}\n"
                    f"Zone: {alert['zone_name']}\n"
                    f"Type: {alert['zone_type']}\n"
                    f"Time: {alert['timestamp'].strftime('%H:%M:%S')}\n"
                    f"Location: {alert['location']['lat']:.4f}, {alert['location']['lng']:.4f}\n"
                    f"{'-'*40}\n\n"
                )
                self.alerts_text.insert(tk.END, alert_text)
                
        self.alert_count_label.config(text=f"Total Alerts: {len(self.alerts)}")
        self.update_status_bar()
        
    def clear_alerts(self):
        """Clear all alerts"""
        if self.alerts and messagebox.askyesno("Clear Alerts", "Clear all alerts?"):
            self.alerts.clear()
            self.update_alerts_display()
            
    def update_status_bar(self):
        """Update status bar information"""
        status_text = (
            f"System Status: {'Active Monitoring' if self.is_monitoring else 'Standby'} | "
            f"GPS: {'Active' if self.current_location else 'Inactive'} | "
            f"Zones: {len(self.red_zones)} | "
            f"Alerts: {len(self.alerts)}"
        )
        self.status_label.config(text=status_text)
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

# Example usage and additional utilities
def save_zones_to_file(zones: List[Dict], filename: str = 'red_zones.json'):
    """Save red zones to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(zones, f, indent=2)
        print(f"Zones saved to {filename}")
    except Exception as e:
        print(f"Error saving zones: {e}")

def load_zones_from_file(filename: str = 'red_zones.json') -> List[Dict]:
    """Load red zones from JSON file"""
    try:
        with open(filename, 'r') as f:
            zones = json.load(f)
        print(f"Zones loaded from {filename}")
        return zones
    except Exception as e:
        print(f"Error loading zones: {e}")
        return []

def calculate_distance(point1: Dict, point2: Dict) -> float:
    """Calculate distance between two GPS points in meters"""
    lat1, lng1 = math.radians(point1['lat']), math.radians(point1['lng'])
    lat2, lng2 = math.radians(point2['lat']), math.radians(point2['lng'])
    
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371000  # Earth's radius in meters
    
    return c * r

if __name__ == "__main__":
    # Create and run the application
    app = RedZoneDetectionSystem()
    
    print("🛡️ Red Zone Detection System Starting...")
    print("Features:")
    print("- GPS simulation with demo mode")
    print("- Point-in-polygon breach detection")
    print("- Real-time alerts and notifications")
    print("- Red zone management")
    print("- Alert logging and history")
    print("\nStarting GUI...")
    
    app.run()