import urwid as u
from .deque_walker import DequeWalker


class Chatlog(u.ListBox):
    def __init__(self) -> None:
        self.exit_focus = None
        self.walker = DequeWalker(wrap_around=False)

        super().__init__(body=self.walker)

    @property
    def size(self) -> int:
        return len(self.walker.contents)

    def append(self, user: str, message: str, attr: str) -> None:
        text_content = [(attr, user), f": {message}"]
        self.walker.append(u.Text(text_content))

    def append_and_set_focus(self, user: str, message: str, attr: str) -> None:
        self.append(user, message, attr)
        self.walker.set_focus(self.size - 1)
