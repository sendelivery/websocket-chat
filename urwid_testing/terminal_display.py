import urwid as u
from urwid_testing.lib import Chatlog, InputBox, InfoPanel


class DebugText(u.Text):
    def __init__(
        self,
    ) -> None:
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

        self.inputbox = InputBox()
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

    def run(self) -> None:
        loop = u.MainLoop(
            self.frame, palette=self.PALETTE, unhandled_input=self.exit_on_q
        )
        loop.run()


t = TerminalDisplay()
t.run()
