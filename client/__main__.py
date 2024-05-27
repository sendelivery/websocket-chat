#!/usr/bin/env python

import asyncio
import nest_asyncio
import websockets
from .client import Client
from .lib import get_random_name
from .lib.ui import TerminalDisplay


async def main():
    uri = "ws://localhost:8005"
    async with websockets.connect(uri) as websocket:

        username = input("What is your name? (Empty for random) ").strip()
        if username == "":
            username = get_random_name()

        client = Client(username, websocket)

        roomid = input("Which room would you like to join? (Empty for random) ").strip()
        if roomid == "":
            roomid = "RANDOM"

        event = {"type": "join", "username": username, "roomid": roomid}
        await client.send_event(event)

        # Wait for server join response
        server_event = await client.receive_event()
        assert server_event["type"] == "server_msg"

        client.set_roomid(roomid)

        # Create and run UI
        t = TerminalDisplay(client)
        await t.run()


if __name__ == "__main__":
    nest_asyncio.apply()
    with asyncio.Runner() as runner:
        runner.run(main())
