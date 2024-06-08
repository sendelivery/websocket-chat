import pytest
from unittest.mock import AsyncMock, Mock, patch
import websockets
from client import __main__ as client_module


@pytest.mark.asyncio(scope="class")
class TestClientModule:
    @pytest.fixture(autouse=True)
    def before_each(self, monkeypatch):
        call_num = 0
        input_dict = {
            0: "MOCK_USER",
            1: "MOCK_ROOMID",
        }

        def get_val(*_):
            nonlocal call_num
            call_num += 1
            return input_dict[call_num - 1]

        monkeypatch.setattr("builtins.input", get_val)

    @patch("client.__main__.asyncio.Runner")
    @patch("client.__main__.nest_asyncio")
    async def test_applies_nested_event_loop_and_runs_program_in_event_loop(
        self, mock_nest_asyncio, mock_asyncio_runner, monkeypatch
    ):
        # Given
        mock_main_connect = AsyncMock()
        connect_coroutine = mock_main_connect()
        monkeypatch.setattr("client.__main__.connect", lambda *_: connect_coroutine)

        # When
        client_module.main()

        # Then
        assert mock_nest_asyncio.apply.called
        assert mock_asyncio_runner.called

        context_manager = mock_asyncio_runner.return_value.__enter__

        assert context_manager.called
        context_manager.return_value.run.assert_called_once_with(connect_coroutine)

    @patch("client.__main__.ConsoleDisplay")
    @patch("client.__main__.websockets.connect")
    async def test_connects_to_the_ws_server_and_starts_program(
        self, mock_websockets_connect, mock_console_display
    ):
        # Given - A mocked websocket and corresponding context manager.
        mock_websocket = Mock(websockets.WebSocketClientProtocol)
        # The websocket is mocked to always receive the same message from the server.
        mock_websocket.recv = AsyncMock(
            return_value='{"type":"server_msg", "roomid":"MOCK_ROOMID"}'
        )
        mock_websockets_connect.return_value.__aenter__.return_value = mock_websocket

        mock_run_console_display = AsyncMock()
        mock_console_display.return_value.run = mock_run_console_display

        # When
        await client_module.connect("USER", "ROOMID")

        # Then
        # A websocket connection should have been established
        assert mock_websockets_connect.called

        # A request to join a room should have been sent
        assert mock_websocket.send.called
        mock_websocket.send.assert_called_once_with(
            '{"type": "join", "username": "USER", "roomid": "ROOMID"}'
        )

        # A corresponding response should have been received
        assert mock_websocket.recv.called

        # Console display is initialised and run
        assert mock_console_display.called
        assert mock_run_console_display.called


class TestClientModuleMiscellaneous:
    def test_input_with_default(self, monkeypatch):
        # Given
        monkeypatch.setattr("builtins.input", lambda *_: "")

        # When
        user_input = client_module.input_with_default("PROMPT", "DEFAULT_VALUE")

        # Then
        assert user_input == "DEFAULT_VALUE"
