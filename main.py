import json
import time

import css
import trebek_bot
from models import Clue
import mesop as me
import mesop.labs as mel
from web_components.gemini_live_connection import gemini_live_connection
from web_components.audio_recorder import audio_recorder
from web_components.audio_player import audio_player
from state import State


def on_load(e: me.LoadEvent):
  """Update system instructions with the randomly selected game categories."""
  state = me.state(State)
  categories = [question_set[0].category for question_set in state.board.clues]
  state.gemini_live_api_config = trebek_bot.make_gemini_live_api_config(
    system_instructions=trebek_bot.make_system_instruction(categories)
  )


@me.page(
  path="/",
  title="Mesop Jeopardy Live",
  security_policy=me.SecurityPolicy(
    allowed_connect_srcs=["wss://generativelanguage.googleapis.com"],
    allowed_iframe_parents=["https://huggingface.co"],
    allowed_script_srcs=[
      "https://cdn.jsdelivr.net",
    ],
  ),
  on_load=on_load,
)
def app():
  state = me.state(State)

  with me.box(style=css.MAIN_COL_GRID):
    with me.box(style=css.board_col_grid()):
      for col_index in range(len(state.board.clues[0])):
        # Render Jeopardy categories
        if col_index == 0:
          for row_index in range(len(state.board.clues)):
            cell = state.board.clues[row_index][col_index]
            with me.box(style=css.category_box()):
              if state.gemini_live_api_enabled:
                me.text(cell.category)
              else:
                me.text("")

        # Render Jeopardy questions
        for row_index in range(len(state.board.clues)):
          cell = state.board.clues[row_index][col_index]
          key = f"clue-{row_index}-{col_index}"
          is_selectable = not (key in state.answered_questions or state.selected_question_key)
          with me.box(
            style=css.clue_box(state.gemini_live_api_enabled and is_selectable),
            key=key,
            on_click=on_click_cell,
          ):
            if not state.gemini_live_api_enabled:
              me.text("")
            elif key in state.answered_questions:
              me.text("")
            elif key == state.selected_question_key:
              me.text(cell.question, style=me.Style(text_align="left"))
            else:
              me.text(f"${cell.normalized_value}", style=me.Style(font_size="2.2vw"))

    # Sidebar
    with me.box(style=css.SIDEBAR):
      me.input(
        label="Google API Key",
        on_input=on_input_api_key,
        readonly=state.gemini_live_api_enabled,
        style=css.TEXT_INPUT,
        type="password",
        value=state.api_key,
      )

      with me.box(style=css.TOOLBAR_SECTION):
        gemini_live_button()
        audio_player_button()
        audio_recorder_button()

      # Score
      with me.box(style=css.SIDEBAR_SECTION):
        me.text("Score", type="headline-5", style=css.sidebar_header())
        with me.box(style=css.score_box()):
          me.text(format_dollars(state.score), style=css.score_text(state.score))

      # Clue
      with me.box(style=css.SIDEBAR_SECTION):
        me.text("Clue", type="headline-5", style=css.sidebar_header())
        with me.box(style=css.current_clue_box()):
          if state.selected_question_key:
            selected_question = get_selected_question(state.board, state.selected_question_key)
            me.text(selected_question.question)
          else:
            me.text("No clue selected. Please select one.", style=me.Style(font_style="italic"))

      # Response
      with me.box(style=css.SIDEBAR_SECTION):
        me.text("Response", type="headline-5", style=css.sidebar_header())
        me.textarea(
          disabled=not bool(state.selected_question_key),
          label="Enter your response",
          on_blur=on_input_response,
          style=css.TEXT_INPUT,
          value=state.response_value,
        )

        disabled = not bool(state.selected_question_key)
        me.button(
          disabled=disabled,
          label="Submit your response",
          on_click=on_click_submit,
          style=css.response_button(disabled),
          type="flat",
        )


@me.component
def gemini_live_button():
  state = me.state(State)
  with gemini_live_connection(
    api_config=state.gemini_live_api_config,
    api_key=state.api_key,
    enabled=state.gemini_live_api_enabled,
    on_start=on_gemini_live_api_started,
    on_stop=on_gemini_live_api_stopped,
    on_tool_call=handle_tool_calls,
    text_input=state.text_input,
    tool_call_responses=state.tool_call_responses,
  ):
    with me.tooltip(message=get_gemini_live_tooltip()):
      with me.content_button(
        disabled=not state.api_key,
        style=css.game_button(),
        type="icon",
      ):
        if state.gemini_live_api_enabled:
          me.icon(icon="stop")
        else:
          me.icon(icon="play_arrow")


@me.component
def audio_player_button():
  state = me.state(State)
  with audio_player(
    enabled=state.audio_player_enabled, on_play=on_audio_play, on_stop=on_audio_stop
  ):
    with me.tooltip(message=get_audio_player_tooltip()):
      with me.content_button(
        disabled=True,
        style=css.audio_button(),
        type="icon",
      ):
        if state.audio_player_enabled:
          me.icon(icon="volume_up")
        else:
          me.icon(icon="volume_mute")


@me.component
def audio_recorder_button():
  state = me.state(State)
  with audio_recorder(
    state=state.audio_recorder_state, on_state_change=on_audio_recorder_state_change
  ):
    with me.tooltip(message=get_audio_recorder_tooltip()):
      with me.content_button(
        disabled=not state.gemini_live_api_enabled,
        style=css.mic_button(),
        type="icon",
      ):
        if state.audio_recorder_state == "initializing":
          me.icon(icon="pending")
        else:
          me.icon(icon="mic")


