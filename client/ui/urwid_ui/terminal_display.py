import asyncio
import urwid as u
from client.ui.urwid_ui.lib import Chatlog, InputBox, InfoPanel
from client.ui.urwid_ui.lib.dummy_text import dummy_text


async def handle_receive_message(callback, urwid_loop):
    for m in dummy_text:
        await asyncio.sleep(1)
        callback(m)
        urwid_loop.draw_screen()


class DebugText(u.Text):

    def __init__(self) -> None:
        super().__init__("Debug: ")

    def log(self, message: str) -> str:
        self.set_text(f"Debug: {message}")


class TerminalDisplay:
    PALETTE = [("normal", "white", "black"), ("selected", "light cyan", "black")]

    def __init__(self) -> None:
        self.debug = DebugText()

        self.chatlog = Chatlog(debug=self.debug)
        self.chatlog_lb = u.AttrMap(
            u.LineBox(self.chatlog, title="Chatlog", title_align="left"),
            "normal",
            "selected",
        )

        self.inputbox = InputBox(self.chatlog.append_and_set_focus)
        self.inputbox_lb = u.AttrMap(
            u.LineBox(self.inputbox, title="Message", title_align="left"),
            "normal",
            "selected",
        )

        self.pile = u.Pile(
            [("weight", 3, self.chatlog_lb), ("weight", 1, self.inputbox_lb)]
        )

        # # Think of a cleaner solution to this, a focus map maybe?
        # def return_to_inputbox() -> None:
        #     self.pile._set_focus_position(1)

        # self.chatlog.exit_focus = return_to_inputbox

        self.infopanel = InfoPanel()
        self.infopanel_lb = u.AttrMap(
            u.LineBox(self.infopanel, title="Information", title_align="left"),
            "normal",
            "selected",
        )

        self.columns = u.Columns([("weight", 2, self.pile), self.infopanel_lb])

        self.frame = u.Frame(self.columns, footer=self.debug)

    def exit_on_q(self, key: str) -> None:
        if key in {"Q", "q"}:
            raise u.ExitMainLoop()

    async def run(self) -> None:
        event_loop = asyncio.get_running_loop()
        urwid_asyncio_loop = u.AsyncioEventLoop(loop=event_loop)

        urwid_loop = u.MainLoop(
            self.frame,
            palette=self.PALETTE,
            unhandled_input=self.exit_on_q,
            event_loop=urwid_asyncio_loop,
        )

        event_loop.create_task(
            handle_receive_message(
                callback=self.chatlog.append_and_set_focus, urwid_loop=urwid_loop
            )
        )

        urwid_loop.run()
