# YatriGuard - AI-Powered Tourist Safety System 🛡️

YatriGuard is an advanced AI/ML-powered safety system designed specifically for tourists visiting Rajasthan, India. It combines cutting-edge machine learning algorithms with reliable rule-based fallback systems to provide comprehensive safety monitoring and emergency response capabilities.

## 🚀 Key Features

### Frontend (React + TypeScript)
- **Digital ID System**: Multi-step form with Aadhaar validation and OTP verification
- **Real-time Safety Dashboard**: Live monitoring and alert display
- **Multi-language Support**: Hindi, English, and regional languages
- **Responsive Mobile-First UI**: Optimized for smartphones and tablets
- **Offline Capability**: Critical functions work without internet

### Backend (FastAPI + AI/ML)
- **🧠 AI-Powered Fall Detection**: LSTM-based detection of the three-phase fall signature (freefall → impact → inactivity)
- **🚗 Vehicle Crash Detection**: Sensor fusion combining GPS speed data and accelerometer impact detection
- **🗺️ Red Zone Breach Detection**: AI-enhanced geofencing with proximity risk assessment
- **😟 Behavioral Distress Analysis**: Unsupervised anomaly detection for identifying distress situations
- **🔋 Smart Battery Optimization**: Adaptive processing based on device battery and network conditions
- **📡 Real-time WebSocket Monitoring**: Live sensor data streaming and instant alerts
- **🛡️ Rule-based Fallback Systems**: Reliable detection when AI models are unavailable

## 🏗️ Architecture

### AI/ML Detection Pipeline
```
Sensor Data → Preprocessing → AI Models → Confidence Check → Alert/Fallback
                                ↓
                        Rule-based Systems (Fallback)
```

### Tech Stack

**Frontend:**
- Vite + React + TypeScript
- Tailwind CSS + shadcn/ui (Radix UI)  
- React Hook Form + Zod validation
- React Router for navigation
- WebSocket client for real-time updates

**Backend:**
- FastAPI for high-performance API
- NumPy for numerical computations
- AsyncIO for concurrent processing
- WebSocket for real-time communication
- Pydantic for data validation

## 🚀 Quick Start

### Frontend Setup
Prerequisites: Node.js 18+ and npm

```bash
cd YatriGuard-main
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

### Backend Setup
Prerequisites: Python 3.8+ and pip

```bash
cd backend
pip install -r requirements.txt
python start.py
```

API available at http://localhost:8000
Interactive docs at http://localhost:8000/docs

### Demo the AI Features
```bash
cd backend
python demo_client.py
```

## 📊 AI/ML Implementation Details

### A. Red Zone & Geo-Fence Breach Detection 🗺️
**Objective**: Automatically alert tourists when entering high-risk areas

**AI Approach**:
- **Primary**: ML-based risk assessment combining geographic, demographic, and contextual data
- **Fallback**: Rule-based point-in-polygon calculation
- **Sensors**: GPS location data
- **Features**: Proximity to borders, military zones, wildlife areas, crime statistics

**Example**: Tourist's GPS coordinates indicate entry into a military zone → AI assesses risk level → Alert sent if confidence > 70%

### B. User Fall Detection 🧗
**Objective**: Detect falls during trekking/exploration activities

**AI Approach**: 
- **Primary**: LSTM neural network trained on IMU time-series data
- **Fallback**: Rule-based three-phase detection (freefall → impact → inactivity)
- **Sensors**: Accelerometer + Gyroscope (IMU)
- **Features**: Magnitude variance, peak detection, temporal patterns

**Detection Pattern**:
1. **Freefall**: <2G for >0.3 seconds
2. **Impact**: >15G spike
3. **Inactivity**: <2G movement for >3 seconds

### C. Vehicle Crash Detection 🚗
**Objective**: Detect vehicle accidents on highways

**AI Approach**:
- **Primary**: Sensor fusion model combining GPS and IMU data
- **Fallback**: Rule-based thresholds for speed + impact
- **Context Required**: Vehicle speed >30 km/h
- **Detection**: Extreme deceleration + high G-force impact

**Example**: Phone moving at 90 km/h → 15G impact detected → Speed drops to 0 km/h → Crash alert triggered

### D. Behavioral Distress Detection 😟
**Objective**: Identify distress without explicit SOS signal

**AI Approach**:
- **Primary**: Unsupervised anomaly detection on behavioral patterns
- **Fallback**: Rule-based pattern matching
- **Analysis**: Location patterns, movement variance, timing anomalies
- **Triggers**: Prolonged inactivity (4+ hours), erratic movement, signal loss

## 🔋 Battery Optimization Strategy

The system implements intelligent power management:

- **High Battery (>60%)**: Full AI processing, 30s GPS intervals
- **Medium Battery (30-60%)**: Reduced AI processing, 2min GPS intervals  
- **Low Battery (<30%)**: Rule-based only, 5min GPS intervals
- **Critical (<15%)**: Emergency mode, GPS only, SMS fallback

## 🌐 Network Resilience

- **Online**: Full AI processing with real-time alerts
- **Offline**: Local buffering with rule-based detection
- **Poor Signal**: SMS fallback for critical alerts
- **Reconnection**: Automatic data sync and model updates

## 📱 API Endpoints

### Core Endpoints
- `POST /api/sensor-data/{user_id}` - Submit sensor data
- `GET /api/user/{user_id}/alerts` - Retrieve user alerts  
- `POST /api/user/{user_id}/panic` - Trigger panic button
- `GET /api/health` - System health check
- `WS /ws/{user_id}` - Real-time WebSocket connection

### Administrative
- `GET /api/red-zones` - Get defined red zones
- `POST /api/red-zones` - Create new red zone (admin)

## Scripts

**Frontend:**
- `npm run dev` — Start development server
- `npm run build` — Production build
- `npm run build:dev` — Development build
- `npm run preview` — Preview production build
- `npm run lint` — Lint the project

**Backend:**
- `python start.py` — Start AI/ML backend server
- `python demo_client.py` — Run feature demonstration
- `pip install -r requirements.txt` — Install dependencies

## 📁 Project Structure

```
YatriGuard-main/           # Frontend (React)
├── src/
│   ├── components/        # UI components
│   ├── pages/            # Application pages
│   ├── i18n/             # Internationalization
│   └── hooks/            # Custom React hooks

