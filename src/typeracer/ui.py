"""Curses-based terminal UI for the type racer game."""

import curses
from typing import List, Tuple
from typeracer.game import GameState


# Color pair IDs
PAIR_CORRECT = 1
PAIR_INCORRECT = 2
PAIR_UNTYPED = 3
PAIR_CURSOR = 4
PAIR_TITLE = 5
PAIR_STATS = 6
PAIR_DIM = 7
PAIR_HIGHLIGHT = 8
PAIR_TEXT_BG = 9

# Box drawing
HORIZONTAL = "─"
VERTICAL = "│"
TOP_LEFT = "╭"
TOP_RIGHT = "╮"
BOTTOM_LEFT = "╰"
BOTTOM_RIGHT = "╯"


def init_colors():
    """Initialize color pairs."""
    curses.start_color()
    curses.use_default_colors()

    # Define a dark gray background for the text area (color 236 = #303030)
    # Fall back gracefully if extended colors aren't supported
    if curses.can_change_color() and curses.COLORS >= 256:
        TEXT_BG = 236
    else:
        TEXT_BG = curses.COLOR_BLUE

    curses.init_pair(PAIR_CORRECT, curses.COLOR_GREEN, TEXT_BG)
    curses.init_pair(PAIR_INCORRECT, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(PAIR_UNTYPED, curses.COLOR_WHITE, TEXT_BG)
    curses.init_pair(PAIR_CURSOR, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(PAIR_TITLE, curses.COLOR_CYAN, -1)
    curses.init_pair(PAIR_STATS, curses.COLOR_YELLOW, -1)
    curses.init_pair(PAIR_DIM, curses.COLOR_WHITE, -1)
    curses.init_pair(PAIR_HIGHLIGHT, curses.COLOR_MAGENTA, -1)
    curses.init_pair(PAIR_TEXT_BG, curses.COLOR_WHITE, TEXT_BG)


def draw_box(stdscr, y: int, x: int, width: int, height: int):
    """Draw a rounded box."""
    # Top border
    stdscr.addstr(y, x, TOP_LEFT + HORIZONTAL * (width - 2) + TOP_RIGHT,
                  curses.color_pair(PAIR_DIM) | curses.A_DIM)
    # Bottom border
    stdscr.addstr(y + height - 1, x,
                  BOTTOM_LEFT + HORIZONTAL * (width - 2) + BOTTOM_RIGHT,
                  curses.color_pair(PAIR_DIM) | curses.A_DIM)
    # Side borders
    for row in range(1, height - 1):
        stdscr.addstr(y + row, x, VERTICAL,
                      curses.color_pair(PAIR_DIM) | curses.A_DIM)
        stdscr.addstr(y + row, x + width - 1, VERTICAL,
                      curses.color_pair(PAIR_DIM) | curses.A_DIM)


def draw_welcome(stdscr):
    """Draw the welcome/start screen."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    logo = [
        "╔╦╗╦ ╦╔═╗╔═╗╦═╗╔═╗╔═╗╔═╗╦═╗",
        " ║ ╚╦╝╠═╝║╣ ╠╦╝╠═╣║  ║╣ ╠╦╝",
        " ╩  ╩ ╩  ╚═╝╩╚═╩ ╩╚═╝╚═╝╩╚═",
    ]

    logo_width = len(logo[0])
    start_x = max(0, (w - logo_width) // 2)
    start_y = max(0, h // 2 - 6)

    for i, line in enumerate(logo):
        stdscr.addstr(start_y + i, start_x, line,
                      curses.color_pair(PAIR_TITLE) | curses.A_BOLD)

    # Tagline
    tagline = "Test your typing speed!"
    stdscr.addstr(start_y + 5, max(0, (w - len(tagline)) // 2), tagline,
                  curses.color_pair(PAIR_DIM))

    # Instructions
    instructions = [
        "HOW TO PLAY",
        "",
        "Type the displayed text as fast and accurately as you can.",
        "Your WPM and accuracy are tracked in real time.",
        "",
        "  Backspace  │  Delete last character",
        "  Escape     │  Quit the game",
    ]

    inst_y = start_y + 8
    for i, line in enumerate(instructions):
        if i == 0:
            stdscr.addstr(inst_y + i, max(0, (w - len(line)) // 2), line,
                          curses.color_pair(PAIR_STATS) | curses.A_BOLD)
        else:
            stdscr.addstr(inst_y + i, max(0, (w - len(line)) // 2), line,
                          curses.color_pair(PAIR_DIM))

    # Start prompt
    prompt = "Press any key to start..."
    prompt_y = min(inst_y + len(instructions) + 2, h - 2)
    stdscr.addstr(prompt_y, max(0, (w - len(prompt)) // 2), prompt,
                  curses.color_pair(PAIR_HIGHLIGHT) | curses.A_BOLD | curses.A_BLINK)

    stdscr.refresh()


def wrap_text(text: str, width: int) -> List[str]:
    """Word-wrap text to fit within a given width."""
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        if current_line and len(current_line) + 1 + len(word) > width:
            lines.append(current_line)
            current_line = word
        elif current_line:
            current_line += " " + word
        else:
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def draw_game(stdscr, game: GameState):
    """Draw the main game screen, centered like the other screens."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    center_x = w // 2

    # Layout dimensions
    text_area_width = min(w - 6, 70)
    text_x = max(3, (w - text_area_width) // 2)

    # Word-wrap the target text to calculate total height needed
    lines = wrap_text(game.target, text_area_width)
    # Total content height: title(1) + sep(1) + stats(1) + bar(1) + sep(1)
    #                        + gap(1) + text lines with spacing + gap(1) + author(1) + hint(1)
    text_lines_height = len(lines) * 2 - 1  # lines with single spacing between
    total_height = 6 + text_lines_height + 4
    start_y = max(1, (h - total_height) // 2)

    y = start_y

    # Title
    title = " TYPERACER "
    stdscr.addstr(y, max(0, center_x - len(title) // 2), title,
                  curses.color_pair(PAIR_TITLE) | curses.A_BOLD)
    y += 1

    # Separator
    stdscr.addstr(y, text_x, HORIZONTAL * text_area_width,
                  curses.color_pair(PAIR_DIM) | curses.A_DIM)
    y += 1

    # Stats bar (centered)
    if game.is_started:
        wpm_str = f"WPM: {game.wpm:5.1f}"
        acc_str = f"ACC: {game.accuracy:5.1f}%"
        time_str = f"TIME: {game.elapsed_seconds:5.1f}s"
    else:
        wpm_str = "WPM:   ---"
        acc_str = "ACC:   ---"
        time_str = "TIME:   0.0s"

    stats_line = f"  {wpm_str}  │  {acc_str}  │  {time_str}  "
    stdscr.addstr(y, max(0, center_x - len(stats_line) // 2), stats_line,
                  curses.color_pair(PAIR_STATS) | curses.A_BOLD)
    y += 1

    # Progress bar (same width as text area)
    bar_width = text_area_width
    filled = int(bar_width * game.progress / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    stdscr.addstr(y, text_x, bar, curses.color_pair(PAIR_TITLE))
    y += 1

    # Separator
    stdscr.addstr(y, text_x, HORIZONTAL * text_area_width,
                  curses.color_pair(PAIR_DIM) | curses.A_DIM)
    y += 2

    # Text area
    text_y = y

    # Build a flat index map: for each char position in target,
    # figure out which (row, col) it maps to on screen.
    # Word-wrapping drops the space at line breaks, so we add it back
    # at the end of each wrapped line to keep positions aligned with target.
    char_positions: List[Tuple[int, int]] = []
    for line_num, line in enumerate(lines):
        for col_num in range(len(line)):
            char_positions.append((text_y + line_num * 2, text_x + col_num))
        # Add the missing space at the wrap boundary (except after the last line)
        if line_num < len(lines) - 1:
            char_positions.append((text_y + line_num * 2, text_x + len(line)))

    # Paint background strips for each text line so spaces are visible
    # Include +1 width for the wrap-boundary space on all lines except the last
    bg_attr = curses.color_pair(PAIR_TEXT_BG)
    painted_rows = set()
    for line_num, line in enumerate(lines):
        row = text_y + line_num * 2
        if row >= h - 2:
            break
        if row not in painted_rows:
            bg_width = len(line) + (1 if line_num < len(lines) - 1 else 0)
            try:
                stdscr.addstr(row, text_x, " " * bg_width, bg_attr)
            except curses.error:
                pass
            painted_rows.add(row)

    # Render characters on top of the background
    for i, char in enumerate(game.target):
        if i >= len(char_positions):
            break
        row, col = char_positions[i]
        if row >= h - 2:
            break

        if i < len(game.typed):
            if game.typed[i] == char:
                attr = curses.color_pair(PAIR_CORRECT) | curses.A_BOLD
            else:
                attr = curses.color_pair(PAIR_INCORRECT) | curses.A_BOLD
        elif i == len(game.typed):
            # Cursor position
            attr = curses.color_pair(PAIR_CURSOR)
        else:
            attr = curses.color_pair(PAIR_UNTYPED) | curses.A_DIM

        try:
            stdscr.addstr(row, col, char, attr)
        except curses.error:
            pass

    # Author attribution below the text
    if game.author:
        last_text_row = text_y + (len(lines) - 1) * 2
        author_str = f"— {game.author}"
        author_y = last_text_row + 2
        if author_y < h - 2:
            try:
                author_x = text_x + text_area_width - len(author_str)
                stdscr.addstr(author_y, max(text_x, author_x), author_str,
                              curses.color_pair(PAIR_DIM) | curses.A_ITALIC)
            except curses.error:
                pass

    # Hint at bottom
    hint = " ESC to quit │ Backspace to correct "
    try:
        stdscr.addstr(h - 1, max(0, center_x - len(hint) // 2), hint,
                      curses.color_pair(PAIR_DIM) | curses.A_DIM)
    except curses.error:
        pass

    stdscr.refresh()


def draw_error(stdscr, error_message: str):
    """Draw a network error screen, centered like the other screens."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    center_x = w // 2

    y = max(2, h // 2 - 5)

    # Error icon and header
    header = "NETWORK ERROR"
    stdscr.addstr(y, max(0, center_x - len(header) // 2), header,
                  curses.color_pair(PAIR_INCORRECT) | curses.A_BOLD)
    y += 2

    stdscr.addstr(y, max(0, center_x - 20), HORIZONTAL * 40,
                  curses.color_pair(PAIR_DIM) | curses.A_DIM)
    y += 2

    # Error message
    msg = "Unable to fetch quote from the server."
    stdscr.addstr(y, max(0, center_x - len(msg) // 2), msg,
                  curses.color_pair(PAIR_DIM))
    y += 2

    # Detail
    detail = error_message if len(error_message) < w - 4 else error_message[:w - 7] + "..."
    stdscr.addstr(y, max(0, center_x - len(detail) // 2), detail,
                  curses.color_pair(PAIR_DIM) | curses.A_DIM)
    y += 2

    stdscr.addstr(y, max(0, center_x - 20), HORIZONTAL * 40,
                  curses.color_pair(PAIR_DIM) | curses.A_DIM)
    y += 2

    # Options
    options = "Press any key to retry  │  ESC to quit"
    stdscr.addstr(y, max(0, center_x - len(options) // 2), options,
                  curses.color_pair(PAIR_HIGHLIGHT) | curses.A_BOLD)

    stdscr.refresh()


def draw_results(stdscr, game: GameState):
    """Draw the results screen after a race."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    center_x = w // 2
    y = max(2, h // 2 - 8)

    # Header
    header = "🏁  RACE COMPLETE!  🏁"
    stdscr.addstr(y, max(0, center_x - len(header) // 2), header,
                  curses.color_pair(PAIR_TITLE) | curses.A_BOLD)
    y += 2

    stdscr.addstr(y, max(0, center_x - 20), HORIZONTAL * 40,
                  curses.color_pair(PAIR_DIM) | curses.A_DIM)
    y += 2

    # Quote attribution
    if game.author:
        author_str = f"Quote by {game.author}"
        stdscr.addstr(y, max(0, center_x - len(author_str) // 2), author_str,
                      curses.color_pair(PAIR_DIM) | curses.A_ITALIC)
        y += 2

    # Stats
    stats = [
        ("WPM", f"{game.wpm:.1f}"),
        ("Raw WPM", f"{game.raw_wpm:.1f}"),
        ("Accuracy", f"{game.accuracy:.1f}%"),
        ("Time", f"{game.elapsed_seconds:.1f}s"),
        ("Characters", f"{game.correct_chars}/{len(game.target)}"),
        ("Keystrokes", f"{game.total_keystrokes}"),
    ]

    for label, value in stats:
        label_str = f"  {label:>12s}  │  "
        stdscr.addstr(y, max(0, center_x - 16), label_str,
                      curses.color_pair(PAIR_DIM))
        stdscr.addstr(y, max(0, center_x - 16) + len(label_str), value,
                      curses.color_pair(PAIR_STATS) | curses.A_BOLD)
        y += 1

    y += 1
    stdscr.addstr(y, max(0, center_x - 20), HORIZONTAL * 40,
                  curses.color_pair(PAIR_DIM) | curses.A_DIM)
    y += 2

    # WPM rating
    wpm = game.wpm
    if wpm >= 100:
        rating = "⚡ LEGENDARY"
        pair = PAIR_HIGHLIGHT
    elif wpm >= 80:
        rating = "🔥 BLAZING FAST"
        pair = PAIR_TITLE
    elif wpm >= 60:
        rating = "✨ IMPRESSIVE"
        pair = PAIR_STATS
    elif wpm >= 40:
        rating = "👍 SOLID"
        pair = PAIR_CORRECT
    elif wpm >= 25:
        rating = "📝 KEEP PRACTICING"
        pair = PAIR_UNTYPED
    else:
        rating = "🐢 WARMING UP"
        pair = PAIR_DIM

    stdscr.addstr(y, max(0, center_x - len(rating) // 2), rating,
                  curses.color_pair(pair) | curses.A_BOLD)
    y += 3

    # Options
    options = "Press any key to race again  │  ESC to quit"
    stdscr.addstr(y, max(0, center_x - len(options) // 2), options,
                  curses.color_pair(PAIR_HIGHLIGHT) | curses.A_BOLD)

    stdscr.refresh()
