"""Tests for the game module."""

import unittest
from unittest.mock import patch
from typeracer.game import GameState
from typeracer.quotes import QuoteFetchError

# Patch where fetch_quote is looked up (in the game module), not where it's defined
FETCH_PATCH = "typeracer.game.fetch_quote"


class TestGameState(unittest.TestCase):
    """Tests for GameState."""

    @patch(FETCH_PATCH, return_value="Hello world.")
    def test_initial_state(self, _mock):
        """New game has correct initial state."""
        game = GameState()
        self.assertEqual(game.target, "Hello world.")
        self.assertEqual(game.typed, [])
        self.assertFalse(game.is_started)
        self.assertFalse(game.is_finished)
        self.assertEqual(game.wpm, 0.0)
        self.assertEqual(game.accuracy, 100.0)
        self.assertEqual(game.progress, 0.0)

    @patch(FETCH_PATCH, return_value="Hi")
    def test_type_char_starts_game(self, _mock):
        """Typing the first character starts the timer."""
        game = GameState()
        self.assertFalse(game.is_started)
        game.type_char("H")
        self.assertTrue(game.is_started)
        self.assertIsNotNone(game.start_time)

    @patch(FETCH_PATCH, return_value="Hi")
    def test_typing_completes_game(self, _mock):
        """Typing all characters finishes the game."""
        game = GameState()
        game.type_char("H")
        self.assertFalse(game.is_finished)
        game.type_char("i")
        self.assertTrue(game.is_finished)
        self.assertIsNotNone(game.end_time)

    @patch(FETCH_PATCH, return_value="Hi")
    def test_type_char_ignored_after_finish(self, _mock):
        """Characters typed after the game ends are ignored."""
        game = GameState()
        game.type_char("H")
        game.type_char("i")
        self.assertTrue(game.is_finished)
        game.type_char("!")
        self.assertEqual(len(game.typed), 2)

    @patch(FETCH_PATCH, return_value="abc")
    def test_backspace(self, _mock):
        """Backspace removes the last typed character."""
        game = GameState()
        game.type_char("a")
        game.type_char("b")
        self.assertEqual(len(game.typed), 2)
        game.backspace()
        self.assertEqual(len(game.typed), 1)
        self.assertEqual(game.typed, ["a"])

    @patch(FETCH_PATCH, return_value="abc")
    def test_backspace_on_empty(self, _mock):
        """Backspace on empty typed list does nothing."""
        game = GameState()
        game.backspace()  # should not raise
        self.assertEqual(game.typed, [])

    @patch(FETCH_PATCH, return_value="abcd")
    def test_progress(self, _mock):
        """Progress tracks percentage of characters typed."""
        game = GameState()
        self.assertEqual(game.progress, 0.0)
        game.type_char("a")
        self.assertAlmostEqual(game.progress, 25.0)
        game.type_char("b")
        self.assertAlmostEqual(game.progress, 50.0)

    @patch(FETCH_PATCH, return_value="ab")
    def test_correct_chars_count(self, _mock):
        """correct_chars only counts matching characters."""
        game = GameState()
        game.type_char("a")  # correct
        game.type_char("x")  # wrong
        self.assertEqual(game.correct_chars, 1)

    @patch(FETCH_PATCH, return_value="ab")
    def test_accuracy(self, _mock):
        """Accuracy reflects correct keystrokes vs total keystrokes."""
        game = GameState()
        game.type_char("a")  # correct
        game.type_char("x")  # wrong
        # 1 correct out of 2 keystrokes = 50%
        self.assertAlmostEqual(game.accuracy, 50.0)

    @patch(FETCH_PATCH)
    def test_reset(self, mock_fetch):
        """Reset clears state and fetches a new quote."""
        mock_fetch.return_value = "test"
        game = GameState()
        game.type_char("t")
        game.type_char("e")

        mock_fetch.return_value = "new quote"
        game.reset()

        self.assertEqual(game.target, "new quote")
        self.assertEqual(game.typed, [])
        self.assertFalse(game.is_started)
        self.assertEqual(game.total_keystrokes, 0)


class TestGameStateNetworkError(unittest.TestCase):
    """Tests for GameState when fetch_quote fails."""

    @patch(FETCH_PATCH,
           side_effect=QuoteFetchError("Network error: Connection refused"))
    def test_init_raises_on_fetch_error(self, _mock):
        """GameState.__init__ propagates QuoteFetchError."""
        with self.assertRaises(QuoteFetchError) as ctx:
            GameState()
        self.assertIn("Network error", str(ctx.exception))

    @patch(FETCH_PATCH)
    def test_reset_raises_on_fetch_error(self, mock_fetch):
        """GameState.reset() propagates QuoteFetchError."""
        mock_fetch.return_value = "initial quote"
        game = GameState()

        mock_fetch.side_effect = QuoteFetchError("timed out")
        with self.assertRaises(QuoteFetchError):
            game.reset()


if __name__ == "__main__":
    unittest.main()
