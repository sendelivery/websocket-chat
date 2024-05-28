import asyncio
import json
from websockets import WebSocketServerProtocol
import redis


class ChatClient:
    """This class encapsulates a chat client from the point of view of our websocket server."""

    def __init__(self, username: str, websocket: WebSocketServerProtocol) -> None:
        self.username = username
        self.websocket = websocket

        self.roomid = None

        self._redis = redis.Redis(host="localhost", port=6379, decode_responses=True)
        self._pubsub = self._redis.pubsub(ignore_subscribe_messages=True)

    def subscribe(self, roomid: str) -> None:
        self._pubsub.subscribe(roomid)
        self.roomid = roomid

    def unsubscribe(self) -> None:
        self._pubsub.unsubscribe()
        self.roomid = None

    async def handle_messages(self):
        async for message in self.websocket:
            event = json.loads(message)
            assert event["type"] == "chat"

            print(f"Received chat event: {json.dumps({ "user": event["user"], "message": event["message"] })}")

            self._redis.publish(self.roomid, json.dumps(event))
            
    async def receive_message(self):
        while True:
            message = self._pubsub.get_message()
            
            if message is not None:
                assert message["type"] == "message"
                event = json.loads(message["data"])
                
                await self.websocket.send(json.dumps(event))
                
            await asyncio.sleep(0)
