import asyncio
from typing import Dict
import urwid as u
from .lib import Chatlog, InputBox, InfoPanel
from client.client import Client


class ConsoleDisplay:

    class LineBoxDecoration(u.AttrMap):
        def __init__(self, w: u.Widget, title: str = "") -> None:
            lb = u.LineBox(w, title, title_align="left")
            super().__init__(lb, "normal", "selected")

    PALETTE = [
        ("normal", "light gray", ""),
        ("selected", "white", "", "bold"),
        ("heading", "white", "", "bold"),
        ("user_highlight", "light green", ""),
        ("self_highlight", "light red", "", "underline"),
    ]

    def __init__(self, client: Client) -> None:
        self.client = client

        self.chatlog = Chatlog()
        chatlog_lb = self.LineBoxDecoration(self.chatlog, "Chatlog")

        self.inputbox = InputBox()
        inputbox_lb = self.LineBoxDecoration(self.inputbox, "Message")

        pile = u.Pile([("weight", 3, chatlog_lb), ("weight", 1, inputbox_lb)])

        self.infopanel = InfoPanel(room=client.roomid)
        infopanel_lb = self.LineBoxDecoration(self.infopanel, "Information")

        columns = u.Columns([("weight", 2, pile), infopanel_lb])

        header = u.AttrMap(
            u.Text("Websocket Chat by sendelivery", align="center"), "heading"
        )
        footer = u.AttrMap(
            u.Text(f"Connected as {client.username}", align="left"), "heading"
        )

        self.frame = u.Frame(columns, header=header, footer=footer)

    async def run(self) -> None:

        def exit_on_esc(key: str) -> None:
            if key in {"esc"}:
                raise u.ExitMainLoop()

        event_loop = asyncio.get_running_loop()
        urwid_asyncio_loop = u.AsyncioEventLoop(loop=event_loop)

        self.urwid_loop = u.MainLoop(
            self.frame,
            palette=self.PALETTE,
            unhandled_input=exit_on_esc,
            event_loop=urwid_asyncio_loop,
        )

        # Behaviour for sending messages on inputbox 'enter'
        def handle_on_enter(message: str) -> None:
            event_loop.create_task(self.client.send_message(message))

        self.inputbox.set_on_enter(handle_on_enter)

        # Behaviour for displaying messages on client receipt
        def handle_receive_message(event: Dict):
            highlight = "user_highlight"
            if event["user"] == self.client.username:
                highlight = "self_highlight"

            self.chatlog.append_and_set_focus(
                event["user"], event["message"], highlight
            )
            self.urwid_loop.draw_screen()

        event_loop.create_task(
            self.client.handle_messages(callback=handle_receive_message)
        )

        self.urwid_loop.run()
