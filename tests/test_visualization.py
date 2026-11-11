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
