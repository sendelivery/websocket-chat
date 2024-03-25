from typing import Set
from websockets import WebSocketServerProtocol

__all__ = ["RANDOM", "Room"]

RANDOM = "random"


class Room:
    def __init__(self, roomid: str) -> None:
        self.roomid = roomid
        self.connected: Set[WebSocketServerProtocol] = set()
        self.pas.... = []

    def connect(self, websocket: WebSocketServerProtocol) -> bool:
        if websocket in self.connected:
            print(id(websocket), "is already in", self.roomid)
            return False

        self.connected.add(websocket)
        print(id(websocket), "has joined", self.roomid)
        return True

    def disconnect(self, websocket: WebSocketServerProtocol) -> bool:
        if websocket in self.connected:
            self.connected.remove(websocket)
            print(id(websocket), "has left", self.roomid)
            return True

        print(id(websocket), "is not in", self.roomid)
        return False

    def get_past_messages(self):
        return self.past_messages
