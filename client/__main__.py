#!/usr/bin/env python

import asyncio
from typing import Any, Coroutine
import nest_asyncio
import websockets
from .client import Client
from .lib import get_random_name
from .lib.ui import ConsoleDisplay


async def connect(username: str, roomid: str) -> Coroutine[Any, Any, None]:
    uri = "ws://localhost:8005"
    async with websockets.connect(uri) as websocket:
        client = Client(username, websocket)

        # Send a message to the server requesting to join a room
        event = {"type": "join", "username": username, "roomid": roomid}
        await client.send_event(event)

        # Wait for the server's response
        server_event = await client.receive_server_event()
        assert server_event["type"] == "server_msg"

        client.set_roomid(roomid)

        # Create and run console UI
        display = ConsoleDisplay(client)
        await display.run()


def input_with_default(prompt: str, default) -> str:
    user_input = input(prompt).strip()

    if user_input == "":
        user_input = default

    return user_input


def main() -> None:
    username = input_with_default(
        "What is your name? (Empty for random) ", default=get_random_name()
    )

    roomid = input_with_default(
        "Which room would you like to join? (Empty for random) ", default="RANDOM"
    )

    nest_asyncio.apply()
    with asyncio.Runner() as runner:
        runner.run(connect(username, roomid))


if __name__ == "__main__":
    main()
