"""Regression tests: MIDI range in note_to_midi."""
import pytest

from theory import note_to_midi


@pytest.mark.parametrize("name", ["G#9", "A9", "B9"])
def test_note_above_midi_range_raises(name):
    with pytest.raises(ValueError, match="MIDI range"):
        note_to_midi(name)


def test_highest_and_lowest_notes():
    assert note_to_midi("G9") == 127
    assert note_to_midi("C0") == 12
