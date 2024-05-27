#!/usr/bin/env python

import asyncio
import websockets
from websockets import WebSocketServerProtocol
import json

from .lib import ServerClient, ServerRoom


EXISTING_ROOMS = {}


async def join_or_create_room(server_client: ServerClient, roomid: str) -> ServerRoom:
    # If our room already exists, we'll add our new user to its set of connections.
    # Otherwise, we'll create one.
    if roomid in EXISTING_ROOMS:
        room = EXISTING_ROOMS[roomid]
    else:
        room = ServerRoom(roomid)
        EXISTING_ROOMS[roomid] = room

    room.subscribe(server_client)
    event = {
        "type": "server_msg",
        "message": f"Joined {roomid} - {len(room.connected) - 1} other user(s) online.",
    }
    await server_client.websocket.send(json.dumps(event))
    return room


async def handler(websocket: WebSocketServerProtocol):
    """
    Handle a connection and dispatch it according to the requested chatroom.
    """
    message = await websocket.recv()
    event = json.loads(message)

    assert event["type"] == "join"
    assert event["roomid"]
    assert event["username"]

    server_client = ServerClient(event["username"], websocket)

    room = await join_or_create_room(server_client, event["roomid"])
    await room.chat(server_client)

    # When the client disconnects, either by terminating their end of the connection or by sending
    # a "leave" message, we'll remove their connection from the room.
    room.unsubscribe(server_client)

    if len(room.connected) == 0:
        EXISTING_ROOMS.pop(room.roomid)


async def main():
    async with websockets.serve(handler, "", 8005):
        await asyncio.Future()