backend/                   # AI/ML Backend (FastAPI)
├── models/               # AI/ML models and data structures
├── services/             # Business logic services
├── utils/                # Utility functions
├── fallback_systems/     # Rule-based fallback systems
├── main.py              # FastAPI application
├── start.py             # Server startup script
└── demo_client.py       # Feature demonstration

legacy/                   # Original rule-based systems
├── red-zone-python.py   # Original red zone detection
└── tourist-app-python.py # Original tourist interface
```

## 🔧 Configuration

The system supports environment-based configuration:

```bash
# Development (default)
ENVIRONMENT=development
AI_MODELS_ENABLED=false    # Use fallback systems for faster development

# Production  
ENVIRONMENT=production
AI_MODELS_ENABLED=true     # Enable full AI processing
FALL_DETECTION_THRESHOLD=0.8
CRASH_DETECTION_THRESHOLD=0.85
```

## 🧪 Testing the AI Features

Run the demo client to test all AI features:

```bash
cd backend
python demo_client.py
```

The demo will test:
- ✅ Red zone detection with sample coordinates
- ✅ Fall detection with simulated IMU data
- ✅ Crash detection with vehicle context
- ✅ Distress detection with behavioral patterns
- ✅ Panic button functionality
- ✅ Real-time WebSocket alerts

## 🚨 Alert System

### Alert Types
- **🔴 Critical**: Fall detected, crash detected, panic button, red zone breach
- **🟡 High**: Proximity warnings, rule-based detections
- **🟢 Medium**: Behavioral anomalies, distress indicators
- **🔵 Low**: System notifications, battery warnings

### Notification Channels
1. **Real-time WebSocket** - Instant app notifications
2. **SMS Fallback** - For critical alerts when offline
3. **Authorities Dashboard** - Emergency services integration
4. **Emergency Contacts** - Family/friend notifications

## 🛡️ Safety Features

- **Multi-layered Detection**: AI + Rule-based redundancy
- **Offline Capability**: Core functions work without internet
- **Battery Aware**: Adaptive processing to preserve power
- **False Positive Mitigation**: Multiple validation layers
- **Privacy First**: Data processed locally when possible

## Project Structure

```
public/            # Static assets
src/
  components/      # UI components (Navigation, Layout, ui/*)
  pages/           # Pages (Home, DigitalID, SignIn, Dashboard, etc.)
  i18n/            # I18n provider and translations
  hooks/, context/ # Custom hooks and providers
  assets/          # Images and media
```

Key files:
- src/pages/DigitalID.tsx — Multi-step Digital ID flow
- src/pages/SignIn.tsx — Email/Name sign-in with i18n validation
- src/i18n/I18nProvider.tsx — i18n context and `t()` helper
- src/i18n/translations.ts — Language dictionaries

## Internationalization

- Add/modify keys in `src/i18n/translations.ts` for each language
- Use in components with:
  ```ts
  const { t } = useI18n();
  t('some.key');
  ```

## Notes

- On Digital ID submit, the app simulates a short “blockchain processing” buffer with a spinner, then navigates to the dashboard.
- OTP flow is demo-only (code is logged to console in dev).

## Deployment

Build and serve the `dist/` folder on any static host (Netlify, Vercel, GitHub Pages, etc.):

```bash
npm run build
npm run preview  # optional local check
```

## License

MIT
