# Musical Harmony Visualization - Interface Map

## Module Structure

### theory.py
Music theory data structures and chord/progression definitions.
- **Constants**: `A4_FREQUENCY`, `A4_MIDI_PITCH`, `SEMITONES_PER_OCTAVE`, `CHORD_TYPES`, `NOTE_NAMES`
- **Enums**: `ProgressionStyle` (JAZZ, CLASSICAL, BLUES, MODAL, IMPRESSIONIST)
- **Dataclasses**: `Note` (pitch, duration, velocity, frequency property), `Chord` (notes, name, color, duration)
- **Functions**: `note_to_midi()`, `create_chord()`, `get_style_progression()`

### synthesis.py
Audio synthesis and MIDI/WAV file generation.
- **Dataclass**: `SynthConfig` (sample_rate, tempo_bpm, num_overtones, fm_mod_freq, fm_mod_depth)
- **Constants**: `DEFAULT_SAMPLE_RATE`, `DEFAULT_TEMPO_BPM`, `NUM_OVERTONES`, ADSR envelope ratios
- **Functions**: `create_audio_files()`, `create_enhanced_chord_waveform()`
- **Internal**: `_create_adsr_envelope()`, `_write_midi_file()`, `_write_wav_file()`
- Depends on: `theory.py`

### visualization.py
Matplotlib-based harmony visualization.
- **Functions**: `create_rich_visualization()` (main entry), `create_motion_visualization()`, `create_advanced_analysis()`
- **Internal**: `_create_style_analysis()`
- Depends on: `theory.py`

### main.py
CLI entry point with argparse support.
- **Usage**: `python main.py [--style jazz|classical|blues|modal|impressionist] [--output-dir DIR] [--tempo BPM]`
- Depends on: `theory.py`, `synthesis.py`, `visualization.py`

### test_theory.py
Unit tests for `theory.py` (20 tests covering Note, Chord, note_to_midi, create_chord, get_style_progression).

### _archive/
Contains the original monolithic scripts (`music-visualizer.py`, `music-visualizer-2.py`) for reference.
