"""
Audio synthesis and MIDI/WAV file generation.

Contains waveform creation with overtones, ADSR envelopes,
and file export for both MIDI and WAV formats.
"""

import io

import numpy as np
from typing import List
from dataclasses import dataclass
from scipy.io import wavfile
from midiutil import MIDIFile

from theory import Chord, Note


# Synthesis configuration constants
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_TEMPO_BPM = 120
NUM_OVERTONES = 3
FM_MODULATION_FREQ = 5.0  # Hz
FM_MODULATION_DEPTH = 0.1

# ADSR envelope ratios (fraction of total duration)
ATTACK_RATIO = 0.1
DECAY_RATIO = 0.2
SUSTAIN_LEVEL = 0.7
RELEASE_RATIO = 0.3


@dataclass
class SynthConfig:
    """Configuration for audio synthesis parameters."""
    sample_rate: int = DEFAULT_SAMPLE_RATE
    tempo_bpm: int = DEFAULT_TEMPO_BPM
    num_overtones: int = NUM_OVERTONES
    fm_mod_freq: float = FM_MODULATION_FREQ
    fm_mod_depth: float = FM_MODULATION_DEPTH


def create_enhanced_chord_waveform(
    chord: Chord,
    duration: float,
    config: SynthConfig = None,
) -> np.ndarray:
    """Create a rich waveform for a chord with overtones and effects.

    Args:
        chord: The Chord to synthesize.
        duration: Duration in seconds.
        config: Synthesis configuration. Uses defaults if None.

    Returns:
        Numpy array of audio samples, normalized to [-1, 1] range.
    """
    if config is None:
        config = SynthConfig()

    samples = int(config.sample_rate * duration)
    chord_wave = np.zeros(samples)
    t = np.linspace(0, duration, samples)

    for note in chord.notes:
        fundamental = note.frequency
        amplitude = note.velocity / 100.0

        # Add fundamental frequency
        wave = amplitude * np.sin(2 * np.pi * fundamental * t)

        # Add overtones with decreasing amplitude
        for i in range(1, config.num_overtones + 1):
            harmonic = fundamental * (i + 1)
            wave += (amplitude / (i + 1)) * np.sin(2 * np.pi * harmonic * t)

        # Add subtle frequency modulation for richness
        wave *= (1 + config.fm_mod_depth * np.sin(2 * np.pi * config.fm_mod_freq * t))

        # Apply ADSR envelope
        envelope = _create_adsr_envelope(samples)
        wave *= envelope
        chord_wave += wave

    # Normalize by number of notes to prevent clipping
    return chord_wave / (2 * len(chord.notes))


def _create_adsr_envelope(samples: int) -> np.ndarray:
    """Create an ADSR amplitude envelope.

    Args:
        samples: Total number of samples.

    Returns:
        Numpy array with the envelope shape.
    """
    attack = int(ATTACK_RATIO * samples)
    decay = int(DECAY_RATIO * samples)
    release = int(RELEASE_RATIO * samples)

    envelope = np.ones(samples)
    # Attack
    envelope[:attack] = np.linspace(0, 1, attack)
    # Decay
    envelope[attack:attack + decay] = np.linspace(1, SUSTAIN_LEVEL, decay)
    # Sustain
    envelope[attack + decay:-release] = SUSTAIN_LEVEL
    # Release
    envelope[-release:] = np.linspace(SUSTAIN_LEVEL, 0, release)

    return envelope


def create_audio_files(
    chords: List[Chord],
    filename_base: str,
    config: SynthConfig = None,
) -> None:
    """Create MIDI and WAV files for a chord progression.

    Args:
        chords: List of Chord objects to render.
        filename_base: Base filename (without extension) for output files.
        config: Synthesis configuration. Uses defaults if None.

    Raises:
        IOError: If files cannot be written.
    """
    if config is None:
        config = SynthConfig()

    _write_midi_file(chords, filename_base, config)
    _write_wav_file(chords, filename_base, config)


def build_midi_bytes(chords: List[Chord], config: SynthConfig = None) -> bytes:
    """Return the Standard MIDI File bytes for the chord progression (durations in beats)."""
    if config is None:
        config = SynthConfig()
    midi = MIDIFile(1)
    track = 0
    time = 0
    midi.addTempo(track, time, config.tempo_bpm)

    current_time = 0.0
    for chord in chords:
        for note in chord.notes:
            midi.addNote(track, 0, note.pitch, current_time,
                         chord.duration, note.velocity)
        current_time += chord.duration

    buf = io.BytesIO()
    midi.writeFile(buf)
    return buf.getvalue()


def render_progression(chords: List[Chord], config: SynthConfig = None) -> np.ndarray:
    """Render the chord progression to float samples clipped to [-1, 1].

    Chord durations are in beats; they are converted to seconds with the
    configured tempo, so the WAV and the MIDI file have the same timing.
    """
    if config is None:
        config = SynthConfig()
    seconds_per_beat = 60.0 / config.tempo_bpm
    total_duration = sum(chord.duration for chord in chords) * seconds_per_beat
    total_samples = int(config.sample_rate * total_duration)
    full_waveform = np.zeros(total_samples)

    current_sample = 0
    for chord in chords:
        seconds = chord.duration * seconds_per_beat
        chord_duration_samples = int(config.sample_rate * seconds)
        chord_wave = create_enhanced_chord_waveform(chord, seconds, config)
        end_sample = min(current_sample + len(chord_wave), total_samples)
        full_waveform[current_sample:end_sample] += chord_wave[:end_sample - current_sample]
        current_sample += chord_duration_samples

    return np.clip(full_waveform, -1, 1)


def to_int16(waveform: np.ndarray) -> np.ndarray:
    """Convert clipped float samples to 16-bit PCM as written to the WAV file."""
    return (waveform * 32767).astype(np.int16)


def _write_midi_file(
    chords: List[Chord],
    filename_base: str,
    config: SynthConfig,
) -> None:
    """Write a MIDI file for the chord progression."""
    data = build_midi_bytes(chords, config)
    try:
        with open(f"{filename_base}.mid", "wb") as f:
            f.write(data)
    except IOError as e:
        raise IOError(f"Failed to write MIDI file: {e}") from e


def _write_wav_file(
    chords: List[Chord],
    filename_base: str,
    config: SynthConfig,
) -> None:
    """Write a 16-bit mono WAV file for the chord progression."""
    full_waveform = render_progression(chords, config)

    try:
        wavfile.write(
            f"{filename_base}.wav",
            config.sample_rate,
            to_int16(full_waveform),
        )
    except IOError as e:
        raise IOError(f"Failed to write WAV file: {e}") from e
