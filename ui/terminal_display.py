import _curses
import curses
import curses.textpad
import os
import signal
from typing import Optional
from types import FrameType


from io import TextIOWrapper


def clamp(n: int, smallest: int, largest: int) -> int:
    return max(smallest, min(largest, n))


class TerminalDisplay:
    class _InputBox:
        def __init__(
            self, textbox: curses.textpad.Textbox, width: int, height: int
        ) -> None:
            self.textbox = textbox
            self.width = width
            self.height = height

    def __init__(self, stdscr: "_curses._CursesWindow", file: TextIOWrapper) -> None:
        self._log_file = file
        self._debug_mode = True

        self._set_resize_signal()
        self._log(f"Set SIGWINCH handler - {id(self)}")

        self.screen = stdscr
        self.finished = False

        # Colours used for debug purposes - find a better place for them.
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
        self.BLACK_ON_GREEN = curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.GREEN_ON_BLACK = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_YELLOW)
        self.BLUE_ON_YELLOW = curses.color_pair(3)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        self.WHITE_ON_MAGENTA = curses.color_pair(4)

        self._log(f"Initialised terminal display - {id(self)}")

    def _log(self, message: str) -> None:
        if self._debug_mode:
            self._log_file.write(f"{message}\n")
            self._log_file.flush()

    def _set_resize_signal(self) -> None:
        def sig_handler(signal: int, frame: Optional[FrameType]) -> None:
            rows, columns = os.popen("stty size", "r").read().split()

            self._log(f"Terminal size changed to {rows} rows and {columns} columns.\n")
            self._draw_display(int(rows), int(columns))

        signal.signal(signal.SIGWINCH, sig_handler)

    def _draw_display(
        self, term_height: Optional[int] = None, term_width: Optional[int] = None
    ) -> None:
        """Draws the terminal display in response to SIGWINCH signals or upon initialisation. The
        current state of the user interface, e.g. messages in the chat log and message in edit are
        cleared and restored upon ending the drawing process.

        Args:
            term_height (Optional[int]): Window height. Passed in by the SIGWINCH handler when the
            terminal size updates.
            term_width (Optional[int]): Window width. Passed in by the SIGWINCH handler when the
            terminal size updates.
        """

        # Update the internal terminal size if arguments are explicitly passed in.
        if term_height and term_width:
            curses.resizeterm(term_height, term_width)

        # Update the instance variables holding our terminal window's size
        self.height, self.width = self.screen.getmaxyx()

        self.screen.clear()

        self._draw_screen_border()
        self._draw_program_instructions()

        self.screen.refresh()

        self.input_box = self._draw_input_area()
        self._draw_chatlog_area()

    def _draw_screen_border(self) -> None:
        curses.textpad.rectangle(
            self.screen, uly=0, ulx=0, lry=self.height - 2, lrx=self.width - 1
        )

    def _draw_program_instructions(self) -> None:
        self.screen.addstr(
            self.height - 1,
            0,
            "f1: debug, esc: quit",
            self.GREEN_ON_BLACK,
        )

    def _draw_input_area(self) -> _InputBox:
        """A window with a textpad for typing in messages.

        Returns:
            _InputBox: An object for interacting with the created input box.
        """
        input_height = clamp(self.height // 5, 1, 8)
        input_width = self.width - 2
        begin_y = self.height - input_height - 2
        begin_x = 1

        input_window = curses.newwin(input_height, input_width, begin_y, begin_x)
        input_window.clear()

        textbox = curses.textpad.Textbox(input_window)

        if self._debug_mode:
            input_window.bkgd(self.WHITE_ON_MAGENTA)

        input_window.refresh()

        return self._InputBox(textbox, input_width, input_height)

    def _draw_chatlog_area(self) -> None:
        """A window with a pad that displays the last 100 messages in the chat log."""
        chat_log_height = self.height - (self.input_box.height + 2)

        chat_log_window = curses.newwin(chat_log_height, self.width, 0, 0)
        chat_log_window.box()

        if self._debug_mode:
            chat_log_window.bkgd(self.BLACK_ON_GREEN)

        chat_log_window.refresh()

        max_pad_width = self.width - 2
        chat_log_pad = curses.newpad(100, max_pad_width)

        if self._debug_mode:
            chat_log_pad.bkgd(self.BLUE_ON_YELLOW)

        chat_log_pad.addstr("Hello this is the first message!\n")

        pminrow = 0
        pmincol = 0
        sminrow = chat_log_height - 2
        smincol = 1
        smaxrow = chat_log_height - 2
        smaxcol = max_pad_width

        chat_log_pad.refresh(pminrow, pmincol, sminrow, smincol, smaxrow, smaxcol)

    def run(self) -> None:
        # Draw the display upon initial run
        self._draw_display()

        self.input_box.textbox.edit()
        msg = self.input_box.textbox.gather()

        self._log(f"User typed: {msg}")


def main(stdscr: "_curses._CursesWindow") -> None:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/debug.txt", mode="w+") as file:
        display = TerminalDisplay(stdscr, file)
        display.run()


if __name__ == "__main__":
    # remove default esc delay that comes with the wrapper
    os.environ["ESCDELAY"] = "25"

    curses.wrapper(main)
