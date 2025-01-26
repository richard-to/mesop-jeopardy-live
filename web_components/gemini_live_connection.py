from typing import Any, Callable

import mesop.labs as mel


_HOST = "generativelanguage.googleapis.com"

_GEMINI_BIDI_WEBSOCKET_URI = "wss://{host}/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={api_key}"


@mel.web_component(path="./gemini_live_connection.js")
def gemini_live_connection(
  *,
  enabled: bool = False,
  api_key: str = "",
  api_config: str = "",
  on_start: Callable[[mel.WebEvent], Any] | None = None,
  on_stop: Callable[[mel.WebEvent], Any] | None = None,
  on_tool_call: Callable[[mel.WebEvent], Any] | None = None,
  tool_call_responses: str = "",
  text_input: str = "",
):
  return mel.insert_web_component(
    name="gemini-live-connection",
    events=_filter_events(
      {
        "startEvent": on_start,
        "stopEvent": on_stop,
        "toolCallEvent": on_tool_call,
      }
    ),
    properties={
      "api_config": api_config,
      "enabled": enabled,
      "endpoint": _GEMINI_BIDI_WEBSOCKET_URI.format(host=_HOST, api_key=api_key),
      "tool_call_responses": tool_call_responses,
      "text_input": text_input,
    },
  )


def _filter_events(events: dict[str, Callable[[mel.WebEvent], Any] | None]):
  return {event: callback for event, callback in events.items() if callback}
