import asyncio
import urwid as u
from client.ui.urwid_ui.lib import Chatlog, InputBox, InfoPanel
from client.client.user import Client


class DebugText(u.Text):

    def __init__(self) -> None:
        super().__init__("Debug: ")

    def log(self, message: str) -> str:
        self.set_text(f"Debug: {message}")


class TerminalDisplay:
    PALETTE = [("normal", "white", "black"), ("selected", "light cyan", "black")]

    def __init__(self, client: Client) -> None:
        self.client = client
        self.handle_receive_message = None
        self.debug = DebugText()

        self.chatlog = Chatlog()
        chatlog_lb = u.AttrMap(
            u.LineBox(self.chatlog, title="Chatlog", title_align="left"),
            "normal",
            "selected",
        )

        self.inputbox = InputBox()
        inputbox_lb = u.AttrMap(
            u.LineBox(self.inputbox, title="Message", title_align="left"),
            "normal",
            "selected",
        )

        pile = u.Pile([("weight", 3, chatlog_lb), ("weight", 1, inputbox_lb)])

        self.infopanel = InfoPanel()
        infopanel_lb = u.AttrMap(
            u.LineBox(self.infopanel, title="Information", title_align="left"),
            "normal",
            "selected",
        )

        columns = u.Columns([("weight", 2, pile), infopanel_lb])

        self.frame = u.Frame(columns, footer=self.debug)

    async def run(self) -> None:

        def exit_on_q(key: str) -> None:
            if key in {"esc"}:
                raise u.ExitMainLoop()

        event_loop = asyncio.get_running_loop()
        urwid_asyncio_loop = u.AsyncioEventLoop(loop=event_loop)

        self.urwid_loop = u.MainLoop(
            self.frame,
            palette=self.PALETTE,
            unhandled_input=exit_on_q,
            event_loop=urwid_asyncio_loop,
        )

        # Behaviour for sending messages on inputbox 'enter'
        def handle_on_enter(message: str) -> None:
            event_loop.create_task(self.client.send_message(message))

        self.inputbox.set_on_enter(handle_on_enter)

        # Behaviour for displaying messages on client receipt
        def handle_receive_message(m: str):
            self.chatlog.append_and_set_focus(m)
            self.urwid_loop.draw_screen()

        event_loop.create_task(
            self.client.receive_messages(callback=handle_receive_message)
        )

        self.urwid_loop.run()
