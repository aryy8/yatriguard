import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading
import time
from datetime import datetime
import math
import socket
import requests
from typing import List, Dict, Optional

class TouristApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SafeTravel - Tourist Safety App")
        self.root.geometry("400x600")
        self.root.configure(bg='#f0f9ff')
        
        # App state
        self.current_location = None
        self.is_tracking = False
        self.tracking_thread = None
        self.my_alerts = []
        self.user_id = f"tourist_{int(time.time())}"
        self.admin_server = "localhost:8080"  # Connection to admin system
        
        # Demo locations for testing
        self.demo_mode = False
        self.demo_locations = [
            {'lat': 26.9000, 'lng': 75.7800, 'name': 'Safe Area - Market'},
            {'lat': 26.9124, 'lng': 75.7873, 'name': 'DANGER - Military Zone'},
            {'lat': 26.9200, 'lng': 75.8000, 'name': 'RESTRICTED - Wildlife Area'},
            {'lat': 26.9300, 'lng': 75.8100, 'name': 'Safe Area - Hotel District'},
        ]
        self.demo_index = 0
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup tourist-friendly mobile-like interface"""
        # Header
        header_frame = tk.Frame(self.root, bg='#0ea5e9', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="🛡️ SafeTravel",
            font=('Arial', 18, 'bold'),
            bg='#0ea5e9',
            fg='white'
        ).pack(pady=20)
        
        # Main content
        main_frame = tk.Frame(self.root, bg='#f0f9ff')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Safety Status Card
        self.setup_safety_status(main_frame)
        
        # Location Card
        self.setup_location_card(main_frame)
        
        # Quick Actions
        self.setup_quick_actions(main_frame)
        
        # Recent Alerts
        self.setup_alerts_section(main_frame)
        
    def setup_safety_status(self, parent):
        """Safety status indicator"""
        status_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        status_frame.pack(fill='x', pady=(0,15))
        
        tk.Label(
            status_frame,
            text="Safety Status",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#374151'
        ).pack(pady=(10,5))
        
        self.safety_indicator = tk.Label(
            status_frame,
            text="🟢 SAFE AREA",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#059669'
        )
        self.safety_indicator.pack(pady=10)
        
        self.safety_message = tk.Label(
            status_frame,
            text="You are in a safe zone",
            font=('Arial', 10),
            bg='white',
            fg='#6b7280'
        )
        self.safety_message.pack(pady=(0,15))
        
    def setup_location_card(self, parent):
        """Current location display"""
        location_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        location_frame.pack(fill='x', pady=(0,15))
        
        tk.Label(
            location_frame,
            text="📍 Current Location",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#374151'
        ).pack(pady=(10,5))
        
        self.location_label = tk.Label(
            location_frame,
            text="Location not available\nEnable GPS tracking",
            font=('Arial', 10),
            bg='white',
            fg='#6b7280',
            justify='center'
        )
        self.location_label.pack(pady=10)
        
        self.accuracy_label = tk.Label(
            location_frame,
            text="",
            font=('Arial', 8),
            bg='white',
            fg='#9ca3af'
        )
        self.accuracy_label.pack(pady=(0,15))
        
    def setup_quick_actions(self, parent):
        """Quick action buttons"""
        actions_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        actions_frame.pack(fill='x', pady=(0,15))
        
        tk.Label(
            actions_frame,
            text="Quick Actions",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#374151'
        ).pack(pady=(10,5))
        
        # GPS Enable/Demo button
        self.gps_button = tk.Button(
            actions_frame,
            text="🎯 Enable GPS Tracking",
            command=self.enable_gps,
            bg='#3b82f6',
            fg='white',
            font=('Arial', 11, 'bold'),
            width=25,
            pady=8
        )
        self.gps_button.pack(pady=5)
        
        # Start/Stop tracking
        self.tracking_button = tk.Button(
            actions_frame,
            text="▶️ Start Safety Tracking",
            command=self.toggle_tracking,
            bg='#10b981',
            fg='white',
            font=('Arial', 11, 'bold'),
            width=25,
            pady=8,
            state='disabled'
        )
        self.tracking_button.pack(pady=5)
        
        # Simulate movement (demo only)
        self.move_button = tk.Button(
            actions_frame,
            text="🚶 Move to Next Location",
            command=self.simulate_movement,
            bg='#f59e0b',
            fg='white',
            font=('Arial', 10),
            width=25,
            pady=6,
            state='disabled'
        )
        self.move_button.pack(pady=5)
        
        # Emergency button
        emergency_button = tk.Button(
            actions_frame,
            text="🚨 EMERGENCY HELP",
            command=self.emergency_alert,
            bg='#ef4444',
            fg='white',
            font=('Arial', 11, 'bold'),
            width=25,
            pady=8
        )
        emergency_button.pack(pady=(10,15))
        
    def setup_alerts_section(self, parent):
        """Recent alerts section"""
        alerts_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        alerts_frame.pack(fill='both', expand=True)
        
        header_frame = tk.Frame(alerts_frame, bg='white')
        header_frame.pack(fill='x', pady=(10,5))
        
        tk.Label(
            header_frame,
            text="⚠️ Safety Alerts",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#374151'
        ).pack(side='left', padx=(10,0))
        
        self.alert_count = tk.Label(
            header_frame,
            text="0",
            font=('Arial', 10, 'bold'),
            bg='#ef4444',
            fg='white',
            padx=8,
            pady=2
        )
        self.alert_count.pack(side='right', padx=(0,10))
        
        # Alerts list
        self.alerts_frame = tk.Frame(alerts_frame, bg='white')
        self.alerts_frame.pack(fill='both', expand=True, padx=10, pady=(0,10))
        
        self.no_alerts_label = tk.Label(
            self.alerts_frame,
            text="🟢 No alerts - Stay safe!",
            font=('Arial', 10),
            bg='white',
            fg='#059669'
        )
        self.no_alerts_label.pack(expand=True)
        
    def enable_gps(self):
        """Enable GPS (demo mode for testing)"""
        self.demo_mode = True
        self.current_location = self.demo_locations[0].copy()
        
        self.gps_button.config(text="✅ GPS Active (Demo)", state='disabled')
        self.tracking_button.config(state='normal')
        self.move_button.config(state='normal')
        
        self.update_location_display()
        messagebox.showinfo("GPS Enabled", "Demo GPS activated!\nYou can now start safety tracking.")
        
    def simulate_movement(self):
        """Move to next demo location"""
        if not self.demo_mode:
            return
            
        self.demo_index = (self.demo_index + 1) % len(self.demo_locations)
        self.current_location = self.demo_locations[self.demo_index].copy()
        
        self.update_location_display()
        
        # Send location to admin system
        if self.is_tracking:
            self.send_location_to_admin()
            
    def toggle_tracking(self):
        """Start/Stop safety tracking"""
        if not self.is_tracking:
            self.start_tracking()
        else:
            self.stop_tracking()
            
    def start_tracking(self):
        """Start safety tracking"""
        self.is_tracking = True
        self.tracking_button.config(text="⏹️ Stop Tracking", bg='#ef4444')
        
        def tracking_loop():
            while self.is_tracking:
                if self.current_location:
                    self.send_location_to_admin()
                time.sleep(5)  # Send location every 5 seconds
                
        self.tracking_thread = threading.Thread(target=tracking_loop, daemon=True)
        self.tracking_thread.start()
        
        messagebox.showinfo("Tracking Started", "Safety tracking is now active!\nWe'll monitor your location for safety.")
        
    def stop_tracking(self):
        """Stop safety tracking"""
        self.is_tracking = False
        self.tracking_button.config(text="▶️ Start Safety Tracking", bg='#10b981')
        messagebox.showinfo("Tracking Stopped", "Safety tracking has been stopped.")
        
    def send_location_to_admin(self):
        """Send current location to admin system (simulated)"""
        if not self.current_location:
            return
            
        try:
            # Simulate API call to admin system
            data = {
                'user_id': self.user_id,
                'location': self.current_location,
                'timestamp': datetime.now().isoformat()
            }
            
            # In real implementation, this would be:
            # response = requests.post(f"http://{self.admin_server}/api/location", json=data)
            
            # Simulate zone check response
            zone_check = self.simulate_zone_check(self.current_location)
            if zone_check['in_danger']:
                self.handle_danger_alert(zone_check)
            else:
                self.update_safety_status(True)
                
        except Exception as e:
            print(f"Error sending location: {e}")
            
    def simulate_zone_check(self, location):
        """Simulate admin system checking if location is in danger zone"""
        # This simulates the response from admin system
        location_name = location.get('name', '')
        
        if 'DANGER' in location_name or 'RESTRICTED' in location_name:
            return {
                'in_danger': True,
                'zone_name': location_name.split(' - ')[1] if ' - ' in location_name else 'Restricted Area',
                'zone_type': 'Military' if 'Military' in location_name else 'Wildlife',
                'severity': 'HIGH',
                'message': 'You have entered a restricted area. Please leave immediately!'
            }
        else:
            return {
                'in_danger': False,
                'message': 'Safe area'
            }
            
    def handle_danger_alert(self, alert_data):
        """Handle danger zone alert"""
        alert = {
            'id': len(self.my_alerts) + 1,
            'timestamp': datetime.now(),
            'zone_name': alert_data['zone_name'],
            'zone_type': alert_data['zone_type'],
            'severity': alert_data['severity'],
            'message': alert_data['message'],
            'location': self.current_location.copy()
        }
        
        self.my_alerts.insert(0, alert)
        
        # Update UI
        self.update_safety_status(False, alert_data['zone_name'])
        self.update_alerts_display()
        
        # Show urgent popup
        messagebox.showwarning(
            "🚨 SAFETY ALERT",
            f"DANGER ZONE DETECTED!\n\n"
            f"Zone: {alert_data['zone_name']}\n"
            f"Severity: {alert_data['severity']}\n\n"
            f"{alert_data['message']}\n\n"
            f"Your location has been reported to authorities."
        )
        
    def update_safety_status(self, is_safe, zone_name=None):
        """Update safety status indicator"""
        if is_safe:
            self.safety_indicator.config(
                text="🟢 SAFE AREA",
                fg='#059669'
            )
            self.safety_message.config(
                text="You are in a safe zone",
                fg='#6b7280'
            )
        else:
            self.safety_indicator.config(
                text="🔴 DANGER ZONE",
                fg='#dc2626'
            )
            self.safety_message.config(
                text=f"WARNING: {zone_name}",
                fg='#dc2626'
            )
            
    def update_location_display(self):
        """Update current location display"""
        if self.current_location:
            location_text = (
                f"Lat: {self.current_location['lat']:.6f}\n"
                f"Lng: {self.current_location['lng']:.6f}"
            )
            
            if 'name' in self.current_location:
                location_text = f"{self.current_location['name']}\n{location_text}"
                
            self.location_label.config(text=location_text, fg='#374151')
            self.accuracy_label.config(text="Demo Mode - Simulated GPS")
            
    def update_alerts_display(self):
        """Update alerts display"""
        # Clear existing alerts
        for widget in self.alerts_frame.winfo_children():
            widget.destroy()
            
        self.alert_count.config(text=str(len(self.my_alerts)))
        
        if not self.my_alerts:
            self.no_alerts_label = tk.Label(
                self.alerts_frame,
                text="🟢 No alerts - Stay safe!",
                font=('Arial', 10),
                bg='white',
                fg='#059669'
            )
            self.no_alerts_label.pack(expand=True)
        else:
            # Show recent alerts
            for i, alert in enumerate(self.my_alerts[:3]):  # Show last 3 alerts
                alert_frame = tk.Frame(self.alerts_frame, bg='#fef2f2', relief='solid', bd=1)
                alert_frame.pack(fill='x', pady=2)
                
                tk.Label(
                    alert_frame,
                    text=f"🚨 {alert['zone_name']}",
                    font=('Arial', 9, 'bold'),
                    bg='#fef2f2',
                    fg='#dc2626'
                ).pack(anchor='w', padx=8, pady=2)
                
                tk.Label(
                    alert_frame,
                    text=f"{alert['timestamp'].strftime('%H:%M:%S')} - {alert['severity']}",
                    font=('Arial', 8),
                    bg='#fef2f2',
                    fg='#991b1b'
                ).pack(anchor='w', padx=8, pady=(0,5))
                
    def emergency_alert(self):
        """Send emergency alert"""
        if messagebox.askyesno("Emergency Alert", "Send emergency alert to authorities?"):
            emergency_data = {
                'user_id': self.user_id,
                'type': 'EMERGENCY',
                'location': self.current_location,
                'timestamp': datetime.now().isoformat(),
                'message': 'Tourist emergency - immediate assistance needed'
            }
            
            # In real app: send to emergency services
            messagebox.showinfo(
                "Emergency Alert Sent",
                "Emergency alert sent to authorities!\n\n"
                "Help is on the way.\n"
                "Stay calm and stay where you are if safe."
            )
            
    def run(self):
        """Start the tourist app"""
        self.root.mainloop()

# Communication module for connecting with admin system
class AdminConnector:
    def __init__(self, server_url="http://localhost:8080"):
        self.server_url = server_url
        
    def send_location(self, user_data):
        """Send location data to admin system"""
        try:
            response = requests.post(f"{self.server_url}/api/tourist/location", json=user_data, timeout=5)
            return response.json()
        except Exception as e:
            print(f"Failed to connect to admin system: {e}")
            return {'status': 'offline', 'in_danger': False}
            
    def get_zones(self):
        """Get current red zones from admin system"""
        try:
            response = requests.get(f"{self.server_url}/api/zones", timeout=5)
            return response.json()
        except Exception as e:
            print(f"Failed to get zones: {e}")
            return []
            
    def send_emergency(self, emergency_data):
        """Send emergency alert to admin system"""
        try:
            response = requests.post(f"{self.server_url}/api/emergency", json=emergency_data, timeout=5)
            return response.json()
        except Exception as e:
            print(f"Failed to send emergency alert: {e}")
            return {'status': 'error'}

if __name__ == "__main__":
    print("🛡️ SafeTravel - Tourist Safety App")
    print("Features:")
    print("- Real-time location tracking")
    print("- Automatic danger zone detection")
    print("- Safety alerts and notifications")  
    print("- Emergency assistance")
    print("- Connection to admin monitoring system")
    print("\nStarting Tourist App...")
    
    app = TouristApp()
    app.run()