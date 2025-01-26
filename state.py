from typing import Literal
from dataclasses import field
import random
import os

import question_bank
import mesop as me
from models import Board


_NUM_CATEGORIES = 6
_QUESTION_SETS = question_bank.load()


@me.stateclass
class State:
  selected_clue: str
  board: Board = field(default_factory=lambda: make_default_board(_QUESTION_SETS))
  # Used for clearing the text input.
  response_value: str
  response: str
  score: int
  # Key format: click-{row_index}-{col_index}
  selected_question_key: str
  # Set is not JSON serializable
  # Key format: click-{row_index}-{col_index}
  answered_questions: set[str] = field(default_factory=set)
  # Gemini Live API
  api_key: str = os.getenv("GOOGLE_API_KEY", "")
  gemini_live_api_enabled: bool = False
  gemini_live_api_config: str
  audio_player_enabled: bool = False
  audio_recorder_state: Literal["disabled", "initializing", "recording"] = "disabled"
  tool_call_responses: str = ""
  text_input: str = ""


def make_default_board(jeopardy_questions) -> Board:
  """Creates a board with some random jeopardy questions."""
  random.shuffle(jeopardy_questions)
  return Board(clues=jeopardy_questions[:_NUM_CATEGORIES])
