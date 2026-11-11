// node engine.test.mjs: the JS ports of theory.py, harmony_layout.py and synthesis.py (waveform, ADSR, PCM, WAV, MIDI)
// against tests/fixtures/harmony_reference.json, written by scripts/make_fixture.py from the Python code.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runAll } from './reference.js';

const ref = JSON.parse(readFileSync(new URL('../../tests/fixtures/harmony_reference.json', import.meta.url)));
const t0 = Date.now();
const res = runAll(ref.theory, ref);
for (const c of res.cases) {
  for (const r of c.rows) {
    console.log(`${r.bad.length ? 'FAIL' : 'ok  '} ${c.name}: ${r.label} (${r.n} values, max abs diff ${r.maxAbs.toExponential(1)})`);
    r.bad.slice(0, 5).forEach(m => console.log('     ' + m));
  }
}
for (const r of res.extras) {
  console.log(`${r.bad.length ? 'FAIL' : 'ok  '} ${r.label} (${r.n} values, max abs diff ${r.maxAbs.toExponential(1)})`);
  r.bad.slice(0, 5).forEach(m => console.log('     ' + m));
}
console.log(`(${((Date.now() - t0) / 1000).toFixed(1)} s)`);
assert.ok(res.ok, 'JS engine differs from the Python reference');
