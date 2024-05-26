import urwid as u


class Chatlog(u.ListBox):

    # TODO
    # Nested class that handles the creation and destruction of individual message text widgets
    # https://urwid.org/manual/widgets.html#list-walkers
    # If you need to display a large number of widgets you should implement your own list
    # walker that manages creating widgets as they are requested and destroying them later to
    # avoid excessive memory use.
    class ChatlogWalker(u.SimpleListWalker):
        def __init__(self) -> None:
            # Always start with no chat history (empty contents), and wrap_around set to False.
            super().__init__(contents=[], wrap_around=False)

    def __init__(self) -> None:
        self.exit_focus = None
        self.walker = self.ChatlogWalker()
        self.size = 0

        super().__init__(body=self.walker)

    def append(self, message: str) -> None:
        self.walker.append(u.Text(message))
        self.size += 1

    def append_and_set_focus(self, message: str) -> None:
        self.append(message)
        self.walker.set_focus(self.size - 1)
