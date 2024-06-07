from collections import deque
import pytest
from unittest.mock import Mock, patch, call
import websockets
from server.lib import ChatClient


@pytest.mark.asyncio(scope="class")
class TestChatClient:
    @pytest.fixture
    @patch("server.lib.chat_client.redis.Redis")
    def mock_client(self, _):
        websocket = Mock(websockets.WebSocketServerProtocol)
        chat_client = ChatClient("MOCK_USER", websocket)

        return chat_client

    async def test_chat_client_properties_exist(self, mock_client):
        assert mock_client.username == "MOCK_USER"
        assert mock_client.websocket is not None
        assert mock_client.roomid is None
        assert mock_client._redis is not None
        assert mock_client._pubsub is not None

    async def test_chat_client_subscribes_to_redis_channel(self, mock_client):
        # When
        assert mock_client.roomid is None
        mock_client.subscribe("MOCK_ROOMID")

        # Then
        mock_client._pubsub.subscribe.assert_called_once_with("MOCK_ROOMID")
        assert mock_client.roomid == "MOCK_ROOMID"

    async def test_chat_client_unsubscribes_to_redis_channel(self, mock_client):
        # Given
        mock_client.subscribe("MOCK_ROOMID")

        mock_client._pubsub.subscribe.assert_called_once_with("MOCK_ROOMID")
        assert mock_client.roomid == "MOCK_ROOMID"

        # When
        mock_client.unsubscribe()

        # Then
        mock_client._pubsub.unsubscribe.assert_called_once()
        assert mock_client.roomid is None

    async def test_chat_client_can_handle_publishing_messages_to_channel(
        self, mock_client
    ):
        # Given
        # We'll mock our chat client's websocket and its __aiter__ magic method so that we can
        # iterate over the below messages as if they've been received over the network.
        m1 = '{"type": "chat", "message": "Message1", "user": "USER"}'
        m2 = '{"type": "chat", "message": "Message2", "user": "USER"}'
        m3 = '{"type": "chat", "message": "Message3", "user": "USER"}'
        mock_client.websocket.messages = deque([m1, m2, m3])

        async def mock_aiter(self):
            while len(self.messages):
                yield self.messages.popleft()

        mock_client.websocket.__aiter__ = mock_aiter

        # When
        roomid = "MOCK_ROOMID"
        mock_client.subscribe(roomid)
        await mock_client.publish_messages()

        # Then
        assert mock_client._redis.publish.call_count == 3

        calls = [call(roomid, m1), call(roomid, m2), call(roomid, m3)]
        mock_client._redis.publish.assert_has_calls(calls)

    async def test_chat_client_can_receive_and_forward_messages_to_websocket(
        self, mock_client, monkeypatch
    ):
        # Given
        chat_events = [
            '{"type": "chat", "message": "Message1", "user": "USER"}',
            '{"type": "chat", "message": "Message2", "user": "USER"}',
            '{"type": "chat", "message": "Message3", "user": "USER"}',
        ]
        messages = [
            {"type": "message", "data": chat_event} for chat_event in chat_events
        ]

        def generate_messages():
            for m in messages:
                yield m

        message_iterator = generate_messages()

        monkeypatch.setattr(
            mock_client._pubsub, "get_message", lambda: next(message_iterator)
        )

        # When - our generator will raise a RuntimeError upon the StopIteration signal
        with pytest.raises(RuntimeError):
            await mock_client.receive_message()

        # Then
        assert mock_client.websocket.send.call_count == 3
        calls = [call(message["data"]) for message in messages]
        mock_client.websocket.send.assert_has_calls(calls)
