"""
WebSocket Service for Real-time Communication
Handles real-time updates between backend and frontend
"""

import asyncio
from typing import Dict, List, Any, Callable
from datetime import datetime
import json
from loguru import logger

class WebSocketService:
    """Manages WebSocket connections and real-time messaging"""

    def __init__(self):
        self.connected_clients: Dict[str, Any] = {}  # sid -> client_info
        self.subscriptions: Dict[str, List[str]] = {}  # topic -> [sids]
        self.event_handlers: Dict[str, List[Callable]] = {}

    def register_event_handler(self, event: str, handler: Callable):
        """Register an event handler"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
        logger.info(f"Registered handler for event: {event}")

    async def handle_connect(self, sid: str, environ: Dict[str, Any]):
        """Handle client connection"""
        self.connected_clients[sid] = {
            "connected_at": datetime.now(),
            "user_agent": environ.get("HTTP_USER_AGENT", "Unknown"),
            "remote_addr": environ.get("REMOTE_ADDR", "Unknown")
        }
        logger.info(f"Client connected: {sid}")

    async def handle_disconnect(self, sid: str):
        """Handle client disconnection"""
        if sid in self.connected_clients:
            del self.connected_clients[sid]

        # Remove from all subscriptions
        for topic in self.subscriptions:
            if sid in self.subscriptions[topic]:
                self.subscriptions[topic].remove(sid)

        logger.info(f"Client disconnected: {sid}")

    async def subscribe_to_topic(self, sid: str, topic: str):
        """Subscribe client to a topic"""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []

        if sid not in self.subscriptions[topic]:
            self.subscriptions[topic].append(sid)
            logger.info(f"Client {sid} subscribed to topic: {topic}")

    async def unsubscribe_from_topic(self, sid: str, topic: str):
        """Unsubscribe client from a topic"""
        if topic in self.subscriptions and sid in self.subscriptions[topic]:
            self.subscriptions[topic].remove(sid)
            logger.info(f"Client {sid} unsubscribed from topic: {topic}")

    async def broadcast_to_topic(self, topic: str, data: Any, sio_server=None):
        """Broadcast message to all subscribers of a topic"""
        if topic not in self.subscriptions:
            return

        subscribers = self.subscriptions[topic]
        if not subscribers:
            return

        message = {
            "topic": topic,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        if sio_server:
            for sid in subscribers:
                await sio_server.emit(topic, message, to=sid)
        else:
            logger.warning("No Socket.IO server provided for broadcasting")

        logger.debug(f"Broadcasted to topic '{topic}': {len(subscribers)} subscribers")

    async def send_to_client(self, sid: str, event: str, data: Any, sio_server=None):
        """Send message to specific client"""
        if sid not in self.connected_clients:
            logger.warning(f"Client {sid} not connected")
            return

        message = {
            "event": event,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        if sio_server:
            await sio_server.emit(event, message, to=sid)
        else:
            logger.warning("No Socket.IO server provided for sending")

        logger.debug(f"Sent to client {sid}: {event}")

    async def broadcast_alert(self, alert_data: Dict[str, Any], sio_server=None):
        """Broadcast emergency alert to all clients"""
        await self.broadcast_to_topic("alerts", {
            "type": "new_alert",
            "alert": alert_data
        }, sio_server)

    async def broadcast_drone_update(self, drone_data: Dict[str, Any], sio_server=None):
        """Broadcast drone telemetry update"""
        await self.broadcast_to_topic("drones", {
            "type": "telemetry_update",
            "drone": drone_data
        }, sio_server)

    async def broadcast_mission_update(self, mission_data: Dict[str, Any], sio_server=None):
        """Broadcast mission status update"""
        await self.broadcast_to_topic("missions", {
            "type": "mission_update",
            "mission": mission_data
        }, sio_server)

    async def notify_emergency_dispatch(self, dispatch_data: Dict[str, Any], sio_server=None):
        """Notify about emergency response dispatch"""
        await self.broadcast_to_topic("emergency", {
            "type": "dispatch",
            "dispatch": dispatch_data
        }, sio_server)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.connected_clients),
            "active_subscriptions": {topic: len(subs) for topic, subs in self.subscriptions.items()},
            "topics": list(self.subscriptions.keys())
        }

    async def cleanup_stale_connections(self, max_age_minutes: int = 30):
        """Clean up stale connections"""
        cutoff_time = datetime.now().timestamp() - (max_age_minutes * 60)
        stale_sids = []

        for sid, client_info in self.connected_clients.items():
            if client_info["connected_at"].timestamp() < cutoff_time:
                stale_sids.append(sid)

        for sid in stale_sids:
            logger.info(f"Cleaning up stale connection: {sid}")
            await self.handle_disconnect(sid)

        if stale_sids:
            logger.info(f"Cleaned up {len(stale_sids)} stale connections")

# Global WebSocket service instance
websocket_service = WebSocketService()