def on_click_cell(e: me.ClickEvent):
  """Selects the given clue by prompting Gemini Live API."""
  state = me.state(State)
  clue = get_selected_question(state.board, e.key)
  me.state(State).text_input = f"I'd like to select {clue.category}, for ${clue.normalized_value}."


def on_input_response(e: me.InputBlurEvent):
  """Stores user input into state, so we can process their response."""
  state = me.state(State)
  state.response = e.value


def on_click_submit(e: me.ClickEvent):
  """Submit user response to clue to check if they are correct using Gemini Live API."""
  state = me.state(State)
  if not state.response.strip():
    return

  state.text_input = state.response

  # Hack to reset text input. Update the initial response value to current response
  # first, which will trigger a diff when we set the initial response back to empty
  # string.
  #
  # A small delay is also needed because some times the yield happens too fast, which
  # does not allow the UI on the client to update properly.
  state.response_value = state.response
  yield
  time.sleep(0.5)
  state.response_value = ""
  yield


def get_selected_question(board, selected_question_key) -> Clue:
  """Gets the selected question from the key."""
  _, row, col = selected_question_key.split("-")
  return board.clues[int(row)][int(col)]


def format_dollars(value: int) -> str:
  """Formats an integer value in US dollars format."""
  if value < 0:
    return f"-${value * -1:,}"
  return f"${value:,}"


def get_gemini_live_tooltip() -> str:
  """Tooltip messages for Gemini Live API web component button."""
  state = me.state(State)
  if state.gemini_live_api_enabled:
    return "Stop game"
  if state.api_key:
    return "Start game"
  return "Game disabled. Enter API Key."


def get_audio_player_tooltip() -> str:
  """Tooltip messages for Audio player web component button."""
  state = me.state(State)
  if state.audio_player_enabled:
    return "Audio playing"
  if state.gemini_live_api_enabled:
    return "Audio not playing"
  return "Audio disabled"


def get_audio_recorder_tooltip() -> str:
  """Tooltip messages for Audio recorder web component button."""
  state = me.state(State)
  if state.audio_recorder_state == "initializing":
    "Microphone initializing"
  if state.audio_recorder_state == "recording":
    return "Microphone on"
  if state.gemini_live_api_enabled:
    return "Microphone muted"
  return "Microphone disabled"


def on_input_api_key(e: me.InputEvent):
  """Captures Google API key input"""
  state = me.state(State)
  state.api_key = e.value


def on_audio_play(e: mel.WebEvent):
  """Event for when audio player play button was clicked."""
  me.state(State).audio_player_enabled = True


def on_audio_stop(e: mel.WebEvent):
  """Event for when audio player stop button was clicked."""
  me.state(State).audio_player_enabled = False


def on_audio_recorder_state_change(e: mel.WebEvent):
  """Event for when audio recorder state changes."""
  me.state(State).audio_recorder_state = e.value


def on_gemini_live_api_started(e: mel.WebEvent):
  """Event for when Gemin Live API start button was clicked."""
  me.state(State).gemini_live_api_enabled = True


def on_gemini_live_api_stopped(e: mel.WebEvent):
  """Event for when Gemin Live API stop button was clicked."""
  state = me.state(State)
  state.gemini_live_api_enabled = False
  state.selected_question_key = ""
  state.response_value = ""


def handle_tool_calls(e: mel.WebEvent):
  """Proceses tool calls from Gemini Live API.

  Supported tool calls:

  - get_clue
  - update_score
  """
  state = me.state(State)
  tool_calls = json.loads(e.value["toolCalls"])
  responses = []
  for tool_call in tool_calls:
    result = None
    if tool_call["name"] == "get_clue":
      result = tool_call_get_clue(
        tool_call["args"]["category_index"], tool_call["args"]["dollar_index"]
      )
    elif tool_call["name"] == "update_score":
      result = tool_call_update_score(tool_call["args"]["is_correct"])

    responses.append(
      {
        "id": tool_call["id"],
        "name": tool_call["name"],
        "response": {
          "result": result,
        },
      }
    )

  if responses:
    print(responses)
    state.tool_call_responses = json.dumps(responses)


def tool_call_update_score(is_correct: bool) -> str:
  """Updates the user's score

  Gemini will determine if the user is correct and then call this tool which will
  allow the game state to be updated appropriately.
  """
  state = me.state(State)
  selected_question = get_selected_question(state.board, state.selected_question_key)
  if is_correct:
    state.score += selected_question.normalized_value
  else:
    state.score -= selected_question.normalized_value

  # Clear question so another can be picked.
  state.answered_questions.add(state.selected_question_key)
  state.selected_question_key = ""

  return f"The user's score is {state.score}"


def tool_call_get_clue(category_index, dollar_index) -> str:
  """Gets the selected clue.

  Gemini will parse the user request and make a tool call with the row/col indexes.

  Example: "Category X for $400".
  """
  cell_key = f"clue-{category_index}-{dollar_index}"
  response = handle_select_clue(cell_key)

  if isinstance(response, str):
    return "There was an error. " + response

  return f"The clue is {response.question}\n\n The answer to the clue is {response.answer}\n\n Please read the clue to the user."


def handle_select_clue(clue_key: str) -> Clue | str:
  """Handles logic for clicking on a clue.

  If it returns a string, it will be an error message.
  If it returns a clue, that means a valid clue was selected.
  """
  state = me.state(State)
  if state.selected_question_key:
    return "A clue has already been selected."
  if clue_key in state.answered_questions:
    return "That clue has already been selected"
  state.selected_question_key = clue_key
  return get_selected_question(state.board, state.selected_question_key)
