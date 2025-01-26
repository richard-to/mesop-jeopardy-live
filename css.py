import mesop as me

from state import State

COLOR_BLUE = "blue"
COLOR_YELLOW = "#f0cd6e"
COLOR_RED = "#cc153c"
COLOR_DISABLED = "#e4e4e4"
COLOR_DISABLED_BUTTON_BG = "#ccc"


MAIN_COL_GRID = me.Style(
  background="#ececec",
  display="grid",
  grid_template_columns="70% 30%",
  height="100vh",
)

SIDEBAR = me.Style(
  color="#111",
  overflow_y="scroll",
  padding=me.Padding.all(20),
)

SIDEBAR_SECTION = me.Style(margin=me.Margin(bottom=15))

TOOLBAR_SECTION = me.Style(
  margin=me.Margin(bottom=15),
  padding=me.Padding.all(5),
  background=me.theme_var("surface-container-highest"),
  justify_content="space-evenly",
  display="flex",
  flex_direction="row",
)

TEXT_INPUT = me.Style(width="100%")


def sidebar_header() -> me.Style:
  state = me.state(State)
  return me.Style(color="#000" if state.gemini_live_api_enabled else "#aaa")


def game_button() -> me.Style:
  state = me.state(State)
  if not state.api_key:
    return me.Style()
  if state.gemini_live_api_enabled:
    return me.Style(background=me.theme_var("error"), color=me.theme_var("on-error"))
  return me.Style(background=me.theme_var("primary"), color=me.theme_var("on-primary"))


def audio_button() -> me.Style:
  state = me.state(State)
  if state.audio_player_enabled:
    return me.Style(background=me.theme_var("tertiary"), color=me.theme_var("on-tertiary"))
  return me.Style()


def mic_button() -> me.Style:
  state = me.state(State)
  if state.audio_recorder_state == "recording":
    return me.Style(background=me.theme_var("tertiary"), color=me.theme_var("on-tertiary"))
  if state.gemini_live_api_enabled:
    return me.Style(background=me.theme_var("error"), color=me.theme_var("on-error"))
  return me.Style()


def score_box() -> me.Style:
  state = me.state(State)
  return me.Style(
    background=COLOR_BLUE if state.gemini_live_api_enabled else COLOR_DISABLED,
    color="white" if state.gemini_live_api_enabled else COLOR_DISABLED,
    font_weight="bold",
    font_size="2.2vw",
    padding=me.Padding.all(15),
    text_align="center",
  )


def current_clue_box() -> me.Style:
  state = me.state(State)
  return me.Style(
    background=COLOR_BLUE if state.gemini_live_api_enabled else COLOR_DISABLED,
    color=COLOR_YELLOW if state.gemini_live_api_enabled else COLOR_DISABLED,
    font_size="1em",
    font_weight="bold",
    padding=me.Padding.all(15),
  )


def board_col_grid() -> me.Style:
  state = me.state(State)
  return me.Style(
    background="#000" if state.gemini_live_api_enabled else "#ddd",
    display="grid",
    gap="5px",
    grid_template_columns="repeat(6, 1fr)",
  )


def category_box() -> me.Style:
  state = me.state(State)
  return me.Style(
    background=COLOR_BLUE if state.gemini_live_api_enabled else COLOR_DISABLED,
    color="white",
    font_weight="bold",
    font_size="1em",
    padding=me.Padding.all(15),
    text_align="center",
  )


def clue_box(is_selectable: bool) -> me.Style:
  """Style for clue box

  Args:
    is_selectable: Visual signify if the clue is selectable.
  """
  state = me.state(State)
  return me.Style(
    background=COLOR_BLUE if state.gemini_live_api_enabled else COLOR_DISABLED,
    color=COLOR_YELLOW,
    cursor="pointer" if is_selectable else "default",
    font_size="1em",
    font_weight="bold",
    padding=me.Padding.all(15),
    text_align="center",
  )


def response_button(disabled: bool) -> me.Style:
  """Styles for response submit button.

  Args:
    disabled: Since we're overriding the style, we need to handle disabled state
  """
  if disabled:
    return me.Style(background=COLOR_DISABLED_BUTTON_BG, color="#eee")
  return me.Style(background=COLOR_BLUE, color="white")


def score_text(score: int) -> me.Style:
  """In Jeopardy when the score is negative, it is red instead of white."""
  state = me.state(State)
  if not state.gemini_live_api_enabled:
    return me.Style(color=COLOR_DISABLED)

  if score < 0:
    return me.Style(color=COLOR_RED)

  return me.Style(color="white")
