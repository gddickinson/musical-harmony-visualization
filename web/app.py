"""FastAPI web app for Musical Harmony Visualization: serves the front end in static/ and the JSON API under /api.

Run with `python run_web.py` (http://127.0.0.1:8165, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below. The two POST
routes (check a progression against Python, render the matplotlib figures) need this server.
"""
import base64
import json
import tempfile
from pathlib import Path
from typing import List, Tuple

import matplotlib

matplotlib.use("Agg")

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from theory import CHORD_TYPES, NOTE_NAMES, ProgressionStyle, create_chord  # noqa: E402
from web.reference import progression_reference, theory_data  # noqa: E402

STATIC = Path(__file__).resolve().parent / "static"
ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "harmony_reference.json"
MAX_CHORDS = 64
MAX_SECONDS = 180.0

SUMMARY = ("Generates chord progressions in five styles, visualizes them as harmonic-motion circles and analysis "
           "panels, and synthesizes them to WAV (additive overtones, ADSR envelope, slow modulation) and MIDI.")

app = FastAPI(title="Musical Harmony Visualization")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class Job(BaseModel):
    progression: List[Tuple[str, str, float]] = Field(..., min_length=1)
    config: dict = {}
    style: str = "classical"


def _chords(job: Job):
    if len(job.progression) > MAX_CHORDS:
        raise HTTPException(400, f"at most {MAX_CHORDS} chords")
    try:
        chords = [create_chord(r, t, float(d)) for r, t, d in job.progression]
    except ValueError as e:
        raise HTTPException(400, str(e))
    tempo = float(job.config.get("tempo_bpm", 120))
    if not 20 <= tempo <= 400:
        raise HTTPException(400, "tempo must be 20-400 BPM")
    if sum(c.duration for c in chords) * 60 / tempo > MAX_SECONDS:
        raise HTTPException(400, f"progression longer than {MAX_SECONDS:.0f} s")
    return chords


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/info")
def info():
    """Project summary and counts for the home page."""
    t = theory_data()
    return {"title": "Musical Harmony Visualization", "summary": SUMMARY,
            "styles": [s["name"] for s in t["styles"]], "chord_types": list(CHORD_TYPES),
            "note_names": NOTE_NAMES, "preset_chords": sum(len(s["progression"]) for s in t["styles"]),
            "sample_rate": t["synth"]["sample_rate"], "num_overtones": t["synth"]["num_overtones"],
            "tempo_bpm": t["synth"]["tempo_bpm"]}


@app.get("/api/theory")
def theory():
    """Chord types, note names, style progressions, synthesis and layout constants (from the Python modules)."""
    return theory_data()


@app.get("/api/reference")
def reference():
    """Python reference values the browser engine is checked against (tests/fixtures/harmony_reference.json)."""
    return json.loads(FIXTURE.read_text())


@app.post("/api/check")
def check(job: Job):
    """Run the Python pipeline on the posted progression (for the Verify page's own-progression check)."""
    _chords(job)
    return progression_reference(job.progression, job.config)


@app.post("/api/figures")
def figures(job: Job):
    """Render the real matplotlib figures (visualization.py) for the posted progression, as base64 PNGs."""
    from visualization import create_rich_visualization
    chords = _chords(job)
    try:
        style = ProgressionStyle(job.style)
    except ValueError:
        style = ProgressionStyle.CLASSICAL
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "harmony"
        create_rich_visualization(chords, str(base), style)
        out = {}
        for kind in ("motion", "advanced_analysis"):
            png = Path(f"{base}_{kind}.png").read_bytes()
            out[kind] = base64.b64encode(png).decode()
    return out


# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = ["/info", "/theory", "/reference"]
