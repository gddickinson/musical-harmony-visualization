// Studio: pick a style progression (or build your own), set the synthesis parameters, see the visualization.py panels
// redrawn live, play the progression (WebAudio, after a click) and download the WAV / MIDI files main.py would write.
import { route, api, app, esc, list, isStatic, needsServer, onLeave, download, slider, $ } from './core.js';
import { Theory, cssColor } from './theory_engine.js';
import { defaultConfig, renderProgression, toInt16, wavBytes, secondsPerBeat, totalBeats } from './synth_engine.js';
import { midiBytes } from './midi_engine.js';
import { chordStarts, motionTrail, motionLabels, noteDensity, harmonicComplexity, patternAngles } from './layout_engine.js';
import { drawMotion, drawRhythm, drawDensity, drawComplexity, drawPattern, drawWave, chordAt } from './draw.js';
import { Player } from './player.js';
import { state } from './state.js';

const MAX_SECONDS = 180;
const player = new Player();
let audio = { key: null, wave: null };

route('studio', async () => {
  const theory = new Theory(await api('/theory'));
  if (!state.progression) { state.progression = theory.progression(state.style); }
  if (!state.config) state.config = defaultConfig(theory.synth);
  const cfg = state.config;
  app().innerHTML = `
  <h1 class="glow">Studio</h1>
  <p class="lead">A style progression from <code>theory.get_style_progression</code>, or your own chords. The panels are the
  plots of <code>visualization.py</code>; Play and the downloads use a port of <code>synthesis.py</code>, so the WAV and MIDI
  match what <code>python main.py</code> writes.</p>
  <div class="panel">
    <div class="ctlgrid" id="ctls">
      <div class="ctl"><label for="style">Style</label><select id="style">${list(theory.styles, s => `<option value="${s.name}">${s.name}</option>`)}<option value="custom">custom</option></select></div>
    </div>
  </div>
  <div class="panel">
    <h3>Progression</h3>
    <div class="scroll"><table class="prog" id="prog"></table></div>
    <div class="bar"><button class="alt" id="add">+ Add chord</button><span class="small mute">Durations are beats; the tempo turns them into seconds.</span></div>
    <div class="bar">
      <button id="play">Play</button><button class="alt" id="wav">Download WAV</button><button class="alt" id="mid">Download MIDI</button>
      <button class="alt" id="mpl">Matplotlib figures</button>
    </div>
    <div class="status" id="status" role="status"></div>
  </div>
  <div class="plots2">
    <figure><canvas class="plot" id="motion" role="img" aria-label="Harmonic motion circle"></canvas>
      <figcaption>Harmonic motion: each chord's notes as rings (radius 0.3 + 0.15 per note), fading through the chord.</figcaption></figure>
    <figure><canvas class="plot" id="pattern" role="img" aria-label="Harmonic pattern polar plot"></canvas>
      <figcaption>Harmonic pattern: chords evenly around the circle at radius = number of notes, joined in order.</figcaption></figure>
  </div>
  <figure class="plotfig"><canvas class="plot" id="rhythm" role="img" aria-label="Harmonic progression timeline"></canvas>
    <figcaption>Harmonic progression: chord blocks over beats, coloured by chord type.</figcaption></figure>
  <div class="plots2">
    <figure><canvas class="plot" id="density" role="img" aria-label="Note density over time"></canvas><figcaption>Note density over time.</figcaption></figure>
    <figure><canvas class="plot" id="complexity" role="img" aria-label="Harmonic complexity bars"></canvas><figcaption>Harmonic complexity: notes × distinct pitch classes.</figcaption></figure>
  </div>
  <figure class="plotfig"><canvas class="plot" id="wave" role="img" aria-label="Synthesized waveform"></canvas>
    <figcaption id="wavecap">Waveform: rendered when you press Play or Download WAV.</figcaption></figure>
  <div id="figs" class="figs"></div>
  <h2>Chords</h2>
  <div class="scroll"><table id="ctab"></table></div>`;

  const ctls = $('#ctls');
  $('#style').value = state.style;
  slider(ctls, { id: 'tempo', label: 'Tempo', min: 40, max: 240, value: cfg.tempo_bpm, unit: ' BPM' }, v => { cfg.tempo_bpm = v; update(); });
  slider(ctls, { id: 'ov', label: 'Overtones', min: 0, max: 8, value: cfg.num_overtones }, v => { cfg.num_overtones = v; update(); });
  slider(ctls, { id: 'mf', label: 'Modulation rate', min: 0, max: 12, step: 0.5, value: cfg.fm_mod_freq, unit: ' Hz' }, v => { cfg.fm_mod_freq = v; update(); });
  slider(ctls, { id: 'md', label: 'Modulation depth', min: 0, max: 0.5, step: 0.01, value: cfg.fm_mod_depth, fmt: v => v.toFixed(2) }, v => { cfg.fm_mod_depth = v; update(); });
  const sr = document.createElement('div');
  sr.className = 'ctl';
  sr.innerHTML = `<label for="sr">Sample rate</label><select id="sr">${list([22050, 44100, 48000], r => `<option value="${r}">${r} Hz</option>`)}</select>`;
  ctls.appendChild(sr);
  $('#sr').value = String(cfg.sample_rate);
  $('#sr').addEventListener('change', e => { cfg.sample_rate = +e.target.value; update(); });
  $('#style').addEventListener('change', e => {
    state.style = e.target.value;
    if (state.style !== 'custom') state.progression = theory.progression(state.style);
    editor(theory); update();
  });
  $('#add').addEventListener('click', () => {
    const last = state.progression[state.progression.length - 1] || ['C4', 'major', 2.0];
    state.progression.push([...last]); custom(); editor(theory); update();
  });
  $('#play').addEventListener('click', () => togglePlay(theory));
  $('#wav').addEventListener('click', async () => {
    const r = await ensureAudio(theory); if (!r) return;
    download(`harmony_${state.style}.wav`, new Blob([wavBytes(toInt16(r.wave), cfg.sample_rate)], { type: 'audio/wav' }));
  });
  $('#mid').addEventListener('click', () => {
    const chords = current(theory); if (!chords) return;
    download(`harmony_${state.style}.mid`, new Blob([midiBytes(chords, cfg.tempo_bpm)], { type: 'audio/midi' }));
  });
  $('#mpl').addEventListener('click', () => figures());
  onLeave(() => { player.stop(); });

  editor(theory);
  update();

  function update() { player.stop(); $('#play').textContent = 'Play'; redraw(theory); }
});

