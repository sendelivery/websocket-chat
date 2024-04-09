#!/usr/bin/env python

import asyncio
import websockets
from websockets import WebSocketServerProtocol
import json

from room.room import ServerRoom


EXISTING_ROOMS = {}


async def chat(websocket: WebSocketServerProtocol, room: ServerRoom):
    async for message in websocket:
        event = json.loads(message)
        assert event["type"] == "chat"

        print("received", event["message"])

        websockets.broadcast(room.connected, message)


async def join(websocket: WebSocketServerProtocol, roomid: str) -> ServerRoom:
    # If our room already exists, we'll add our new user to its set of connections.
    # Otherwise, we'll create one.
    if roomid in EXISTING_ROOMS:
        room = EXISTING_ROOMS[roomid]
    else:
        room = ServerRoom(roomid)
        EXISTING_ROOMS[roomid] = room

    room.connect(websocket)
    event = {
        "type": "server_msg",
        "message": f"Joined {roomid} - {len(room.connected) - 1} other user(s) online.",
    }
    await websocket.send(json.dumps(event))
    return room


async def handler(websocket: WebSocketServerProtocol):
    """
    Handle a connection and dispatch it according to the requested chatroom.
    """
    message = await websocket.recv()
    event = json.loads(message)

    assert event["type"] == "join"

    if "roomid" in event:
        room = await join(websocket, event["roomid"])
        await chat(websocket, room)
    else:
        raise NotImplementedError("Unable to join random room at this time.")

    # When the client disconnects, either by terminating their end of the connection or by sending
    # a "leave" message, we'll remove their connection from the room.
    room.disconnect(websocket)

    if len(room.connected) == 0:
        EXISTING_ROOMS.pop(room.roomid)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()
