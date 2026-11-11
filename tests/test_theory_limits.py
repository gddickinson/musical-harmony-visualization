"""Regression tests: MIDI range in note_to_midi, minimum chord duration in create_chord, tiny waveforms."""
import pytest

from synthesis import SynthConfig, create_audio_files, create_enhanced_chord_waveform
from theory import MIN_CHORD_DURATION, create_chord, note_to_midi


@pytest.mark.parametrize("name", ["G#9", "A9", "B9"])
def test_note_above_midi_range_raises(name):
    with pytest.raises(ValueError, match="MIDI range"):
        note_to_midi(name)


def test_highest_and_lowest_notes():
    assert note_to_midi("G9") == 127
    assert note_to_midi("C0") == 12


@pytest.mark.parametrize("beats", [1e-6, 0.001, 1 / 961])
def test_too_short_chord_raises(beats):
    with pytest.raises(ValueError, match="at least"):
        create_chord("C4", "major", beats)


def test_shortest_chord_writes_files(tmp_path):
    """A chord of exactly the minimum duration exports to MIDI and WAV (even a few samples long)."""
    chords = [create_chord("C4", "major", MIN_CHORD_DURATION), create_chord("C4", "major", MIN_CHORD_DURATION)]
    create_audio_files(chords, str(tmp_path / "s"), SynthConfig(tempo_bpm=400, sample_rate=8000))
    assert (tmp_path / "s.mid").stat().st_size > 0 and (tmp_path / "s.wav").stat().st_size >= 44


@pytest.mark.parametrize("samples_seconds", [0.0, 1 / 44100, 3 / 44100])
def test_waveform_of_a_few_samples(samples_seconds):
    w = create_enhanced_chord_waveform(create_chord("C4", "major", 1.0), samples_seconds)
    assert len(w) == int(44100 * samples_seconds)
