"""
Matplotlib-based harmony visualization.

Contains functions for motion trail, harmonic analysis,
and style-specific chord progression plots.
"""

import matplotlib.pyplot as plt
from typing import List

from theory import Chord, ProgressionStyle
from harmony_layout import (
    chord_starts, harmonic_complexity, motion_labels, motion_trail, note_density, pattern_angles,
    MOTION_LABEL_RADIUS,
)


def create_motion_visualization(
    chords: List[Chord],
    filename_base: str,
) -> None:
    """Create a circular visualization with motion trails.

    Args:
        chords: List of Chord objects.
        filename_base: Base filename for the output PNG.
    """
    fig = plt.figure(figsize=(15, 15))
    ax = plt.subplot(111, projection='polar')

    # Create motion trails
    for p in motion_trail(chords):
        ax.scatter(p["angle"], p["radius"],
                   color=chords[p["chord"]].color, alpha=p["alpha"], s=100)

    # Add chord names
    for angle, rotation, name in motion_labels(chords):
        ax.text(angle, MOTION_LABEL_RADIUS, name,
                rotation=rotation, ha='center', va='center')

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
    x_vals, note_times = note_density(chords)
    ax2.plot(x_vals, note_times, 'b-', alpha=0.6)
    ax2.fill_between(x_vals, note_times, alpha=0.2)
    ax2.set_title('Note Density Over Time')

    # Harmonic complexity
    ax3 = fig.add_subplot(gs[1, 1])
    complexity = harmonic_complexity(chords)
    for i, (chord, start) in enumerate(zip(chords, chord_starts(chords))):
        ax3.bar(start, complexity[i],
                width=chord.duration, align='edge', color=chord.color, alpha=0.6)
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
    angles = pattern_angles(chords)

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
