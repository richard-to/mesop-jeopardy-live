from typing import Literal
import json


type VoiceName = Literal["Aoede", "Charon", "Fenrir", "Kore", "Puck"]
type GeminiModel = Literal["gemini-2.0-flash-exp"]


_TOOL_DEFINITIONS = {
  "functionDeclarations": [
    {
      "name": "get_clue",
      "description": "Gets the clue from the board which returns the clue and answer",
      "parameters": {
        "type": "object",
        "properties": {
          "category_index": {"type": "integer", "description": "Index of selected category."},
          "dollar_index": {"type": "integer", "description": "Index of selected dollar amount."},
        },
        "required": ["category_index", "dollar_index"],
      },
    },
    {
      "name": "update_score",
      "description": "Updates whether user got the question correct or not.",
      "parameters": {
        "type": "object",
        "properties": {
          "is_correct": {"type": "boolean", "description": "True if correct. False is incorrect."},
        },
        "required": ["is_correct"],
      },
    },
  ]
}

_SYSTEM_INSTRUCTIONS = """
You are the host of Jeopardy. Make sure users follow the rules of the game.

You have access to the following tools:
- get_clue: Gets the clue selected by the user. Always use this for picking clues. Do not make up your own clues.
- update_score: Updates the users score depending on if they answered the clue correctly.

The categories are [[categories]]. Each category has 5 questions, with the following dollar
amounts: $200, $400, $600, $800, $1000.

When the user asks for a clue, they will specify the category and dollar amount. Use the
`get_clue` tool by passing in the corresponding indexes for the category and dollar
amount.

For example if the categories are Witches, Gold Rush, American History, Desserts, Wet & Wild,
and the user says "American History for $800", the index will be 2 for the category and 3
for the dollar amount.

The `get_clue` tool will return the clue and answer if it is valid. If it is invalid it
will return an error message.

Wait for the `get_clue` tool response before responding.

When you get the response to the `get_clue` tool, read the clue to the user.

Briefly explain to the user why their answer is correct or wrong.

Use the `update_score` tool to update their score. Pass in true if they were correct.
Pass in false if they were not correct. This tool will return the user's current score.
""".strip()


def make_system_instruction(categories: list[str]):
  return _SYSTEM_INSTRUCTIONS.replace("[[categories]]", ", ".join(categories))


def make_gemini_live_api_config(
  model: GeminiModel = "gemini-2.0-flash-exp",
  system_instructions: str = "",
  voice_name: VoiceName = "Puck",
):
  return json.dumps(
    {
      "setup": {
        "model": f"models/{model}",
        "system_instruction": {"role": "user", "parts": [{"text": system_instructions}]},
        "tools": _TOOL_DEFINITIONS,
        "generation_config": {
          "temperature": 0.3,
          "response_modalities": ["audio"],
          "speech_config": {"voice_config": {"prebuilt_voice_config": {"voice_name": voice_name}}},
        },
      }
    }
  )
