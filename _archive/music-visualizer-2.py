import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from midiutil import MIDIFile
import colorsys
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import math
from scipy.io import wavfile
from scipy import signal
import random
from enum import Enum

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
        return 440 * (2 ** ((self.pitch - 69) / 12))

@dataclass
class Chord:
    notes: List[Note]
    name: str
    color: Tuple[float, float, float]
    duration: float = 1.0

class EnhancedHarmonyVisualizer:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.base_octave = 4
        self.setup_chord_types()

    def setup_chord_types(self):
        """Initialize extended chord types with colors"""
        self.chord_types = {
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
            'min9': ([0, 3, 7, 10, 14], (0.8, 0.3, 0.5))
        }

    def get_style_progression(self, style: ProgressionStyle) -> List[Tuple[str, str, float]]:
        """Generate a progression based on musical style"""
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
                ('C4', 'maj9', 4.0)
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
                ('G4', 'maj9', 4.0)
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
                ('D4', 'minor7', 4.0)
            ]
        else:  # Default to classical-style progression
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
                ('C4', 'major', 4.0)
            ]


    def create_advanced_chord(self, root: str, chord_type: str, duration: float) -> Chord:
        """Create a chord with extended voicings"""
        root_midi = self.note_to_midi(root)
        intervals, color = self.chord_types[chord_type]

        # Create notes with varying velocities for more dynamic sound
        notes = []
        for i, interval in enumerate(intervals):
            velocity = 100 - (i * 5)  # Gradually decrease velocity for upper notes
            notes.append(Note(root_midi + interval, duration, velocity))

        return Chord(notes, f"{root}{chord_type}", color, duration)

    def note_to_midi(self, note_name: str) -> int:
        """Convert note name to MIDI pitch"""
        octave = int(note_name[-1])
        note = note_name[:-1]
        pitch_class = self.note_names.index(note)
        return pitch_class + (octave + 1) * 12

    def create_rich_visualization(self, chords: List[Chord],
                                filename_base: str = "harmony",
                                style: ProgressionStyle = ProgressionStyle.CLASSICAL):
        """Create enhanced visualizations with style-specific elements"""
        # Create MIDI and audio files (previous implementation)
        self.create_audio_files(chords, filename_base)

        # Create new circular visualization with motion trails
        self.create_motion_visualization(chords, filename_base)

        # Create enhanced analysis visualization
        self.create_advanced_analysis(chords, filename_base, style)

    def create_motion_visualization(self, chords: List[Chord], filename_base: str):
        """Create an animated circular visualization with motion trails"""
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

        ax.set_title(f'Harmonic Motion Visualization', pad=20)
        plt.savefig(f"{filename_base}_motion.png", dpi=300, bbox_inches='tight')
        plt.close()

    def create_advanced_analysis(self, chords: List[Chord],
                               filename_base: str,
                               style: ProgressionStyle):
        """Create an enhanced analysis visualization with style-specific elements"""
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
            ax1.text(current_time + chord.duration/2, 0.5, chord.name,
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
        ax2.plot(np.linspace(0, total_duration, len(note_times)),
                note_times, 'b-', alpha=0.6)
        ax2.fill_between(np.linspace(0, total_duration, len(note_times)),
                        note_times, alpha=0.2)
        ax2.set_title('Note Density Over Time')

        # Harmonic complexity
        ax3 = fig.add_subplot(gs[1, 1])
        complexity = [len(chord.notes) * len(set(note.pitch % 12 for note in chord.notes))
                     for chord in chords]
        current_time = 0
        for i, chord in enumerate(chords):
            ax3.bar(current_time, complexity[i],
                   width=chord.duration, color=chord.color, alpha=0.6)
            current_time += chord.duration
        ax3.set_title('Harmonic Complexity')

        # Add style-specific analysis
        ax4 = fig.add_subplot(gs[2, :])
        self.create_style_analysis(ax4, chords, style)

        plt.tight_layout()
        plt.savefig(f"{filename_base}_advanced_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()

    def create_style_analysis(self, ax, chords: List[Chord], style: ProgressionStyle):
        """Create style-specific analysis visualization"""
        # Create a circular representation of the chord progression
        angles = np.linspace(0, 2*np.pi, len(chords) + 1)[:-1]
        ax = plt.subplot(111, projection='polar')

        # Plot chords as points on the circle
        for i, (chord, angle) in enumerate(zip(chords, angles)):
            ax.scatter(angle, len(chord.notes),
                      c=[chord.color], s=200, alpha=0.6)

            # Add chord name
            ax.text(angle, len(chord.notes) + 0.5, chord.name,
                   ha='center', va='bottom')

        # Connect related chords
        for i in range(len(chords)):
            j = (i + 1) % len(chords)
            ax.plot([angles[i], angles[j]],
                   [len(chords[i].notes), len(chords[j].notes)],
                   'gray', alpha=0.3)

        ax.set_title(f'Harmonic Pattern Analysis - {style.value} style')

    def create_audio_files(self, chords: List[Chord], filename_base: str):
        """Create MIDI and WAV files for the progression"""
        # MIDI file creation
        midi = MIDIFile(1)
        track = 0
        time = 0
        midi.addTempo(track, time, 120)

        # Add notes to MIDI file
        current_time = 0
        for chord in chords:
            for note in chord.notes:
                midi.addNote(track, 0, note.pitch, current_time,
                           chord.duration, note.velocity)
            current_time += chord.duration

        # Save MIDI file
        with open(f"{filename_base}.mid", "wb") as f:
            midi.writeFile(f)

        # Create WAV file with enhanced synthesis
        total_duration = sum(chord.duration for chord in chords)
        total_samples = int(self.sample_rate * total_duration)
        full_waveform = np.zeros(total_samples)

        current_sample = 0
        for chord in chords:
            chord_duration_samples = int(self.sample_rate * chord.duration)
            chord_wave = self.create_enhanced_chord_waveform(chord, chord.duration)
            full_waveform[current_sample:current_sample + len(chord_wave)] += chord_wave
            current_sample += chord_duration_samples

        # Normalize and save
        full_waveform = np.clip(full_waveform, -1, 1)
        wavfile.write(f"{filename_base}.wav", self.sample_rate,
                     (full_waveform * 32767).astype(np.int16))

    def create_enhanced_chord_waveform(self, chord: Chord, duration: float) -> np.ndarray:
        """Create a rich waveform for a chord with overtones and effects"""
        samples = int(self.sample_rate * duration)
        chord_wave = np.zeros(samples)
        t = np.linspace(0, duration, samples)

        for note in chord.notes:
            fundamental = note.frequency
            amplitude = note.velocity / 100.0

            # Add fundamental frequency
            wave = amplitude * np.sin(2 * np.pi * fundamental * t)

            # Add overtones with decreasing amplitude
            for i in range(1, 4):
                harmonic = fundamental * (i + 1)
                wave += (amplitude / (i + 1)) * np.sin(2 * np.pi * harmonic * t)

            # Add a subtle frequency modulation for richness
            mod_freq = 5.0  # 5 Hz modulation
            mod_depth = 0.1
            wave *= (1 + mod_depth * np.sin(2 * np.pi * mod_freq * t))

            # Apply ADSR envelope
            attack = int(0.1 * samples)
            decay = int(0.2 * samples)
            sustain = 0.7
            release = int(0.3 * samples)

            envelope = np.ones(samples)
            # Attack
            envelope[:attack] = np.linspace(0, 1, attack)
            # Decay
            envelope[attack:attack+decay] = np.linspace(1, sustain, decay)
            # Sustain (already set to sustain level)
            envelope[attack+decay:-release] = sustain
            # Release
            envelope[-release:] = np.linspace(sustain, 0, release)

            wave *= envelope
            chord_wave += wave

        return chord_wave / (2 * len(chord.notes))  # Normalize

if __name__ == "__main__":
    # Create visualizer
    visualizer = EnhancedHarmonyVisualizer()

    # Generate different style progressions
    styles = [
        ProgressionStyle.JAZZ,
        ProgressionStyle.IMPRESSIONIST,
        ProgressionStyle.MODAL,
        ProgressionStyle.CLASSICAL
    ]

    for style in styles:
        print(f"\nGenerating {style.value} progression...")

        # Get progression for this style
        progression_data = visualizer.get_style_progression(style)

        # Create chords
        chords = [
            visualizer.create_advanced_chord(root, chord_type, duration)
            for root, chord_type, duration in progression_data
        ]

        # Generate visualizations and audio
        output_base = f"harmony_{style.value}"
        visualizer.create_rich_visualization(chords, output_base, style)

        print(f"Generated files for {style.value}:")
        print(f"- {output_base}.mid (MIDI file)")
        print(f"- {output_base}.wav (Audio file)")
        print(f"- {output_base}_motion.png (Motion visualization)")
        print(f"- {output_base}_advanced_analysis.png (Advanced analysis)")
