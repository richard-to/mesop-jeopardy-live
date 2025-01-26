from pydantic import BaseModel


class Clue(BaseModel):
  air_date: str
  category: str
  question: str
  value: str | None
  answer: str
  round: str
  show_number: str
  raw_value: int = 0
  normalized_value: int = 0


class Board(BaseModel):
  clues: list[list[Clue]]
