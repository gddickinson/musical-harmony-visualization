# Musical Harmony Visualization - Interface Map

## Entry points

| File | Purpose |
|------|---------|
| `main.py` | CLI: `python main.py [--style jazz\|classical\|blues\|modal\|impressionist] [--output-dir DIR] [--tempo BPM]` |
| `run_web.py` | Web app on http://127.0.0.1:8165 (`web.app:app`) |
| `scripts/build_static.py` | Export the static GitHub Pages site to `site/` |
| `scripts/make_fixture.py` | Regenerate `tests/fixtures/harmony_reference.json` from the Python code |
| `scripts/screenshots.py` | Playwright smoke test (`--static` / `--base`) and README images (`--shots` -> `docs/img/`) |
| `.github/workflows/pages.yml` | Test, build and publish the static site on push to `main` |

## Python modules

### theory.py
Music theory data structures and chord/progression definitions.
- **Constants**: `A4_FREQUENCY`, `A4_MIDI_PITCH`, `SEMITONES_PER_OCTAVE`, `CHORD_TYPES` (name -> (intervals, colour)), `NOTE_NAMES`
- **Enums**: `ProgressionStyle` (JAZZ, CLASSICAL, BLUES, MODAL, IMPRESSIONIST)
- **Dataclasses**: `Note` (pitch, duration, velocity, frequency property), `Chord` (notes, name, color, duration in beats)
- **Functions**: `note_to_midi()`, `create_chord()`, `get_style_progression()`

### synthesis.py
Audio synthesis and MIDI/WAV export. Depends on `theory.py`.
- **Dataclass**: `SynthConfig` (sample_rate, tempo_bpm, num_overtones, fm_mod_freq, fm_mod_depth)
- **Constants**: `DEFAULT_SAMPLE_RATE`, `DEFAULT_TEMPO_BPM`, `NUM_OVERTONES`, ADSR ratios
- **Functions**: `create_audio_files()`, `create_enhanced_chord_waveform()`, `render_progression()` (beats -> seconds via
  tempo, clipped float samples), `to_int16()`, `build_midi_bytes()`
- **Internal**: `_create_adsr_envelope()`, `_write_midi_file()`, `_write_wav_file()`

### harmony_layout.py
Plot geometry (numpy only): `chord_starts`, `motion_trail`, `motion_labels`, `note_density`, `harmonic_complexity`,
`pattern_angles`. Used by `visualization.py` and ported to `web/static/layout_engine.js`.

### visualization.py
Matplotlib figures. Depends on `theory.py`, `harmony_layout.py`.
- **Functions**: `create_rich_visualization()` (main entry), `create_motion_visualization()`, `create_advanced_analysis()`
- **Internal**: `_create_style_analysis()` (polar panel in the bottom row)

## Web: `web/`

| File | Purpose | Key names |
|------|---------|-----------|
| `app.py` | FastAPI: static front end; GET `/api/info`, `/theory`, `/reference`; POST `/check`, `/figures` | `app`, `STATIC`, `STATIC_ENDPOINTS` |
| `reference.py` | Python reference values (theory tables, chords, layout, strided samples, WAV header, MIDI bytes) | `theory_data`, `progression_reference`, `reference_cases` |
| `static/index.html`, `style.css` (kit), `style_app.css`, `core.js` (kit), `main.js`, `static_api.js`, `icon.svg` | Shell, theme, router, static-site data layer | |
| `static/theory_engine.js` | Port of `theory.py` | `Theory`, `cssColor` |
| `static/synth_engine.js` | Port of `synthesis.py` waveform, ADSR, render, int16, WAV bytes | `chordWaveform`, `renderProgression`, `wavBytes` |
| `static/midi_engine.js` | Port of `build_midi_bytes` (MIDIUtil 1.2.1 output) | `midiBytes` |
| `static/layout_engine.js` | Port of `harmony_layout.py` | `motionTrail`, `noteDensity`, ... |
| `static/draw.js` | Canvas panels (motion, pattern, progression, density, complexity, waveform, keyboard) | `drawMotion`, ... |
| `static/player.js`, `state.js` | WebAudio playback (after a click); shared Studio state | `Player`, `state` |
| `static/reference.js` | Runs the JS engine on the reference cases and compares | `runAll`, `runCase`, `compare` |
| `static/home.js`, `studio.js`, `chords.js`, `verify.js`, `about.js` | Pages `#/`, `#/studio`, `#/chords`, `#/verify`, `#/about` | |
| `static/engine.test.mjs` | Node test of the JS port against `tests/fixtures/harmony_reference.json` | |

## Tests

| File | Coverage |
|------|----------|
| `test_theory.py` | Note, Chord, note_to_midi, create_chord, get_style_progression (20 tests) |
| `tests/test_synthesis.py` | WAV length follows the tempo; MIDI tempo event |
| `tests/test_visualization.py` | Style panel in the bottom row; complexity bars aligned with chord onsets |
| `tests/test_web.py` | Endpoints, static build, node tests, fixture current (rtol 1e-9), `/check`, input validation, `/figures` |

## Data flow

```
Python:  get_style_progression -> create_chord -> Chord[] -> synthesis (WAV, MIDI) + visualization (PNG via harmony_layout)
Web:     /api/theory (tables from theory.py) -> Theory (JS) -> layout_engine -> draw.js canvases
         synth_engine.renderProgression -> Player (WebAudio) / wavBytes;  midi_engine.midiBytes -> download
         scripts/build_static.py -> site/ (static/ + api/*.json) -> GitHub Pages
```

### _archive/
The original monolithic scripts (`music-visualizer.py`, `music-visualizer-2.py`) for reference.
