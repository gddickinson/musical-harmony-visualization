"""
Music theory data structures and chord/progression definitions.

Contains Note, Chord dataclasses, ProgressionStyle enum, and chord type definitions.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum


# Named constants for synthesis and music theory
A4_FREQUENCY = 440.0
A4_MIDI_PITCH = 69
SEMITONES_PER_OCTAVE = 12


class ProgressionStyle(Enum):
    JAZZ = "jazz"
    CLASSICAL = "classical"
    BLUES = "blues"
    MODAL = "modal"
    IMPRESSIONIST = "impressionist"


@dataclass
class Note:
    pitch: int
    duration: float
    velocity: int = 100
    start_time: float = 0.0

    @property
    def frequency(self) -> float:
        """Calculate frequency for the given MIDI pitch using equal temperament."""
        return A4_FREQUENCY * (2 ** ((self.pitch - A4_MIDI_PITCH) / SEMITONES_PER_OCTAVE))


@dataclass
class Chord:
    notes: List[Note]
    name: str
    color: Tuple[float, float, float]
    duration: float = 1.0


# Extended chord types: maps chord name -> (intervals, display_color)
CHORD_TYPES: Dict[str, Tuple[List[int], Tuple[float, float, float]]] = {
    'major': ([0, 4, 7], (0.2, 0.7, 0.3)),
    'minor': ([0, 3, 7], (0.7, 0.3, 0.2)),
    'diminished': ([0, 3, 6], (0.5, 0.2, 0.7)),
    'augmented': ([0, 4, 8], (0.3, 0.2, 0.8)),
    'dominant7': ([0, 4, 7, 10], (0.8, 0.6, 0.2)),
    'major7': ([0, 4, 7, 11], (0.2, 0.8, 0.6)),
    'minor7': ([0, 3, 7, 10], (0.6, 0.2, 0.4)),
    'half_diminished': ([0, 3, 6, 10], (0.4, 0.3, 0.7)),
    'diminished7': ([0, 3, 6, 9], (0.7, 0.2, 0.7)),
    'sus4': ([0, 5, 7], (0.5, 0.5, 0.7)),
    'maj9': ([0, 4, 7, 11, 14], (0.3, 0.8, 0.8)),
    'min9': ([0, 3, 7, 10, 14], (0.8, 0.3, 0.5)),
}

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def note_to_midi(note_name: str) -> int:
    """Convert note name (e.g. 'C4') to MIDI pitch number.

    Args:
        note_name: Note name with octave, e.g. 'C4', 'F#3'.

    Returns:
        MIDI pitch number (0-127).

    Raises:
        ValueError: If the note name is invalid.
    """
    if len(note_name) < 2:
        raise ValueError(f"Invalid note name: {note_name}")

    octave_str = note_name[-1]
    note = note_name[:-1]

    if not octave_str.isdigit():
        raise ValueError(f"Invalid octave in note name: {note_name}")

    if note not in NOTE_NAMES:
        raise ValueError(f"Unknown note: {note} (valid: {NOTE_NAMES})")

    octave = int(octave_str)
    pitch_class = NOTE_NAMES.index(note)
    return pitch_class + (octave + 1) * SEMITONES_PER_OCTAVE


def create_chord(root: str, chord_type: str, duration: float) -> Chord:
    """Create a chord with extended voicings.

    Args:
        root: Root note name, e.g. 'C4'.
        chord_type: Chord type key from CHORD_TYPES.
        duration: Duration in beats.

    Returns:
        A Chord instance.

    Raises:
        ValueError: If chord_type is not recognized, or root is invalid.
    """
    if chord_type not in CHORD_TYPES:
        raise ValueError(
            f"Unknown chord type: {chord_type}. "
            f"Valid types: {list(CHORD_TYPES.keys())}"
        )

    root_midi = note_to_midi(root)
    intervals, color = CHORD_TYPES[chord_type]

    # Validate MIDI range
    max_pitch = root_midi + max(intervals)
    if max_pitch > 127 or root_midi < 0:
        raise ValueError(
            f"Chord pitches out of valid MIDI range (0-127): root={root_midi}, max={max_pitch}"
        )

    if duration <= 0:
        raise ValueError(f"Duration must be positive, got {duration}")

    notes = []
    for i, interval in enumerate(intervals):
        velocity = max(1, 100 - (i * 5))  # Gradually decrease velocity for upper notes
        notes.append(Note(root_midi + interval, duration, velocity))

    return Chord(notes, f"{root}{chord_type}", color, duration)


def get_style_progression(style: ProgressionStyle) -> List[Tuple[str, str, float]]:
    """Generate a progression based on musical style.

    Args:
        style: The ProgressionStyle to generate.

    Returns:
        List of (root_note, chord_type, duration) tuples.
    """
    if style == ProgressionStyle.JAZZ:
        return [
            ('C4', 'maj9', 2.0),
            ('A4', 'minor7', 2.0),
            ('D4', 'minor7', 2.0),
            ('G4', 'dominant7', 2.0),
            ('F4', 'major7', 2.0),
            ('A#4', 'dominant7', 2.0),
            ('E4', 'half_diminished', 2.0),
            ('A4', 'dominant7', 2.0),
            ('D4', 'minor7', 2.0),
            ('G4', 'dominant7', 2.0),
            ('C4', 'maj9', 4.0),
        ]
    elif style == ProgressionStyle.IMPRESSIONIST:
        return [
            ('C4', 'major7', 3.0),
            ('E4', 'minor7', 3.0),
            ('D#4', 'major7', 3.0),
            ('G#4', 'maj9', 3.0),
            ('G4', 'sus4', 2.0),
            ('F#4', 'diminished7', 2.0),
            ('B4', 'minor7', 2.0),
            ('E4', 'dominant7', 2.0),
            ('A4', 'minor7', 3.0),
            ('D4', 'dominant7', 3.0),
            ('G4', 'maj9', 4.0),
        ]
    elif style == ProgressionStyle.MODAL:
        return [
            ('D4', 'minor7', 4.0),
            ('C4', 'major7', 4.0),
            ('A#4', 'maj9', 4.0),
            ('A4', 'minor7', 4.0),
            ('G4', 'sus4', 4.0),
            ('F4', 'major7', 4.0),
            ('E4', 'half_diminished', 4.0),
            ('D4', 'minor7', 4.0),
        ]
    elif style == ProgressionStyle.BLUES:
        return [
            ('C4', 'dominant7', 2.0),
            ('C4', 'dominant7', 2.0),
            ('C4', 'dominant7', 2.0),
            ('C4', 'dominant7', 2.0),
            ('F4', 'dominant7', 2.0),
            ('F4', 'dominant7', 2.0),
            ('C4', 'dominant7', 2.0),
            ('C4', 'dominant7', 2.0),
            ('G4', 'dominant7', 2.0),
            ('F4', 'dominant7', 2.0),
            ('C4', 'dominant7', 2.0),
            ('G4', 'dominant7', 2.0),
        ]
    else:
        # Default to classical-style progression
        return [
            ('C4', 'major', 2.0),
            ('G4', 'dominant7', 2.0),
            ('A4', 'minor7', 2.0),
            ('F4', 'major7', 2.0),
            ('D4', 'minor7', 2.0),
            ('G4', 'dominant7', 2.0),
            ('E4', 'minor7', 2.0),
            ('A4', 'dominant7', 2.0),
            ('F4', 'major7', 2.0),
            ('G4', 'dominant7', 2.0),
            ('C4', 'major', 4.0),
        ]
