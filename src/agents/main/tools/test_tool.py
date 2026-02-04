from agno.tools import tool


@tool
def count_words(text: str) -> int:
  """Counts the number of words in a given text."""
  return len(text.split())
