import curses
import curses.textpad
import _curses

import os
from io import TextIOWrapper
import time
from random_sentences import sentences

import asyncio


class TerminalDisplay:
    def __init__(self, stdscr: "_curses._CursesWindow", file: TextIOWrapper) -> None:
        self.debug_file = file
        self.debug = True
        self.__log__(f"Initialised terminal display - {id(self)}")
        self.debug = False

        self.screen = stdscr
        self.finished = False

        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
        self.BLACK_ON_GREEN = curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.GREEN_ON_BLACK = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_YELLOW)
        self.BLUE_ON_YELLOW = curses.color_pair(3)

        self.pad_scroll = 0

        self.draw_display()

    def __log__(self, message: str) -> None:
        if self.debug:
            self.debug_file.write(f"{message}\n")
            self.debug_file.flush()

    def draw_display(self) -> None:
        # Update the instance variables holding our terminal window's size
        self.max_y, self.max_x = self.screen.getmaxyx()

        # Draw a rectangle along the border of the terminal window
        # and welcome message along the bottom.
        self.screen.clear()
        curses.textpad.rectangle(
            self.screen, uly=0, ulx=0, lry=self.max_y - 2, lrx=self.max_x - 1
        )
        self.screen.addstr(
            self.max_y - 1,
            0,
            "d: debug, q: quit",
            self.GREEN_ON_BLACK,
        )
        self.screen.refresh()

        # Create a new window which will hold our input textbox
        input_height = min(4, self.max_y // 5)
        input_width = self.max_x - 2
        begin_y = self.max_y - input_height - 2
        begin_x = 1
        self.input_window = curses.newwin(input_height, input_width, begin_y, begin_x)
        self.input_window.clear()

        if self.debug:
            self.input_window.bkgd(self.BLACK_ON_GREEN)

        self.input_box = curses.textpad.Textbox(self.input_window)
        curses.textpad.rectangle(
            self.screen,
            uly=self.max_y - input_height - 3,
            ulx=0,
            lry=self.max_y - 2,
            lrx=self.max_x - 1,
        )
        self.screen.refresh()
        self.input_window.refresh()

        self.chat_log_height = self.max_y - (input_height + 4)

        self.__log__(f"{self.chat_log_height}")

        # if chat_log_height > 0:
        #     self.debug_window = curses.newwin(chat_log_height, input_width, 1, 1)
        #     self.debug_window.bkgd(self.BLUE_ON_YELLOW)
        #     self.debug_window.refresh()

        # Create pad for displaying last 100 messages in chat log
        max_screen_width = self.max_x - 2
        self.chat_log_pad = curses.newpad(100, max_screen_width)
        if self.debug:
            self.chat_log_pad.bkgd(self.BLUE_ON_YELLOW)
        self.chat_log_pad.addstr("\n")
        self.chat_log_pad.addstr("Hello this is the first message!\n")
        self.chat_log_pad.addstr("Here's a second message!")
        self.chat_log_pad.refresh(
            0, 0, self.chat_log_height, 1, self.chat_log_height, max_screen_width
        )

        # for i, sentence in enumerate(sentences):
        #     self.chat_log_pad.addstr(f"{sentence}\n")
        #     self.chat_log_pad.refresh(
        #         0, 0, chat_log_height - i, 1, chat_log_height, max_screen_width
        #     )
        #     if i == 6:
        #         break
        #     time.sleep(1)

        # This method should be called async / in a separate thread so it doesn't block the program
        # self.type_message()

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
            self.max_x - 2,
        )

    def type_message(self) -> None:
        while True:
            self.input_box.edit()
            message = self.input_box.gather()

            message = message.strip()

            self.__log__(f"user typed: {message}\n")

            if message == "qqqq":
                self.__log__("quitting program...")
                self.finished = True
                break

            self.add_message_to_chat_log(message)

            self.input_window.clear()

    def run(self) -> None:
        # self.screen.nodelay(True)  # Set getch to non-blocking
        while not self.finished:
            char = self.screen.getch()

            if char == curses.KEY_RESIZE:
                self.draw_display()
            elif char == ord("q"):
                self.finished = True
            elif char == ord("d"):
                self.debug = not self.debug
                self.draw_display()


def program(stdscr: "_curses._CursesWindow") -> None:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/debug.txt", mode="w+") as file:
        display = TerminalDisplay(stdscr, file)
        display.run()


if __name__ == "__main__":
    curses.wrapper(program)
