# 🛡️ NHAA RSTAM — Real-Time Stress and Trauma Assessment Module

**AI-enabled psychological assessment system for India's National Helpline Against Atrocities (14566)**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Overview

RSTAM is a prototype AI-powered module that assesses psychological stress, trauma, fear, anxiety, and vulnerability levels of victims/complainants interacting through the NHAA helpline (14566), Integrated Portal, chatbot, IVRS, mobile app, or other approved digital interfaces.

### Key Features

- 🎙️ **Voice Analysis** — Speech-to-text (Whisper), acoustic feature extraction (pitch, pauses, jitter), voice emotion detection
- 📝 **Text Analysis** — Trauma keyword detection, sentiment analysis, suicidal ideation screening
- 📊 **Stress Vulnerability Index (SVI)** — Composite score (0-100) from 6 weighted components
- ⚠️ **Risk Categorization** — Low / Moderate / High / Critical with automatic escalation
- 💡 **Intervention Recommender** — Context-aware recommendations (counselling, legal aid, police, medical)
- 🌐 **Multilingual Support** — English, Hindi, Tamil, Telugu, Marathi, Bengali, Kannada, Gujarati, Malayalam, Punjabi, Odia, Urdu
- 🔒 **Privacy & Ethics** — PII anonymization, AES-256 encryption, informed consent, audit trails

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────────────────────┐     ┌─────────────────┐
│  Input Channels  │────▶│        RSTAM Backend (FastAPI)     │────▶│   Dashboard UI   │
│  - NHAA 14566   │     │                                    │     │   (React)        │
│  - Portal       │     │  ┌────────────┐  ┌──────────────┐  │     │                  │
│  - Chatbot      │     │  │   Voice    │  │    Text      │  │     │  ┌────────────┐  │
│  - IVRS         │     │  │  Pipeline  │  │  Pipeline    │  │     │  │ SVI Gauge  │  │
│  - Mobile App   │     │  │ STT→Acous→ │  │ Lang→Trans→  │  │     │  │ Risk Card  │  │
│                 │     │  │ Emotion    │  │ Trauma→Sent→ │  │     │  │ Recommend  │  │
│                 │     │  └─────┬──────┘  └──────┬───────┘  │     │  └────────────┘  │
│                 │     │        └──────┬──────────┘          │     │                  │
│                 │     │         ┌─────▼─────┐               │     │                  │
│                 │     │         │ SVI Engine │               │     │                  │
│                 │     │         └─────┬─────┘               │     │                  │
│                 │     │         ┌─────▼──────┐              │     │                  │
│                 │     │         │ Recommender │              │     │                  │
│                 │     │         └────────────┘              │     │                  │
└─────────────────┘     └──────────────────────────────────┘     └─────────────────┘
```

## 📊 SVI Scoring

| Component | Weight | Source |
|-----------|--------|--------|
| Acoustic Distress | 20% | Voice pitch, pauses, jitter |
| Voice Emotion | 15% | Emotion classification |
| Text Sentiment | 15% | Sentiment analysis |
| Trauma Keywords | 20% | Keyword density |
| Suicidal Ideation | 15% | SI pattern detection |
| Contextual Vulnerability | 15% | Prior complaints, displacement |

| SVI Range | Risk Level | Response SLA |
|-----------|------------|-------------|
| 0–25 | 🟢 Low | 72 hours |
| 26–50 | 🟡 Moderate | 24 hours |
| 51–75 | 🔴 High | 4 hours |
| 76–100 | ⚫ Critical | Immediate |

> ⚠️ Suicidal ideation detection **automatically escalates** to Critical regardless of SVI score.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- ffmpeg (for audio processing)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API will be available at http://localhost:8000. API docs at http://localhost:8000/docs.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at http://localhost:5173.

### Docker Setup

```bash
docker-compose up --build
```

---

## 🧪 Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/assess/voice` | Voice recording assessment |
| `POST` | `/api/v1/assess/text` | Text narrative assessment |
| `POST` | `/api/v1/assess/combined` | Combined voice + text |
| `GET` | `/api/v1/assess/{case_id}` | Get assessment result |
| `POST` | `/api/v1/consent/record` | Record informed consent |
| `GET` | `/api/v1/cases/` | List cases (paginated) |
| `GET` | `/api/v1/dashboard/stats` | Dashboard statistics |
| `GET` | `/api/v1/dashboard/alerts` | Active alerts |

---

## 🔒 Privacy & Security

- **Informed consent** recorded before any analysis
- **PII anonymization** — phone numbers, Aadhaar, emails redacted
- **AES-256 encryption** for stored audio and transcripts
- **Audit trail** of all system actions (encrypted)
- **Data minimization** — raw audio purged after configurable retention
- **Role-based access** for dashboard operators

---

## 📁 Project Structure

```
nhaa-rstam/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers
│   │   ├── analyzers/    # ML/AI analysis modules
│   │   ├── models/       # Database & Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── utils/        # Encryption, anonymization
│   ├── tests/            # Unit & integration tests
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/   # React UI components
│       ├── pages/        # Dashboard pages
│       └── services/     # API client
├── sample_data/          # Synthetic test scenarios
├── docker-compose.yml
└── README.md
```

---

## ⚖️ Disclaimer

This is a **prototype** for demonstration purposes. The SVI scoring rubric and suicidal ideation detection algorithms require **clinical validation** by qualified mental health professionals before any real-world deployment. All test data is synthetic.

---

## 👥 Stakeholders

- Department of Social Justice and Empowerment
- National Helpline Against Atrocities (14566)
- State Governments and Union Territories
- District Administrations
- Counsellors and Mental Health Professionals
- Law Enforcement Agencies
- Rehabilitation and Welfare Authorities

---

*Built with ❤️ for social justice*
