// About: what the project is, how chords, sound and pictures are computed (from the code), what the web version
// covers, how to run the Python program and the web app, credits (from the README).
import { route, api, app, esc, list } from './core.js';

route('about', async () => {
  const t = await api('/theory');
  const s = t.synth;
  app().innerHTML = `
  <h1 class="glow">About</h1>
  <p class="lead">A Python system that generates, visualizes and synthesizes musical harmonies across different styles,
  combining music theory, audio synthesis and visualization. This site is its web interface.</p>

  <h2>How it works</h2>
  <h3>Chords (theory.py)</h3>
  <p>Note names with a single-digit octave map to MIDI pitches (<code>C4</code> = 60, sharps only). A chord is a root plus
  the intervals of one of the ${Object.keys(t.chord_types).length} chord types; upper notes get a velocity 5 lower per
  step. Each style (${list(t.styles, x => esc(x.name), ', ')}) is a fixed list of (root, type, beats).</p>
  <p><span class="eq">f = ${t.a4_frequency} Hz · 2^((pitch − ${t.a4_midi_pitch}) / ${t.semitones_per_octave})</span></p>
  <h3>Sound (synthesis.py)</h3>
  <p>Each note is a sine at its frequency (amplitude velocity / 100) plus ${s.num_overtones} overtones at 2f, 3f, 4f with
  amplitudes 1/2, 1/3, 1/4; the sum is multiplied by a slow ${s.fm_mod_freq} Hz modulation of depth ${s.fm_mod_depth} and an
  ADSR envelope (attack ${s.attack_ratio * 100}% of the chord, decay ${s.decay_ratio * 100}% to ${s.sustain_level},
  release ${s.release_ratio * 100}%). The chord is the sum of its notes divided by twice the note count; the progression is
  clipped to [−1, 1] and written as 16-bit mono WAV at ${s.sample_rate} Hz. Durations are beats, converted with the tempo
  (default ${s.tempo_bpm} BPM); the MIDI file (MIDIUtil, 960 ticks per beat) uses the same tempo.</p>
  <h3>Pictures (visualization.py, harmony_layout.py)</h3>
  <p><b>Harmonic motion</b>: ${t.layout.motion_time_points} time samples around a circle; at each, the sounding chord's
  notes are drawn on rings of radius ${t.layout.base_radius} + ${t.layout.radius_step} per note, fading over the chord.
  <b>Advanced analysis</b>: the chord blocks over beats, the note count over time, harmonic complexity (notes × distinct
  pitch classes) and the style pattern (chords evenly around a circle at radius = note count).</p>

  <h2>This web version</h2>
  <ul>
    <li>Everything on the Studio and Chords pages runs in the browser: JavaScript ports of <code>theory.py</code>,
    <code>harmony_layout.py</code> and <code>synthesis.py</code> (including the MIDI writer). The chord tables and constants
    are exported from the Python modules (<code>/api/theory</code>).</li>
    <li>Play uses WebAudio on the same samples the WAV file holds; audio starts only when you press a Play button.</li>
    <li>The canvas panels redraw the matplotlib figures' content; with the local server, the Studio's "Matplotlib
    figures" button renders the real PNGs with <code>visualization.py</code>.</li>
    <li>The <a href="#/verify">Verify</a> page compares the JS engine with the Python output.</li>
  </ul>

  <h2>Run it yourself</h2>
  <h3>Python program</h3>
  <pre>git clone https://github.com/gddickinson/musical-harmony-visualization.git
cd musical-harmony-visualization
pip install -r requirements.txt
python main.py --style jazz --tempo 120 --output-dir out</pre>
  <p>Writes <code>harmony_jazz.mid</code>, <code>.wav</code>, <code>_motion.png</code> and <code>_advanced_analysis.png</code>
  (all five styles without <code>--style</code>).</p>
  <h3>Web app</h3>
  <pre>pip install -r requirements-web.txt
python run_web.py          # http://127.0.0.1:8165</pre>

  <h2>Credits</h2>
  <p>By George Dickinson. Built using numpy, matplotlib, scipy and MIDIUtil; music theory principles from various
  traditions; synthesis techniques inspired by classic synthesizers. Built with AI assistance from
  <a href="https://claude.com/">Claude (Anthropic)</a>. MIT licence.
  <a href="https://github.com/gddickinson/musical-harmony-visualization">Source on GitHub</a>.</p>`;
});
