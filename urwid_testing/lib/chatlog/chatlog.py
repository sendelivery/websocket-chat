import urwid as u
from .dummy_text import generate_dummy_text


class Chatlog(u.ListBox):
    def __init__(
        self,
        debug=None,
    ) -> None:
        self.debug = debug

        self.exit_focus = None
        self.walker = self.create_walker()

        self.debug_text_generator = generate_dummy_text()

        super().__init__(body=self.walker)

    def create_walker(self) -> u.SimpleListWalker:
        # TODO
        # https://urwid.org/manual/widgets.html#list-walkers
        # If you need to display a large number of widgets you should implement your own list
        # walker that manages creating widgets as they are requested and destroying them later to
        # avoid excessive memory use.
        return u.SimpleListWalker([])

    def append(self, message: str) -> None:
        self.walker.append(u.Text(message))

    # def keypress(self, size: tuple[int, int], key: str) -> str | None:
    #     key_map = {"j": "down", "k": "up", "q": "q"}

    #     if key in key_map:
    #         if key in {"j", "k"}:
    #             self.debug.log(repr(self.walker.get_next()))

    #         return super().keypress(size, key_map[key])
    #     elif key == "c":
    #         self.append(next(self.debug_text_generator))
    #     elif self.exit_focus is not None:
    #         self.exit_focus()
