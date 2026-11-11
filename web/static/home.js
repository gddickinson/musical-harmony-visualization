// Home page: hero with the jazz progression's harmonic-motion circle (a silent playhead sweeps it), counts from the
// API, entry cards and the five style progressions.
import { route, api, app, list, esc, animate, $ } from './core.js';
import { Theory, cssColor } from './theory_engine.js';
import { motionTrail, motionLabels } from './layout_engine.js';
import { totalBeats } from './synth_engine.js';
import { drawMotion } from './draw.js';

const DOORS = [
  ['#/studio', 'Studio', 'Pick a style or build a progression, watch the motion circle and analysis panels, play it and download the WAV and MIDI files.'],
  ['#/chords', 'Chords', 'All 12 chord types on any root: keyboard, MIDI pitches, frequencies, velocities and the synthesized waveform.'],
  ['#/verify', 'Verify', 'The browser engine against the Python code: chords, plot geometry, waveform samples, WAV header and MIDI bytes.'],
  ['#/about', 'About', 'How chords, sound and pictures are made, how to run the Python program and the web app, credits.'],
];

route('home', async () => {
  const [info, data] = await Promise.all([api('/info'), api('/theory')]);
  const theory = new Theory(data);
  app().innerHTML = `
  <section class="hero two">
    <div>
      <p class="kicker">Music theory · visualization · synthesis</p>
      <h1 class="glow">Musical Harmony Visualization</h1>
      <p class="lead">${esc(info.summary)} This site runs it in your browser: a JavaScript port of the Python code,
      checked value by value against it.</p>
      <a class="btn" href="#/studio">Open the studio</a><a class="btn alt" href="#/chords">Explore chords</a>
    </div>
    <figure class="fig"><canvas id="hero" role="img" aria-label="Harmonic motion circle of the jazz progression"></canvas>
      <figcaption class="small mute">Harmonic motion of the jazz progression (as <code>harmony_jazz_motion.png</code>), with a silent playhead.</figcaption></figure>
  </section>
  <div class="tiles">
    <div class="tile"><b>${info.styles.length}</b><span>progression styles</span></div>
    <div class="tile"><b>${info.chord_types.length}</b><span>chord types</span></div>
    <div class="tile"><b>${info.preset_chords}</b><span>chords in the style presets</span></div>
    <div class="tile"><b>${info.num_overtones}</b><span>overtones per note</span></div>
    <div class="tile"><b>${(info.sample_rate / 1000).toFixed(1)}k</b><span>samples per second</span></div>
    <div class="tile"><b>${info.tempo_bpm}</b><span>BPM default tempo</span></div>
  </div>
  <div class="grid wide">${list(DOORS, ([href, t, d]) => `<a class="card door" href="${href}"><b>${t}</b><span>${d}</span></a>`)}</div>
  <h2>The five styles</h2>
  ${list(theory.styles, s => `<h3>${esc(s.name)}</h3><p>${list(theory.chords(s.progression), c =>
    `<span class="tag" style="color:${cssColor(c.color)};border-color:${cssColor(c.color, 0.5)}">${esc(c.name)} · ${c.duration}</span>`)}</p>`)}`;
  hero(theory);
});

function hero(theory) {
  const canvas = $('#hero');
  const chords = theory.chords(theory.progression('jazz'));
  const trail = motionTrail(chords, theory.layout), labels = motionLabels(chords), T = totalBeats(chords);
  const size = Math.min(520, Math.max(280, canvas.parentElement.clientWidth));
  const draw = beat => drawMotion(canvas, size, chords, trail, labels, theory.layout, beat, T);
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { draw(null); return; }
  const bps = 2;  // 120 BPM
  let t0 = null;
  animate(t => { if (t0 == null) t0 = t; draw(((t - t0) / 1000 * bps) % T); });
}
