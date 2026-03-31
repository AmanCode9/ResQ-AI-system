# ResQ-AI Backend Hub

Real-time backend server for the ResQ-AI disaster response system, built with FastAPI and WebSocket support.

## 🚀 Features

- **FastAPI Server**: High-performance REST API with automatic OpenAPI documentation
- **Real-time Communication**: WebSocket support for live updates using Socket.IO
- **AI Integration**: Seamless integration with AI engine for video processing and NLP analysis
- **Drone Management**: Complete drone fleet management and telemetry tracking
- **Mission Control**: Automated mission dispatch and coordination
- **Alert System**: Real-time emergency alert broadcasting and management

## 🛠️ Tech Stack

- **FastAPI**: Modern Python web framework
- **Socket.IO**: Real-time bidirectional communication
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server
- **Loguru**: Structured logging
- **HTTPX**: Async HTTP client for AI engine communication

## 📁 Project Structure

```
backend-hub/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── ai_client.py         # AI engine communication client
│   ├── drone_controller.py  # Drone fleet management
│   ├── websocket_service.py # WebSocket service for real-time updates
│   └── routes.py            # REST API route definitions
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── .env                   # Environment variables
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   cd resq-ai-system/backend-hub
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the server**
   ```bash
   python src/main.py
   ```

The server will start on `http://localhost:8000`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build backend-hub

# Or run standalone
docker build -t resq-ai-backend .
docker run -p 8000:8000 resq-ai-backend
```

## 📡 API Endpoints

### Core Endpoints

- `GET /` - Health check
- `GET /api/system/health` - System health status
- `GET /api/system/stats` - System statistics

### Drone Management

- `POST /api/drones/register` - Register new drone
- `GET /api/drones` - Get all drones
- `GET /api/drones/{drone_id}` - Get specific drone
- `POST /api/drones/{drone_id}/telemetry` - Update drone telemetry
- `GET /api/drones/{drone_id}/telemetry` - Get telemetry history
- `GET /api/drones/{drone_id}/health` - Get drone health status

### Mission Control

- `POST /api/missions` - Create new mission
- `GET /api/missions/history` - Get mission history
- `POST /api/missions/{command_id}/complete` - Mark mission complete

### Alert Management

- `POST /api/alerts` - Create emergency alert
- `GET /api/alerts` - Get active alerts

### AI Integration

- `POST /api/ai/process-video` - Process video with AI
- `POST /api/ai/analyze-message` - Analyze emergency message
- `GET /api/ai/status` - Get AI engine status

Local model mode:
- Configure `.env` with `AI_MODEL_PATH=/full/path/to/your/model_adapter.py`.
- Your module must expose:
  - `process_video(video_url, drone_id)`
  - `analyze_message(message)`
  - `analyze_alert(alert_data)`
  - `status()`
- Remote engine mode remains the same using `AI_ENGINE_URL`.

## 🔌 WebSocket Events

### Client Events

- `subscribe_alerts` - Subscribe to real-time alerts
- `subscribe_drones` - Subscribe to drone telemetry
- `subscribe_missions` - Subscribe to mission updates

### Server Events

- `new_alert` - New emergency alert
- `drone_update` - Drone telemetry update
- `mission_update` - Mission status update
- `emergency_dispatch` - Emergency response dispatch

## 🔧 Configuration

Environment variables in `.env`:

```env
PORT=8000
AI_ENGINE_URL=http://localhost:5000
SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## 📊 Monitoring

- **Health Checks**: `/api/system/health`
- **Metrics**: `/api/system/stats`
- **Logs**: Structured logging with Loguru

## 🔒 Security

- CORS protection
- Input validation with Pydantic
- Rate limiting (configurable)
- Authentication middleware (extensible)

## 🤝 Integration

### AI Engine

The backend communicates with the AI engine via HTTP API:

- Video processing: `POST /api/detect`
- Message analysis: `POST /api/analyze`
- Alert insights: `POST /api/alert-insights`

### Frontend Dashboard

Real-time updates via WebSocket:

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:8000');

// Subscribe to alerts
socket.emit('subscribe_alerts');

// Listen for updates
socket.on('new_alert', (data) => {
  console.log('New alert:', data);
});
```

## 📈 Performance

- **Async/Await**: Full async support for high concurrency
- **Connection Pooling**: HTTPX client for efficient AI engine communication
- **Background Tasks**: Non-blocking mission processing
- **WebSocket**: Efficient real-time communication

## 🚀 Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure CORS origins
- [ ] Set up monitoring and logging
- [ ] Configure database (if using)
- [ ] Set up reverse proxy (nginx)
- [ ] Enable SSL/TLS
- [ ] Configure firewall rules

### Scaling

- Horizontal scaling with load balancer
- Redis for session storage (future)
- Database clustering (future)
- CDN for static assets (if any)

## 🐛 Troubleshooting

### Common Issues

1. **AI Engine Connection Failed**
   - Check AI_ENGINE_URL in .env
   - Ensure AI engine is running on port 5000

2. **WebSocket Connection Issues**
   - Check CORS settings
   - Verify firewall allows WebSocket connections

3. **High Memory Usage**
   - Monitor telemetry buffer size
   - Implement data cleanup routines

## 📝 API Documentation

Automatic API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.