// Canvas versions of the visualization.py panels (motion circle, harmonic progression, note density, complexity,
// style pattern), plus a waveform overview and a keyboard. Geometry comes from layout_engine.js (port of
// harmony_layout.py); matplotlib conventions kept: polar angle 0 at the right, counter-clockwise.
import { cssColor } from './theory_engine.js';

const INK = '#e8f1ff', MUTE = '#94a3c6', GRID = 'rgba(148,163,198,.22)', BG = '#070914';
const FONT = 'ui-monospace,"SF Mono",Menlo,Consolas,monospace';

// Size the canvas backing store for the device pixel ratio; returns a context drawing in CSS-pixel units.
export function prep(canvas, w, h) {
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = BG; ctx.fillRect(0, 0, w, h);
  return ctx;
}

const polar = (cx, cy, scale) => (a, r) => [cx + r * scale * Math.cos(a), cy - r * scale * Math.sin(a)];

function polarGrid(ctx, cx, cy, scale, rings, label) {
  ctx.strokeStyle = GRID; ctx.lineWidth = 1; ctx.fillStyle = MUTE; ctx.font = `10px ${FONT}`;
  for (const r of rings) {
    ctx.beginPath(); ctx.arc(cx, cy, r * scale, 0, 2 * Math.PI); ctx.stroke();
    ctx.fillText(label(r), cx + r * scale * Math.cos(Math.PI / 8) + 3, cy - r * scale * Math.sin(Math.PI / 8));
  }
  const R = rings[rings.length - 1] * scale;
  for (let k = 0; k < 8; k++) {
    const a = k * Math.PI / 4;
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + R * Math.cos(a), cy - R * Math.sin(a)); ctx.stroke();
  }
}

