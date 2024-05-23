import urwid as u
from .dummy_text import generate_dummy_text


class Chatlog(u.ListBox):

    # Nested class that handles the creation and destruction of individual message text widgets
    class ChatlogWalker(u.SimpleListWalker):
        def __init__(self) -> None:
            # Always start with no chat history (empty contents), and wrap_around set to False.
            super().__init__(contents=[], wrap_around=False)

    def __init__(
        self,
        debug=None,
    ) -> None:
        self.debug = debug

        self.exit_focus = None
        self.walker, self.size = self.create_walker()

        self.debug_text_generator = generate_dummy_text()

        super().__init__(body=self.walker)

    def create_walker(self) -> tuple[u.SimpleListWalker, int]:
        # TODO
        # https://urwid.org/manual/widgets.html#list-walkers
        # If you need to display a large number of widgets you should implement your own list
        # walker that manages creating widgets as they are requested and destroying them later to
        # avoid excessive memory use.
        return u.SimpleListWalker([]), 0

    def append(self, message: str) -> None:
        self.walker.append(u.Text(message))
        self.size += 1

    def append_and_set_focus(self, message: str) -> None:
        self.append(message)
        self.walker.set_focus(self.size - 1)

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
