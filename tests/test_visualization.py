"""Regression tests for visualization.py (matplotlib, Agg backend)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import visualization  # noqa: E402
from theory import ProgressionStyle, create_chord, get_style_progression  # noqa: E402


def _chords(style):
    return [create_chord(r, t, d) for r, t, d in get_style_progression(style)]


def test_style_panel_stays_in_bottom_row(tmp_path, monkeypatch):
    """The style-pattern polar plot must occupy the bottom row of the analysis figure, not cover the whole figure."""
    figs = []
    monkeypatch.setattr(visualization.plt, "close", lambda *a: figs.append(plt.gcf()))
    visualization.create_advanced_analysis(_chords(ProgressionStyle.JAZZ), str(tmp_path / "x"), ProgressionStyle.JAZZ)
    fig = figs[0]
    polar = [ax for ax in fig.axes if ax.name == "polar"]
    assert len(fig.axes) == 4 and len(polar) == 1
    box = polar[0].get_position()
    assert box.y1 < 0.4, f"polar panel spans the figure: {box}"
    rhythm = [ax for ax in fig.axes if ax.get_title().startswith("Harmonic Progression")]
    assert len(rhythm) == 1 and not rhythm[0].get_position().overlaps(box)
    plt.close("all")


def test_complexity_bars_start_at_chord_onsets(tmp_path, monkeypatch):
    """Each complexity bar spans its chord's time range [start, start + duration), like the rhythm panel."""
    figs = []
    monkeypatch.setattr(visualization.plt, "close", lambda *a: figs.append(plt.gcf()))
    chords = _chords(ProgressionStyle.JAZZ)
    visualization.create_advanced_analysis(chords, str(tmp_path / "x"), ProgressionStyle.JAZZ)
    ax = [a for a in figs[0].axes if a.get_title() == "Harmonic Complexity"][0]
    starts, t = [], 0.0
    for c in chords:
        starts.append(t)
        t += c.duration
    got = [(p.get_x(), p.get_width()) for p in ax.patches]
    assert got == [(s, c.duration) for s, c in zip(starts, chords)]
    plt.close("all")
