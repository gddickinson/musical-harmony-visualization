// Runs the JS engine on the Python reference cases (tests/fixtures/harmony_reference.json, served as /api/reference)
// and compares every value. Used by the node test (engine.test.mjs) and the Verify page.
import { Theory } from './theory_engine.js';
import { adsr, chordWaveform, renderProgression, toInt16, wavBytes } from './synth_engine.js';
import { midiBytes, toHex } from './midi_engine.js';
import { chordStarts, motionTrail, motionLabels, noteDensity, harmonicComplexity, patternAngles } from './layout_engine.js';

export const TOL = 1e-9;

// Compare two (nested) numeric arrays; strings must match exactly. Returns { n, maxAbs, bad: [messages] }.
export function compare(a, b, tol = TOL, path = '') {
  const r = { n: 0, maxAbs: 0, bad: [] };
  const walk = (x, y, p) => {
    if (Array.isArray(x) || ArrayBuffer.isView(x)) {
      if (!y || x.length !== y.length) { r.bad.push(`${p}: length ${x.length} vs ${y && y.length}`); return; }
      for (let i = 0; i < x.length; i++) walk(x[i], y[i], `${p}[${i}]`);
    } else if (typeof x === 'number') {
      r.n++;
      const d = Math.abs(x - y);
      if (!(d <= tol * Math.max(1, Math.abs(x)))) r.bad.push(`${p}: ${x} vs ${y}`);
      if (d > r.maxAbs) r.maxAbs = d;
    } else { r.n++; if (x !== y) r.bad.push(`${p}: ${String(x).slice(0, 80)} vs ${String(y).slice(0, 80)}`); }
  };
  walk(a, b, path);
  return r;
}

function merge(into, r, label) {
  into.n += r.n; into.maxAbs = Math.max(into.maxAbs, r.maxAbs);
  into.bad.push(...r.bad.slice(0, 5).map(m => `${label} ${m}`));
}

// One progression case: chords, layout, waveform samples, PCM checksums, WAV header and MIDI bytes.
export function runCase(theory, ref) {
  const out = { name: ref.name, rows: [] };
  const row = (label, r) => { out.rows.push({ label, n: r.n, maxAbs: r.maxAbs, bad: r.bad }); };
  const chords = theory.chords(ref.progression);
  const cfg = ref.config, synth = theory.synth;

  const c = { n: 0, maxAbs: 0, bad: [] };
  merge(c, compare(ref.chords.map(x => x.name), chords.map(x => x.name)), 'name');
  merge(c, compare(ref.chords.map(x => x.pitches), chords.map(x => x.notes.map(n => n.pitch)), 0), 'pitch');
  merge(c, compare(ref.chords.map(x => x.velocities), chords.map(x => x.notes.map(n => n.velocity)), 0), 'velocity');
  merge(c, compare(ref.chords.map(x => x.frequencies), chords.map(x => x.notes.map(n => n.frequency))), 'frequency');
  merge(c, compare(ref.chords.map(x => x.color), chords.map(x => x.color), 0), 'color');
  row('chords: names, pitches, velocities, frequencies', c);

  const L = theory.layout, l = { n: 0, maxAbs: 0, bad: [] };
  merge(l, compare(ref.layout.starts, chordStarts(chords)), 'starts');
  merge(l, compare(ref.layout.trail, motionTrail(chords, L)), 'trail');
  merge(l, compare(ref.layout.labels, motionLabels(chords)), 'labels');
  const dens = noteDensity(chords, L);
  merge(l, compare(ref.layout.density_x, dens.x), 'density_x');
  merge(l, compare(ref.layout.density, dens.y, 0), 'density');
  merge(l, compare(ref.layout.complexity, harmonicComplexity(chords), 0), 'complexity');
  merge(l, compare(ref.layout.pattern_angles, patternAngles(chords)), 'pattern');
  row('plot geometry (motion trail, labels, density, complexity, pattern)', l);

  const wave = renderProgression(chords, cfg, synth);
  const w = ref.wave, s = { n: 0, maxAbs: 0, bad: [] };
  if (wave.length !== w.length) s.bad.push(`length ${w.length} vs ${wave.length}`);
  const strided = [];
  for (let k = 0; k < wave.length; k += w.stride) strided.push(wave[k]);
  merge(s, compare(w.samples, strided, 1e-12), 'sample');
  row(`waveform: ${wave.length.toLocaleString('en')} samples (every ${w.stride}th compared)`, s);

  const pcm = toInt16(wave), p = { n: 0, maxAbs: 0, bad: [] };
  const pcmStrided = [];
  for (let k = 0; k < pcm.length; k += w.stride) pcmStrided.push(pcm[k]);
  merge(p, compare(w.pcm, pcmStrided, 0.5), 'pcm');   // at most 1 LSB apart (truncation at a boundary)
  let sum = 0, abs = 0;
  for (const v of pcm) { sum += v; abs += Math.abs(v); }
  merge(p, compare([w.pcm_sum, w.pcm_abs_sum], [sum, abs], 1e-6), 'checksum');
  merge(p, compare(w.wav_header, toHex(wavBytes(pcm, cfg.sample_rate).subarray(0, 44))), 'wav header');
  merge(p, compare(w.wav_size, 44 + pcm.length * 2, 0), 'wav size');
  row('16-bit PCM, checksums and WAV header', p);

  const m = compare(ref.midi, toHex(midiBytes(chords, cfg.tempo_bpm)));
  row('MIDI file bytes', m);
  out.ok = out.rows.every(r => !r.bad.length);
  return out;
}

