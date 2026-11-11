"""
Plot geometry for the harmony visualizations (numpy only, no matplotlib).

visualization.py draws these values with matplotlib; the web front end
(web/static/layout_engine.js) ports the same functions and is tested against
them, so the browser plots show the same points as the PNG figures.
"""

from typing import Dict, List, Tuple

import numpy as np

from theory import Chord

MOTION_TIME_POINTS = 100
MOTION_BASE_RADIUS = 0.3
MOTION_RADIUS_STEP = 0.15
MOTION_ALPHA_SCALE = 0.3
MOTION_LABEL_RADIUS = 1.2
DENSITY_SAMPLES_PER_BEAT = 10


def chord_starts(chords: List[Chord]) -> List[float]:
    """Start time (in beats) of each chord."""
    starts, t = [], 0
    for chord in chords:
        starts.append(t)
        t += chord.duration
    return starts


def motion_trail(chords: List[Chord], n_points: int = MOTION_TIME_POINTS) -> List[Dict]:
    """Points of the circular motion trail: one per sounding note at each time sample.

    Returns:
        List of dicts with t, angle (radians), radius, alpha and chord index.
    """
    total_duration = sum(chord.duration for chord in chords)
    points = []
    for t in np.linspace(0, total_duration, n_points):
        current_time = 0
        for k, chord in enumerate(chords):
            if current_time <= t < current_time + chord.duration:
                angle = (t / total_duration) * 2 * np.pi
                for i, _note in enumerate(chord.notes):
                    radius = MOTION_BASE_RADIUS + i * MOTION_RADIUS_STEP
                    alpha = 1.0 - (t - current_time) / chord.duration
                    points.append({"t": float(t), "angle": float(angle), "radius": radius,
                                   "alpha": float(alpha * MOTION_ALPHA_SCALE), "chord": k})
            current_time += chord.duration
    return points


def motion_labels(chords: List[Chord]) -> List[Tuple[float, float, str]]:
    """(angle, rotation in degrees, name) of each chord label around the motion circle."""
    total_duration = sum(chord.duration for chord in chords)
    labels, current_angle = [], 0
    for chord in chords:
        angle = current_angle + (chord.duration / total_duration * np.pi)
        labels.append((float(angle), float(np.degrees(angle) - 90), chord.name))
        current_angle += (chord.duration / total_duration * 2 * np.pi)
    return labels


def note_density(chords: List[Chord]) -> Tuple[np.ndarray, List[int]]:
    """(x values in beats, number of notes) for the note-density plot."""
    total_duration = sum(chord.duration for chord in chords)
    note_times = []
    for chord in chords:
        note_times.extend([len(chord.notes)] * int(chord.duration * DENSITY_SAMPLES_PER_BEAT))
    return np.linspace(0, total_duration, len(note_times)), note_times


def harmonic_complexity(chords: List[Chord]) -> List[int]:
    """Per chord: number of notes x number of distinct pitch classes."""
    return [len(chord.notes) * len(set(note.pitch % 12 for note in chord.notes)) for chord in chords]


def pattern_angles(chords: List[Chord]) -> np.ndarray:
    """Evenly spaced angles (radians) of the chords on the style-pattern polar plot."""
    return np.linspace(0, 2 * np.pi, len(chords) + 1)[:-1]
