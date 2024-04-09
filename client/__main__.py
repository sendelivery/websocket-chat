#!/usr/bin/env python

import asyncio
import curses
import websockets
from .client import Client
from .ui import TerminalDisplay


async def main():
    uri = "ws://localhost:8001"
    async with websockets.connect(uri) as websocket:

        username = ""
        while username == "":
            username = input("What is your name: ").strip()

        client = Client(username, websocket)

        roomid = input("Which room would you like to join? (Empty for random) ")
        if roomid == "":
            roomid = "RANDOM"

        event = {"type": "join", "username": username, "roomid": roomid}
        await client.send_event(event)

        # Wait for server join response
        server_event = await client.receive_event()
        assert server_event["type"] == "server_msg"
        # print(server_event["message"])

        async def program(stdscr):
            # Create UI
            display = TerminalDisplay(stdscr, client)

            # Run the program
            await display.run()

        await curses.wrapper(program)


asyncio.run(main())
