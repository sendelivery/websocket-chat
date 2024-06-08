import pytest
from unittest.mock import AsyncMock, Mock, patch
from server import __main__ as server_module
from server.lib import ChatClient


@pytest.mark.asyncio(scope="class")
class TestServerModule:
    @patch("server.__main__.asyncio.run")
    async def test_main_starts_server_in_event_loop(
        self, mock_asyncio_run, monkeypatch
    ):
        # Given
        coro_func = AsyncMock()
        coro = coro_func()

        monkeypatch.setattr(server_module, "start_server", lambda: coro)

        # When
        server_module.main()

        # Then
        mock_asyncio_run.assert_called_once_with(server_module.start_server())

    @patch("server.__main__.asyncio.Future", new_callable=AsyncMock)
    @patch("server.__main__.websockets.serve")
    async def test_start_server_starts_ws_server_and_awaits_indefinitely(
        self, mock_websockets_serve, mock_asyncio_future
    ):
        # When
        await server_module.start_server()

        # Then
        mock_websockets_serve.assert_called_once_with(
            server_module.handler, server_module.HOST, server_module.PORT
        )
        assert mock_websockets_serve.return_value.__aenter__.called
        assert mock_asyncio_future.called

    @patch("server.__main__.ChatClient")
    @patch("server.__main__.websockets.WebSocketServerProtocol")
    @patch("server.__main__.asyncio.gather", new_callable=AsyncMock)
    async def test_handler_subcribes_to_channel_and_awaits_sending_receiving_messages(
        self, mock_asyncio_gather, mock_ws, mock_chat_client
    ):
        # Given
        roomid = "MOCK_ROOMID"
        username = "MOCK_USERNAME"
        join_client_event = (
            f'{{"type": "join", "roomid": "{roomid}", "username": "{username}"}}'
        )
        join_server_event = f'{{"type": "server_msg", "message": "Joined {roomid}"}}'

        # Let's replace the default client mock's websocket so we can assert on it in a
        # straightforward way.
        mock_chat_client.return_value.websocket = mock_ws

        mock_ws.recv = AsyncMock(return_value=join_client_event)
        mock_ws.send = AsyncMock()

        # When
        await server_module.handler(mock_ws)

        # Then
        assert mock_ws.recv.called
        mock_chat_client.assert_called_once_with(username, mock_ws)
        mock_ws.send.assert_called_once_with(join_server_event)
        mock_asyncio_gather.assert_called_once_with(
            mock_chat_client.return_value.publish_messages(),
            mock_chat_client.return_value.poll_messages(),
        )
        assert mock_chat_client.return_value.unsubscribe.called

    @patch("server.__main__.websockets.WebSocketServerProtocol")
    async def test_subscribe_to_channel_calls_client_subscribe_and_sends_ws_event(
        self, mock_ws
    ):
        # Given
        roomid = "MOCK_ROOMID"
        mock_chat_client_instance = Mock(ChatClient).return_value
        mock_chat_client_instance.username = "MOCK_USER"
        join_server_event = f'{{"type": "server_msg", "message": "Joined {roomid}"}}'

        # Let's replace the default client mock's websocket so we can assert on it in a
        # straightforward way.
        mock_chat_client_instance.websocket = mock_ws

        mock_ws.send = AsyncMock()

        # When
        await server_module.subscribe_to_channel(mock_chat_client_instance, roomid)

        # Then
        mock_chat_client_instance.subscribe.assert_called_once_with(roomid)
        mock_ws.send.assert_called_once_with(join_server_event)
