# volta_api/vehicles/ws.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
from volta_api.core.redis import redis_client
import json
import asyncio

router = APIRouter(prefix="/volta/ws", tags=["vehicles"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("")
async def vehicle_locations(websocket: WebSocket):
    """
    Handles both vehicles sending updates and commuters receiving them.
    """
    await manager.connect(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_json()
            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "error": "Invalid payload",
                        "expected_format": {
                            "vehicle_id": "string",
                            "lat": "number",
                            "lng": "number",
                        },
                        "example": {
                            "vehicle_id": "EL25G74vBuE",
                            "lat": -6.8,
                            "lng": 39.3,
                        },
                    }
                )
                continue
            # Example data: {"vehicle_id": "EL25G74vBuE", "lat": -6.8, "lng": 39.3}
            # Publish the data to Redis
            await redis_client.publish("vehicle_locations", json.dumps(data))
            await redis_client.rpush("vehicle_locations_history", json.dumps(data))
            await redis_client.expire("vehicle_locations_history", 60 * 60)  # 1 hour expiry
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
