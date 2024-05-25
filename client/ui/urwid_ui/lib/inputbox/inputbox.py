import urwid as u
from typing import Callable


class InputBox(u.Edit):

    def __init__(self, on_enter: Callable[[str], None]) -> None:
        self.on_enter = on_enter
        super().__init__()

    def keypress(self, size: tuple[int], key: str) -> str | None:
        if key != "enter":
            return super().keypress(size, key)
        else:
            edit_text = self.get_edit_text()

            try:
                self.validate(edit_text)
            except ValueError:
                return

            self.on_enter(edit_text)
            self.set_edit_text("")
            return

    def validate(self, edit_text: str) -> None:
        if edit_text == "":
            raise ValueError("Empty edit text.")
