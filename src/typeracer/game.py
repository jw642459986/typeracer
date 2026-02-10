"""Core game state and logic for the type racer."""

import time
from typing import List, Optional
from typeracer.quotes import fetch_quote, QuoteFetchError


class GameState:
    """Tracks the state of a single typing race."""

    def __init__(self):
        self.target: str = ""
        self.typed: List[str] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.total_keystrokes: int = 0
        self.reset()

    def reset(self):
        """Reset for a new game with a fresh quote."""
        self.target = fetch_quote()
        self.typed = []
        self.start_time = None
        self.end_time = None
        self.total_keystrokes = 0

    @property
    def is_started(self) -> bool:
        return self.start_time is not None

    @property
    def is_finished(self) -> bool:
        return len(self.typed) >= len(self.target)

    @property
    def elapsed_seconds(self) -> float:
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

    @property
    def elapsed_minutes(self) -> float:
        return self.elapsed_seconds / 60.0

    @property
    def wpm(self) -> float:
        """Words per minute (standard: 5 chars = 1 word)."""
        if self.elapsed_minutes <= 0:
            return 0.0
        correct_chars = sum(
            1 for i, ch in enumerate(self.typed)
            if i < len(self.target) and ch == self.target[i]
        )
        return (correct_chars / 5.0) / self.elapsed_minutes

    @property
    def raw_wpm(self) -> float:
        """Raw WPM including mistakes."""
        if self.elapsed_minutes <= 0:
            return 0.0
        return (len(self.typed) / 5.0) / self.elapsed_minutes

    @property
    def accuracy(self) -> float:
        """Accuracy percentage."""
        if self.total_keystrokes == 0:
            return 100.0
        correct = sum(
            1 for i, ch in enumerate(self.typed)
            if i < len(self.target) and ch == self.target[i]
        )
        return (correct / self.total_keystrokes) * 100.0

    @property
    def correct_chars(self) -> int:
        return sum(
            1 for i, ch in enumerate(self.typed)
            if i < len(self.target) and ch == self.target[i]
        )

    @property
    def progress(self) -> float:
        """Progress percentage."""
        if len(self.target) == 0:
            return 0.0
        return (len(self.typed) / len(self.target)) * 100.0

    def type_char(self, char: str):
        """Register a typed character."""
        if self.is_finished:
            return

        if self.start_time is None:
            self.start_time = time.time()

        self.typed.append(char)
        self.total_keystrokes += 1

        if self.is_finished:
            self.end_time = time.time()

    def backspace(self):
        """Delete the last typed character."""
        if self.typed:
            self.typed.pop()
