"""Entry point for the type racer game."""

import curses
import sys
from typeracer.game import GameState
from typeracer.quotes import QuoteFetchError
from typeracer.ui import (
    init_colors, draw_welcome, draw_game, draw_results, draw_error,
)


def game_loop(stdscr):
    """Main game loop driven by curses."""
    # Setup
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(False)
    stdscr.keypad(True)
    init_colors()

    # Welcome screen (shown only once)
    draw_welcome(stdscr)
    key = stdscr.getch()
    if key == 27:  # ESC
        return

    while True:
        # Try to create a new game, retrying on network errors
        game = None
        while game is None:
            try:
                game = GameState()
            except QuoteFetchError as e:
                stdscr.timeout(-1)
                draw_error(stdscr, str(e))
                key = stdscr.getch()
                if key == 27:  # ESC
                    return
                # Any other key retries

        # Enable timeout so we can refresh stats while waiting for input
        stdscr.timeout(100)  # 100ms refresh

        while not game.is_finished:
            draw_game(stdscr, game)
            key = stdscr.getch()

            if key == -1:
                # Timeout, just refresh
                continue
            elif key == 27:  # ESC
                return
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                game.backspace()
            elif key == curses.KEY_RESIZE:
                # Terminal resized, just redraw
                continue
            elif 32 <= key <= 126:
                game.type_char(chr(key))

        # Show final state
        draw_game(stdscr, game)

        # Disable timeout for results screen
        stdscr.timeout(-1)

        # Results
        draw_results(stdscr, game)
        key = stdscr.getch()

        if key == 27:  # ESC
            return
        # Any other key starts a new race


def main():
    """Entry point."""
    try:
        curses.wrapper(game_loop)
    except KeyboardInterrupt:
        pass
    print("Thanks for playing TypeRacer!")
    sys.exit(0)


if __name__ == "__main__":
    main()
