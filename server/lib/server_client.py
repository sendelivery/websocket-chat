from websockets import WebSocketServerProtocol


class ServerClient:
    """This class represents a chat client from the point of view of our websocket server."""

    def __init__(self, username: str, websocket: WebSocketServerProtocol) -> None:
        self.username = username
        self.websocket = websocket