function custom() { state.style = 'custom'; const s = $('#style'); if (s) s.value = 'custom'; }

function status(msg, cls = '') { const s = $('#status'); if (s) { s.className = 'status ' + cls; s.innerHTML = msg; } }

// Chords for the current progression, or null (with a message) if a chord is invalid.
function current(theory) {
  try {
    const chords = theory.chords(state.progression);
    if (!chords.length) throw new Error('Add at least one chord.');
    const secs = totalBeats(chords) * secondsPerBeat(state.config);
    if (secs > MAX_SECONDS) throw new Error(`The progression lasts ${secs.toFixed(0)} s; the limit here is ${MAX_SECONDS} s.`);
    return chords;
  } catch (e) { status(esc(e.message), 'err'); return null; }
}

function editor(theory) {
  const notes = theory.noteNames, types = Object.keys(theory.chordTypes);
  const opt = (vals, sel) => list(vals, v => `<option${String(v) === String(sel) ? ' selected' : ''}>${v}</option>`);
  $('#prog').innerHTML = `<tr><th>#</th><th>Root</th><th>Octave</th><th>Type</th><th>Beats</th><th></th></tr>` +
    list(state.progression, ([root, type, beats], i) => {
      const note = root.slice(0, -1), oct = root.slice(-1), col = theory.chordTypes[type]?.color || [0.5, 0.5, 0.5];
      return `<tr data-i="${i}"><td class="num"><span class="sw" style="background:${cssColor(col)}"></span> ${i + 1}</td>
        <td><select aria-label="Root note of chord ${i + 1}" data-f="note">${opt(notes, note)}</select></td>
        <td><select aria-label="Octave of chord ${i + 1}" data-f="oct">${opt([0, 1, 2, 3, 4, 5, 6, 7, 8], oct)}</select></td>
        <td><select aria-label="Type of chord ${i + 1}" data-f="type">${opt(types, type)}</select></td>
        <td><input aria-label="Beats of chord ${i + 1}" data-f="beats" type="number" min="0.25" max="16" step="0.25" value="${beats}"></td>
        <td><button class="alt" data-act="del" aria-label="Remove chord ${i + 1}">✕</button></td></tr>`;
    });
  $('#prog').onchange = e => {
    const tr = e.target.closest('tr'); if (!tr) return;
    const i = +tr.dataset.i, p = state.progression[i];
    const f = e.target.dataset.f, v = e.target.value;
    if (f === 'note') p[0] = v + p[0].slice(-1);
    if (f === 'oct') p[0] = p[0].slice(0, -1) + v;
    if (f === 'type') p[1] = v;
    if (f === 'beats') p[2] = Math.min(16, Math.max(0.25, Number(v) || 0.25));
    custom(); editor(theory); redraw(theory); player.stop(); $('#play').textContent = 'Play';
  };
  $('#prog').onclick = e => {
    const b = e.target.closest('button[data-act="del"]'); if (!b) return;
    state.progression.splice(+b.closest('tr').dataset.i, 1);
    custom(); editor(theory); redraw(theory);
  };
}

function sizes() {
  const w = Math.max(280, $('#rhythm').parentElement.clientWidth);
  const half = window.innerWidth < 760 ? w : Math.floor((w - 14) / 2);
  return { w, half };
}

