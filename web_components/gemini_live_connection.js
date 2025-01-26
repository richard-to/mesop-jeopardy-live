import {
  LitElement,
  html,
} from "https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js";

class GeminiLiveConnection extends LitElement {
  static properties = {
    api_config: { type: String },
    enabled: { type: Boolean },
    endpoint: { type: String },
    startEvent: { type: String },
    stopEvent: { type: String },
    text_input: { type: String },
    toolCallEvent: { type: String },
    tool_call_responses: { type: String },
  };

  constructor() {
    super();
    this.onSetupComplete = () => {
      console.log("Setup complete...");
    };
    this.onAudioData = (base64Data) => {
      this.dispatchEvent(
        new CustomEvent("audio-output-received", {
          detail: { data: base64Data },
          // Allow event to cross shadow DOM boundaries (both need to be true)
          bubbles: true,
          composed: true,
        })
      );
    };
    this.onInterrupted = () => {};
    this.onTurnComplete = () => {};
    this.onError = () => {};
    this.onClose = () => {
      console.log("Web socket closed...");
    };
    this.onToolCall = (toolCalls) => {
      this.dispatchEvent(
        new MesopEvent(this.toolCallEvent, {
          toolCalls: JSON.stringify(toolCalls.functionCalls),
        })
      );
    };
    this.pendingSetupMessage = null;

    this.onAudioInputReceived = (e) => {
      this.sendAudioChunk(e.detail.data);
    };
  }

  connectedCallback() {
    super.connectedCallback();
    // Start listening for events when component is connected
    window.addEventListener("audio-input-received", this.onAudioInputReceived);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    window.removeEventListener(
      "audio-input-received",
      this.onAudioInputReceived
    );
    if (this.ws) {
      this.ws.close();
    }
  }

  firstUpdated() {
    if (this.enabled) {
      this.setupWebSocket();
    }
  }

  updated(changedProperties) {
    if (
      changedProperties.has("tool_call_responses") &&
      this.tool_call_responses.length > 0
    ) {
      this.sendToolResponse(JSON.parse(this.tool_call_responses));
    }
    if (changedProperties.has("text_input") && this.text_input.length > 0) {
      this.sendTextMessage(this.text_input);
    }
  }

  start() {
    if (!this.enabled) {
      this.dispatchEvent(new MesopEvent(this.startEvent, {}));
      this.dispatchEvent(
        new CustomEvent("gemini-live-api-started", {
          detail: {},
          // Allow event to cross shadow DOM boundaries (both need to be true)
          bubbles: true,
          composed: true,
        })
      );
    }
    this.setupWebSocket();
  }

  stop() {
    this.dispatchEvent(new MesopEvent(this.stopEvent, {}));
    this.dispatchEvent(
      new CustomEvent("gemini-live-api-stopped", {
        detail: {},
        // Allow event to cross shadow DOM boundaries (both need to be true)
        bubbles: true,
        composed: true,
      })
    );
    if (this.ws) {
      this.ws.close();
    }
  }

  setupWebSocket() {
    this.ws = new WebSocket(this.endpoint);
    this.ws.onopen = () => {
      console.log("WebSocket connection is opening...");
      this.sendSetupMessage();
    };

    this.ws.onmessage = async (event) => {
      try {
        let wsResponse;
        if (event.data instanceof Blob) {
          const responseText = await event.data.text();
          wsResponse = JSON.parse(responseText);
        } else {
          wsResponse = JSON.parse(event.data);
        }

        if (wsResponse.setupComplete) {
          this.onSetupComplete();
        } else if (wsResponse.toolCall) {
          this.onToolCall(wsResponse.toolCall);
        } else if (wsResponse.serverContent) {
          if (wsResponse.serverContent.interrupted) {
            this.onInterrupted();
            return;
          }

          if (wsResponse.serverContent.modelTurn?.parts?.[0]?.inlineData) {
            const audioData =
              wsResponse.serverContent.modelTurn.parts[0].inlineData.data;
            this.onAudioData(audioData);

            if (!wsResponse.serverContent.turnComplete) {
              this.sendContinueSignal();
            }
          }

          if (wsResponse.serverContent.turnComplete) {
            this.onTurnComplete();
          }
        }
      } catch (error) {
        console.error("Error parsing response:", error);
        this.onError("Error parsing response: " + error.message);
      }
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket Error:", error);
      this.onError("WebSocket Error: " + error.message);
    };

    this.ws.onclose = (event) => {
      console.log("Connection closed:", event);
      this.onClose(event);
    };
  }

  sendMessage(message) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error(
        "WebSocket is not open. Current state:",
        this.ws.readyState
      );
      this.onError("WebSocket is not ready. Please try again.");
    }
  }

  sendSetupMessage() {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(this.api_config);
    } else {
      console.error("Connection not ready.");
    }
  }

  sendAudioChunk(base64Audio) {
    const message = {
      realtime_input: {
        media_chunks: [
          {
            mime_type: "audio/pcm",
            data: base64Audio,
          },
        ],
      },
    };
    this.sendMessage(message);
  }

  sendEndMessage() {
    const message = {
      client_content: {
        turns: [
          {
            role: "user",
            parts: [],
          },
        ],
        turn_complete: true,
      },
    };
    this.sendMessage(message);
  }

  sendContinueSignal() {
    const message = {
      client_content: {
        turns: [
          {
            role: "user",
            parts: [],
          },
        ],
        turn_complete: false,
      },
    };
    this.sendMessage(message);
  }

  sendTextMessage(text) {
    this.sendMessage({
      client_content: {
        turn_complete: true,
        turns: [{ role: "user", parts: [{ text: text }] }],
      },
    });
  }

  sendToolResponse(functionResponses) {
    const toolResponse = {
      tool_response: {
        function_responses: functionResponses,
      },
    };
    this.sendMessage(toolResponse);
  }

  async ensureConnected() {
    if (this.ws.readyState === WebSocket.OPEN) {
      return;
    }

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error("Connection timeout"));
      }, 5000);

      const onOpen = () => {
        clearTimeout(timeout);
        this.ws.removeEventListener("open", onOpen);
        this.ws.removeEventListener("error", onError);
        resolve();
      };

      const onError = (error) => {
        clearTimeout(timeout);
        this.ws.removeEventListener("open", onOpen);
        this.ws.removeEventListener("error", onError);
        reject(error);
      };

      this.ws.addEventListener("open", onOpen);
      this.ws.addEventListener("error", onError);
    });
  }

  render() {
    if (this.enabled) {
      return html`<span @click="${this.stop}"><slot></slot></span>`;
    } else {
      return html`<span @click="${this.start}"><slot></slot></span>`;
    }
  }
}

customElements.define("gemini-live-connection", GeminiLiveConnection);
