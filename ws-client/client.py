#!/usr/bin/env python

import asyncio
import sys
import websockets
from websockets import WebSocketClientProtocol
import json


async def ainput(string: str) -> str:
    await asyncio.to_thread(sys.stdout.write, f"{string} ")
    return await asyncio.to_thread(sys.stdin.readline)


async def send_message(websocket: WebSocketClientProtocol):
    msg = await ainput(">>>")
    while msg != "dc":
        event = {"type": "chat", "message": msg}
        asyncio.create_task(websocket.send(json.dumps(event)))
        msg = await ainput(">>>")


async def chat(websocket: WebSocketClientProtocol):
    asyncio.create_task(send_message(websocket))
    print("now receiving...")
    async for message in websocket:
        event = json.loads(message)

        assert event["type"] == "chat"
        print(event["message"])


async def join_room():
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


async def handler():
    await join_room()


if __name__ == "__main__":
    asyncio.run(handler())
