from src.agents.main.tools.test_tool import count_words


def test_count_words_basic():
  assert count_words.entrypoint("hello world") == 2


def test_count_words_empty():
  assert count_words.entrypoint("") == 0


def test_count_words_multiple_spaces():
  assert count_words.entrypoint("hello   world") == 2


def test_count_words_single_word():
  assert count_words.entrypoint("hello") == 1
