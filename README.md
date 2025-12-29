# ITKARS Online Assessment Platform

A comprehensive online hiring assessment platform with AI-powered question generation and anti-cheating features.

## Features

- 🔐 **Admin Dashboard** - Manage questions, test links, and view results
- 📝 **AI Question Generation** - Generate question variants using Gemini AI
- ⏱️ **Timed Tests** - Per-question timers with auto-submission
- 🔗 **Multi-Use Links** - Share single link with unlimited candidates
- 📊 **Results Analytics** - Score tracking, tab switch detection
- 🛡️ **Anti-Cheat** - Tab switch monitoring, IP tracking
- 📤 **Export Results** - Download CSV reports

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- MongoDB (Motor async driver)
- JWT Authentication

### Frontend
- React 18 (Vite)
- TailwindCSS
- React Router

## Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your MongoDB URI and secrets
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend (.env)
```
MONGODB_URI=mongodb+srv://...
JWT_SECRET=your-secret-key
GEMINI_API_KEY=your-gemini-key
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api
```

## License

MIT
