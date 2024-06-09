import urwid as u
from collections import deque
from typing import Self


class DequeWalker(deque, u.ListWalker):
    """This custom list walker class inherits from the :class:`deque` and :class:`ListWalker`
    classes. This means that widgets appended to a :class:`DequeWalker` class, beyond its
    maxlen (default 10,000 elements), results in then element at the start of the deque being
    destroyed to prevent excessive memory use.

    Raises:
        IndexError: If attempting to access an element outside of the length or capacity of the
        underlying deque. Additionally, attempting to retrieve a position using `next_position` or
        `prev_position` that exceeds the deque's range with `wrap_around` set to false will raise
        an `IndexError`.
    """

    DEFAULT_MAXLEN = 10_000

    def __init__(self, wrap_around: bool = False, maxlen: int = DEFAULT_MAXLEN) -> None:
        """
        contents -- list to copy into this object

        wrap_around -- if true, jumps to beginning/end of list on move

        This class inherits :class:`deque` which means
        it can be treated as a deque would.

        Changes made to this object (when it is treated as a deque) are
        detected automatically and will cause ListBox objects using
        this list walker to be updated.
        """
        super().__init__([], maxlen=maxlen)
        self.focus = 0
        self.wrap_around = wrap_around

    @property
    def contents(self) -> Self:
        return self

    # def _modified(self) -> None:
    #     if self.focus >= len(self):
    #         self.focus = max(0, len(self) - 1)
    #     super()._modified(self)

    def set_focus(self, position: int) -> None:
        """Set focus position."""

        if not 0 <= position < len(self):
            raise IndexError(f"No widget at position {position}")

        self.focus = position
        super()._modified()

    def next_position(self, position: int) -> int:
        """
        Return position after start_from.
        """
        if len(self) - 1 <= position:
            if self.wrap_around:
                return 0
            raise IndexError
        return position + 1

    def prev_position(self, position: int) -> int:
        """
        Return position before start_from.
        """
        if position <= 0:
            if self.wrap_around:
                return len(self) - 1
            raise IndexError
        return position - 1

    # def positions(self, reverse: bool = False) -> Iterable[int]:
    #     """
    #     Optional method for returning an iterable of positions.
    #     """
    #     if reverse:
    #         return range(len(self) - 1, -1, -1)
    #     return range(len(self))
