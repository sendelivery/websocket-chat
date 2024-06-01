#!/usr/bin/env python

import asyncio
import websockets
from websockets import WebSocketServerProtocol
import json
from .lib import ChatClient


async def subscribe_to_channel(chat_client: ChatClient, roomid: str) -> None:
    event = {
        "type": "server_msg",
        "message": f"Joined {roomid}",
    }
    chat_client.subscribe(roomid)
    await chat_client.websocket.send(json.dumps(event))


async def handler(websocket: WebSocketServerProtocol):
    """
    Handle a connection and dispatch it according to the requested chatroom.
    """
    message = await websocket.recv()
    event = json.loads(message)

    assert event["type"] == "join"
    assert event["roomid"]
    assert event["username"]

    chat_client = ChatClient(event["username"], websocket)

    await subscribe_to_channel(chat_client, event["roomid"])

    await asyncio.gather(chat_client.handle_messages(), chat_client.receive_message())

    # When the client disconnects, either by terminating their end of the connection or by sending
    # a "leave" message, we'll remove their connection from the room.
    chat_client.unsubscribe()


async def main():
    async with websockets.serve(handler, "", 8005):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
