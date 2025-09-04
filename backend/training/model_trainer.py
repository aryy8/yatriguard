"""
AI/ML Model Training System for YatriGuard
Comprehensive training pipeline for all detection models
"""

import numpy as np
import pandas as pd
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    """Main training orchestrator for all YatriGuard AI/ML models"""
    
    def __init__(self):
        self.models_dir = "trained_models"
        self.data_dir = "training_data"
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create necessary directories for training"""
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(f"{self.data_dir}/fall_detection", exist_ok=True)
        os.makedirs(f"{self.data_dir}/crash_detection", exist_ok=True)
        os.makedirs(f"{self.data_dir}/distress_detection", exist_ok=True)
        os.makedirs(f"{self.data_dir}/red_zone_detection", exist_ok=True)
        
    async def train_all_models(self):
        """Train all AI/ML models in sequence"""
        logger.info("Starting comprehensive model training pipeline...")
        
        try:
            # Generate synthetic training data
            await self.generate_training_data()
            
            # Train individual models
            await self.train_fall_detection_model()
            await self.train_crash_detection_model()
            await self.train_distress_detection_model()
            await self.train_red_zone_model()
            
            logger.info("All models trained successfully!")
            
        except Exception as e:
            logger.error(f"Training pipeline failed: {str(e)}")
            raise
    
    async def generate_training_data(self):
        """Generate synthetic training data for all models"""
        logger.info("Generating synthetic training data...")
        
        # Generate fall detection data
        await self._generate_fall_data()
        
        # Generate crash detection data
        await self._generate_crash_data()
        
        # Generate distress detection data
        await self._generate_distress_data()
        
        # Generate red zone data
        await self._generate_red_zone_data()
        
        logger.info("Training data generation completed")
    
    async def _generate_fall_data(self):
        """Generate synthetic IMU data for fall detection"""
        logger.info("Generating fall detection training data...")
        
        # Normal activity data
        normal_data = []
        for i in range(1000):
            # Simulate normal walking/standing IMU data
            sequence = []
            for j in range(100):  # 100 data points per sequence
                accel_x = np.random.normal(0, 1.5)  # Normal activity
                accel_y = np.random.normal(0, 1.5)
                accel_z = np.random.normal(9.8, 2.0)  # Gravity + movement
                gyro_x = np.random.normal(0, 0.5)
                gyro_y = np.random.normal(0, 0.5)
                gyro_z = np.random.normal(0, 0.5)
                
                sequence.append({
                    'accel_x': accel_x,
                    'accel_y': accel_y,
                    'accel_z': accel_z,
                    'gyro_x': gyro_x,
                    'gyro_y': gyro_y,
                    'gyro_z': gyro_z,
                    'timestamp': j * 0.02  # 50Hz sampling
                })
            
            normal_data.append({
                'sequence': sequence,
                'label': 0,  # No fall
                'fall_type': 'none'
            })
        
        # Fall data
        fall_data = []
        fall_types = ['forward_fall', 'backward_fall', 'side_fall', 'trip']
        
        for fall_type in fall_types:
            for i in range(250):  # 250 samples per fall type
                sequence = self._generate_fall_sequence(fall_type)
                fall_data.append({
                    'sequence': sequence,
                    'label': 1,  # Fall detected
                    'fall_type': fall_type
                })
        
        # Combine and save
        training_data = normal_data + fall_data
        np.random.shuffle(training_data)
        
        with open(f"{self.data_dir}/fall_detection/training_data.json", 'w') as f:
            json.dump(training_data, f, indent=2)
        
        logger.info(f"Generated {len(training_data)} fall detection samples")
    
    def _generate_fall_sequence(self, fall_type: str) -> List[Dict]:
        """Generate realistic fall sequence with three phases"""
        sequence = []
        
        # Phase 1: Pre-fall (normal activity) - 30 samples
        for i in range(30):
            sequence.append({
                'accel_x': np.random.normal(0, 1.5),
                'accel_y': np.random.normal(0, 1.5),
                'accel_z': np.random.normal(9.8, 2.0),
                'gyro_x': np.random.normal(0, 0.5),
                'gyro_y': np.random.normal(0, 0.5),
                'gyro_z': np.random.normal(0, 0.5),
                'timestamp': i * 0.02
            })
        
        # Phase 2: Free fall - 20 samples
        for i in range(30, 50):
            # Sudden drop in acceleration, high gyroscope values
            accel_magnitude = np.random.uniform(0, 2)  # Low acceleration
            gyro_magnitude = np.random.uniform(5, 15)  # High rotation
            
            sequence.append({
                'accel_x': np.random.normal(0, accel_magnitude),
                'accel_y': np.random.normal(0, accel_magnitude),
                'accel_z': np.random.normal(0, accel_magnitude),
                'gyro_x': np.random.normal(0, gyro_magnitude),
                'gyro_y': np.random.normal(0, gyro_magnitude),
                'gyro_z': np.random.normal(0, gyro_magnitude),
                'timestamp': i * 0.02
            })
        
        # Phase 3: Impact and recovery - 50 samples
        for i in range(50, 100):
            if i < 55:  # Impact
                impact_magnitude = np.random.uniform(15, 25)
                sequence.append({
                    'accel_x': np.random.normal(0, impact_magnitude),
                    'accel_y': np.random.normal(0, impact_magnitude),
                    'accel_z': np.random.normal(0, impact_magnitude),
                    'gyro_x': np.random.normal(0, 2),
                    'gyro_y': np.random.normal(0, 2),
                    'gyro_z': np.random.normal(0, 2),
                    'timestamp': i * 0.02
                })
            else:  # Post-impact stillness
                sequence.append({
                    'accel_x': np.random.normal(0, 0.5),
                    'accel_y': np.random.normal(0, 0.5),
                    'accel_z': np.random.normal(9.8, 1.0),
                    'gyro_x': np.random.normal(0, 0.1),
                    'gyro_y': np.random.normal(0, 0.1),
                    'gyro_z': np.random.normal(0, 0.1),
                    'timestamp': i * 0.02
                })
        
        return sequence
    
    async def _generate_crash_data(self):
        """Generate synthetic crash detection data"""
        logger.info("Generating crash detection training data...")
        
        crash_data = []
        
        # Normal driving data
        for i in range(800):
            imu_sequence = []
            speed_sequence = []
            
            # Normal driving with gradual speed changes
            current_speed = np.random.uniform(30, 80)  # km/h
            
            for j in range(50):
                # Normal driving accelerations
                accel_x = np.random.normal(0, 2)
                accel_y = np.random.normal(0, 2)
                accel_z = np.random.normal(9.8, 1)
                
                # Gradual speed changes
                speed_change = np.random.normal(0, 2)
                current_speed = max(0, current_speed + speed_change)
                
                imu_sequence.append({
                    'accel_x': accel_x,
                    'accel_y': accel_y,
                    'accel_z': accel_z,
                    'gyro_x': np.random.normal(0, 1),
                    'gyro_y': np.random.normal(0, 1),
                    'gyro_z': np.random.normal(0, 1),
                    'timestamp': j * 0.1
                })
                
                speed_sequence.append({
                    'speed': current_speed,
                    'timestamp': j * 0.1
                })
            
            crash_data.append({
                'imu_data': imu_sequence,
                'speed_data': speed_sequence,
                'label': 0,  # No crash
                'crash_type': 'none'
            })
        
        # Crash scenarios
        crash_types = ['frontal_collision', 'rear_collision', 'side_collision', 'rollover']
        
        for crash_type in crash_types:
            for i in range(50):
                imu_sequence, speed_sequence = self._generate_crash_sequence(crash_type)
                crash_data.append({
                    'imu_data': imu_sequence,
                    'speed_data': speed_sequence,
                    'label': 1,  # Crash detected
                    'crash_type': crash_type
                })
        
        with open(f"{self.data_dir}/crash_detection/training_data.json", 'w') as f:
            json.dump(crash_data, f, indent=2)
        
        logger.info(f"Generated {len(crash_data)} crash detection samples")
    
    def _generate_crash_sequence(self, crash_type: str) -> Tuple[List[Dict], List[Dict]]:
        """Generate crash sequence with pre-crash, impact, and post-crash phases"""
        imu_sequence = []
        speed_sequence = []
        
        initial_speed = np.random.uniform(40, 90)
        current_speed = initial_speed
        
        # Pre-crash phase (normal driving)
        for i in range(30):
            imu_sequence.append({
                'accel_x': np.random.normal(0, 2),
                'accel_y': np.random.normal(0, 2),
                'accel_z': np.random.normal(9.8, 1),
                'gyro_x': np.random.normal(0, 1),
                'gyro_y': np.random.normal(0, 1),
                'gyro_z': np.random.normal(0, 1),
                'timestamp': i * 0.1
            })
            
            speed_sequence.append({
                'speed': current_speed,
                'timestamp': i * 0.1
            })
        
        # Impact phase
        for i in range(30, 40):
            # Extreme deceleration and impact forces
            impact_decel = np.random.uniform(-15, -25)  # Severe deceleration
            impact_force = np.random.uniform(20, 40)    # High impact
            
            if crash_type == 'frontal_collision':
                accel_x = impact_decel + np.random.normal(0, 5)
                accel_y = np.random.normal(0, impact_force/2)
            elif crash_type == 'side_collision':
                accel_x = np.random.normal(0, impact_force/2)
                accel_y = np.random.choice([-1, 1]) * impact_force + np.random.normal(0, 5)
            else:  # rear_collision, rollover
                accel_x = -impact_decel/2 + np.random.normal(0, 5)
                accel_y = np.random.normal(0, impact_force/2)
            
            current_speed = max(0, current_speed * (1 + impact_decel/100))
            
            imu_sequence.append({
                'accel_x': accel_x,
                'accel_y': accel_y,
                'accel_z': np.random.normal(9.8, impact_force/2),
                'gyro_x': np.random.normal(0, impact_force/2),
                'gyro_y': np.random.normal(0, impact_force/2),
                'gyro_z': np.random.normal(0, impact_force/2),
                'timestamp': i * 0.1
            })
            
            speed_sequence.append({
                'speed': current_speed,
                'timestamp': i * 0.1
            })
        
        # Post-crash phase (vehicle stopped)
        for i in range(40, 50):
            imu_sequence.append({
                'accel_x': np.random.normal(0, 1),
                'accel_y': np.random.normal(0, 1),
                'accel_z': np.random.normal(9.8, 1),
                'gyro_x': np.random.normal(0, 0.5),
                'gyro_y': np.random.normal(0, 0.5),
                'gyro_z': np.random.normal(0, 0.5),
                'timestamp': i * 0.1
            })
            
            current_speed = max(0, current_speed * 0.8)  # Gradual stop
            speed_sequence.append({
                'speed': current_speed,
                'timestamp': i * 0.1
            })
        
        return imu_sequence, speed_sequence
    
    async def _generate_distress_data(self):
        """Generate behavioral pattern data for distress detection"""
        logger.info("Generating distress detection training data...")
        
        distress_data = []
        
        # Normal behavior patterns
        for i in range(600):
            behavior_data = self._generate_normal_behavior()
            distress_data.append({
                'behavior_data': behavior_data,
                'label': 0,  # Normal behavior
                'distress_type': 'none'
            })
        
        # Distress patterns
        distress_types = ['panic_movement', 'unusual_location_time', 'erratic_pattern', 'signal_loss']
        
        for distress_type in distress_types:
            for i in range(100):
                behavior_data = self._generate_distress_behavior(distress_type)
                distress_data.append({
                    'behavior_data': behavior_data,
                    'label': 1,  # Distress detected
                    'distress_type': distress_type
                })
        
        with open(f"{self.data_dir}/distress_detection/training_data.json", 'w') as f:
            json.dump(distress_data, f, indent=2)
        
        logger.info(f"Generated {len(distress_data)} distress detection samples")
    
    def _generate_normal_behavior(self) -> Dict:
        """Generate normal behavioral patterns"""
        return {
            'location_changes': np.random.randint(5, 20),
            'avg_speed': np.random.uniform(2, 6),  # km/h walking speed
            'time_at_locations': np.random.uniform(10, 120),  # minutes
            'movement_variance': np.random.uniform(0.1, 0.5),
            'activity_score': np.random.uniform(0.6, 0.9),
            'signal_stability': np.random.uniform(0.8, 1.0)
        }
    
    def _generate_distress_behavior(self, distress_type: str) -> Dict:
        """Generate distress behavioral patterns"""
        if distress_type == 'panic_movement':
            return {
                'location_changes': np.random.randint(30, 60),
                'avg_speed': np.random.uniform(8, 15),
                'time_at_locations': np.random.uniform(1, 5),
                'movement_variance': np.random.uniform(0.8, 1.5),
                'activity_score': np.random.uniform(0.9, 1.0),
                'signal_stability': np.random.uniform(0.7, 0.9)
            }
        elif distress_type == 'unusual_location_time':
            return {
                'location_changes': np.random.randint(1, 3),
                'avg_speed': np.random.uniform(0.5, 2),
                'time_at_locations': np.random.uniform(180, 480),  # Long time
                'movement_variance': np.random.uniform(0.01, 0.1),
                'activity_score': np.random.uniform(0.1, 0.3),
                'signal_stability': np.random.uniform(0.8, 1.0)
            }
        elif distress_type == 'erratic_pattern':
            return {
                'location_changes': np.random.randint(15, 40),
                'avg_speed': np.random.uniform(1, 10),
                'time_at_locations': np.random.uniform(2, 15),
                'movement_variance': np.random.uniform(0.7, 1.2),
                'activity_score': np.random.uniform(0.4, 0.8),
                'signal_stability': np.random.uniform(0.6, 0.8)
            }
        else:  # signal_loss
            return {
                'location_changes': np.random.randint(0, 2),
                'avg_speed': np.random.uniform(0, 1),
                'time_at_locations': np.random.uniform(120, 300),
                'movement_variance': np.random.uniform(0, 0.05),
                'activity_score': np.random.uniform(0.0, 0.2),
                'signal_stability': np.random.uniform(0.0, 0.3)
            }
    
    async def _generate_red_zone_data(self):
        """Generate red zone detection training data"""
        logger.info("Generating red zone detection training data...")
        
        red_zone_data = []
        
        # Safe locations in Rajasthan
        safe_locations = [
            {'lat': 26.9124, 'lng': 75.7873, 'area': 'Pink City, Jaipur'},
            {'lat': 26.2389, 'lng': 73.0243, 'area': 'Jodhpur Fort Area'},
            {'lat': 25.2138, 'lng': 75.8648, 'area': 'Kota City Center'},
            {'lat': 27.0238, 'lng': 74.2179, 'area': 'Ajmer Dargah'},
        ]
        
        for i in range(400):
            location = np.random.choice(safe_locations)
            # Add some noise to coordinates
            lat_noise = np.random.normal(0, 0.01)
            lng_noise = np.random.normal(0, 0.01)
            
            red_zone_data.append({
                'location': {
                    'latitude': location['lat'] + lat_noise,
                    'longitude': location['lng'] + lng_noise,
                    'timestamp': datetime.now().isoformat()
                },
                'label': 0,  # Safe zone
                'risk_factors': {
                    'crime_density': np.random.uniform(0.1, 0.3),
                    'safety_score': np.random.uniform(0.7, 0.9),
                    'police_presence': np.random.uniform(0.6, 0.9)
                }
            })
        
        # High-risk locations
        risk_locations = [
            {'lat': 26.8897, 'lng': 75.8173, 'area': 'Remote Border Area'},
            {'lat': 26.1234, 'lng': 73.5678, 'area': 'Industrial Outskirt'},
            {'lat': 25.1111, 'lng': 75.9999, 'area': 'Isolated Highway'},
        ]
        
        for i in range(200):
            location = np.random.choice(risk_locations)
            lat_noise = np.random.normal(0, 0.02)
            lng_noise = np.random.normal(0, 0.02)
            
            red_zone_data.append({
                'location': {
                    'latitude': location['lat'] + lat_noise,
                    'longitude': location['lng'] + lng_noise,
                    'timestamp': datetime.now().isoformat()
                },
                'label': 1,  # Red zone
                'risk_factors': {
                    'crime_density': np.random.uniform(0.6, 0.9),
                    'safety_score': np.random.uniform(0.1, 0.4),
                    'police_presence': np.random.uniform(0.1, 0.3)
                }
            })
        
        with open(f"{self.data_dir}/red_zone_detection/training_data.json", 'w') as f:
            json.dump(red_zone_data, f, indent=2)
        
        logger.info(f"Generated {len(red_zone_data)} red zone detection samples")
    
    async def train_fall_detection_model(self):
        """Train fall detection model using generated data"""
        logger.info("Training fall detection model...")
        
        # Load training data
        with open(f"{self.data_dir}/fall_detection/training_data.json", 'r') as f:
            data = json.load(f)
        
        # Extract features from IMU sequences
        features = []
        labels = []
        
        for sample in data:
            sequence = sample['sequence']
            
            # Calculate statistical features from the sequence
            accel_x = [point['accel_x'] for point in sequence]
            accel_y = [point['accel_y'] for point in sequence]
            accel_z = [point['accel_z'] for point in sequence]
            gyro_x = [point['gyro_x'] for point in sequence]
            gyro_y = [point['gyro_y'] for point in sequence]
            gyro_z = [point['gyro_z'] for point in sequence]
            
            # Feature extraction
            feature_vector = [
                # Acceleration features
                np.mean(accel_x), np.std(accel_x), np.max(accel_x), np.min(accel_x),
                np.mean(accel_y), np.std(accel_y), np.max(accel_y), np.min(accel_y),
                np.mean(accel_z), np.std(accel_z), np.max(accel_z), np.min(accel_z),
                
                # Gyroscope features
                np.mean(gyro_x), np.std(gyro_x), np.max(gyro_x), np.min(gyro_x),
                np.mean(gyro_y), np.std(gyro_y), np.max(gyro_y), np.min(gyro_y),
                np.mean(gyro_z), np.std(gyro_z), np.max(gyro_z), np.min(gyro_z),
                
                # Magnitude features
                np.mean([np.sqrt(ax**2 + ay**2 + az**2) for ax, ay, az in zip(accel_x, accel_y, accel_z)]),
                np.std([np.sqrt(ax**2 + ay**2 + az**2) for ax, ay, az in zip(accel_x, accel_y, accel_z)]),
                
                # Energy and frequency domain features
                np.sum([x**2 for x in accel_x]),  # Energy in X
                np.sum([y**2 for y in accel_y]),  # Energy in Y
                np.sum([z**2 for z in accel_z]),  # Energy in Z
            ]
            
            features.append(feature_vector)
            labels.append(sample['label'])
        
        # Convert to numpy arrays
        X = np.array(features)
        y = np.array(labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Fall Detection Model Accuracy: {accuracy:.4f}")
        logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")
        
        # Save model and scaler
        joblib.dump(model, f"{self.models_dir}/fall_detection_model.pkl")
        joblib.dump(scaler, f"{self.models_dir}/fall_detection_scaler.pkl")
        
        # Save feature names for reference
        feature_names = [
            'accel_x_mean', 'accel_x_std', 'accel_x_max', 'accel_x_min',
            'accel_y_mean', 'accel_y_std', 'accel_y_max', 'accel_y_min',
            'accel_z_mean', 'accel_z_std', 'accel_z_max', 'accel_z_min',
            'gyro_x_mean', 'gyro_x_std', 'gyro_x_max', 'gyro_x_min',
            'gyro_y_mean', 'gyro_y_std', 'gyro_y_max', 'gyro_y_min',
            'gyro_z_mean', 'gyro_z_std', 'gyro_z_max', 'gyro_z_min',
            'magnitude_mean', 'magnitude_std',
            'energy_x', 'energy_y', 'energy_z'
        ]
        
        with open(f"{self.models_dir}/fall_detection_features.json", 'w') as f:
            json.dump(feature_names, f, indent=2)
        
        logger.info("Fall detection model training completed")
    
    async def train_crash_detection_model(self):
        """Train crash detection model"""
        logger.info("Training crash detection model...")
        
        # Similar implementation for crash detection
        with open(f"{self.data_dir}/crash_detection/training_data.json", 'r') as f:
            data = json.load(f)
        
        features = []
        labels = []
        
        for sample in data:
            imu_data = sample['imu_data']
            speed_data = sample['speed_data']
            
            # Extract crash-specific features
            speeds = [point['speed'] for point in speed_data]
            accels = [np.sqrt(point['accel_x']**2 + point['accel_y']**2 + point['accel_z']**2) for point in imu_data]
            
            feature_vector = [
                # Speed features
                np.mean(speeds), np.std(speeds), np.max(speeds), np.min(speeds),
                speeds[0] - speeds[-1] if len(speeds) > 1 else 0,  # Speed change
                
                # Acceleration features
                np.mean(accels), np.std(accels), np.max(accels), np.min(accels),
                np.sum([abs(accels[i+1] - accels[i]) for i in range(len(accels)-1)]),  # Jerk
                
                # Crash indicators
                max(0, -min([(speeds[i+1] - speeds[i])/0.1 for i in range(len(speeds)-1)])) if len(speeds) > 1 else 0,  # Max deceleration
                len([a for a in accels if a > 15]),  # High impact count
            ]
            
            features.append(feature_vector)
            labels.append(sample['label'])
        
        X = np.array(features)
        y = np.array(labels)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Crash Detection Model Accuracy: {accuracy:.4f}")
        
        joblib.dump(model, f"{self.models_dir}/crash_detection_model.pkl")
        joblib.dump(scaler, f"{self.models_dir}/crash_detection_scaler.pkl")
        
        logger.info("Crash detection model training completed")
    
    async def train_distress_detection_model(self):
        """Train distress detection model using anomaly detection"""
        logger.info("Training distress detection model...")
        
        with open(f"{self.data_dir}/distress_detection/training_data.json", 'r') as f:
            data = json.load(f)
        
        features = []
        labels = []
        
        for sample in data:
            behavior = sample['behavior_data']
            feature_vector = [
                behavior['location_changes'],
                behavior['avg_speed'],
                behavior['time_at_locations'],
                behavior['movement_variance'],
                behavior['activity_score'],
                behavior['signal_stability']
            ]
            
            features.append(feature_vector)
            labels.append(sample['label'])
        
        X = np.array(features)
        y = np.array(labels)
        
        # Use only normal behavior for training anomaly detector
        X_normal = X[y == 0]
        
        # Train Isolation Forest for anomaly detection
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X_normal)
        
        # Evaluate on full dataset
        y_pred = model.predict(X)
        y_pred_binary = (y_pred == -1).astype(int)  # Convert to binary labels
        
        accuracy = accuracy_score(y, y_pred_binary)
        logger.info(f"Distress Detection Model Accuracy: {accuracy:.4f}")
        
        joblib.dump(model, f"{self.models_dir}/distress_detection_model.pkl")
        
        logger.info("Distress detection model training completed")
    
    async def train_red_zone_model(self):
        """Train red zone risk assessment model"""
        logger.info("Training red zone detection model...")
        
        with open(f"{self.data_dir}/red_zone_detection/training_data.json", 'r') as f:
            data = json.load(f)
        
        features = []
        labels = []
        
        for sample in data:
            location = sample['location']
            risk_factors = sample['risk_factors']
            
            feature_vector = [
                location['latitude'],
                location['longitude'],
                risk_factors['crime_density'],
                risk_factors['safety_score'],
                risk_factors['police_presence']
            ]
            
            features.append(feature_vector)
            labels.append(sample['label'])
        
        X = np.array(features)
        y = np.array(labels)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Red Zone Detection Model Accuracy: {accuracy:.4f}")
        
        joblib.dump(model, f"{self.models_dir}/red_zone_model.pkl")
        joblib.dump(scaler, f"{self.models_dir}/red_zone_scaler.pkl")
        
        logger.info("Red zone detection model training completed")

# Training script entry point
async def main():
    """Main training function"""
    trainer = ModelTrainer()
    await trainer.train_all_models()
    
    print("\n" + "="*50)
    print("YatriGuard AI/ML Model Training Complete!")
    print("="*50)
    print("Trained models saved in 'trained_models/' directory:")
    print("- fall_detection_model.pkl")
    print("- crash_detection_model.pkl") 
    print("- distress_detection_model.pkl")
    print("- red_zone_model.pkl")
    print("- Associated scalers and metadata files")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