// Motion circle: trail points (alpha fades through each chord), chord labels at radius 1.2, optional playhead (beats).
export function drawMotion(canvas, size, chords, trail, labels, L, beat = null, totalBeats = 1) {
  const ctx = prep(canvas, size, size);
  const cx = size / 2, cy = size / 2, scale = size * 0.34, P = polar(cx, cy, scale);
  polarGrid(ctx, cx, cy, scale, [0.2, 0.4, 0.6, 0.8, 1.0], r => r.toFixed(1));
  const cur = beat == null ? -1 : chordAt(chords, beat);
  const dot = Math.max(2.5, size / 95);
  for (const [a, r, alpha, k] of trail) {
    const [x, y] = P(a, r);
    const boost = k === cur ? 2.4 : 1;
    ctx.fillStyle = cssColor(chords[k].color, Math.min(1, alpha * boost + (k === cur ? 0.15 : 0.04)));
    ctx.beginPath(); ctx.arc(x, y, dot * (k === cur ? 1.25 : 1), 0, 2 * Math.PI); ctx.fill();
  }
  ctx.font = `${Math.max(9, Math.round(size / 52))}px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  labels.forEach(([a, rot, name], k) => {
    const [x, y] = P(a, L.label_radius);
    ctx.save(); ctx.translate(x, y); ctx.rotate(-rot * Math.PI / 180);
    ctx.fillStyle = k === cur ? '#fff' : INK; ctx.fillText(name, 0, 0); ctx.restore();
  });
  if (beat != null) {
    const a = beat / totalBeats * 2 * Math.PI, [x, y] = P(a, 1.08);
    ctx.strokeStyle = 'rgba(255,181,71,.9)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(x, y); ctx.stroke();
  }
}

export function chordAt(chords, beat) {
  let t = 0;
  for (let k = 0; k < chords.length; k++) { if (beat < t + chords[k].duration) return k; t += chords[k].duration; }
  return chords.length - 1;
}

// Axes frame with x ticks (beats) and optional y ticks; returns a mapper from data to pixels.
function axes(ctx, w, h, x0, x1, y0, y1, { yTicks = [], xLabel = 'beats' } = {}) {
  const m = { l: 34, r: 10, t: 10, b: 26 };
  const X = x => m.l + (x - x0) / (x1 - x0) * (w - m.l - m.r);
  const Y = y => h - m.b - (y - y0) / (y1 - y0) * (h - m.t - m.b);
  ctx.strokeStyle = GRID; ctx.fillStyle = MUTE; ctx.font = `10px ${FONT}`; ctx.lineWidth = 1;
  ctx.strokeRect(m.l, m.t, w - m.l - m.r, h - m.t - m.b);
  const step = niceStep((x1 - x0) / Math.max(2, Math.floor((w - m.l - m.r) / 60)));
  ctx.textAlign = 'center'; ctx.textBaseline = 'top';
  for (let x = Math.ceil(x0 / step) * step; x <= x1 + 1e-9; x += step) ctx.fillText(String(+x.toFixed(2)), X(x), h - m.b + 4);
  ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
  for (const y of yTicks) { ctx.fillText(String(y), m.l - 4, Y(y)); }
  ctx.textAlign = 'right'; ctx.textBaseline = 'bottom';
  ctx.fillText(xLabel, w - m.r, h - 1);
  return { X, Y, m };
}

function niceStep(raw) {
  const p = 10 ** Math.floor(Math.log10(raw)), f = raw / p;
  return (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * p;
}

// Harmonic progression: one coloured block per chord over its beats, with the chord name.
export function drawRhythm(canvas, w, h, chords, starts, beat = null) {
  const ctx = prep(canvas, w, h);
  const T = starts.length ? starts[starts.length - 1] + chords[chords.length - 1].duration : 1;
  const { X, Y } = axes(ctx, w, h, 0, T, 0, 1);
  const cur = beat == null ? -1 : chordAt(chords, beat);
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  chords.forEach((c, k) => {
    const x0 = X(starts[k]), x1 = X(starts[k] + c.duration);
    ctx.fillStyle = cssColor(c.color, k === cur ? 0.95 : 0.6); ctx.fillRect(x0, Y(1), x1 - x0, Y(0) - Y(1));
    ctx.strokeStyle = BG; ctx.strokeRect(x0, Y(1), x1 - x0, Y(0) - Y(1));
    ctx.save(); ctx.translate((x0 + x1) / 2, (Y(0) + Y(1)) / 2);
    const fs = Math.max(9, Math.min(13, (x1 - x0) / 6));
    ctx.font = `${fs}px ${FONT}`; ctx.fillStyle = '#05060c';
    if (ctx.measureText(c.name).width > x1 - x0 - 4) ctx.rotate(-Math.PI / 2);
    ctx.fillText(c.name, 0, 0); ctx.restore();
  });
  if (beat != null) { ctx.fillStyle = '#ffb547'; ctx.fillRect(X(beat) - 1, Y(1), 2, Y(0) - Y(1)); }
}

// Note density over time (line + fill), as visualization.py's ax2.
export function drawDensity(canvas, w, h, dens) {
  const ctx = prep(canvas, w, h);
  const ymax = Math.max(1, ...dens.y) + 1;
  const T = dens.x.length ? dens.x[dens.x.length - 1] : 1;
  const { X, Y } = axes(ctx, w, h, 0, T, 0, ymax, { yTicks: range(0, ymax) });
  ctx.beginPath(); ctx.moveTo(X(dens.x[0] || 0), Y(0));
  dens.x.forEach((x, i) => ctx.lineTo(X(x), Y(dens.y[i])));
  ctx.lineTo(X(T), Y(0)); ctx.closePath();
  ctx.fillStyle = 'rgba(61,224,208,.18)'; ctx.fill();
  ctx.beginPath(); dens.x.forEach((x, i) => (i ? ctx.lineTo : ctx.moveTo).call(ctx, X(x), Y(dens.y[i])));
  ctx.strokeStyle = '#3de0d0'; ctx.lineWidth = 1.5; ctx.stroke();
}

const range = (a, b) => Array.from({ length: b - a + 1 }, (_, i) => a + i);

// Harmonic complexity bars (notes x distinct pitch classes), aligned with the chord's beats.
export function drawComplexity(canvas, w, h, chords, starts, comp) {
  const ctx = prep(canvas, w, h);
  const T = starts[starts.length - 1] + chords[chords.length - 1].duration;
  const ymax = Math.max(...comp) * 1.1;
  const ticks = [0, Math.round(ymax / 2), Math.floor(ymax)];
  const { X, Y } = axes(ctx, w, h, 0, T, 0, ymax, { yTicks: ticks });
  chords.forEach((c, k) => {
    ctx.fillStyle = cssColor(c.color, 0.6);
    ctx.fillRect(X(starts[k]), Y(comp[k]), X(starts[k] + c.duration) - X(starts[k]), Y(0) - Y(comp[k]));
  });
}

// Style pattern: chords evenly around a circle at radius = number of notes, joined in order.
export function drawPattern(canvas, size, chords, angles) {
  const ctx = prep(canvas, size, size);
  const rmax = Math.max(...chords.map(c => c.notes.length)) + 1;
  const cx = size / 2, cy = size / 2, scale = size * 0.36 / rmax, P = polar(cx, cy, scale);
  polarGrid(ctx, cx, cy, scale, range(1, rmax), r => String(r));
  ctx.strokeStyle = 'rgba(150,150,150,.45)'; ctx.lineWidth = 1;
  chords.forEach((c, i) => {
    const j = (i + 1) % chords.length;
    const [x0, y0] = P(angles[i], c.notes.length), [x1, y1] = P(angles[j], chords[j].notes.length);
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
  });
  ctx.font = `${Math.max(9, Math.round(size / 50))}px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
  chords.forEach((c, i) => {
    const [x, y] = P(angles[i], c.notes.length);
    ctx.fillStyle = cssColor(c.color, 0.85); ctx.beginPath(); ctx.arc(x, y, Math.max(4, size / 60), 0, 2 * Math.PI); ctx.fill();
    const [lx, ly] = P(angles[i], c.notes.length + 0.5);
    ctx.fillStyle = INK; ctx.fillText(c.name, lx, ly);
  });
}

