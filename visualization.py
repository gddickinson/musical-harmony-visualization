"""
Matplotlib-based harmony visualization.

Contains functions for motion trail, harmonic analysis,
and style-specific chord progression plots.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List

from theory import Chord, ProgressionStyle


def create_motion_visualization(
    chords: List[Chord],
    filename_base: str,
) -> None:
    """Create a circular visualization with motion trails.

    Args:
        chords: List of Chord objects.
        filename_base: Base filename for the output PNG.
    """
    total_duration = sum(chord.duration for chord in chords)
    fig = plt.figure(figsize=(15, 15))
    ax = plt.subplot(111, projection='polar')

    # Create motion trails
    time_points = np.linspace(0, total_duration, 100)
    for t in time_points:
        current_time = 0
        for chord in chords:
            if current_time <= t < current_time + chord.duration:
                angle = (t / total_duration) * 2 * np.pi
                for i, note in enumerate(chord.notes):
                    radius = 0.3 + i * 0.15
                    alpha = 1.0 - (t - current_time) / chord.duration
                    ax.scatter(angle, radius,
                               color=chord.color, alpha=alpha * 0.3, s=100)
            current_time += chord.duration

    # Add chord names and connection lines
    current_angle = 0
    for chord in chords:
        angle = current_angle + (chord.duration / total_duration * np.pi)
        ax.text(angle, 1.2, chord.name,
                rotation=np.degrees(angle) - 90,
                ha='center', va='center')
        current_angle += (chord.duration / total_duration * 2 * np.pi)

    ax.set_title('Harmonic Motion Visualization', pad=20)
    plt.savefig(f"{filename_base}_motion.png", dpi=300, bbox_inches='tight')
    plt.close()


def create_advanced_analysis(
    chords: List[Chord],
    filename_base: str,
    style: ProgressionStyle,
) -> None:
    """Create an enhanced analysis visualization with style-specific elements.

    Args:
        chords: List of Chord objects.
        filename_base: Base filename for the output PNG.
        style: The ProgressionStyle used.
    """
    total_duration = sum(chord.duration for chord in chords)

    fig = plt.figure(figsize=(20, 15))
    gs = plt.GridSpec(3, 2, figure=fig)

    # Harmonic rhythm visualization
    ax1 = fig.add_subplot(gs[0, :])
    current_time = 0
    for chord in chords:
        rect = plt.Rectangle((current_time, 0), chord.duration, 1,
                              facecolor=chord.color, alpha=0.6)
        ax1.add_patch(rect)
        ax1.text(current_time + chord.duration / 2, 0.5, chord.name,
                 ha='center', va='center')
        current_time += chord.duration

    ax1.set_xlim(0, total_duration)
    ax1.set_ylim(0, 1)
    ax1.set_title(f'Harmonic Progression ({style.value})')

    # Note density plot
    ax2 = fig.add_subplot(gs[1, 0])
    note_times = []
    for chord in chords:
        note_times.extend([len(chord.notes)] * int(chord.duration * 10))
    x_vals = np.linspace(0, total_duration, len(note_times))
    ax2.plot(x_vals, note_times, 'b-', alpha=0.6)
    ax2.fill_between(x_vals, note_times, alpha=0.2)
    ax2.set_title('Note Density Over Time')

    # Harmonic complexity
    ax3 = fig.add_subplot(gs[1, 1])
    complexity = [
        len(chord.notes) * len(set(note.pitch % 12 for note in chord.notes))
        for chord in chords
    ]
    current_time = 0
    for i, chord in enumerate(chords):
        ax3.bar(current_time, complexity[i],
                width=chord.duration, align='edge', color=chord.color, alpha=0.6)
        current_time += chord.duration
    ax3.set_title('Harmonic Complexity')

    # Style-specific analysis (polar panel in the bottom row)
    ax4 = fig.add_subplot(gs[2, :], projection='polar')
    _create_style_analysis(ax4, chords, style)

    plt.tight_layout()
    plt.savefig(f"{filename_base}_advanced_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()


def _create_style_analysis(
    ax,
    chords: List[Chord],
    style: ProgressionStyle,
) -> None:
    """Create style-specific analysis visualization on a polar subplot.

    Args:
        ax: Matplotlib polar axes to draw on.
        chords: List of Chord objects.
        style: The ProgressionStyle used.
    """
    angles = np.linspace(0, 2 * np.pi, len(chords) + 1)[:-1]

    for i, (chord, angle) in enumerate(zip(chords, angles)):
        ax.scatter(angle, len(chord.notes),
                   c=[chord.color], s=200, alpha=0.6)
        ax.text(angle, len(chord.notes) + 0.5, chord.name,
                ha='center', va='bottom')

    # Connect related chords
    for i in range(len(chords)):
        j = (i + 1) % len(chords)
        ax.plot([angles[i], angles[j]],
                [len(chords[i].notes), len(chords[j].notes)],
                'gray', alpha=0.3)

    ax.set_title(f'Harmonic Pattern Analysis - {style.value} style')


def create_rich_visualization(
    chords: List[Chord],
    filename_base: str = "harmony",
    style: ProgressionStyle = ProgressionStyle.CLASSICAL,
) -> None:
    """Create all visualizations for a chord progression.

    This is the main entry point that generates motion and analysis plots.
    Audio files are created separately via synthesis.create_audio_files().

    Args:
        chords: List of Chord objects.
        filename_base: Base filename for output files.
        style: The ProgressionStyle used.
    """
    create_motion_visualization(chords, filename_base)
    create_advanced_analysis(chords, filename_base, style)
