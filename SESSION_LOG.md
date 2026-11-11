# Session log

## 2026-11-11 — Web interface and static GitHub Pages site (branch `web-interface`)

Done
- `harmony_layout.py`: plot geometry factored out of `visualization.py` (numpy only); all 10 figures render
  byte-identical before/after. `synthesis.py`: `render_progression`, `to_int16`, `build_midi_bytes` factored out of the
  WAV/MIDI writers; WAV and MIDI for all 5 styles byte-identical before/after.
- Web app `web/` (FastAPI, port 8165) + static site that is the working program: JS ports of theory.py,
  harmony_layout.py, synthesis.py (waveform, ADSR, render, int16, WAV) and the MIDIUtil writer. Pages: Studio (presets,
  custom progressions, synth settings, five canvas panels, WebAudio playback after a click with playhead, WAV/MIDI
  download, matplotlib PNGs via the local server), Chords (12 types, keyboard, waveform, play), Verify, About.
- Agreement: `tests/fixtures/harmony_reference.json` (scripts/make_fixture.py): 6 progressions + extras, 24,357
  values; samples max abs diff 3.5e-13, frequencies 1.1e-13, geometry exact, int16 PCM/checksums/WAV header/MIDI exact.
  WAV and MIDI downloaded from the browser (modal preset) are byte-identical to `create_audio_files` output.
- README web section with screenshots; INTERFACE.md rewritten; CLAUDE.md references @INTERFACE.md; Pages workflow
  (runs all tests, not only test_web.py).

Bugs found and fixed (each in its own "Fix" commit, regression test failed first)
- Style-pattern polar panel was created with `plt.subplot(111, projection='polar')` and covered the whole
  advanced-analysis figure (`tests/test_visualization.py`).
- Harmonic-complexity bars were centred on each chord's onset (default `align='center'`), so they started half a
  chord early and overlapped (`tests/test_visualization.py`).
- WAV export used chord durations (beats) as seconds, i.e. always 60 BPM; `--tempo` changed only the MIDI and at the
  default 120 BPM the WAV was twice as long as the MIDI (`tests/test_synthesis.py`). WAV files are now half as long
  at 120 BPM.
- README usage imported a non-existent `harmony_visualizer` module; claimed 11th/13th chords, FM synthesis (it is
  5 Hz amplitude modulation), real-time animation; ROADMAP ticked a .gitignore item that was not done.

Open / for George
- The committed example outputs (`harmony_*.png/.wav/.mid`, ~18 MB) were made by the old code: the analysis PNGs show
  the overlapping polar panel and the WAVs run at 60 BPM. Regenerate (adds ~10 MB to history) or remove them?
- Very short chords crash the Python writers: < 1/960 beat -> MIDIUtil KeyError; < 4 samples -> ADSR broadcast
  error. The web UI limits durations to >= 0.25 beats; a minimum duration in `create_chord` is a design decision.
- `note_to_midi('B9')` returns 131 (> 127); `create_chord` catches it, `note_to_midi` alone does not.
