// Entry point: registers the lazily loaded pages, sets the footer mode text, draws the background and starts the router.
import { start, route, lazy, app, isStatic, $ } from './core.js';

const PAGES = { 'home.js': ['home'], 'studio.js': ['studio'], 'chords.js': ['chords'], 'verify.js': ['verify'], 'about.js': ['about'] };
lazy(Object.fromEntries(Object.entries(PAGES).flatMap(([file, names]) => names.map(n => [n, () => import('./' + file)]))));

route('notfound', () => { app().innerHTML = '<h1>Not found</h1><p><a href="#/">Back to the start</a></p>'; });

$('#mode').textContent = isStatic() ? 'static site: harmony, synthesis and plots run in your browser' : 'local app (Python server)';
background();
start();

// Faint staff lines drifting behind the page (still under prefers-reduced-motion).
function background() {
  const c = $('#bg'), ctx = c.getContext('2d');
  const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const draw = t => {
    c.width = innerWidth; c.height = innerHeight;
    ctx.strokeStyle = 'rgba(185,139,255,.35)'; ctx.lineWidth = 1;
    for (let s = 0; s < 3; s++) {
      const y0 = c.height * (0.2 + 0.3 * s);
      for (let l = 0; l < 5; l++) {
        ctx.beginPath();
        for (let x = 0; x <= c.width; x += 16) {
          const y = y0 + l * 9 + 6 * Math.sin(x / 180 + t / 4000 + s);
          x ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
        }
        ctx.stroke();
      }
    }
  };
  if (still) { draw(0); return; }
  let last = 0;
  const loop = t => { if (t - last > 80) { draw(t); last = t; } requestAnimationFrame(loop); };
  requestAnimationFrame(loop);
}
