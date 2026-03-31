"""
ResQ-AI Backend Hub - FastAPI Server
Real-time disaster response coordination system
"""

import asyncio
import os
from contextlib import asynccontextmanager
from typing import List, Dict, Any
from datetime import datetime
import json

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import socketio
from loguru import logger
import httpx

# Import our modules
from .ai_client import ai_client
from .drone_controller import drone_controller
from .websocket_service import websocket_service
from .routes import router

# Data Models
class DroneTelemetry(BaseModel):
    drone_id: str
    latitude: float
    longitude: float
    altitude: float
    battery_level: float
    status: str  # "active", "standby", "emergency"
    last_seen: datetime

class EmergencyAlert(BaseModel):
    alert_id: str
    alert_type: str  # "landslide", "flood", "fire", "earthquake"
    severity: str  # "low", "medium", "high", "critical"
    location: Dict[str, float]  # {"lat": float, "lng": float}
    description: str
    timestamp: datetime
    source: str  # "ai_detection", "user_report", "sensor"

class MissionCommand(BaseModel):
    command_id: str
    drone_id: str
    command_type: str  # "search", "rescue", "return", "hover"
    target_location: Dict[str, float]
    priority: str  # "low", "medium", "high"

# Global state
active_drones: Dict[str, DroneTelemetry] = {}
active_alerts: List[EmergencyAlert] = []
mission_queue: List[MissionCommand] = []

# Socket.IO server for real-time communication
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio)

# AI Engine Client is imported from ai_client module

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting ResQ-AI Backend Hub...")
    await ai_client.connect()

    # Initialize sample data
    await initialize_sample_data()

    # Register WebSocket event handlers
    sio.on('connect', websocket_service.handle_connect)
    sio.on('disconnect', websocket_service.handle_disconnect)
    sio.on('subscribe_alerts', lambda sid: websocket_service.subscribe_to_topic(sid, 'alerts'))
    sio.on('subscribe_drones', lambda sid: websocket_service.subscribe_to_topic(sid, 'drones'))
    sio.on('subscribe_missions', lambda sid: websocket_service.subscribe_to_topic(sid, 'missions'))

    yield

    # Shutdown
    logger.info("Shutting down ResQ-AI Backend Hub...")
    await ai_client.disconnect()

app = FastAPI(
    title="ResQ-AI Backend Hub",
    description="Real-time disaster response coordination API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO app
app.mount("/socket.io", socket_app)

# Include API routes
app.include_router(router, prefix="/api", tags=["api"])

# Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "ResQ-AI Backend Hub is running", "status": "healthy"}

@app.get("/api/drones")
async def get_drones():
    """Get all active drones"""
    return {"drones": list(active_drones.values())}

@app.post("/api/drones/telemetry")
async def update_drone_telemetry(telemetry: DroneTelemetry):
    """Update drone telemetry data"""
    active_drones[telemetry.drone_id] = telemetry

    # Broadcast update to all connected clients
    await sio.emit('drone_update', telemetry.dict())

    return {"status": "telemetry_updated", "drone_id": telemetry.drone_id}

@app.get("/api/alerts")
async def get_alerts():
    """Get all active alerts"""
    return {"alerts": [alert.dict() for alert in active_alerts]}

@app.post("/api/alerts")
async def create_alert(alert: EmergencyAlert):
    """Create a new emergency alert"""
    active_alerts.append(alert)

    # Process alert with AI engine
    ai_insights = await ai_client.analyze_alert(alert.dict())

    # Broadcast alert to all connected clients
    await sio.emit('new_alert', {
        **alert.dict(),
        "ai_insights": ai_insights
    })

    # If critical, trigger automatic mission dispatch
    if alert.severity == "critical":
        await dispatch_emergency_mission(alert)

    return {"status": "alert_created", "alert_id": alert.alert_id}

@app.post("/api/missions")
async def create_mission(command: MissionCommand, background_tasks: BackgroundTasks):
    """Create a new mission command"""
    mission_queue.append(command)

    # Add to background processing
    background_tasks.add_task(process_mission, command)

    return {"status": "mission_queued", "command_id": command.command_id}

@app.get("/api/missions/queue")
async def get_mission_queue():
    """Get current mission queue"""
    return {"missions": [mission.dict() for mission in mission_queue]}

@app.post("/api/ai/process-video")
async def process_video_feed(video_url: str, drone_id: str):
    """Process video feed through AI engine"""
    try:
        results = await ai_client.process_video(video_url, drone_id)

        # If survivors detected, create alert
        if results.get("survivors_detected", False):
            alert = EmergencyAlert(
                alert_id=f"auto_{datetime.now().isoformat()}",
                alert_type="survivor_detected",
                severity="high",
                location=results.get("location", {"lat": 0, "lng": 0}),
                description=f"AI detected potential survivors at location",
                timestamp=datetime.now(),
                source="ai_detection"
            )
            await create_alert(alert)

        return {"status": "processed", "results": results}

    except Exception as e:
        logger.error(f"Video processing failed: {e}")
        raise HTTPException(status_code=500, detail="Video processing failed")

@app.post("/api/ai/analyze-message")
async def analyze_emergency_message(message: str, sender_info: Dict[str, Any]):
    """Analyze emergency message with NLP"""
    try:
        analysis = await ai_client.analyze_message(message)

        # If urgent, create alert
        if analysis.get("urgency") == "high":
            alert = EmergencyAlert(
                alert_id=f"msg_{datetime.now().isoformat()}",
                alert_type="emergency_message",
                severity="high",
                location=sender_info.get("location", {"lat": 0, "lng": 0}),
                description=f"Urgent message: {message[:100]}...",
                timestamp=datetime.now(),
                source="user_report"
            )
            await create_alert(alert)

        return {"status": "analyzed", "analysis": analysis}

    except Exception as e:
        logger.error(f"Message analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Message analysis failed")

# Helper functions
async def initialize_sample_data():
    """Initialize with sample data for development"""
    # Sample drone
    sample_drone = DroneTelemetry(
        drone_id="drone_001",
        latitude=28.7041,
        longitude=77.1025,
        altitude=50.0,
        battery_level=85.0,
        status="active",
        last_seen=datetime.now()
    )
    active_drones[sample_drone.drone_id] = sample_drone

    # Sample alert
    sample_alert = EmergencyAlert(
        alert_id="sample_001",
        alert_type="flood",
        severity="medium",
        location={"lat": 26.1445, "lng": 91.7362},
        description="Flood warning in Assam region",
        timestamp=datetime.now(),
        source="sensor"
    )
    active_alerts.append(sample_alert)

async def dispatch_emergency_mission(alert: EmergencyAlert):
    """Automatically dispatch drones for critical alerts"""
    # Find nearest available drone
    available_drones = [d for d in active_drones.values() if d.status == "active"]

    if available_drones:
        nearest_drone = available_drones[0]  # Simplified - in real app, calculate distance

        mission = MissionCommand(
            command_id=f"auto_mission_{datetime.now().isoformat()}",
            drone_id=nearest_drone.drone_id,
            command_type="search",
            target_location=alert.location,
            priority="high"
        )

        mission_queue.append(mission)
        await sio.emit('mission_dispatched', mission.dict())

async def process_mission(command: MissionCommand):
    """Process mission command"""
    # Simulate mission processing
    await asyncio.sleep(2)  # Simulate processing time

    # Update drone status
    if command.drone_id in active_drones:
        active_drones[command.drone_id].status = "busy"

    # Broadcast mission update
    await sio.emit('mission_update', {
        "command_id": command.command_id,
        "status": "in_progress",
        "drone_id": command.drone_id
    })

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    )