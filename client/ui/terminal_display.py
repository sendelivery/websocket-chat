import _curses
import curses
import curses.textpad
from io import TextIOWrapper
import os
import signal
from typing import Optional, List, Callable
from types import FrameType

import asyncio

from ..client import Client

def clamp(n: int, smallest: int, largest: int) -> int:
    return max(smallest, min(largest, n))


class TerminalDisplay:
    class _InputBox:

        def __init__(
            self,
            window: "_curses._CursesWindow",
            textbox: curses.textpad.Textbox,
            width: int,
            height: int,
            logger: Callable[[str], None],
        ) -> None:
            self.window = window
            self.textbox = textbox
            self.width = width
            self.height = height
            self.logger = logger

        def edit(self) -> str:
            self.textbox.edit()
            msg = self.textbox.gather()

            self.logger(f"typed: {msg}")

            msg = msg.replace("\n", "")

            self.window.clear()
            self.window.refresh()

            return msg

    class _Chatlog:

        def __init__(
            self,
            window: Optional["_curses._CursesWindow"] = None,
            pad: Optional["_curses._CursesWindow"] = None,
        ) -> None:
            self.window = window
            self.pad = pad
            self.pad_start_row = 0
            self.pad_bottom = 0

            # user, message tuple array
            self.messages = []

            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            self.GREEN_ON_BLACK = curses.color_pair(1)
            curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_WHITE)
            self.CYAN_ON_BLACK = curses.color_pair(2)

        def _scroll_chatlog(self) -> None:
            self.pad_start_row += 1
            self.pad.refresh(
                self.pad_start_row, 0, 1, 1, self.pad_bottom, self.width - 2
            )

        def add_message(self, user: str, message: str) -> None:
            self.messages.append((user, message))
            self.draw_message(user, message)

        def draw_message(self, user: str, message: str) -> None:
            _, width = self.window.getmaxyx()
            self.pad.addstr(f"{user}: ", self.GREEN_ON_BLACK)
            self.pad.addstr(f"{message}\n")
            self.pad.refresh(0, 0, 1, 1, self.pad_bottom, width)

        def get_messages(self) -> List[str]:
            return self.messages

        def draw(self) -> None:
            for user, message in self.messages:
                self.draw_message(user, message)

    def __init__(
        self,
        stdscr: "_curses._CursesWindow",
        client: Client,
        log_file: Optional[TextIOWrapper] = None,
    ) -> None:
        self._log_file = log_file
        self._debug_mode = False

        self.client = client

        self._set_resize_signal()
        self._log("Set SIGWINCH handler")

        self.screen = stdscr
        curses.curs_set(0)

        self.finished = False

        self.chatlog = self._Chatlog(log_file)

        # Colours used for debug purposes - find a better place for them.
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
        self.BLACK_ON_GREEN = curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.GREEN_ON_BLACK = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_YELLOW)
        self.BLUE_ON_YELLOW = curses.color_pair(3)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        self.WHITE_ON_MAGENTA = curses.color_pair(4)
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
        self.CYAN_ON_BLACK = curses.color_pair(5)

        self._log(f"Initialised terminal display - {id(self)}")

    def _log(self, message: str) -> None:
        # if self._debug_mode and self._log_file:
        self._log_file.write(f"{message}\n")
        self._log_file.flush()

    def _set_resize_signal(self) -> None:
        def sig_handler(signal: int, frame: Optional[FrameType]) -> None:
            rows, columns = os.popen("stty size", "r").read().split()

            try:
                self._draw_display(int(rows), int(columns))
            except Exception as e:
                self._log(f"Failed to redraw screen {e}")
                self._draw_err_screen()

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

    def _draw_err_screen(self) -> None:
        self.screen.clear()
        message = "Unable to refresh screen."
        xpos = (self.width - len(message)) // 2
        self.screen.addstr(self.height // 2, xpos, message)
        self.screen.refresh()

    def _draw_screen_border(self) -> None:
        curses.textpad.rectangle(
            self.screen, uly=0, ulx=0, lry=self.height - 2, lrx=self.width - 1
        )

    def _draw_program_instructions(self) -> None:
        self.screen.addstr(
            self.height - 1,
            0,
            "f1: debug, q: quit",
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

        return self._InputBox(
            input_window, textbox, input_width, input_height, self._log
        )

    def _draw_chatlog_area(self) -> "_curses._CursesWindow":
        """A window with a pad that displays the last 100 messages in the chat log."""
        chatlog_height = self.height - (self.input_box.height + 2)

        window = curses.newwin(chatlog_height, self.width, 0, 0)
        window.box()

        if self._debug_mode:
            window.bkgd(self.BLACK_ON_GREEN)

        window.refresh()

        max_pad_width = self.width - 2
        pad = curses.newpad(100, max_pad_width)

        if self._debug_mode:
            pad.bkgd(self.BLUE_ON_YELLOW)

        chatlog_bottom = chatlog_height - 2

        pminrow = 0
        pmincol = 0
        sminrow = 1
        smincol = 1
        smaxrow = chatlog_bottom
        smaxcol = max_pad_width

        pad.refresh(pminrow, pmincol, sminrow, smincol, smaxrow, smaxcol)

        self.chatlog.window = window
        self.chatlog.pad = pad
        self.chatlog.pad_bottom = chatlog_bottom

        self.chatlog.draw()

    async def control(self) -> None:
        self.screen.nodelay(True)
        while not self.finished:
            char = self.screen.getch()

            if char == ord("c"):
                message = await asyncio.to_thread(self.input_box.edit)
                await self.client.send_message(message)
                self.chatlog.add_message(self.client, message)
            elif char == ord("q"):
                self.screen.clear()
                self.screen.refresh()
                self.finished = True

            await asyncio.sleep(0)

    async def receive_messages(self) -> None:
        def callback(message: str) -> None:
            self.chatlog.add_message("someone", message)

        await self.client.receive_messages(callback)

    async def run(self) -> None:
        # Draw the display upon initial run
        self._draw_display()

        tasks = (
            asyncio.create_task(self.control()),
            asyncio.create_task(self.receive_messages()),
        )
        await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED,
        )
