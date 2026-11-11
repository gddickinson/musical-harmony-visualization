// Chords: every chord type of theory.CHORD_TYPES on a keyboard, with MIDI pitches, frequencies and velocities as
// create_chord builds them, the synthesized waveform (synthesis.py port) and playback after a click.
import { route, api, app, esc, list, go, onLeave, $ } from './core.js';
import { Theory, cssColor } from './theory_engine.js';
import { defaultConfig, chordWaveform, secondsPerBeat } from './synth_engine.js';
import { drawKeyboard, drawWave, drawWaveLine } from './draw.js';
import { Player } from './player.js';
import { state } from './state.js';

const player = new Player();
const sel = { note: 'C', oct: '4', type: 'major7', beats: 2 };

route('chords', async () => {
  const theory = new Theory(await api('/theory'));
  const types = Object.entries(theory.chordTypes);
  app().innerHTML = `
  <h1 class="glow">Chords</h1>
  <p class="lead">The ${types.length} chord types of <code>theory.CHORD_TYPES</code>, built on any root by
  <code>create_chord</code>: intervals in semitones above the root, velocity 100 lowered by 5 per upper note, and the
  equal-tempered frequency A4 = 440 Hz · 2<sup>(pitch − 69)/12</sup>.</p>
  <div class="panel">
    <div class="row">
      <div><label for="cn">Root note</label><select id="cn">${list(theory.noteNames, n => `<option>${n}</option>`)}</select></div>
      <div><label for="co">Octave</label><select id="co">${list([0, 1, 2, 3, 4, 5, 6, 7, 8], o => `<option>${o}</option>`)}</select></div>
      <div><label for="cb">Beats (at the Studio tempo)</label><input id="cb" type="number" min="0.25" max="16" step="0.25"></div>
    </div>
    <h3>Chord type</h3>
    <div class="types" id="types">${list(types, ([name, t]) => `<button data-t="${name}"><span class="sw" style="background:${cssColor(t.color)}"></span>${name}</button>`)}</div>
    <div class="bar"><button id="cplay">Play chord</button><button class="alt" id="cadd">Add to Studio progression</button></div>
    <div class="status" id="cstat" role="status"></div>
  </div>
  <canvas class="kbd" id="kbd" role="img" aria-label="Keyboard with the chord's notes highlighted"></canvas>
  <div class="scroll"><table id="notes"></table></div>
  <div class="plots2">
    <figure><canvas class="plot" id="cwave" role="img" aria-label="Whole chord waveform"></canvas><figcaption id="cwcap"></figcaption></figure>
    <figure><canvas class="plot" id="czoom" role="img" aria-label="20 millisecond window of the waveform"></canvas><figcaption>20 ms from the middle of the chord: fundamentals plus overtones at 1/2, 1/3, 1/4 amplitude.</figcaption></figure>
  </div>
  <h2>All chord types</h2>
  <div class="scroll"><table>${'<tr><th>Type</th><th>Intervals (semitones)</th><th>Notes on C4</th></tr>' +
    list(types, ([name, t]) => `<tr><td><span class="tag" style="color:${cssColor(t.color)};border-color:${cssColor(t.color, 0.6)}">${name}</span></td>
      <td class="mono">${t.intervals.join(', ')}</td><td class="mono">${theory.createChord('C4', name, 1).notes.map(n => theory.midiToName(n.pitch)).join(' ')}</td></tr>`)}</table></div>`;

  $('#cn').value = sel.note; $('#co').value = sel.oct; $('#cb').value = sel.beats;
  $('#cn').onchange = e => { sel.note = e.target.value; show(theory); };
  $('#co').onchange = e => { sel.oct = e.target.value; show(theory); };
  $('#cb').onchange = e => { sel.beats = Math.min(16, Math.max(0.25, Number(e.target.value) || 1)); e.target.value = sel.beats; show(theory); };
  $('#types').onclick = e => { const b = e.target.closest('button'); if (b) { sel.type = b.dataset.t; show(theory); } };
  $('#cplay').onclick = () => play(theory);
  $('#cadd').onclick = () => {
    if (!state.progression) state.progression = theory.progression(state.style);
    state.progression.push([sel.note + sel.oct, sel.type, sel.beats]);
    state.style = 'custom';
    go('#/studio');
  };
  onLeave(() => player.stop());
  show(theory);
});

const cfgOf = theory => state.config || defaultConfig(theory.synth);

function show(theory) {
  player.stop();
  $$types().forEach(b => b.classList.toggle('on', b.dataset.t === sel.type));
  let chord;
  try { chord = theory.createChord(sel.note + sel.oct, sel.type, sel.beats); }
  catch (e) { $('#cstat').innerHTML = `<span class="err">${esc(e.message)}</span>`; return; }
  const cfg = cfgOf(theory), secs = sel.beats * secondsPerBeat(cfg);
  $('#cstat').textContent = `${chord.name}: ${chord.notes.length} notes, ${sel.beats} beats = ${secs.toFixed(3)} s at ${cfg.tempo_bpm} BPM`;
  const w = Math.max(280, app().clientWidth - 2);
  const root = chord.notes[0].pitch, lo = Math.max(0, Math.floor(root / 12) * 12), hi = Math.min(127, lo + 35);
  drawKeyboard($('#kbd'), w, Math.min(120, w / 6), lo, hi, chord.notes.map(n => n.pitch), chord.color, p => theory.midiToName(p));
  $('#notes').innerHTML = '<tr><th>Note</th><th>Semitones above root</th><th>MIDI</th><th>Frequency (Hz)</th><th>Velocity</th></tr>' +
    list(chord.notes, n => `<tr><td class="mono">${theory.midiToName(n.pitch)}</td><td class="mono">${n.pitch - root}</td>
      <td class="mono">${n.pitch}</td><td class="mono">${n.frequency.toFixed(3)}</td><td class="mono">${n.velocity}</td></tr>`);
  const wave = chordWaveform(chord, secs, cfg, theory.synth);
  const half = window.innerWidth < 760 ? w : Math.floor((w - 14) / 2);
  drawWave($('#cwave'), half, 160, wave);
  $('#cwcap').textContent = `Whole chord (${secs.toFixed(2)} s): ADSR envelope (attack ${theory.synth.attack_ratio * 100}%, decay ${theory.synth.decay_ratio * 100}% to ${theory.synth.sustain_level}, release ${theory.synth.release_ratio * 100}%) with ${cfg.fm_mod_freq} Hz modulation.`;
  const mid = Math.floor(wave.length / 2), n = Math.round(cfg.sample_rate * 0.02);
  drawWaveLine($('#czoom'), half, 160, wave.subarray(mid, Math.min(wave.length, mid + n)));
}

const $$types = () => [...document.querySelectorAll('#types button')];

function play(theory) {
  let chord;
  try { chord = theory.createChord(sel.note + sel.oct, sel.type, sel.beats); } catch { return; }
  const cfg = cfgOf(theory);
  player.play(chordWaveform(chord, sel.beats * secondsPerBeat(cfg), cfg, theory.synth), cfg.sample_rate);
}
