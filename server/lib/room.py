import json
from typing import Set
from websockets import WebSocketServerProtocol
import websockets
from .server_client import ServerClient

__all__ = ["RANDOM", "Room"]

RANDOM = "random"


class Room:
    def __init__(self, roomid: str) -> None:
        self.roomid = roomid
        self.connected: Set[WebSocketServerProtocol] = set()
        self.chatlog = []

    def subscribe(self, client: ServerClient) -> bool:
        if client.websocket in self.connected:
            print(client.username, "is already in", self.roomid)
            return False

        self.connected.add(client.websocket)
        print(client.username, "has joined", self.roomid)
        return True

    def unsubscribe(self, client: ServerClient) -> bool:
        if client.websocket in self.connected:
            self.connected.remove(client.websocket)
            print(client.username, "has left", self.roomid)
            return True

        print(client.username, "is not in", self.roomid)
        return False

    async def chat(self, server_client: ServerClient):
        async for message in server_client.websocket:
            event = json.loads(message)
            assert event["type"] == "chat"

            print(f"Received chat event: {json.dumps({ "user": event["user"], "message": event["message"] })}")

            websockets.broadcast(self.connected, message)


class ServerRoom(Room):
    def __init__(self, roomid: str) -> None:
        super().__init__(roomid)
