# Musical Harmony Visualization — Roadmap

## Current State
The project has two monolithic scripts (`music-visualizer.py`, `music-visualizer-2.py`) that combine music theory, audio synthesis, MIDI generation, and matplotlib visualization into single files. The code uses good Python patterns (dataclasses, enums, type hints) but everything lives in just two large files with no tests, no packaging, and generated output files committed alongside source code.

## Short-term Improvements
- [x] Split `music-visualizer-2.py` into focused modules: `theory.py` (Note, Chord, ProgressionStyle), `synthesis.py` (WAV/MIDI generation), `visualization.py` (matplotlib plotting), `main.py` (CLI entry point)
- [x] Add a `requirements.txt` or `pyproject.toml` with pinned dependencies (numpy, matplotlib, scipy, midiutil)
- [x] Add `.gitignore` to exclude generated `.wav`, `.mid`, and `.png` files from the repo
- [x] Add input validation for chord types, note ranges, and duration values in `create_advanced_chord()`
- [x] Add docstrings to all public methods in `EnhancedHarmonyVisualizer`
- [x] Add error handling around WAV file writing and MIDI generation

## Feature Enhancements
- [x] Add a CLI with argparse: `python -m harmony --style jazz --output-dir ./output`
- [ ] Support custom color palettes for visualizations beyond the hardcoded colorsys mapping
- [x] Add a "Blues" style progression (the enum defines it but check if progressions exist)
- [ ] Add real-time audio playback using `sounddevice` instead of only file export
- [ ] Generate animated visualizations (GIF/MP4) showing chord progression over time
- [ ] Add chord voicing options (open voicing, drop-2, close position)
- [x] Support tempo and time signature as user parameters

## Long-term Vision
- [ ] Build an interactive web UI (Streamlit or Gradio) for parameter tweaking and live preview
- [ ] Add MIDI input support to visualize externally played progressions
- [ ] Integrate with music21 library for deeper music theory analysis
- [ ] Support multi-instrument arrangements (bass, melody, comping)
- [ ] Package as a pip-installable library with a public API

## Technical Debt
- [x] Consolidate `music-visualizer.py` and `music-visualizer-2.py` into a single codebase — unclear which is canonical
- [x] Extract synthesis parameters (sample rate 44100, overtone count) into a config dataclass
- [x] Replace magic numbers in frequency calculations and envelope shaping with named constants
- [x] Add unit tests for chord construction, interval calculation, and note-to-frequency conversion
- [x] Add type hints to any remaining untyped functions
