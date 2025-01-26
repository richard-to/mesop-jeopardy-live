import {
  LitElement,
  html,
  css,
} from "https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js";

class VideoRecorder extends LitElement {
  static styles = css`
    :host {
      display: block;
    }

    .video-container {
      position: relative;
      width: 100%;
      max-width: 640px;
      margin: 0 auto;
    }

    video {
      width: 100%;
      height: auto;
      background: #000;
    }

    .controls {
      margin-top: 10px;
      text-align: center;
    }

    button {
      padding: 8px 16px;
      font-size: 16px;
      cursor: pointer;
    }
  `;

  static properties = {
    dataEvent: { type: String },
    recordEvent: { type: String },
    isRecording: { type: Boolean },
    enabled: { type: Boolean },
    quality: { type: Number },
    fps: { type: Number },
    showPreview: { type: Boolean },
  };

  constructor() {
    super();
    this.debug = false;
    this.mediaStream = null;
    this.isStreaming = false;
    this.isRecording = false;
    this.isInitializing = false;
    this.enabled = false;
    this.quality = 0.8; // JPEG quality
    this.fps = 2; // Frames per second
    this.showPreview = true; // Enable preview by default

    // Setup canvas and video elements
    this.video = document.createElement("video");
    this.video.setAttribute("playsinline", ""); // Better mobile support
    this.video.setAttribute("autoplay", "");
    this.video.setAttribute("muted", "");
    this.canvas = document.createElement("canvas");
    this.ctx = this.canvas.getContext("2d");
    this.captureInterval = null;
  }

  disconnectedCallback() {
    this.stop();
    super.disconnectedCallback();
  }

  firstUpdated() {
    if (this.enabled) {
      this.startStreaming();
    }
  }

  log(...args) {
    if (this.debug) {
      console.log(...args);
    }
  }

  warn(...args) {
    if (this.debug) {
      console.warn(...args);
    }
  }

  error(...args) {
    if (this.debug) {
      console.error(...args);
    }
  }

  async startStreaming() {
    if (!this.enabled) {
      // this.dispatchEvent(new MesopEvent(this.recordEvent, {}));
    }
    this.isInitializing = true;
    const initialized = await this.initialize();
    this.isInitializing = false;
    if (initialized) {
      this.isRecording = true;
      this.start();
    }
  }

  async initialize() {
    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      });

      this.video.srcObject = this.mediaStream;
      await this.video.play();

      // Wait for video to be ready
      await new Promise((resolve) => {
        this.video.onloadedmetadata = () => {
          this.canvas.width = this.video.videoWidth;
          this.canvas.height = this.video.videoHeight;
          resolve();
        };
      });

      // Request a redraw to show the video preview
      this.requestUpdate();
      return true;
    } catch (error) {
      this.error("Error accessing webcam:", error);
      return false;
    }
  }

  captureFrame() {
    if (!this.mediaStream) {
      this.error("Webcam not started");
      return null;
    }

    // Draw current video frame to canvas
    this.ctx.drawImage(this.video, 0, 0);

    // Convert to JPEG and base64 encode
    const base64Data = this.canvas.toDataURL("image/jpeg", this.quality);

    // Remove the data URL prefix to get just the base64 data
    return base64Data.replace("data:image/jpeg;base64,", "");
  }

  start() {
    this.isStreaming = true;

    // Start capturing frames at specified FPS
    const intervalMs = 1000 / this.fps;
    this.captureInterval = setInterval(() => {
      const base64Frame = this.captureFrame();
      if (base64Frame) {
        this.dispatchEvent(
          new MesopEvent(this.dataEvent, {
            data: base64Frame,
          })
        );
      }
    }, intervalMs);

    return true;
  }

  stop() {
    this.isStreaming = false;
    this.isRecording = false;

    if (this.captureInterval) {
      clearInterval(this.captureInterval);
      this.captureInterval = null;
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }

    // Clear video source
    if (this.video.srcObject) {
      this.video.srcObject = null;
    }
  }

  render() {
    return html`
      <div class="video-container">
        ${this.showPreview && (this.isRecording || this.isInitializing)
          ? html`<video
              .srcObject="${this.mediaStream}"
              playsinline
              autoplay
              muted
            ></video>`
          : null}

        <div class="controls">
          ${this.isInitializing
            ? html`<div>Initializing video recorder...</div>`
            : this.isRecording
            ? html`<button @click="${this.stop}">Stop Recording</button>`
            : html`<button @click="${this.startStreaming}">
                Start Recording
              </button>`}
        </div>
      </div>
    `;
  }
}

customElements.define("video-recorder", VideoRecorder);
