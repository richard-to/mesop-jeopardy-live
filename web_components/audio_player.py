from typing import Any, Callable
import base64

import mesop.labs as mel


@mel.web_component(path="./audio_player.js")
def audio_player(
  *,
  enabled: bool = False,
  data: bytes = b"",
  on_play: Callable[[mel.WebEvent], Any] | None = None,
  on_stop: Callable[[mel.WebEvent], Any] | None = None,
):
  """Plays audio streamed from the server.

  An important thing to note is that the audio player does not persist the data it
  receives. Instead the data is stored in a queue and removed once the audio has been
  played.

  This is a barebones configuration that sets the sample rate to 24000hz since that is
  what Gemini returns. In addition we expect the data to be in PCM format.
  """
  return mel.insert_web_component(
    name="audio-player",
    events=_filter_events(
      {
        "playEvent": on_play,
        "stopEvent": on_stop,
      }
    ),
    properties={
      "enabled": enabled,
      "data": base64.b64encode(data).decode("utf-8"),
    },
  )


def _filter_events(events: dict[str, Callable[[mel.WebEvent], Any] | None]):
  return {event: callback for event, callback in events.items() if callback}
