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

@dataclass
class Note:
    pitch: int
    duration: float
    velocity: int = 100
    start_time: float = 0.0
    
    @property
    def frequency(self) -> float:
        """Calculate frequency for the given MIDI pitch"""
        return 440 * (2 ** ((self.pitch - 69) / 12))

@dataclass
class Chord:
    notes: List[Note]
    name: str
    color: Tuple[float, float, float]
    
class HarmonyVisualizer:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.chord_colors = {
            'major': (0.2, 0.7, 0.3),
            'minor': (0.7, 0.3, 0.2),
            'diminished': (0.5, 0.2, 0.7),
            'augmented': (0.3, 0.2, 0.8),
            'dominant7': (0.8, 0.6, 0.2)
        }
        
        # Musical constants
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.base_octave = 4
        
    def note_to_midi(self, note_name: str) -> int:
        """Convert note name to MIDI pitch"""
        octave = int(note_name[-1])
        note = note_name[:-1]
        pitch_class = self.note_names.index(note)
        return pitch_class + (octave + 1) * 12

    def create_chord(self, root: str, chord_type: str) -> Chord:
        """Create a chord from root note and type"""
        root_midi = self.note_to_midi(root)
        
        if chord_type == 'major':
            intervals = [0, 4, 7]  # Major triad
            color = self.chord_colors['major']
        elif chord_type == 'minor':
            intervals = [0, 3, 7]  # Minor triad
            color = self.chord_colors['minor']
        elif chord_type == 'diminished':
            intervals = [0, 3, 6]  # Diminished triad
            color = self.chord_colors['diminished']
        elif chord_type == 'augmented':
            intervals = [0, 4, 8]  # Augmented triad
            color = self.chord_colors['augmented']
        elif chord_type == 'dominant7':
            intervals = [0, 4, 7, 10]  # Dominant seventh
            color = self.chord_colors['dominant7']
        else:
            raise ValueError(f"Unknown chord type: {chord_type}")
        
        notes = [Note(root_midi + interval, 1.0) for interval in intervals]
        return Chord(notes, f"{root}{chord_type}", color)

    def generate_chord_progression(self) -> List[Chord]:
        """Generate an interesting chord progression"""
        progressions = [
            # ii-V-I in C major
            [('D4', 'minor'), ('G4', 'dominant7'), ('C4', 'major')],
            # I-vi-IV-V
            [('C4', 'major'), ('A4', 'minor'), ('F4', 'major'), ('G4', 'major')],
            # I-IV-V-IV
            [('C4', 'major'), ('F4', 'major'), ('G4', 'major'), ('F4', 'major')]
        ]
        
        chosen_prog = random.choice(progressions)
        return [self.create_chord(root, chord_type) for root, chord_type in chosen_prog]

    def create_waveform(self, frequency: float, duration: float, 
                       amplitude: float = 0.5) -> np.ndarray:
        """Create a waveform for a given frequency"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        # Combine sine and triangle waves for richer sound
        sine = amplitude * np.sin(2 * np.pi * frequency * t)
        triangle = amplitude * signal.sawtooth(2 * np.pi * frequency * t, 0.5)
        # Apply envelope
        envelope = np.exp(-3 * t / duration)
        return (0.7 * sine + 0.3 * triangle) * envelope

    def create_chord_waveform(self, chord: Chord, duration: float) -> np.ndarray:
        """Create a waveform for an entire chord"""
        chord_wave = np.zeros(int(self.sample_rate * duration))
        for note in chord.notes:
            wave = self.create_waveform(note.frequency, duration, 0.5 / len(chord.notes))
            chord_wave += wave
        return np.clip(chord_wave, -1, 1)

    def create_visualization(self, chords: List[Chord], 
                           filename_base: str = "harmony",
                           duration: float = 2.0):
        """Create various visualizations of the chord progression"""
        # Create MIDI file
        midi = MIDIFile(1)
        track = 0
        time = 0
        midi.addTempo(track, time, 120)
        
        # Add notes to MIDI file
        for chord in chords:
            for note in chord.notes:
                midi.addNote(track, 0, note.pitch, time, duration, note.velocity)
            time += duration
        
        # Save MIDI file
        with open(f"{filename_base}.mid", "wb") as f:
            midi.writeFile(f)
        
        # Create waveform visualization
        total_duration = len(chords) * duration
        total_samples = int(self.sample_rate * total_duration)
        full_waveform = np.zeros(total_samples)
        
        # Generate full waveform
        for i, chord in enumerate(chords):
            start = int(i * duration * self.sample_rate)
            chord_wave = self.create_chord_waveform(chord, duration)
            full_waveform[start:start + len(chord_wave)] += chord_wave
        
        # Save audio file
        wavfile.write(f"{filename_base}.wav", self.sample_rate, 
                     (full_waveform * 32767).astype(np.int16))
        
        # Create visualizations
        fig = plt.figure(figsize=(15, 10))
        
        # 1. Waveform plot
        ax1 = plt.subplot(311)
        times = np.linspace(0, total_duration, len(full_waveform))
        ax1.plot(times, full_waveform, 'b-', lw=0.5, alpha=0.7)
        ax1.set_title('Waveform')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Amplitude')
        
        # 2. Spectrogram
        ax2 = plt.subplot(312)
        f, t, Sxx = signal.spectrogram(full_waveform, self.sample_rate,
                                     nperseg=2048, noverlap=1024)
        ax2.pcolormesh(t, f[:500], Sxx[:500], shading='gouraud', cmap='viridis')
        ax2.set_title('Spectrogram')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Frequency (Hz)')
        
        # 3. Chord progression visualization
        ax3 = plt.subplot(313)
        for i, chord in enumerate(chords):
            # Create colored rectangle for each chord
            rect = plt.Rectangle((i * duration, 0), duration, 1,
                               facecolor=chord.color, alpha=0.6)
            ax3.add_patch(rect)
            # Add chord name
            ax3.text(i * duration + duration/2, 0.5, chord.name,
                    ha='center', va='center')
        
        ax3.set_xlim(0, total_duration)
        ax3.set_ylim(0, 1)
        ax3.set_title('Chord Progression')
        ax3.set_xlabel('Time (s)')
        ax3.set_yticks([])
        
        plt.tight_layout()
        plt.savefig(f"{filename_base}_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create circular chord visualization
        fig = plt.figure(figsize=(10, 10))
        ax = plt.subplot(111, projection='polar')
        
        for i, chord in enumerate(chords):
            angle = i * 2 * np.pi / len(chords)
            angles = np.linspace(angle, angle + 2 * np.pi / len(chords), 100)
            
            # Create circles for each note in the chord
            for j, note in enumerate(chord.notes):
                radius = 0.3 + j * 0.15
                ax.fill_between(angles, radius - 0.1, radius + 0.1,
                              color=chord.color, alpha=0.6)
                # Add note name
                mid_angle = angle + np.pi / len(chords)
                note_name = self.note_names[note.pitch % 12]
                ax.text(mid_angle, radius, note_name,
                       ha='center', va='center')
        
        ax.set_title('Circular Harmony Visualization')
        plt.savefig(f"{filename_base}_circular.png", dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    # Create visualizer
    visualizer = HarmonyVisualizer()
    
    # Generate chord progression
    progression = visualizer.generate_chord_progression()
    
    # Create visualizations and audio files
    visualizer.create_visualization(progression, "harmony_output")
    
    print("Generated files:")
    print("- harmony_output.mid (MIDI file)")
    print("- harmony_output.wav (Audio file)")
    print("- harmony_output_analysis.png (Waveform and spectrogram analysis)")
    print("- harmony_output_circular.png (Circular harmony visualization)")