export function runExtras(theory, ref) {
  const rows = [];
  const a = { n: 0, maxAbs: 0, bad: [] };
  for (const [n, env] of Object.entries(ref.adsr)) merge(a, compare(env, adsr(Number(n), theory.synth)), `adsr ${n}`);
  rows.push({ label: `ADSR envelope (${Object.keys(ref.adsr).join(', ')} samples)`, ...a });

  const w = { n: 0, maxAbs: 0, bad: [] };
  for (const cw of ref.chord_waves) {
    const cfg = { ...defaultsFrom(theory), ...cw.config };
    merge(w, compare(cw.samples, chordWaveform(theory.createChord(cw.root, cw.type, 1.0), cw.seconds, cfg, theory.synth), 1e-12), cw.root + cw.type);
  }
  rows.push({ label: 'single-chord waveforms (3 chords, 3 synth configs)', ...w });

  const m = { n: 0, maxAbs: 0, bad: [] };
  const blues = theory.chords(theory.progression('blues'));
  merge(m, compare(ref.midi.blues_60bpm, toHex(midiBytes(blues, 60))), 'blues');
  const odd = [theory.createChord('E4', 'minor', 0.3333), theory.createChord('E4', 'minor', 1.1), theory.createChord('B3', 'dominant7', 0.26)];
  merge(m, compare(ref.midi.odd_durations_137bpm, toHex(midiBytes(odd, 137))), 'odd');
  rows.push({ label: 'MIDI: repeated chords at 60 BPM, odd durations at 137 BPM', ...m });

  const t = { n: 0, maxAbs: 0, bad: [] };
  for (const [name, want] of Object.entries(ref.note_to_midi)) {
    let got = null;
    try { got = theory.noteToMidi(name); } catch { got = null; }
    t.n++;
    if (got !== want) t.bad.push(`note_to_midi(${JSON.stringify(name)}): ${want} vs ${got}`);
  }
  rows.push({ label: 'note_to_midi on valid and invalid names', ...t });
  return rows;
}

const defaultsFrom = theory => {
  const s = theory.synth;
  return { sample_rate: s.sample_rate, tempo_bpm: s.tempo_bpm, num_overtones: s.num_overtones, fm_mod_freq: s.fm_mod_freq, fm_mod_depth: s.fm_mod_depth };
};

export function runAll(theoryData, ref) {
  const theory = new Theory(theoryData);
  const cases = ref.cases.map(c => runCase(theory, c));
  const extras = runExtras(theory, ref);
  const ok = cases.every(c => c.ok) && extras.every(r => !r.bad.length);
  return { cases, extras, ok };
}
