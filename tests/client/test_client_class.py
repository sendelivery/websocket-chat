import pytest
from unittest.mock import AsyncMock, Mock
import json
from jsonschema import ValidationError
from websockets import WebSocketClientProtocol
from client.client import Client
from collections import deque


@pytest.fixture
def mock_websocket():
    return AsyncMock(WebSocketClientProtocol)


@pytest.mark.asyncio(scope="class")
class TestClientClass:

    async def test_has_expected_properties(self, mock_websocket):
        # Given
        client = Client("MOCK_USERNAME", mock_websocket)

        # When
        client.set_roomid("MOCK_ROOMID")

        # Then
        assert client.username == "MOCK_USERNAME"
        assert client.roomid == "MOCK_ROOMID"
        assert client.websocket == mock_websocket
        assert str(client) == client.username

    async def test_can_receive_server_events(self, mock_websocket):
        # Given
        dummy_server_event = '{"type": "join", "roomid": "DUMMY"}'

        # Mock our websocket to receive a dummy event from the server
        mock_websocket.recv = AsyncMock(return_value=dummy_server_event)

        client = Client("MOCK_USERNAME", mock_websocket)

        # When
        event = await client.receive_server_event()

        # Then
        assert event == json.loads(dummy_server_event)

    async def test_raises_ValidationError_if_incoming_message_doesnt_match_schema(
        self, mock_websocket
    ):
        # Given
        invalid_dummy_server_event = '{"not": "what", "we": "expect!"}'

        mock_websocket.recv = AsyncMock(return_value=invalid_dummy_server_event)

        client = Client("MOCK_USERNAME", mock_websocket)

        # When & Then
        with pytest.raises(ValidationError):
            await client.receive_server_event()

    async def test_can_handle_incoming_messages(self, mock_websocket):
        # Given
        # We'll mock a websocket and its __aiter__ magic method so that we can iterate over the
        # below three messages as if they've been received over the network.
        mock_websocket.messages = deque(
            [
                '{"type":"chat", "message": "Message1"}',
                '{"type":"chat", "message": "Message2"}',
                '{"type":"chat", "message": "Message3"}',
            ]
        )

        async def mock_aiter(self):
            while len(self.messages):
                yield self.messages.popleft()

        mock_websocket.__aiter__ = mock_aiter

        # Next we'll create a client that will handle incoming messages by simply appending them to
        # a list.
        client = Client("MOCK_USERNAME", mock_websocket)

        handled = []

        def callback(event):
            handled.append(event["message"])

        # When
        await client.handle_incoming_messages(callback)

        # Then
        assert len(handled) == 3
        assert handled == ["Message1", "Message2", "Message3"]

    async def test_raise_AssertionError_if_message_type_is_invalid(
        self, mock_websocket
    ):
        # Given
        mock_websocket.messages = deque(['{"type":"INVALID", "message": "Message1"}'])

        async def mock_aiter(self):
            while len(self.messages):
                yield self.messages.popleft()

        mock_websocket.__aiter__ = mock_aiter

        client = Client("MOCK_USERNAME", mock_websocket)
        mock_callback = Mock()

        # When & Then
        with pytest.raises(AssertionError):
            await client.handle_incoming_messages(mock_callback)

        mock_callback.assert_not_called()

    async def test_calls_websocket_send_when_sending_an_event(self, mock_websocket):
        # Given
        client = Client("MOCK_USERNAME", mock_websocket)
        event = {"type": "chat", "message": "Hello!"}

        # When
        await client.send_event(event)

        # Then
        mock_websocket.send.assert_called_once_with(json.dumps(event))

    async def test_raises_a_ValidationError_if_invalid_message_on_send_event(
        self, mock_websocket
    ):
        # Given
        client = Client("MOCK_USERNAME", mock_websocket)
        event = {"not": "a", "valid": "event!"}

        # When & Then
        with pytest.raises(ValidationError):
            await client.send_event(event)

        mock_websocket.send.assert_not_called()

    async def test_send_message_results_in_sending_a_message_to_the_ws_server(
        self, mock_websocket
    ):
        # Given
        client = Client("MOCK_USERNAME", mock_websocket)
        message = "Hello, all!"

        # When
        # Send message attaches the clien't username to the event
        await client.send_message(message)

        # Then
        event = {"type": "chat", "message": message, "user": "MOCK_USERNAME"}
        mock_websocket.send.assert_called_once_with(json.dumps(event))
