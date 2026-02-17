# RLProfilePicturesREVAMP - Backend API

> Python FastAPI backend providing avatar resolution for multiple gaming platforms.

## 🎯 Overview

RESTful API that:
- Resolves avatars from Steam, Xbox, PSN, Nintendo Switch, and Epic Games
- Handles custom Epic avatar uploads
- Provides caching for optimal performance
- Implements rate limiting and analytics

## 🏗️ Architecture

```
server/
├── main.py                 # FastAPI application entry
├── run.py                  # Development server runner
├── config.py               # Configuration management
├── routes/
│   ├── avatar.py           # Avatar resolution endpoints
│   ├── upload.py           # Custom avatar uploads
│   ├── tos.py              # Terms of Service pages
│   └── ...
├── services/
│   ├── steam.py            # Steam Web API integration
│   ├── xbox.py             # Xbox Live API integration
│   ├── psn.py              # PlayStation Network integration
│   ├── switch.py           # Nintendo Switch integration
│   └── epic.py             # Epic Games integration
├── cache/
│   └── redis_cache.py      # Redis caching layer
├── database/
│   └── models.py           # Data models
├── middleware/
│   └── rate_limit.py       # Rate limiting (40 req/min)
├── utils/
│   └── helpers.py          # Utility functions
└── tests/
    └── ...                 # Test suite
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Redis (for caching)
- Platform API keys (Steam, Xbox, etc.)

### Installation

```bash
# Clone and navigate
cd server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your API keys
```

### Running

```bash
# Development
python run.py

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### Avatar Resolution

```http
GET /avatar/{platform}/{user_id}
```

| Platform | User ID Format |
|----------|---------------|
| `steam` | Steam64 ID |
| `xbox` | Xbox Gamertag or XUID |
| `psn` | PSN Online ID |
| `switch` | Friend Code |
| `epic` | Epic Account ID |

**Response:**
```json
{
  "avatar_url": "https://...",
  "platform": "steam",
  "cached": true
}
```

### Custom Avatar Upload

```http
POST /upload/epic
Content-Type: multipart/form-data
```

### Health Check

```http
GET /health
```

## ⚙️ Configuration

Environment variables (`.env`):

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Redis
REDIS_URL=redis://localhost:6379

# Platform APIs
STEAM_API_KEY=your_key_here
XBOX_CLIENT_ID=your_client_id
XBOX_CLIENT_SECRET=your_secret
# ... etc
```

## 🔒 Rate Limiting

- **40 requests per minute** per IP address
- Tracked via Redis
- Returns `429 Too Many Requests` when exceeded

## 📊 Analytics

The API tracks:
- Request counts per platform
- Response times
- Cache hit rates
- Error rates

## 🧪 Testing

```bash
# Run tests
python run_tests.py

# Or with pytest directly
pytest tests/ -v
```

## 📦 Dependencies

Key packages from `requirements.txt`:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `redis` - Caching
- `httpx` - Async HTTP client
- `pillow` - Image processing

---

## ⚠️ Notes:
- Very minimal backend
- Still has issues based on caching, platform rate limits and I/O

*Part of the RLProfilePicturesREVAMP project by [@borgox](https://github.com/borgox)*