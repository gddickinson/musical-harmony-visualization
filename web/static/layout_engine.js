// Port of harmony_layout.py: the geometry visualization.py plots (motion trail, labels, note density, complexity,
// pattern angles). `L` is theory.layout from /api/theory (constants of the Python module).
import { linspace } from './synth_engine.js';

export function chordStarts(chords) {
  const out = [];
  let t = 0;
  for (const c of chords) { out.push(t); t += c.duration; }
  return out;
}

const total = chords => chords.reduce((s, c) => s + c.duration, 0);

// motion_trail: [angle, radius, alpha, chordIndex] for each sounding note at n time samples
export function motionTrail(chords, L, n = L.motion_time_points) {
  const T = total(chords), pts = [];
  for (const t of linspace(0, T, n)) {
    let cur = 0;
    chords.forEach((c, k) => {
      if (cur <= t && t < cur + c.duration) {
        const angle = (t / T) * 2 * Math.PI;
        c.notes.forEach((_, i) => {
          const alpha = 1.0 - (t - cur) / c.duration;
          pts.push([angle, L.base_radius + i * L.radius_step, alpha * L.alpha_scale, k]);
        });
      }
      cur += c.duration;
    });
  }
  return pts;
}

// motion_labels: [angle, rotationDegrees, name]
export function motionLabels(chords) {
  const T = total(chords), out = [];
  let a = 0;
  for (const c of chords) {
    const angle = a + (c.duration / T * Math.PI);
    out.push([angle, angle * (180 / Math.PI) - 90, c.name]);
    a += (c.duration / T * 2 * Math.PI);
  }
  return out;
}

// note_density: x (beats) and note counts, density_samples_per_beat samples per beat of each chord
export function noteDensity(chords, L) {
  const ys = [];
  for (const c of chords) {
    const n = Math.trunc(c.duration * L.density_samples_per_beat);
    for (let i = 0; i < n; i++) ys.push(c.notes.length);
  }
  return { x: Array.from(linspace(0, total(chords), ys.length)), y: ys };
}

// harmonic_complexity: notes x distinct pitch classes
export const harmonicComplexity = chords =>
  chords.map(c => c.notes.length * new Set(c.notes.map(n => ((n.pitch % 12) + 12) % 12)).size);

export const patternAngles = chords => Array.from(linspace(0, 2 * Math.PI, chords.length + 1)).slice(0, -1);
