import json
from jsonschema import validate
from typing import Dict, Callable
from websockets import WebSocketClientProtocol


schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Client Event",
    "type": "object",
    "properties": {
        "type": {"type": "string"},  # "join" | "chat" | "disconnect"
        "roomid": {"type": "string"},  # required for "join" and "disconnect"
        "message": {"type": "string"},  # required for "chat"
        "user": {"type": "string"},  # required for "chat"
    },
    "required": ["type"],
}


class Client:

    def __init__(self, username: str, websocket: WebSocketClientProtocol) -> None:
        self.username = username
        self.roomid = ""
        self.websocket = websocket

    def __repr__(self) -> str:
        return self.username

    def set_roomid(self, roomid: str) -> None:
        self.roomid = roomid

    async def receive_server_event(self) -> Dict:
        server_event = json.loads(await self.websocket.recv())
        validate(server_event, schema)
        return server_event

    async def handle_incoming_messages(self, callback: Callable[[Dict], None]) -> None:
        async for message in self.websocket:
            event = json.loads(message)
            assert event["type"] == "chat"
            callback(event)

    async def send_event(self, event: Dict) -> None:
        validate(event, schema)
        await self.websocket.send(json.dumps(event))

    async def send_message(self, msg: str) -> None:
        event = {"type": "chat", "message": msg, "user": self.username}
        await self.send_event(event)
