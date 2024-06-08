#!/usr/bin/env python

import asyncio
import websockets
from websockets import WebSocketServerProtocol
import json
from .lib import ChatClient

HOST = ""
PORT = 8005


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

    await asyncio.gather(chat_client.publish_messages(), chat_client.poll_messages())

    # When the client disconnects, either by terminating their end of the connection or by sending
    # a "leave" message, we'll remove their connection from the room.
    chat_client.unsubscribe()


async def start_server():
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()


def main():
    asyncio.run(start_server())


if __name__ == "__main__":
    main()
