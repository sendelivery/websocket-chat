#!/usr/bin/env python

from typing import Set

import asyncio
import websockets
from websockets import WebSocketServerProtocol
import json

from chatrooms.room import Room


EXISTING_ROOMS: Set[Room] = {}


async def chat(websocket: WebSocketServerProtocol, room: Room):
    async for message in websocket:
        event = json.loads(message)
        assert event["type"] == "chat"

        websockets.broadcast(room.connected, message)


async def join(websocket: WebSocketServerProtocol, roomid: str) -> Room:
    # If our room already exists, we'll add our new user to its set of connections.
    # Otherwise, we'll create
    if roomid in EXISTING_ROOMS:
        room = EXISTING_ROOMS[roomid]
    else:
        room = Room(roomid)
        EXISTING_ROOMS[roomid] = room

    room.connect(websocket)
    event = {
        "type": "server_msg",
        "message": f"Joined {roomid} - {len(room.connected)} user(s) online.",
    }
    await websocket.send(json.dumps(event))

    try:
        await chat(websocket, room)
    finally:
        room.disconnect(websocket)


async def handler(websocket: WebSocketServerProtocol):
    """
    Handle a connection and dispatch it according to the requested chatroom.
    """
    message = await websocket.recv()
    event = json.loads(message)

    assert event["type"] == "join"

    if "roomid" in event:
        room = await join(websocket, event["roomid"])
    else:
        raise NotImplementedError("Unable to join random room at this time.")


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
