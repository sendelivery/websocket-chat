#!/usr/bin/env python

import asyncio
import websockets
from websockets import WebSocketClientProtocol
import json
import sys


async def receive_messages(websocket: WebSocketClientProtocol) -> None:
    async for message in websocket:
        event = json.loads(message)
        assert event["type"] == "chat"
        print(event["message"])


async def send_message(websocket: WebSocketClientProtocol) -> None:
    while True:
        msg = await asyncio.to_thread(sys.stdin.readline)
        event = {"type": "chat", "message": msg}
        await websocket.send(json.dumps(event))


async def chat(websocket: WebSocketClientProtocol):
    await asyncio.gather(
        send_message(websocket),
        receive_messages(websocket),
    )


async def main():
    uri = "ws://localhost:8001"
    async with websockets.connect(uri) as websocket:
        event = {"type": "join"}
        roomid = input("Which room would you like to join? (Empty for random) ")
        if roomid != "":
            event["roomid"] = roomid
        await websocket.send(json.dumps(event))
        server_event = json.loads(await websocket.recv())

        # Wait for server join response
        assert server_event["type"] == "server_msg"
        print(server_event["message"])
        await chat(websocket)


if __name__ == "__main__":
    asyncio.run(main())
