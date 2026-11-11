"""Regression tests for synthesis.py (WAV/MIDI export)."""
from scipy.io import wavfile

from synthesis import SynthConfig, create_audio_files
from theory import create_chord


def _wav_seconds(path):
    rate, data = wavfile.read(path)
    return len(data) / rate


def test_wav_follows_tempo(tmp_path):
    """Chord durations are in beats: at 120 BPM, 4 beats last 2 s in the WAV, as in the MIDI file."""
    chords = [create_chord("C4", "major", 2.0), create_chord("G4", "dominant7", 2.0)]
    for bpm, seconds in [(120, 2.0), (60, 4.0), (90, 4 * 60 / 90)]:
        base = tmp_path / f"t{bpm}"
        create_audio_files(chords, str(base), SynthConfig(tempo_bpm=bpm, sample_rate=8000))
        assert abs(_wav_seconds(f"{base}.wav") - seconds) < 1e-3, bpm


def test_midi_tempo_written(tmp_path):
    chords = [create_chord("C4", "major", 1.0)]
    base = tmp_path / "m"
    create_audio_files(chords, str(base), SynthConfig(tempo_bpm=90, sample_rate=8000))
    data = (tmp_path / "m.mid").read_bytes()
    us = int(60000000 / 90)
    assert bytes([0xFF, 0x51, 0x03]) + us.to_bytes(3, "big") in data
