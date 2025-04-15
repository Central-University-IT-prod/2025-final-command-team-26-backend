from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[UUID, dict[WebSocket, UUID | None]] = {}

    async def connect(
        self, websocket: WebSocket, room_id: UUID, user_id: UUID | None = None
    ) -> None:
        if not self.active_connections.get(room_id):
            self.active_connections[room_id] = {}

        if websocket not in self.active_connections[room_id].keys():
            await websocket.accept()

        self.active_connections[room_id][websocket] = user_id

    async def disconnect(self, websocket: WebSocket, room_id: UUID) -> UUID | None:
        if room_id not in self.active_connections.keys():
            return None
        if websocket not in self.active_connections[room_id].keys():
            return None

        try:
            await websocket.close()
        except:
            pass

        val = self.active_connections[room_id].pop(websocket)
        if len(self.active_connections[room_id]) == 0:
            self.active_connections.pop(room_id)

        return val

    async def send_personal_data(
        self, websocket: WebSocket, room_id: UUID, data: dict
    ) -> None:
        try:
            await websocket.send_json(data)
        except Exception as e:
            await self.disconnect(websocket, room_id)

    async def broadcast(self, room_id: UUID, data: dict) -> None:
        if room_id not in self.active_connections.keys():
            return

        room_connections = self.active_connections.get(room_id, {}).copy()
        for connection in self.active_connections.get(room_id, {}).keys():
            try:
                await connection.send_json(data)
            except:
                room_connections.pop(connection)
        self.active_connections[room_id] = room_connections
