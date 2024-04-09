#!/usr/bin/env python

import asyncio
import websockets
from websockets import WebSocketClientProtocol
import json
import sys

from .ui import TerminalDisplay
import curses


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

        # Wait for server join response
        server_event = json.loads(await websocket.recv())
        assert server_event["type"] == "server_msg"
        print(server_event["message"])

        async def program(stdscr):
            # Create UI
            display = TerminalDisplay(stdscr)

            # Run the program
            tasks = (
                asyncio.create_task(display.run(websocket)),
                asyncio.create_task(display.receive_messages(websocket)),
            )
            await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )

        await curses.wrapper(program)
