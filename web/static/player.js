// WebAudio playback of samples rendered by synth_engine.js (the same samples the WAV file holds). The AudioContext is
// created on the first play() call, i.e. only after the user clicks.
let ctx = null;

export class Player {
  constructor() { this.src = null; this.t0 = 0; this.duration = 0; this.onend = null; }

  get playing() { return !!this.src; }

  play(wave, sampleRate, onend = null) {
    this.stop();
    ctx ||= new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === 'suspended') ctx.resume();
    const buf = ctx.createBuffer(1, wave.length, sampleRate);
    buf.getChannelData(0).set(Float32Array.from(wave));
    const src = ctx.createBufferSource();
    src.buffer = buf; src.connect(ctx.destination);
    src.onended = () => { if (this.src === src) { this.src = null; if (onend) onend(); } };
    this.src = src; this.duration = wave.length / sampleRate; this.t0 = ctx.currentTime;
    src.start();
  }

  // seconds since play() started (null when stopped)
  position() { return this.src ? Math.min(this.duration, ctx.currentTime - this.t0) : null; }

  stop() {
    const s = this.src;
    this.src = null;
    if (s) { try { s.stop(); } catch { /* already stopped */ } }
  }
}
