"""Python reference values for the browser engine, computed by the repo's own code.

`theory_data()` is the music-theory table the front end runs on (chord types, note names, style progressions, synthesis
defaults). `progression_reference()` runs theory.create_chord, harmony_layout and synthesis on one progression and keeps
what the JS port must reproduce: chords, plot geometry, strided waveform samples, int16 checksums, WAV header, MIDI bytes.
`reference_cases()` is the set written to tests/fixtures/harmony_reference.json by scripts/make_fixture.py.
"""
import io
from typing import Dict, List, Sequence, Tuple

import numpy as np
from scipy.io import wavfile

import harmony_layout as layout
import synthesis
from synthesis import SynthConfig, build_midi_bytes, render_progression, to_int16
from theory import (A4_FREQUENCY, A4_MIDI_PITCH, CHORD_TYPES, NOTE_NAMES, SEMITONES_PER_OCTAVE, ProgressionStyle,
                    create_chord, get_style_progression, note_to_midi)

WAVE_STRIDE = 4001          # keep every n-th sample of a full progression
ADSR_SIZES = [4, 10, 101, 1000, 4410]

Progression = Sequence[Tuple[str, str, float]]


def synth_defaults() -> Dict:
    c = SynthConfig()
    return {"sample_rate": c.sample_rate, "tempo_bpm": c.tempo_bpm, "num_overtones": c.num_overtones,
            "fm_mod_freq": c.fm_mod_freq, "fm_mod_depth": c.fm_mod_depth,
            "attack_ratio": synthesis.ATTACK_RATIO, "decay_ratio": synthesis.DECAY_RATIO,
            "sustain_level": synthesis.SUSTAIN_LEVEL, "release_ratio": synthesis.RELEASE_RATIO}


def theory_data() -> Dict:
    """Everything the front end needs from theory.py and synthesis.py, as JSON."""
    return {
        "a4_frequency": A4_FREQUENCY, "a4_midi_pitch": A4_MIDI_PITCH, "semitones_per_octave": SEMITONES_PER_OCTAVE,
        "note_names": NOTE_NAMES,
        "chord_types": {k: {"intervals": iv, "color": list(col)} for k, (iv, col) in CHORD_TYPES.items()},
        "styles": [{"name": s.value, "progression": [list(p) for p in get_style_progression(s)]}
                   for s in ProgressionStyle],
        "synth": synth_defaults(),
        "layout": {"motion_time_points": layout.MOTION_TIME_POINTS, "base_radius": layout.MOTION_BASE_RADIUS,
                   "radius_step": layout.MOTION_RADIUS_STEP, "alpha_scale": layout.MOTION_ALPHA_SCALE,
                   "label_radius": layout.MOTION_LABEL_RADIUS,
                   "density_samples_per_beat": layout.DENSITY_SAMPLES_PER_BEAT},
    }


def config_from(d: Dict) -> SynthConfig:
    base = SynthConfig()
    return SynthConfig(sample_rate=int(d.get("sample_rate", base.sample_rate)),
                       tempo_bpm=d.get("tempo_bpm", base.tempo_bpm),
                       num_overtones=int(d.get("num_overtones", base.num_overtones)),
                       fm_mod_freq=float(d.get("fm_mod_freq", base.fm_mod_freq)),
                       fm_mod_depth=float(d.get("fm_mod_depth", base.fm_mod_depth)))


def wav_bytes(samples16: np.ndarray, rate: int) -> bytes:
    buf = io.BytesIO()
    wavfile.write(buf, rate, samples16)
    return buf.getvalue()


