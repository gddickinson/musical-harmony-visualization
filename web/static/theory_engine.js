// Port of theory.py: note names -> MIDI, equal-temperament frequency, chord construction. The tables (chord types,
// note names, style progressions) come from /api/theory, which is exported from the Python module itself.

export class Theory {
  constructor(data) {
    this.data = data;
    this.noteNames = data.note_names;
    this.chordTypes = data.chord_types;            // name -> { intervals, color }
    this.styles = data.styles;                     // [{ name, progression: [[root, type, beats], ...] }]
    this.synth = data.synth;
    this.layout = data.layout;
  }

  // Note.frequency: A4 * 2 ** ((pitch - 69) / 12)
  frequency(pitch) {
    const d = this.data;
    return d.a4_frequency * (2 ** ((pitch - d.a4_midi_pitch) / d.semitones_per_octave));
  }

  // note_to_midi('C4') -> 60. Single-digit octave, sharps only (as in Python); throws on invalid names.
  noteToMidi(name) {
    if (typeof name !== 'string' || name.length < 2) throw new Error(`Invalid note name: ${name}`);
    const oct = name.slice(-1), note = name.slice(0, -1);
    if (!/^[0-9]$/.test(oct)) throw new Error(`Invalid octave in note name: ${name}`);
    const pc = this.noteNames.indexOf(note);
    if (pc < 0) throw new Error(`Unknown note: ${note}`);
    const pitch = pc + (Number(oct) + 1) * this.data.semitones_per_octave;
    if (pitch > 127) throw new Error(`Note ${name} (pitch ${pitch}) is outside the MIDI range 0-127`);
    return pitch;
  }

  midiToName(pitch) {
    return this.noteNames[((pitch % 12) + 12) % 12] + (Math.floor(pitch / 12) - 1);
  }

  // create_chord(root, type, beats): notes with velocity 100 - 5 i (min 1); same validation as Python.
  createChord(root, type, duration) {
    const ct = this.chordTypes[type];
    if (!ct) throw new Error(`Unknown chord type: ${type}`);
    const rootMidi = this.noteToMidi(root);
    const maxPitch = rootMidi + Math.max(...ct.intervals);
    if (maxPitch > 127 || rootMidi < 0) throw new Error(`Chord pitches out of valid MIDI range (0-127): root=${rootMidi}, max=${maxPitch}`);
    if (!(duration > 0)) throw new Error(`Duration must be positive, got ${duration}`);
    if (duration < 1 / 960) throw new Error(`Duration must be at least 1/960 beat (one MIDI tick), got ${duration}`);
    const notes = ct.intervals.map((iv, i) => {
      const pitch = rootMidi + iv;
      return { pitch, duration, velocity: Math.max(1, 100 - i * 5), frequency: this.frequency(pitch) };
    });
    return { notes, name: `${root}${type}`, root, type, color: ct.color, duration };
  }

  progression(style) {
    const s = this.styles.find(x => x.name === style);
    if (!s) throw new Error(`Unknown style: ${style}`);
    return s.progression.map(p => [...p]);
  }

  chords(progression) {
    return progression.map(([r, t, d]) => this.createChord(r, t, d));
  }
}

export const cssColor = (rgb, alpha = 1) =>
  `rgba(${Math.round(rgb[0] * 255)},${Math.round(rgb[1] * 255)},${Math.round(rgb[2] * 255)},${alpha})`;
