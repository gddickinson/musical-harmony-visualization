// Port of synthesis.py: additive chord waveform (fundamental + overtones at 1/(i+1)), slow amplitude modulation,
// ADSR envelope, progression rendering (beats -> seconds via the tempo), 16-bit PCM and the WAV file bytes.
// Operation order follows the numpy code so samples agree to ~1e-15 (tests/fixtures/harmony_reference.json).

// numpy.linspace(start, stop, num) with endpoint=True
export function linspace(start, stop, num) {
  const out = new Float64Array(Math.max(0, num));
  if (num <= 0) return out;
  if (num === 1) { out[0] = start; return out; }
  const step = (stop - start) / (num - 1);
  for (let i = 0; i < num; i++) out[i] = i * step + start;
  out[num - 1] = stop;
  return out;
}

export const defaultConfig = synth => ({
  sample_rate: synth.sample_rate, tempo_bpm: synth.tempo_bpm, num_overtones: synth.num_overtones,
  fm_mod_freq: synth.fm_mod_freq, fm_mod_depth: synth.fm_mod_depth,
});

// _create_adsr_envelope(samples)
export function adsr(samples, r) {
  const attack = Math.trunc(r.attack_ratio * samples);
  const decay = Math.trunc(r.decay_ratio * samples);
  const release = Math.trunc(r.release_ratio * samples);
  const env = new Float64Array(samples).fill(1);
  env.set(linspace(0, 1, attack), 0);
  env.set(linspace(1, r.sustain_level, decay), attack);
  for (let i = attack + decay; i < samples - release; i++) env[i] = r.sustain_level;
  if (release > 0) env.set(linspace(r.sustain_level, 0, release), samples - release);
  return env;
}

// create_enhanced_chord_waveform(chord, seconds, config); `ratios` = theory.synth (ADSR constants)
export function chordWaveform(chord, seconds, cfg, ratios) {
  const samples = Math.trunc(cfg.sample_rate * seconds);
  const out = new Float64Array(samples);
  const t = linspace(0, seconds, samples);
  const env = adsr(samples, ratios);
  const twoPi = 2 * Math.PI;
  const modW = twoPi * cfg.fm_mod_freq;
  const nOver = cfg.num_overtones;
  const wave = new Float64Array(samples);
  for (const note of chord.notes) {
    const f = note.frequency, amp = note.velocity / 100.0;
    const w0 = twoPi * f;
    for (let k = 0; k < samples; k++) wave[k] = amp * Math.sin(w0 * t[k]);
    for (let i = 1; i <= nOver; i++) {
      const wh = twoPi * (f * (i + 1)), a = amp / (i + 1);
      for (let k = 0; k < samples; k++) wave[k] += a * Math.sin(wh * t[k]);
    }
    for (let k = 0; k < samples; k++) {
      wave[k] *= (1 + cfg.fm_mod_depth * Math.sin(modW * t[k]));
      wave[k] *= env[k];
      out[k] += wave[k];
    }
  }
  const norm = 2 * chord.notes.length;
  for (let k = 0; k < samples; k++) out[k] /= norm;
  return out;
}

export const secondsPerBeat = cfg => 60.0 / cfg.tempo_bpm;
export const totalBeats = chords => chords.reduce((s, c) => s + c.duration, 0);

// render_progression(chords, config): float samples clipped to [-1, 1]
export function renderProgression(chords, cfg, ratios, onChord = null) {
  const spb = secondsPerBeat(cfg);
  const total = Math.trunc(cfg.sample_rate * (totalBeats(chords) * spb));
  const full = new Float64Array(total);
  let cur = 0;
  chords.forEach((chord, i) => {
    const seconds = chord.duration * spb;
    const n = Math.trunc(cfg.sample_rate * seconds);
    const w = chordWaveform(chord, seconds, cfg, ratios);
    const end = Math.min(cur + w.length, total);
    for (let k = cur; k < end; k++) full[k] += w[k - cur];
    cur += n;
    if (onChord) onChord(i);
  });
  for (let k = 0; k < total; k++) full[k] = Math.min(1, Math.max(-1, full[k]));
  return full;
}

// to_int16: (x * 32767).astype(np.int16) truncates toward zero
export function toInt16(wave) {
  const out = new Int16Array(wave.length);
  for (let k = 0; k < wave.length; k++) out[k] = Math.trunc(wave[k] * 32767);
  return out;
}

// scipy.io.wavfile.write(rate, int16 mono): 44-byte RIFF/WAVE PCM header + little-endian samples
export function wavBytes(pcm, rate) {
  const buf = new ArrayBuffer(44 + pcm.length * 2), v = new DataView(buf);
  const str = (o, s) => [...s].forEach((c, i) => v.setUint8(o + i, c.charCodeAt(0)));
  str(0, 'RIFF'); v.setUint32(4, 36 + pcm.length * 2, true); str(8, 'WAVE');
  str(12, 'fmt '); v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
  v.setUint32(24, rate, true); v.setUint32(28, rate * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true);
  str(36, 'data'); v.setUint32(40, pcm.length * 2, true);
  for (let k = 0; k < pcm.length; k++) v.setInt16(44 + 2 * k, pcm[k], true);
  return new Uint8Array(buf);
}
