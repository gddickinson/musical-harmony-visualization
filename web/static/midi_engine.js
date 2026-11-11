// Port of synthesis.build_midi_bytes (MIDIUtil 1.2.1 MIDIFile(1), format 1, 960 ticks per quarter note):
// a tempo track and one note track, events sorted by (tick, NoteOff-before-NoteOn, insertion order), note-off
// velocity = note-on velocity, de-interleaving of overlapping same-pitch notes as MIDIUtil does. Byte-identical to
// the Python output for the fixture progressions.

const TPQ = 960;

function varLen(i) {
  if (i === 0) return [0];
  const out = [];
  let hi = 0;
  while (i > 0) { out.push((i & 0x7f) | hi); i = Math.floor(i / 128); hi = 0x80; }
  return out.reverse();
}

const sortKey = (a, b) => (a.tick - b.tick) || (a.sec - b.sec) || (a.order - b.order);

function noteTrack(chords) {
  let order = 1;                   // insertion order 0 is the tempo event (added first)
  let time = 0.0;
  let events = [];
  for (const chord of chords) {
    const start = Math.trunc(time * TPQ), dur = Math.trunc(chord.duration * TPQ);
    for (const n of chord.notes) {
      events.push({ kind: 'on', tick: start, sec: 3, order, pitch: n.pitch, vel: n.velocity });
      events.push({ kind: 'off', tick: start + dur, sec: 2, order, pitch: n.pitch, vel: n.velocity });
      order++;
    }
    time += chord.duration;
  }
  // removeDuplicates: NoteOn/NoteOff equal when kind, tick and pitch agree (channel 0 only)
  const seen = new Set();
  events = events.filter(e => { const k = `${e.kind}|${e.tick}|${e.pitch}`; if (seen.has(k)) return false; seen.add(k); return true; });
  events.sort(sortKey);
  // deInterleaveNotes
  const stack = {};
  for (const e of events) {
    const key = String(e.pitch) + '0';
    if (e.kind === 'on') (stack[key] ||= []).push(e.tick);
    else {
      if (!stack[key] || !stack[key].length) throw new Error('MIDI note-off before note-on (chord shorter than 1/960 beat)');
      if (stack[key].length > 1) e.tick = stack[key].pop(); else stack[key].pop();
    }
  }
  events.sort(sortKey);
  return events;
}

function trackBytes(events, serialize) {
  const data = [];
  let prev = 0;
  for (const e of events) { data.push(...varLen(e.tick - prev), ...serialize(e)); prev = e.tick; }
  data.push(0x00, 0xff, 0x2f, 0x00);
  const len = data.length;
  return [0x4d, 0x54, 0x72, 0x6b, (len >>> 24) & 255, (len >>> 16) & 255, (len >>> 8) & 255, len & 255, ...data];
}

export function midiBytes(chords, tempoBpm) {
  const us = Math.trunc(60000000 / tempoBpm);
  const tempo = trackBytes([{ tick: 0 }], () => [0xff, 0x51, 0x03, (us >>> 16) & 255, (us >>> 8) & 255, us & 255]);
  const notes = trackBytes(noteTrack(chords), e => [e.kind === 'on' ? 0x90 : 0x80, e.pitch, e.vel]);
  const header = [0x4d, 0x54, 0x68, 0x64, 0, 0, 0, 6, 0, 1, 0, 2, TPQ >> 8, TPQ & 255];
  return new Uint8Array([...header, ...tempo, ...notes]);
}

export const toHex = bytes => Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
