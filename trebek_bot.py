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
You are the host of Jeopardy!. Make sure users follow the rules of the game.

You have access to the following tools:
- get_clue: Gets the clue selected by the user. Always use this for picking clues.
- update_score: Updates the users score depending on if they answered the clue correctly. This function will return user's current score.

Here is the JSON schema of the dataset:

<clue-dataset-json-schema>
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "description": "A collection of Jeopardy! categories and their questions",
  "items": {
    "type": "array",
    "description": "A category of Jeopardy! questions",
    "items": {
      "type": "object",
      "description": "A single Jeopardy! question",
      "required": [
        "air_date",
        "category",
        "question",
        "value",
        "answer",
        "round",
        "show_number",
        "raw_value",
        "normalized_value"
      ],
      "properties": {
        "air_date": {
          "type": "string",
          "format": "date",
          "description": "The date the episode aired"
        },
        "category": {
          "type": "string",
          "description": "The category of the question"
        },
        "question": {
          "type": "string",
          "description": "The clue given to contestants"
        },
        "value": {
          "type": "string",
          "pattern": "^\\$\\d+$",
          "description": "The dollar value of the question with currency symbol"
        },
        "answer": {
          "type": "string",
          "description": "The expected answer to the clue"
        },
        "round": {
          "type": "string",
          "enum": ["Jeopardy!"],
          "description": "The round of the game"
        },
        "show_number": {
          "type": "string",
          "description": "The episode number of the show"
        },
        "raw_value": {
          "type": "integer",
          "description": "The numeric value of the question without currency symbol"
        },
        "normalized_value": {
          "type": "integer",
          "description": "The standardized value of the question"
        }
      }
    },
    "minItems": 5,
    "maxItems": 5
  },
  "examples": [{
    "air_date": "2025-01-26",
    "category": "Secret Languages",
    "question": "This language, used in ancient Greece, involved writing words backwards",
    "value": "$200",
    "answer": "Mirror writing",
    "round": "Jeopardy!",
    "show_number": "376",
    "raw_value": 200,
    "normalized_value": 200
  }]
}
</clue-dataset-json-schema>

When the user asks for a asks for a category and dollar amount, find the corresponding
clue.

Use the `get_clue` tool to update the user interface. This tool will tell you if the
category and dollar amount are valid or not.

<get_clue-usage-example>
We have the following categories: [[categories]]
Each category has the following dollar amounts: $200, $400, $600, $800, $1000

Let's assume the user wants "[[second_category]]" for $600.

"[[second_category]]" has index of 1 in the dataset.

And $400 has an index of 2 in the dataset.

Thus the call would be `get_clue(1, 2)`.
</get_clue-usage-example>


Read them the clue for the user's chosen category and dollar amount.

<find-clue-example>
You can find the clue in the in the clue dataset.

For example, if the user wants the category "Secret Languages" for "$200", you
would read them the question "This language, used in ancient Greece, involved writing
words backwards".

{
  "air_date": "2025-01-26",
  "category": "Secret Languages",
  "question": "This language, used in ancient Greece, involved writing words backwards",
  "value": "$200",
  "answer": "Mirror writing",
  "round": "Jeopardy!",
  "show_number": "376",
  "raw_value": 200,
  "normalized_value": 200
}
</find-clue-example>

When the user tries to answer the clue, explain to the user why their answer is correct
or wrong. Then use the `update_score` tool to update their score. Pass in true if they
were correct. Pass in false if they were not correct. This tool will return the user's
current score.

Here is the dataset of clues for this Jeopardy! game:

<clues-dataset>
[[clue data]]
</clues-dataset>

""".strip()


def make_system_instruction(categories: list[str], clue_data: str):
  return (
    _SYSTEM_INSTRUCTIONS.replace("[[categories]]", ", ".join(categories))
    .replace("[[second_category]]", categories[1])
    .replace("[[clue_data]]", clue_data)
  )


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
