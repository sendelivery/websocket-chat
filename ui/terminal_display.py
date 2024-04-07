import curses
import curses.textpad
import _curses
import signal

import os
from io import TextIOWrapper
from random_sentences import sentences

import typing


def clamp(n: int, smallest: int, largest: int) -> int:
    return max(smallest, min(largest, n))


class TerminalDisplay:
    def __init__(self, stdscr: "_curses._CursesWindow", file: TextIOWrapper) -> None:
        self.debug_file = file
        self.debug = True
        self.__log__(f"Initialised terminal display - {id(self)}")
        # self.debug = False

        self.screen = stdscr
        self.finished = False

        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
        self.BLACK_ON_GREEN = curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.GREEN_ON_BLACK = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_YELLOW)
        self.BLUE_ON_YELLOW = curses.color_pair(3)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        self.WHITE_ON_MAGENTA = curses.color_pair(4)

        self.pad_scroll = 0

    def __log__(self, message: str) -> None:
        if self.debug:
            self.debug_file.write(f"{message}\n")
            self.debug_file.flush()

    def draw_display(self, y: int = None, x: int = None) -> None:
        if y and x:
            curses.resizeterm(y, x)
        # Update the instance variables holding our terminal window's size
        self.height, self.width = self.screen.getmaxyx()

        # Draw a rectangle along the border of the terminal window
        # and welcome message along the bottom.
        self.screen.clear()
        curses.textpad.rectangle(
            self.screen, uly=0, ulx=0, lry=self.height - 2, lrx=self.width - 1
        )
        self.screen.addstr(
            self.height - 1,
            0,
            "f1: debug, esc: quit",
            self.GREEN_ON_BLACK,
        )
        self.screen.refresh()

        # Create a new window which will hold our input textbox
        input_height = clamp(self.height // 5, 3, 8)
        input_width = self.width - 2
        begin_y = self.height - input_height - 2
        begin_x = 1
        self.input_window = curses.newwin(input_height, input_width, begin_y, begin_x)
        self.input_window.clear()

        # TEXTPAD FOR INPUT WINDOW
        self.box = curses.textpad.Textbox(self.input_window)

        if self.debug:
            self.input_window.bkgd(self.WHITE_ON_MAGENTA)

        self.input_window.refresh()

        # Create a window and pad for displaying last 100 messages in chat log
        self.chat_log_height = self.height - (input_height + 2)

        self.chat_log_window = curses.newwin(self.chat_log_height, self.width, 0, 0)
        self.chat_log_window.box()

        if self.debug:
            self.chat_log_window.bkgd(self.BLACK_ON_GREEN)
        self.chat_log_window.refresh()

        max_pad_width = self.width - 2
        self.chat_log_pad = curses.newpad(100, max_pad_width)
        if self.debug:
            self.chat_log_pad.bkgd(self.BLUE_ON_YELLOW)
        self.chat_log_pad.addstr("Hello this is the first message!\n")
        self.chat_log_pad.refresh(
            0, 0, self.chat_log_height - 2, 1, self.chat_log_height - 2, max_pad_width
        )

        # position cursor
        self.screen.move(self.chat_log_height, 1)

    def add_message_to_chat_log(self, message: str) -> None:
        # Add message to pad
        self.chat_log_pad.addstr(f"{message}\n")
        # Scroll pad
        self.pad_scroll += 1
        self.chat_log_pad.refresh(
            0,
            0,
            self.chat_log_height - self.pad_scroll,
            1,
            self.chat_log_height,
            self.width - 2,
        )

    def run(self) -> None:
        self.draw_display()  # Draw the display upon initial run

        self.box.edit()
        msg = self.box.gather()

        self.__log__(f"user typed: {msg}")

        # curses.echo()  # echo keys
        # while not self.finished:
        #     char = self.screen.getch()

        #     self.__log__(f"char: {char}")

        #     # if char == curses.KEY_RESIZE:
        #     #     self.draw_display()
        #     if char == 27:  # esc - quit
        #         self.finished = True
        #     elif char == 265:  # f1 - enable debug
        #         self.debug = not self.debug
        #         self.draw_display()


def program(stdscr: "_curses._CursesWindow") -> None:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/debug.txt", mode="w+") as file:
        display = TerminalDisplay(stdscr, file)

        def sighandler(signal, frame):
            rows, columns = os.popen("stty size", "r").read().split()
            file.write(f"Terminal size changed to {rows} rows and {columns} columns.\n")
            file.flush()
            display.draw_display(int(rows), int(columns))

        signal.signal(signal.SIGWINCH, sighandler)

        display.run()


if __name__ == "__main__":
    os.environ["ESCDELAY"] = (
        "25"  # remove default esc delay that comes with the wrapper
    )
    curses.wrapper(program)
