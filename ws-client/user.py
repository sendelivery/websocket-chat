import asyncio
from websockets import WebSocketClientProtocol


class User:
    def __init__(self, name: str, connection: WebSocketClientProtocol) -> None:
        self.name = name
        self.connection = connection

    async def send(message: str) -> None:
        pass

    async def receive() -> None:
        pass
