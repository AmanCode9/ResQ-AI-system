"""
API Routes for ResQ-AI Backend
REST API endpoints for disaster response coordination
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from pydantic import BaseModel

# Import services
from .drone_controller import drone_controller
from .websocket_service import websocket_service
from .ai_client import ai_client

# Data Models
class DroneRegistration(BaseModel):
    drone_id: str
    model: str
    capabilities: List[str]

class TelemetryUpdate(BaseModel):
    drone_id: str
    latitude: float
    longitude: float
    altitude: float
    battery_level: float
    status: str

class EmergencyAlert(BaseModel):
    alert_type: str
    severity: str
    location: Dict[str, float]
    description: str
    source: str

class MissionCommand(BaseModel):
    drone_id: str
    command_type: str
    target_location: Dict[str, float]
    priority: str

class MessageAnalysis(BaseModel):
    message: str
    sender_location: Optional[Dict[str, float]] = None

# Create router
router = APIRouter()

# Drone Management Routes
@router.post("/drones/register")
async def register_drone(drone: DroneRegistration):
    """Register a new drone in the system"""
    success = drone_controller.register_drone(
        drone.drone_id,
        drone.model,
        drone.capabilities
    )

    if not success:
        raise HTTPException(status_code=400, detail="Drone registration failed")

    return {"status": "registered", "drone_id": drone.drone_id}

@router.get("/drones")
async def get_drones():
    """Get all registered drones"""
    drones = drone_controller.get_all_drones()
    return {"drones": drones, "count": len(drones)}

@router.get("/drones/{drone_id}")
async def get_drone(drone_id: str):
    """Get specific drone information"""
    drone = drone_controller.get_drone_status(drone_id)
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")

    return drone

@router.post("/drones/{drone_id}/telemetry")
async def update_telemetry(drone_id: str, telemetry: TelemetryUpdate, background_tasks: BackgroundTasks):
    """Update drone telemetry"""
    success = drone_controller.update_telemetry(drone_id, telemetry.dict())

    if not success:
        raise HTTPException(status_code=400, detail="Telemetry update failed")

    # Broadcast update via WebSocket
    background_tasks.add_task(
        websocket_service.broadcast_drone_update,
        telemetry.dict()
    )

    return {"status": "updated", "drone_id": drone_id}

@router.get("/drones/{drone_id}/telemetry")
async def get_drone_telemetry(
    drone_id: str,
    hours: int = Query(1, description="Hours of history to retrieve")
):
    """Get drone telemetry history"""
    if drone_id not in drone_controller.drones:
        raise HTTPException(status_code=404, detail="Drone not found")

    history = drone_controller.get_telemetry_history(drone_id, hours)
    return {"drone_id": drone_id, "telemetry": history}

@router.get("/drones/{drone_id}/health")
async def get_drone_health(drone_id: str):
    """Get drone health status"""
    health = drone_controller.check_drone_health(drone_id)
    return health

# Mission Management Routes
@router.post("/missions")
async def create_mission(command: MissionCommand, background_tasks: BackgroundTasks):
    """Create and dispatch a mission"""
    command_id = f"mission_{uuid.uuid4().hex[:8]}"

    success = drone_controller.assign_mission(
        command.drone_id,
        command_id,
        command.command_type
    )

    if not success:
        raise HTTPException(status_code=400, detail="Mission assignment failed")

    mission_data = {
        "command_id": command_id,
        **command.dict(),
        "status": "assigned",
        "assigned_at": datetime.now().isoformat()
    }

    # Broadcast mission update
    background_tasks.add_task(
        websocket_service.broadcast_mission_update,
        mission_data
    )

    return {"status": "mission_created", "command_id": command_id}

@router.get("/missions/history")
async def get_mission_history(
    drone_id: Optional[str] = None,
    limit: int = Query(50, description="Maximum number of missions to return")
):
    """Get mission history"""
    history = drone_controller.get_mission_history(drone_id, limit)
    return {"missions": history, "count": len(history)}

@router.post("/missions/{command_id}/complete")
async def complete_mission(command_id: str, background_tasks: BackgroundTasks, success: bool = True):
    """Mark mission as completed"""
    # Find the mission
    mission = None
    for m in drone_controller.mission_history:
        if m["mission_id"] == command_id:
            mission = m
            break

    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    drone_controller.complete_mission(mission["drone_id"], command_id, success)

    # Broadcast completion
    background_tasks.add_task(
        websocket_service.broadcast_mission_update,
        {
            "command_id": command_id,
            "status": "completed" if success else "failed",
            "completed_at": datetime.now().isoformat()
        }
    )

    return {"status": "mission_completed", "command_id": command_id}

# Alert Management Routes
@router.post("/alerts")
async def create_alert(alert: EmergencyAlert, background_tasks: BackgroundTasks):
    """Create a new emergency alert"""
    alert_id = f"alert_{uuid.uuid4().hex[:8]}"

    alert_data = {
        "alert_id": alert_id,
        **alert.dict(),
        "timestamp": datetime.now().isoformat()
    }

    # Get AI insights
    ai_insights = await ai_client.analyze_alert(alert_data)

    alert_data["ai_insights"] = ai_insights

    # Broadcast alert
    background_tasks.add_task(
        websocket_service.broadcast_alert,
        alert_data
    )

    # Auto-dispatch for critical alerts
    if alert.severity == "critical":
        background_tasks.add_task(dispatch_emergency_response, alert_data)

    return {"status": "alert_created", "alert_id": alert_id, "ai_insights": ai_insights}

@router.get("/alerts")
async def get_alerts(
    severity: Optional[str] = None,
    limit: int = Query(100, description="Maximum number of alerts to return")
):
    """Get emergency alerts"""
    # In a real implementation, this would query a database
    # For now, return mock data
    mock_alerts = [
        {
            "alert_id": "alert_001",
            "alert_type": "flood",
            "severity": "high",
            "location": {"lat": 26.1445, "lng": 91.7362},
            "description": "Flash flood warning in Assam region",
            "timestamp": datetime.now().isoformat(),
            "source": "sensor"
        }
    ]

    if severity:
        mock_alerts = [a for a in mock_alerts if a["severity"] == severity]

    return {"alerts": mock_alerts[:limit], "count": len(mock_alerts)}

# AI Integration Routes
@router.post("/ai/process-video")
async def process_video(video_url: str, drone_id: str):
    """Process video feed through AI engine"""
    results = await ai_client.process_video(video_url, drone_id)

    if "error" in results:
        raise HTTPException(status_code=500, detail=results["error"])

    return {"status": "processed", "results": results}

@router.post("/ai/analyze-message")
async def analyze_message(analysis: MessageAnalysis):
    """Analyze emergency message with NLP"""
    results = await ai_client.analyze_message(analysis.message)

    if "error" in results:
        raise HTTPException(status_code=500, detail=results["error"])

    # Create alert if urgent
    if results.get("urgency") == "high":
        alert_data = {
            "alert_type": "emergency_message",
            "severity": "high",
            "location": analysis.sender_location or {"lat": 0, "lng": 0},
            "description": f"Urgent message: {analysis.message[:100]}...",
            "source": "user_report"
        }
        # This would trigger alert creation in a real implementation

    return {"status": "analyzed", "results": results}

@router.get("/ai/status")
async def get_ai_status():
    """Get AI engine status"""
    status = await ai_client.get_model_status()
    return status

# System Routes
@router.get("/system/stats")
async def get_system_stats():
    """Get system statistics"""
    return {
        "drones": {
            "total": len(drone_controller.drones),
            "active": len([d for d in drone_controller.drones.values() if d.status == "active"]),
            "busy": len([d for d in drone_controller.drones.values() if d.status == "busy"])
        },
        "websocket": websocket_service.get_connection_stats(),
        "ai_engine": await ai_client.health_check()
    }

@router.get("/system/health")
async def health_check():
    """System health check"""
    ai_healthy = await ai_client.health_check()

    return {
        "status": "healthy" if ai_healthy else "degraded",
        "services": {
            "backend": "healthy",
            "ai_engine": "healthy" if ai_healthy else "unhealthy",
            "websocket": "healthy"
        },
        "timestamp": datetime.now().isoformat()
    }

# Helper functions
async def dispatch_emergency_response(alert_data: Dict[str, Any]):
    """Automatically dispatch emergency response"""
    # Find available drones
    available_drones = [
        drone_id for drone_id, drone in drone_controller.drones.items()
        if drone.status in ["active", "standby"]
    ]

    if not available_drones:
        return

    # Select nearest drone (simplified)
    selected_drone = available_drones[0]

    # Create emergency mission
    mission_data = {
        "command_id": f"emergency_{uuid.uuid4().hex[:8]}",
        "drone_id": selected_drone,
        "command_type": "rescue",
        "target_location": alert_data["location"],
        "priority": "critical"
    }

    drone_controller.assign_mission(
        selected_drone,
        mission_data["command_id"],
        mission_data["command_type"]
    )

    # Broadcast emergency dispatch
    await websocket_service.notify_emergency_dispatch({
        "alert_id": alert_data["alert_id"],
        "mission": mission_data,
        "dispatched_at": datetime.now().isoformat()
    })