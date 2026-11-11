"""Web interface for Musical Harmony Visualization.

Contents:
    app.py        FastAPI app: static front end + JSON API (/api/info, /theory, /reference; POST /check, /figures)
    reference.py  Python reference values (theory tables, chords, layout, waveform samples, WAV/MIDI bytes)
    static/       ES-module front end; *_engine.js are the JS ports of theory.py, harmony_layout.py, synthesis.py
"""
