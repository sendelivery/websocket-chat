import pytest
from unittest.mock import patch, Mock
from urwid import ExitMainLoop
from websockets import WebSocketClientProtocol
from client.client import Client
from client.lib.ui import ConsoleDisplay


# Arrange a fixture for a mock client that will be reused across tests
@pytest.fixture
def mock_client():
    mock_ws = Mock(WebSocketClientProtocol)
    return Mock(Client("MOCK_USERNAME", mock_ws))


# The pytest-asyncio plugin facilitates testing of code that uses the asyncio
# library. We'll set it to apply to the entire test class for simplicity.
@pytest.mark.asyncio(scope="class")
class TestConsoleDisplay:

    # Most tests in this class patch the urwid MainLoop class to prevent urwid hijacking our
    # terminal. However, we need some of its functionality depending on the test, so we won't
    # patch it at the class level.

    async def test_ui_has_expected_widgets(self, mock_client):
        display = ConsoleDisplay(mock_client)

        assert display.chatlog is not None
        assert display.inputbox is not None
        assert display.infopanel is not None

    @patch("client.lib.ui.console_display.u.MainLoop")
    @patch("client.lib.ui.console_display.asyncio.get_running_loop")
    @patch("client.lib.ui.console_display.u.AsyncioEventLoop")
    async def test_urwid_loop_hooks_into_asyncio_loop(
        self, MockAsyncioEventLoop, mocked_get_running_loop, MockMainLoop, mock_client
    ):
        display = ConsoleDisplay(mock_client)
        await display.run()

        # Here we're testing to make sure the asyncio event loop is hooked up correctly with the
        # urwid library's MainLoop class. Otherwise our console display can't manage multiple
        # the coroutine we want to run in response to incoming and outgoing messages.

        # First, we want to ensure urwid's event loop wrapper class has the currently running
        # asyncio event loop passed in.
        assert mocked_get_running_loop.called
        assert (
            MockAsyncioEventLoop.call_args.kwargs["loop"]
            == mocked_get_running_loop.return_value
        )

        # Next, we want urwid's main loop to have the wrapped event loop passed in.
        assert MockMainLoop.called
        assert (
            MockMainLoop.call_args.kwargs["event_loop"]
            == MockAsyncioEventLoop.return_value
        )

        # Finally, MainLoop.run should have been called.
        assert MockMainLoop.return_value.run.called

    @patch("client.lib.ui.console_display.u.MainLoop")
    @patch("client.lib.ui.console_display.asyncio.get_running_loop")
    async def test_creates_a_task_to_handle_incoming_messages(
        self, mocked_get_running_loop, _, monkeypatch, mock_client
    ):
        async def dummy_coroutine():
            pass

        coro = dummy_coroutine()
        monkeypatch.setattr(
            mock_client, "handle_incoming_messages", lambda callback: coro
        )

        # When we initialise and run our console display
        display = ConsoleDisplay(mock_client)
        await display.run()

        # Then we want the display to have created a task for handling incoming messages.
        loop = mocked_get_running_loop.return_value

        assert mocked_get_running_loop.call_count == 1
        assert loop.create_task.call_count == 1
        loop.create_task.assert_called_with(coro)

    @patch("client.lib.ui.console_display.u.MainLoop")
    @patch("client.lib.ui.console_display.asyncio.get_running_loop")
    async def test_correctly_calls_client_send_message(
        self, mocked_get_running_loop, _, monkeypatch, mock_client
    ):
        async def dummy_coroutine():
            pass

        coro = dummy_coroutine()
        monkeypatch.setattr(mock_client, "send_message", lambda message: coro)

        # When we initialise and run our console display
        display = ConsoleDisplay(mock_client)
        await display.run()

        # And the user types in their message and hits 'enter'
        display.inputbox.set_edit_text("Here's my message!")
        display.inputbox.keypress((5, 5), "enter")

        # Then we want the display to have created a task for handling the outgoing message.
        loop = mocked_get_running_loop.return_value

        assert mocked_get_running_loop.call_count == 1
        assert loop.create_task.call_count == 2
        loop.create_task.assert_called_with(coro)

    @patch("client.lib.ui.console_display.u.MainLoop.run")
    async def test_can_exit_display_with_esc(self, _, mock_client):
        display = ConsoleDisplay(mock_client)

        await display.run()

        with pytest.raises(ExitMainLoop):
            display.urwid_loop.process_input(["esc"])
