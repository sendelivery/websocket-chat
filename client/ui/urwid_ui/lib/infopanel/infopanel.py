import urwid as u
from typing import Iterable
from collections import defaultdict


class InfoPanel(u.WidgetWrap[u.ListBox]):
    CONTROL_MAP = defaultdict(tuple)
    CONTROL_MAP["chatlog"] = ("J / K to scroll", "Q to quit")
    CONTROL_MAP["inputbox"] = ("Start typing to chat", "Enter to send message")

    def __init__(
        self,
        room: str = "Empty Room",
        num_online: int = 0,
        control_key: str | None = None,
    ) -> None:

        infowidgets = self.create_text_content(
            room, num_online, self.CONTROL_MAP[control_key]
        )
        infopile = u.Pile(infowidgets)
        div = u.Divider()
        join = u.Edit("Join a new room: ")

        def quit(_):
            raise u.ExitMainLoop()

        disconnect = u.Button("Disconnect", on_press=quit)

        self.walker = u.SimpleListWalker([infopile, div, join, div, disconnect])
        self.listbox = u.ListBox(self.walker)

        super().__init__(self.listbox)

    def create_text_content(
        self, room: str, num_online: int, controls: Iterable[str]
    ) -> Iterable[u.Widget]:
        content = [
            u.Text(f"Room: {room}"),
            u.Text(f"Users: {num_online}"),
        ]

        if len(controls) > 0:
            content.append(u.Divider())
            content.extend([u.Text(line) for line in controls]),

        return content

    # def keypress(self, size, key: str) -> str | None:
    #     if len(key) > 1 or key in {"Q", "q"}:
    #         return key
