// Verify: runs the JS engine on the Python reference cases (tests/fixtures/harmony_reference.json) and compares every
// value. With the local server, the current Studio progression is also run through Python (POST /api/check).
import { route, api, app, esc, list, isStatic, needsServer, $ } from './core.js';
import { Theory } from './theory_engine.js';
import { runAll, runCase } from './reference.js';
import { defaultConfig } from './synth_engine.js';
import { state } from './state.js';

const rowHtml = (r, name = '') => `<tr><td>${esc(name)}</td><td>${esc(r.label)}</td><td class="mono">${r.n.toLocaleString('en')}</td>
  <td class="mono">${r.maxAbs.toExponential(1)}</td><td class="${r.bad.length ? 'err' : 'ok'}">${r.bad.length ? 'differs' : 'match'}</td></tr>
  ${r.bad.length ? `<tr><td></td><td colspan="4" class="err small mono">${list(r.bad.slice(0, 5), esc, '<br>')}</td></tr>` : ''}`;
const HEAD = '<tr><th>Case</th><th>Check</th><th>Values</th><th>Max abs diff</th><th>Result</th></tr>';

route('verify', async () => {
  app().innerHTML = `
  <h1 class="glow">Verify</h1>
  <p class="lead">The site runs JavaScript ports of <code>theory.py</code>, <code>harmony_layout.py</code> (the geometry
  behind <code>visualization.py</code>) and <code>synthesis.py</code>. Here they are run on the inputs the Python code was
  run on (<code>scripts/make_fixture.py</code>) and every value is compared: tolerance 1e-9 relative (1e-12 for samples),
  16-bit samples within 1, WAV header and MIDI file byte for byte.</p>
  <p id="vstat" class="status" role="status">Loading the Python reference values...</p>
  <div class="scroll"><table id="vtab"></table></div>
  <h2>Your Studio progression</h2>
  <div id="own"></div>`;
  const [data, ref] = await Promise.all([api('/theory'), api('/reference')]);
  $('#vstat').textContent = 'Running the JS engine on 6 progressions (about a second)...';
  await new Promise(r => setTimeout(r, 30));
  const t0 = performance.now();
  const res = runAll(data, ref);
  const n = [...res.cases.flatMap(c => c.rows), ...res.extras].reduce((s, r) => s + r.n, 0);
  $('#vstat').innerHTML = `<span class="${res.ok ? 'ok' : 'err'}">${res.ok ? 'All checks match' : 'Some checks differ'}</span>
    · ${n.toLocaleString('en')} values · ${((performance.now() - t0) / 1000).toFixed(1)} s in your browser`;
  $('#vtab').innerHTML = HEAD + list(res.cases, c => list(c.rows, (r, i) => rowHtml(r, i ? '' : c.name))) +
    list(res.extras, (r, i) => rowHtml(r, i ? '' : 'extras'));
  own(data);
});

function own(data) {
  const host = $('#own');
  if (isStatic()) { host.innerHTML = needsServer('Checking your own progression against Python'); return; }
  const theory = new Theory(data);
  const progression = state.progression || theory.progression(state.style === 'custom' ? 'jazz' : state.style);
  const config = state.config || defaultConfig(theory.synth);
  host.innerHTML = `<p>${progression.length} chords at ${config.tempo_bpm} BPM, ${config.sample_rate} Hz, ${config.num_overtones} overtones
    (edit them in the <a href="#/studio">Studio</a>).</p><button id="chk">Check with Python</button><div class="scroll"><table id="otab"></table></div>`;
  $('#chk').onclick = async () => {
    $('#chk').disabled = true;
    try {
      const ref = await api('/check', { body: { progression, config } });
      const r = runCase(theory, { name: 'studio', ...ref });
      $('#otab').innerHTML = HEAD + list(r.rows, (x, i) => rowHtml(x, i ? '' : 'studio'));
    } catch (e) { $('#otab').innerHTML = `<tr><td class="err">${esc(e.message)}</td></tr>`; }
    $('#chk').disabled = false;
  };
}
