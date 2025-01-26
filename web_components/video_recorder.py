from typing import Any, Callable

import mesop.labs as mel


@mel.web_component(path="./video_recorder.js")
def video_recorder(
  *,
  enabled: bool = False,
  on_data: Callable[[mel.WebEvent], Any],
  on_record: Callable[[mel.WebEvent], Any],
):
  """Records video and streams video to the Mesop server.

  This web components is designed to work with `MESOP_WEBSOCKETS_ENABLED=true`.

  The data event looks like:

    {
      "data": <base64-encoded-string>
    }
  """
  return mel.insert_web_component(
    name="video-recorder",
    events={
      "dataEvent": on_data,
      "recordEvent": on_record,
    },
    properties={
      "enabled": enabled,
    },
  )
