"""Unit tests for music theory module."""

import pytest
from theory import (
    Note, Chord, ProgressionStyle, CHORD_TYPES, NOTE_NAMES,
    note_to_midi, create_chord, get_style_progression,
    A4_FREQUENCY, A4_MIDI_PITCH,
)


class TestNote:
    """Tests for the Note dataclass."""

    def test_a4_frequency(self):
        """A4 (MIDI 69) should be 440 Hz."""
        note = Note(pitch=69, duration=1.0)
        assert abs(note.frequency - 440.0) < 0.01

    def test_c4_frequency(self):
        """C4 (MIDI 60) should be ~261.63 Hz."""
        note = Note(pitch=60, duration=1.0)
        assert abs(note.frequency - 261.63) < 0.1

    def test_octave_doubling(self):
        """An octave up should double the frequency."""
        low = Note(pitch=60, duration=1.0)
        high = Note(pitch=72, duration=1.0)
        assert abs(high.frequency / low.frequency - 2.0) < 0.001

    def test_default_velocity(self):
        note = Note(pitch=60, duration=1.0)
        assert note.velocity == 100


class TestNoteToMidi:
    """Tests for note_to_midi conversion."""

    def test_c4(self):
        assert note_to_midi('C4') == 60

    def test_a4(self):
        assert note_to_midi('A4') == 69

    def test_sharp_notes(self):
        assert note_to_midi('C#4') == 61
        assert note_to_midi('F#3') == 54

    def test_invalid_note_raises(self):
        with pytest.raises(ValueError):
            note_to_midi('X4')

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            note_to_midi('C')

    def test_invalid_octave_raises(self):
        with pytest.raises(ValueError):
            note_to_midi('CA')


class TestCreateChord:
    """Tests for chord construction."""

    def test_major_triad(self):
        chord = create_chord('C4', 'major', 2.0)
        pitches = [n.pitch for n in chord.notes]
        assert pitches == [60, 64, 67]

    def test_minor_triad(self):
        chord = create_chord('A4', 'minor', 1.0)
        pitches = [n.pitch for n in chord.notes]
        assert pitches == [69, 72, 76]

    def test_dominant7(self):
        chord = create_chord('G4', 'dominant7', 1.0)
        assert len(chord.notes) == 4

    def test_invalid_chord_type_raises(self):
        with pytest.raises(ValueError, match="Unknown chord type"):
            create_chord('C4', 'nonexistent', 1.0)

    def test_negative_duration_raises(self):
        with pytest.raises(ValueError, match="Duration must be positive"):
            create_chord('C4', 'major', -1.0)

    def test_chord_name(self):
        chord = create_chord('C4', 'major', 1.0)
        assert chord.name == 'C4major'

    def test_velocity_decreases_for_upper_notes(self):
        chord = create_chord('C4', 'maj9', 1.0)
        velocities = [n.velocity for n in chord.notes]
        assert velocities == sorted(velocities, reverse=True)


class TestGetStyleProgression:
    """Tests for style progression generation."""

    def test_all_styles_return_nonempty(self):
        for style in ProgressionStyle:
            prog = get_style_progression(style)
            assert len(prog) > 0, f"{style.value} returned empty progression"

    def test_progression_entries_are_valid(self):
        """All entries should be (root, chord_type, duration) with valid types."""
        for style in ProgressionStyle:
            for root, chord_type, duration in get_style_progression(style):
                assert chord_type in CHORD_TYPES, (
                    f"Invalid chord type '{chord_type}' in {style.value}"
                )
                assert duration > 0

    def test_blues_style_exists(self):
        """Blues style should return a progression."""
        prog = get_style_progression(ProgressionStyle.BLUES)
        assert len(prog) >= 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