let view = null;  // cached geometry for the playhead redraw
function redraw(theory, beat = null) {
  const chords = beat == null ? current(theory) : view.chords;
  if (!chords) return;
  if (beat == null) {
    const L = theory.layout;
    view = { chords, L, starts: chordStarts(chords), trail: motionTrail(chords, L), labels: motionLabels(chords), T: totalBeats(chords) };
    const { w, half } = sizes();
    drawPattern($('#pattern'), half, chords, patternAngles(chords));
    drawDensity($('#density'), half, 200, noteDensity(chords, L));
    drawComplexity($('#complexity'), half, 200, chords, view.starts, harmonicComplexity(chords));
    table(theory, chords);
    const secs = view.T * secondsPerBeat(state.config);
    status(`${chords.length} chords · ${view.T} beats · ${secs.toFixed(2)} s at ${state.config.tempo_bpm} BPM`);
    if (audio.key !== key()) { drawWave($('#wave'), w, 110, new Float64Array(0)); $('#wavecap').textContent = 'Waveform: rendered when you press Play or Download WAV.'; }
    else drawWave($('#wave'), w, 110, audio.wave);
  }
  const { w, half } = sizes();
  drawMotion($('#motion'), half, view.chords, view.trail, view.labels, view.L, beat, view.T);
  drawRhythm($("#rhythm"), w, 140, view.chords, view.starts, beat);
}

function table(theory, chords) {
  const secs = secondsPerBeat(state.config);
  $('#ctab').innerHTML = `<tr><th>Chord</th><th>Notes</th><th>MIDI</th><th>Frequency (Hz)</th><th>Velocity</th><th>Beats</th><th>Seconds</th></tr>` +
    list(chords, c => `<tr><td><span class="tag" style="color:${cssColor(c.color)};border-color:${cssColor(c.color, 0.6)}">${esc(c.name)}</span></td>
      <td class="mono">${c.notes.map(n => theory.midiToName(n.pitch)).join(' ')}</td>
      <td class="mono">${c.notes.map(n => n.pitch).join(' ')}</td>
      <td class="mono">${c.notes.map(n => n.frequency.toFixed(2)).join(' ')}</td>
      <td class="mono">${c.notes.map(n => n.velocity).join(' ')}</td>
      <td class="mono">${c.duration}</td><td class="mono">${(c.duration * secs).toFixed(3)}</td></tr>`);
}

const key = () => JSON.stringify([state.progression, state.config]);

async function ensureAudio(theory) {
  const chords = current(theory); if (!chords) return null;
  if (audio.key === key()) return audio;
  status('Rendering audio (additive synthesis, in your browser)...');
  await new Promise(r => setTimeout(r, 30));
  const t0 = performance.now();
  const wave = renderProgression(chords, state.config, theory.synth);
  audio = { key: key(), wave };
  const s = (wave.length / state.config.sample_rate).toFixed(2);
  status(`Rendered ${wave.length.toLocaleString('en')} samples (${s} s) in ${((performance.now() - t0) / 1000).toFixed(2)} s.`);
  drawWave($('#wave'), sizes().w, 110, wave);
  $('#wavecap').textContent = `Waveform: ${wave.length.toLocaleString('en')} samples at ${state.config.sample_rate} Hz, clipped to [-1, 1] (what the WAV holds).`;
  return audio;
}

let raf = 0;
async function togglePlay(theory) {
  const btn = $('#play');
  if (player.playing) { player.stop(); btn.textContent = 'Play'; return; }
  const r = await ensureAudio(theory); if (!r) return;
  const spb = secondsPerBeat(state.config), sr = state.config.sample_rate;
  player.play(r.wave, sr, () => { btn.textContent = 'Play'; cancelAnimationFrame(raf); redraw(theory); });
  btn.textContent = 'Stop';
  const tick = () => {
    const pos = player.position();
    if (pos == null || !document.body.contains(btn)) return;
    const beat = Math.min(view.T - 1e-9, pos / spb);
    redraw(theory, beat);
    drawWave($('#wave'), sizes().w, 110, r.wave, pos / (r.wave.length / sr));
    const k = chordAt(view.chords, beat);
    status(`Playing ${esc(view.chords[k].name)} (chord ${k + 1} of ${view.chords.length}) · ${pos.toFixed(1)} s`);
    raf = requestAnimationFrame(tick);
  };
  raf = requestAnimationFrame(tick);
  onLeave(() => { player.stop(); cancelAnimationFrame(raf); });
}

async function figures() {
  const host = $('#figs');
  if (isStatic()) { host.innerHTML = needsServer('Rendering the matplotlib PNG figures'); return; }
  host.innerHTML = '<p class="mute">Rendering with matplotlib (300 dpi, a few seconds)...</p>';
  try {
    const style = state.style === 'custom' ? 'classical' : state.style;
    const r = await api('/figures', { body: { progression: state.progression, config: state.config, style } });
    host.innerHTML = `<h2>Matplotlib figures (visualization.py)</h2>
      <img alt="Harmonic motion visualization rendered by matplotlib" src="data:image/png;base64,${r.motion}">
      <img alt="Advanced analysis figure rendered by matplotlib" src="data:image/png;base64,${r.advanced_analysis}">`;
  } catch (e) { host.innerHTML = `<p class="err">${esc(e.message)}</p>`; }
}