def progression_reference(progression: Progression, config: Dict = None, stride: int = WAVE_STRIDE) -> Dict:
    """Run the Python pipeline on one progression and return the values the JS engine is compared with."""
    cfg = config_from(config or {})
    chords = [create_chord(r, t, float(d)) for r, t, d in progression]
    wave = render_progression(chords, cfg)
    pcm = to_int16(wave)
    wav = wav_bytes(pcm, cfg.sample_rate)
    x, dens = layout.note_density(chords)
    trail = layout.motion_trail(chords)
    return {
        "progression": [[r, t, float(d)] for r, t, d in progression],
        "config": {"sample_rate": cfg.sample_rate, "tempo_bpm": cfg.tempo_bpm, "num_overtones": cfg.num_overtones,
                   "fm_mod_freq": cfg.fm_mod_freq, "fm_mod_depth": cfg.fm_mod_depth},
        "chords": [{"name": c.name, "duration": c.duration, "color": list(c.color),
                    "pitches": [n.pitch for n in c.notes], "velocities": [n.velocity for n in c.notes],
                    "frequencies": [n.frequency for n in c.notes]} for c in chords],
        "layout": {"starts": [float(s) for s in layout.chord_starts(chords)],
                   "trail": [[p["angle"], p["radius"], p["alpha"], p["chord"]] for p in trail],
                   "labels": [list(lab) for lab in layout.motion_labels(chords)],
                   "density_x": x.tolist(), "density": dens,
                   "complexity": layout.harmonic_complexity(chords),
                   "pattern_angles": layout.pattern_angles(chords).tolist()},
        "wave": {"length": int(len(wave)), "stride": stride, "samples": wave[::stride].tolist(),
                 "pcm": pcm[::stride].tolist(), "pcm_sum": int(pcm.astype(np.int64).sum()),
                 "pcm_abs_sum": int(np.abs(pcm.astype(np.int64)).sum()),
                 "wav_header": wav[:44].hex(), "wav_size": len(wav)},
        "midi": build_midi_bytes(chords, cfg).hex(),
    }


def adsr_reference() -> Dict:
    return {str(n): synthesis._create_adsr_envelope(n).tolist() for n in ADSR_SIZES}


def chord_wave_reference() -> List[Dict]:
    """Single-chord waveforms (start of the chord) for a few chord types and configs."""
    out = []
    for root, ctype, seconds, cfg in [("C4", "maj9", 0.05, {}), ("F#3", "diminished7", 0.02, {"num_overtones": 0}),
                                      ("A4", "sus4", 0.03, {"num_overtones": 6, "fm_mod_freq": 9.0,
                                                            "fm_mod_depth": 0.4, "sample_rate": 22050})]:
        w = synthesis.create_enhanced_chord_waveform(create_chord(root, ctype, 1.0), seconds, config_from(cfg))
        out.append({"root": root, "type": ctype, "seconds": seconds, "config": cfg, "samples": w.tolist()})
    return out


def reference_cases() -> Dict:
    cases = [{"name": s.value, **progression_reference(get_style_progression(s))} for s in ProgressionStyle]
    custom = [("C4", "major7", 1.5), ("A3", "min9", 0.75), ("D#5", "augmented", 2.25), ("G2", "half_diminished", 1.0)]
    cases.append({"name": "custom (90 BPM, 5 overtones, 22.05 kHz)",
                  **progression_reference(custom, {"tempo_bpm": 90, "num_overtones": 5, "fm_mod_freq": 3.0,
                                                   "fm_mod_depth": 0.2, "sample_rate": 22050})})
    midi_cases = {
        "blues_60bpm": build_midi_bytes([create_chord(*p) for p in get_style_progression(ProgressionStyle.BLUES)],
                                        SynthConfig(tempo_bpm=60)).hex(),
        "odd_durations_137bpm": build_midi_bytes([create_chord("E4", "minor", 0.3333), create_chord("E4", "minor", 1.1),
                                                  create_chord("B3", "dominant7", 0.26)],
                                                 SynthConfig(tempo_bpm=137)).hex(),
    }
    return {"theory": theory_data(), "cases": cases, "adsr": adsr_reference(), "chord_waves": chord_wave_reference(), "midi": midi_cases,
            "note_to_midi": note_to_midi_reference()}


def note_to_midi_reference() -> Dict:
    """theory.note_to_midi on valid and invalid names (None = ValueError)."""
    out = {}
    for name in ["C0", "G9", "G#9", "B9", "C#4", "F#3", "A4", "G#2", "X4", "C", "CA", "Db4", "C10", "c4", ""]:
        try:
            out[name] = note_to_midi(name)
        except ValueError:
            out[name] = None
    return out
