import urwid as u


class InputBox(u.WidgetWrap):
    def __init__(self) -> None:
        self.edit = u.Edit()

        super().__init__(self.edit)