// Waveform overview: min/max of the samples in each pixel column; optional playhead (fraction 0..1).
export function drawWave(canvas, w, h, wave, frac = null, color = '#b98bff') {
  const ctx = prep(canvas, w, h);
  const mid = h / 2, n = wave.length, cols = Math.floor(w);
  ctx.strokeStyle = GRID; ctx.beginPath(); ctx.moveTo(0, mid); ctx.lineTo(w, mid); ctx.stroke();
  ctx.fillStyle = color;
  for (let c = 0; c < cols; c++) {
    const a = Math.floor(c / cols * n), b = Math.max(a + 1, Math.floor((c + 1) / cols * n));
    let lo = 1, hi = -1;
    for (let k = a; k < b && k < n; k++) { const v = wave[k]; if (v < lo) lo = v; if (v > hi) hi = v; }
    if (hi < lo) continue;
    ctx.fillRect(c, mid - hi * mid * 0.95, 1, Math.max(1, (hi - lo) * mid * 0.95));
  }
  if (frac != null) { ctx.fillStyle = '#ffb547'; ctx.fillRect(frac * w - 1, 0, 2, h); }
}

// Waveform detail: a line through every sample of a short window.
export function drawWaveLine(canvas, w, h, wave, color = '#3de0d0') {
  const ctx = prep(canvas, w, h);
  const mid = h / 2;
  ctx.strokeStyle = GRID; ctx.beginPath(); ctx.moveTo(0, mid); ctx.lineTo(w, mid); ctx.stroke();
  const peak = Math.max(1e-9, ...Array.from(wave, Math.abs));
  ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.beginPath();
  wave.forEach((v, i) => { const x = i / (wave.length - 1) * w, y = mid - v / peak * mid * 0.9; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); });
  ctx.stroke();
}

// Piano keyboard from MIDI lo..hi (inclusive, starting on a C), pitches in `on` drawn in `color`.
export function drawKeyboard(canvas, w, h, lo, hi, on, color, nameOf) {
  const ctx = prep(canvas, w, h);
  const black = p => [1, 3, 6, 8, 10].includes(((p % 12) + 12) % 12);
  const whites = []; for (let p = lo; p <= hi; p++) if (!black(p)) whites.push(p);
  const kw = w / whites.length, fill = cssColor(color, 1);
  ctx.font = `10px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
  whites.forEach((p, i) => {
    ctx.fillStyle = on.includes(p) ? fill : '#e9edf6'; ctx.fillRect(i * kw + 0.5, 0, kw - 1, h);
    if (p % 12 === 0) { ctx.fillStyle = '#334'; ctx.fillText(nameOf(p), i * kw + kw / 2, h - 3); }
  });
  for (let p = lo; p <= hi; p++) {
    if (!black(p)) continue;
    const i = whites.indexOf(p - 1);
    ctx.fillStyle = on.includes(p) ? fill : '#111522';
    ctx.fillRect((i + 1) * kw - kw * 0.32, 0, kw * 0.64, h * 0.6);
  }
}
