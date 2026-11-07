// ============================================================================
// Music Theory Engine  -  pure, derived-from-interval-math (no hardcoded tables)
// Everything (scales, chords, spelling, names, Roman numerals) is COMPUTED.
// Works in Node (for testing) and in the browser (inlined into index.html).
// ============================================================================

(function (root) {
  'use strict';

  const LETTERS = ['C', 'D', 'E', 'F', 'G', 'A', 'B'];
  const LETTER_PC = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };

  // --- note = { letter: 'C', acc: 0 }  (acc in semitones: -2..+2, etc.) ------

  function accString(acc) {
    if (acc === 0) return '';
    return acc > 0 ? '♯'.repeat(acc) : '♭'.repeat(-acc); // ♯ / ♭
  }
  function noteName(n) { return n.letter + accString(n.acc); }
  function pitchClass(n) { return ((LETTER_PC[n.letter] + n.acc) % 12 + 12) % 12; }

  // --- scale building: one letter per degree, accidental chosen to hit pitch --

  // pattern    = semitone offsets from tonic, e.g. major = [0,2,4,5,7,9,11]
  // letterSteps= letter-name advance per degree (0=same letter as tonic, 1=next...).
  //   Omit for 7-note scales (defaults to one letter per degree). REQUIRED for
  //   non-heptatonic scales so spelling stays correct (e.g. C maj pent = C D E G A,
  //   which skips letters F and B -> letterSteps [0,1,2,4,5]).
  function buildScale(tonic, pattern, letterSteps) {
    const tonicPC = pitchClass(tonic);
    const tIdx = LETTERS.indexOf(tonic.letter);
    const steps = letterSteps || pattern.map((_, i) => i); // default: sequential (7-note)
    const notes = [];
    const abs = []; // absolute (un-mod) semitone height for interval math
    for (let i = 0; i < pattern.length; i++) {
      const letter = LETTERS[(tIdx + steps[i]) % 7];
      const naturalPC = LETTER_PC[letter];
      const targetPC = (tonicPC + pattern[i]) % 12;
      let acc = targetPC - naturalPC;
      while (acc > 6) acc -= 12;
      while (acc < -6) acc += 12;
      notes.push({ letter, acc, step: steps[i] });
      abs.push(tonicPC + pattern[i]);
    }
    return { notes, abs };
  }

  // generic interval of a scale degree from the tonic (for the scale strip)
  const REF = [0, 2, 4, 5, 7, 9, 11]; // major/perfect reference per diatonic number-1
  function degreeInterval(letterStep, semis) {
    const num = ((letterStep % 7) + 7) % 7;       // 0..6  ->  1st..7th
    let diff = semis - REF[num];
    while (diff > 6) diff -= 12; while (diff < -6) diff += 12;
    const perfect = (num === 0 || num === 3 || num === 4);
    let q;
    if (perfect) q = diff === 0 ? 'P' : diff > 0 ? 'A'.repeat(diff) : 'd'.repeat(-diff);
    else q = diff === 0 ? 'M' : diff === -1 ? 'm' : diff > 0 ? 'A'.repeat(diff) : 'd'.repeat(-diff - 1);
    const numName = num + 1;
    const accSym = diff > 0 ? '♯'.repeat(diff) : diff < 0 ? '♭'.repeat(-diff) : '';
    return {
      name: (num === 0 && diff === 0) ? 'R' : q + numName,
      token: num === 0 ? '1' : accSym + numName
    };
  }

  // --- interval naming (degree-aware, fully correct) -------------------------

  const INTERVAL_NAME = {
    // key: degreeKind(3/5/7/9/11/13) + ':' + semitones
    '3:2': 'd3', '3:3': 'm3', '3:4': 'M3', '3:5': 'A3',
    '5:6': 'd5', '5:7': 'P5', '5:8': 'A5',
    '7:9': 'd7', '7:10': 'm7', '7:11': 'M7',
    '9:13': '♭9', '9:14': '9', '9:15': '♯9',
    '11:16': '♭11', '11:17': '11', '11:18': '♯11',
    '13:20': '♭13', '13:21': '13', '13:22': '♯13',
    '1:0': 'R'
  };
  // short formula token per chord degree (1 b3 3 5 b7 etc.) for the "1 3 5 7" line
  function formulaToken(degreeKind, semis) {
    const map = {
      1: { 0: '1' },
      3: { 2: '♭♭3', 3: '♭3', 4: '3', 5: '♯3' },
      5: { 6: '♭5', 7: '5', 8: '♯5' },
      7: { 9: '♭♭7', 10: '♭7', 11: '7' },
      9: { 13: '♭9', 14: '9', 15: '♯9' },
      11: { 16: '♭11', 17: '11', 18: '♯11' },
      13: { 20: '♭13', 21: '13', 22: '♯13' }
    };
    return (map[degreeKind] && map[degreeKind][semis]) || ('?' + semis);
  }

  // --- chord building: stack diatonic thirds within a scale -------------------

  const DEGREE_KIND = [1, 3, 5, 7, 9, 11, 13]; // for stack positions 0..6

  // Build the full stacked chord (up to 13th) on scale-degree d (0-indexed).
  function buildChord(scale, d) {
    const rootAbs = scale.abs[d];
    const tones = [];
    for (let k = 0; k < 7; k++) {
      const idx = d + 2 * k;
      const note = scale.notes[idx % 7];
      const absPitch = scale.abs[idx % 7] + 12 * Math.floor(idx / 7);
      const semis = absPitch - rootAbs;
      const kind = DEGREE_KIND[k];
      tones.push({
        note,
        name: noteName(note),
        semis,
        kind,
        intervalName: INTERVAL_NAME[kind + ':' + semis] || ('?' + semis),
        token: formulaToken(kind, semis)
      });
    }
    return tones; // [root,3,5,7,9,11,13]
  }

  // --- chord quality / symbol naming (triads + 7ths verified; tensions exact) -

  function triadQuality(t3, t5) {
    if (t3 === 4 && t5 === 7) return 'maj';
    if (t3 === 3 && t5 === 7) return 'min';
    if (t3 === 3 && t5 === 6) return 'dim';
    if (t3 === 4 && t5 === 8) return 'aug';
    if (t3 === 4 && t5 === 6) return 'majb5';
    if (t3 === 3 && t5 === 8) return 'min#5';
    return 'other';
  }

  const TRIAD_SUFFIX = { maj: '', min: 'm', dim: 'dim', aug: 'aug', majb5: '(♭5)', 'min#5': 'm(♯5)', other: '?' };
  const TRIAD_ROMAN = { maj: 'UP', min: 'low', dim: 'low°', aug: 'UP+', majb5: 'UP', 'min#5': 'low', other: 'UP' };

  // seventh-chord symbol from triad quality + 7th semitones
  function seventhSuffix(tri, t7) {
    if (tri === 'maj' && t7 === 11) return 'maj7';
    if (tri === 'maj' && t7 === 10) return '7';
    if (tri === 'min' && t7 === 10) return 'm7';
    if (tri === 'min' && t7 === 11) return 'm(maj7)';
    if (tri === 'dim' && t7 === 9) return 'dim7';
    if (tri === 'dim' && t7 === 10) return 'm7♭5';      // half-diminished ø7
    if (tri === 'aug' && t7 === 11) return 'maj7♯5';
    if (tri === 'aug' && t7 === 10) return '7♯5';
    return TRIAD_SUFFIX[tri] + '7';
  }

  // plain-language explanation per 7th-chord quality
  const QUALITY_BLURB = {
    'maj7': 'Major triad + major 7th. Lush, resolved, the warm "major jazz" sound.',
    '7': 'Major triad + minor 7th. Tense and restless, wants to resolve. This is the dominant (V) sound.',
    'm7': 'Minor triad + minor 7th. Smooth, mellow, the everyday minor.',
    'm(maj7)': 'Minor triad + major 7th. Eerie, noir, "spy theme" tension over a minor chord.',
    'dim7': 'Stacked minor thirds (symmetrical). Maximum instability, classic transition chord.',
    'm7♭5': 'Half-diminished. Diminished triad + minor 7th. Dark and unstable, the ii in a minor key.',
    'maj7♯5': 'Augmented triad + major 7th. Dreamlike, floating, unresolved.',
    '7♯5': 'Augmented triad + minor 7th. Whole-tone, dominant tension stretched wider.'
  };

  function chordInfo(scale, d) {
    const tones = buildChord(scale, d);
    const t3 = tones[1].semis, t5 = tones[2].semis, t7 = tones[3].semis;
    const tri = triadQuality(t3, t5);
    const triadSuffix = TRIAD_SUFFIX[tri];
    const seventhSuf = seventhSuffix(tri, t7);
    const rootName = tones[0].name;

    // Roman numeral from triad quality + scale degree
    const ROMAN_BASE = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'];
    let rn = ROMAN_BASE[d];
    if (tri === 'min' || tri === 'dim' || tri === 'min#5') rn = rn.toLowerCase();
    if (tri === 'dim') rn += '°';
    if (tri === 'aug') rn += '+';

    // exotic scales can yield non-tertian triads; show real intervals, never a guessed name
    let triadSymbol, seventhSymbol;
    if (tri === 'other') {
      triadSymbol = rootName + '(' + tones[1].token + ' ' + tones[2].token + ')';
      seventhSymbol = rootName + '(' + tones[1].token + ' ' + tones[2].token + ' ' + tones[3].token + ')';
    } else {
      triadSymbol = rootName + triadSuffix;
      seventhSymbol = rootName + seventhSuf;
    }

    return {
      degree: d,
      roman: rn,
      root: rootName,
      triadQuality: tri,
      triadSymbol,
      seventhSymbol,
      seventhSuffix: seventhSuf,
      blurb: QUALITY_BLURB[seventhSuf] || 'Read the notes and formula below as the source of truth for this chord.',
      tones // full stack [R,3,5,7,9,11,13]
    };
  }

  // --- inversions (standard for triads & 7ths; figured bass is textbook) ------

  const FIGURED = { 3: ['5/3', '6', '6/4'], 4: ['7', '6/5', '4/3', '4/2'] };
  const INV_NAME = ['Root position', '1st inversion', '2nd inversion',
    '3rd inversion', '4th inversion', '5th inversion', '6th inversion'];

  // count = how many chord tones (3 = triad, 4 = 7th); inv = 0-based inversion
  function inversion(ci, count, inv) {
    const tones = ci.tones.slice(0, count);
    const bass = tones[inv];
    const reordered = tones.slice(inv).concat(tones.slice(0, inv)); // bass first
    return {
      count, inv,
      name: INV_NAME[inv],
      bass,
      reordered,
      figured: FIGURED[count] ? FIGURED[count][inv] : null,
      slashBass: inv === 0 ? null : bass.name
    };
  }

  // --- suspended chords (1-2-5 / 1-4-5), built from the scale, honestly named -

  function susToken(kind, semis) {
    if (kind === 1) return '1';
    if (kind === 2) return semis === 2 ? '2' : semis === 1 ? '♭2' : '♯2';
    if (kind === 4) return semis === 5 ? '4' : semis === 6 ? '♯4' : '♭4';
    if (kind === 5) return semis === 7 ? '5' : semis === 6 ? '♭5' : '♯5';
    return '?';
  }
  const SUS_IV = {
    1: { 0: 'R' },
    2: { 1: 'm2', 2: 'M2', 3: 'A2' },
    4: { 4: 'd4', 5: 'P4', 6: 'A4' },
    5: { 6: 'd5', 7: 'P5', 8: 'A5' }
  };
  // type = 'sus2' | 'sus4'
  function susChord(scale, d, type) {
    const rootAbs = scale.abs[d];
    function tone(step, kind) {
      const idx = d + step;
      const note = scale.notes[idx % 7];
      const semis = scale.abs[idx % 7] + 12 * Math.floor(idx / 7) - rootAbs;
      return {
        note, name: noteName(note), semis, kind,
        intervalName: (SUS_IV[kind] && SUS_IV[kind][semis]) || ('?' + semis),
        token: susToken(kind, semis)
      };
    }
    const rootT = tone(0, 1), fifth = tone(4, 5);
    const mid = type === 'sus2' ? tone(1, 2) : tone(3, 4);
    const tones = [rootT, mid, fifth];
    const midOk = type === 'sus2' ? mid.semis === 2 : mid.semis === 5; // M2 / P4
    const fifthOk = fifth.semis === 7;
    const rn = rootT.name;
    let symbol, available, note;
    if (!midOk) {
      available = false; symbol = rn + type;
      note = 'No standard ' + type + ' on this degree: the ' + (type === 'sus2' ? '2nd' : '4th') +
        ' above the root is ' + mid.intervalName + ', not a ' +
        (type === 'sus2' ? 'major 2nd' : 'perfect 4th') + '.';
    } else {
      available = true;
      let suffix = type;
      if (fifth.semis === 6) suffix += '♭5'; else if (fifth.semis === 8) suffix += '♯5';
      symbol = rn + suffix;
      note = fifthOk ? '' : 'The 5th here is ' + fifth.intervalName + ' (borrowed from the scale).';
    }
    return { type, tones, symbol, available, midOk, fifthOk, note, root: rn };
  }

  // --- chords for symmetric scales (computed from the scale; symbols exact) ---
  // Symmetric (whole-tone, octatonic) scales have no functional Roman-numeral
  // harmony, but they ARE chord-rich. We extract their characteristic chords.
  const SYM_QUAL = {
    aug:  { ivs: [0, 4, 8],     names: ['R', 'M3', 'A5'],          toks: ['1', '3', '♯5'],         suf: 'aug' },
    dim7: { ivs: [0, 3, 6, 9],  names: ['R', 'm3', 'd5', 'd7'],    toks: ['1', '♭3', '♭5', '♭♭7'], suf: 'dim7' },
    dom7: { ivs: [0, 4, 7, 10], names: ['R', 'M3', 'P5', 'm7'],    toks: ['1', '3', '5', '♭7'],    suf: '7' }
  };
  // build a chord on scale-degree `deg` of quality `q`, spelled from the scale
  function scaleChord(scale, deg, q) {
    const spec = SYM_QUAL[q];
    const byPC = {}; scale.notes.forEach(n => { byPC[pitchClass(n)] = n; });
    const rootPC = pitchClass(scale.notes[deg]);
    const tones = spec.ivs.map((iv, i) => {
      const note = byPC[(rootPC + iv) % 12] || scale.notes[deg];
      return { note, name: noteName(note), intervalName: spec.names[i], token: spec.toks[i] };
    });
    return { symbol: noteName(scale.notes[deg]) + spec.suf, tones, quality: q };
  }

  // --- scale catalog ----------------------------------------------------------
  // Each family lists its modes (name + interval pattern from that mode's tonic).

  const SCALES = {
    'Major (Diatonic)': [
      { name: 'Ionian (Major)', pattern: [0, 2, 4, 5, 7, 9, 11] },
      { name: 'Dorian', pattern: [0, 2, 3, 5, 7, 9, 10] },
      { name: 'Phrygian', pattern: [0, 1, 3, 5, 7, 8, 10] },
      { name: 'Lydian', pattern: [0, 2, 4, 6, 7, 9, 11] },
      { name: 'Mixolydian', pattern: [0, 2, 4, 5, 7, 9, 10] },
      { name: 'Aeolian (Natural Minor)', pattern: [0, 2, 3, 5, 7, 8, 10] },
      { name: 'Locrian', pattern: [0, 1, 3, 5, 6, 8, 10] }
    ],
    'Harmonic Minor': [
      { name: 'Harmonic Minor', pattern: [0, 2, 3, 5, 7, 8, 11] },
      { name: 'Locrian ♮6', pattern: [0, 1, 3, 5, 6, 9, 10] },
      { name: 'Ionian ♯5 (Augmented Major)', pattern: [0, 2, 4, 5, 8, 9, 11] },
      { name: 'Dorian ♯4 (Ukrainian Dorian)', pattern: [0, 2, 3, 6, 7, 9, 10] },
      { name: 'Phrygian Dominant', pattern: [0, 1, 4, 5, 7, 8, 10] },
      { name: 'Lydian ♯2', pattern: [0, 3, 4, 6, 7, 9, 11] },
      { name: 'Ultralocrian', pattern: [0, 1, 3, 4, 6, 8, 9] }
    ],
    'Melodic Minor': [
      { name: 'Melodic Minor', pattern: [0, 2, 3, 5, 7, 9, 11] },
      { name: 'Dorian ♭2', pattern: [0, 1, 3, 5, 7, 9, 10] },
      { name: 'Lydian Augmented', pattern: [0, 2, 4, 6, 8, 9, 11] },
      { name: 'Lydian Dominant', pattern: [0, 2, 4, 6, 7, 9, 10] },
      { name: 'Mixolydian ♭6', pattern: [0, 2, 4, 5, 7, 8, 10] },
      { name: 'Locrian ♮2 (Half-Diminished)', pattern: [0, 2, 3, 5, 6, 8, 10] },
      { name: 'Altered (Super Locrian)', pattern: [0, 1, 3, 4, 6, 8, 10] }
    ],
    'Other Heptatonic': [
      { name: 'Harmonic Major', pattern: [0, 2, 4, 5, 7, 8, 11] },
      { name: 'Double Harmonic (Byzantine)', pattern: [0, 1, 4, 5, 7, 8, 11] },
      { name: 'Hungarian Minor', pattern: [0, 2, 3, 6, 7, 8, 11] },
      { name: 'Neapolitan Minor', pattern: [0, 1, 3, 5, 7, 8, 11] },
      { name: 'Neapolitan Major', pattern: [0, 1, 3, 5, 7, 9, 11] }
    ],
    'Pentatonic / Blues': [
      { name: 'Major Pentatonic', pattern: [0, 2, 4, 7, 9], letterSteps: [0, 1, 2, 4, 5] },
      { name: 'Minor Pentatonic', pattern: [0, 3, 5, 7, 10], letterSteps: [0, 2, 3, 4, 6] },
      { name: 'Blues (Minor)', pattern: [0, 3, 5, 6, 7, 10], letterSteps: [0, 2, 3, 4, 4, 6] }
    ],
    'Symmetric': [
      { name: 'Whole Tone', pattern: [0, 2, 4, 6, 8, 10], letterSteps: [0, 1, 2, 3, 4, 5],
        usage: 'All whole steps and symmetric — it yields just two augmented triads (plus floating dominant 7♭5 / 7♯5 colors). Dreamlike, unresolved.',
        chordSpec: [{ deg: 0, q: 'aug' }, { deg: 1, q: 'aug' }] },
      { name: 'Diminished (Whole–Half)', pattern: [0, 2, 3, 5, 6, 8, 9, 11], letterSteps: [0, 1, 2, 3, 4, 5, 5, 6],
        note: 'Octatonic: 8 notes can’t map to 7 letters, so one letter repeats by convention.',
        usage: 'Played over diminished 7th chords. The scale is literally the union of two dim7 chords a whole step apart.',
        chordSpec: [{ deg: 0, q: 'dim7' }, { deg: 1, q: 'dim7' }] },
      { name: 'Diminished (Half–Whole)', pattern: [0, 1, 3, 4, 6, 7, 9, 10], letterSteps: [0, 1, 2, 2, 4, 4, 5, 6],
        note: 'Octatonic: 8 notes can’t map to 7 letters, so letters repeat by convention.',
        usage: 'The go-to scale over a dominant 7♭9. It contains four dominant 7th chords a minor 3rd apart, plus two diminished 7th chords.',
        chordSpec: [{ deg: 0, q: 'dom7' }, { deg: 2, q: 'dom7' }, { deg: 4, q: 'dom7' }, { deg: 6, q: 'dom7' }, { deg: 0, q: 'dim7' }, { deg: 1, q: 'dim7' }] }
    ]
  };

  // tonic spellings offered in the root selector (engine spells the rest)
  const ROOTS = [
    { letter: 'C', acc: 0 }, { letter: 'C', acc: 1 }, { letter: 'D', acc: -1 },
    { letter: 'D', acc: 0 }, { letter: 'E', acc: -1 }, { letter: 'E', acc: 0 },
    { letter: 'F', acc: 0 }, { letter: 'F', acc: 1 }, { letter: 'G', acc: -1 },
    { letter: 'G', acc: 0 }, { letter: 'A', acc: -1 }, { letter: 'A', acc: 0 },
    { letter: 'B', acc: -1 }, { letter: 'B', acc: 0 }
  ];

  function analyzeScale(tonic, pattern, letterSteps) {
    const scale = buildScale(tonic, pattern, letterSteps);
    const chordable = pattern.length === 7; // tertian harmony only meaningful for 7-note scales
    const chords = [];
    if (chordable) for (let d = 0; d < 7; d++) chords.push(chordInfo(scale, d));
    return { scale, chords, chordable };
  }

  const API = {
    LETTERS, LETTER_PC, SCALES, ROOTS, FIGURED, INV_NAME,
    accString, noteName, pitchClass, buildScale, buildChord, chordInfo,
    analyzeScale, triadQuality, seventhSuffix, inversion, susChord, degreeInterval, scaleChord
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  else root.Theory = API;

})(typeof window !== 'undefined' ? window : globalThis);


// ============================================================================
// SELF-TEST  (runs only under Node:  `node theory.js`)
// Reference values are foundational, cross-checkable music facts - not guesses.
// ============================================================================
if (typeof require !== 'undefined' && require.main === module) {
  const T = module.exports;
  let pass = 0, fail = 0;
  function eq(label, got, want) {
    const g = JSON.stringify(got), w = JSON.stringify(want);
    if (g === w) { pass++; }
    else { fail++; console.log('FAIL: ' + label + '\n   got:  ' + g + '\n   want: ' + w); }
  }
  const note = (l, a) => ({ letter: l, acc: a });
  const scaleNames = (tonic, pat) => T.buildScale(tonic, pat).notes.map(T.noteName);
  const MAJOR = [0, 2, 4, 5, 7, 9, 11];

  // 1. Spelling of major scales across the circle of fifths
  eq('C major', scaleNames(note('C', 0), MAJOR), ['C', 'D', 'E', 'F', 'G', 'A', 'B']);
  eq('G major', scaleNames(note('G', 0), MAJOR), ['G', 'A', 'B', 'C', 'D', 'E', 'F♯']);
  eq('F major', scaleNames(note('F', 0), MAJOR), ['F', 'G', 'A', 'B♭', 'C', 'D', 'E']);
  eq('F# major (E# not F)', scaleNames(note('F', 1), MAJOR), ['F♯', 'G♯', 'A♯', 'B', 'C♯', 'D♯', 'E♯']);
  eq('Db major', scaleNames(note('D', -1), MAJOR), ['D♭', 'E♭', 'F', 'G♭', 'A♭', 'B♭', 'C']);
  eq('B major', scaleNames(note('B', 0), MAJOR), ['B', 'C♯', 'D♯', 'E', 'F♯', 'G♯', 'A♯']);

  // 2. C major diatonic triads + 7ths + Roman numerals
  const cmaj = T.analyzeScale(note('C', 0), MAJOR);
  eq('C major triads',
    cmaj.chords.map(c => c.triadSymbol),
    ['C', 'Dm', 'Em', 'F', 'G', 'Am', 'Bdim']);
  eq('C major 7ths',
    cmaj.chords.map(c => c.seventhSymbol),
    ['Cmaj7', 'Dm7', 'Em7', 'Fmaj7', 'G7', 'Am7', 'Bm7♭5']);
  eq('C major Roman numerals',
    cmaj.chords.map(c => c.roman),
    ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']);

  // 3. C major I chord full stack -> C E G B D F A
  eq('Cmaj13 notes', cmaj.chords[0].tones.map(t => t.name), ['C', 'E', 'G', 'B', 'D', 'F', 'A']);
  // V chord extension intervals -> natural 9,11,13
  eq('G7 stack tokens', cmaj.chords[4].tones.map(t => t.token), ['1', '3', '5', '♭7', '9', '11', '13']);

  // 4. A harmonic minor: scale, key chords
  const HARM = T.SCALES['Harmonic Minor'][0].pattern;
  eq('A harmonic minor', scaleNames(note('A', 0), HARM), ['A', 'B', 'C', 'D', 'E', 'F', 'G♯']);
  const aharm = T.analyzeScale(note('A', 0), HARM);
  eq('A harm minor 7ths',
    aharm.chords.map(c => c.seventhSymbol),
    ['Am(maj7)', 'Bm7♭5', 'Cmaj7♯5', 'Dm7', 'E7', 'Fmaj7', 'G♯dim7']);
  eq('A harm minor Roman',
    aharm.chords.map(c => c.roman),
    ['i', 'ii°', 'III+', 'iv', 'V', 'VI', 'vii°']);

  // 5. C melodic minor
  const MEL = T.SCALES['Melodic Minor'][0].pattern;
  eq('C melodic minor', scaleNames(note('C', 0), MEL), ['C', 'D', 'E♭', 'F', 'G', 'A', 'B']);
  const cmel = T.analyzeScale(note('C', 0), MEL);
  eq('C melodic minor 7ths',
    cmel.chords.map(c => c.seventhSymbol),
    ['Cm(maj7)', 'Dm7', 'E♭maj7♯5', 'F7', 'G7', 'Am7♭5', 'Bm7♭5']);

  // 6. D Dorian (white-key mode)
  const DOR = T.SCALES['Major (Diatonic)'][1].pattern;
  eq('D Dorian', scaleNames(note('D', 0), DOR), ['D', 'E', 'F', 'G', 'A', 'B', 'C']);
  eq('D Dorian Roman',
    T.analyzeScale(note('D', 0), DOR).chords.map(c => c.roman),
    ['i', 'ii', 'III', 'IV', 'v', 'vi°', 'VII']);

  // 7. C Lydian -> #11 present
  const LYD = T.SCALES['Major (Diatonic)'][3].pattern;
  eq('C Lydian', scaleNames(note('C', 0), LYD), ['C', 'D', 'E', 'F♯', 'G', 'A', 'B']);
  eq('C Lydian I has #11', T.analyzeScale(note('C', 0), LYD).chords[0].tones[5].intervalName, '♯11');

  // 8. Inversions  (figured bass + slash bass = standard music theory)
  const cI = T.chordInfo(T.buildScale(note('C', 0), MAJOR), 0); // C major / Cmaj7
  eq('C triad root reorder', T.inversion(cI, 3, 0).reordered.map(t => t.name), ['C', 'E', 'G']);
  eq('C triad 1st inv reorder', T.inversion(cI, 3, 1).reordered.map(t => t.name), ['E', 'G', 'C']);
  eq('C triad 2nd inv reorder', T.inversion(cI, 3, 2).reordered.map(t => t.name), ['G', 'C', 'E']);
  eq('C triad figured bass', [0, 1, 2].map(i => T.inversion(cI, 3, i).figured), ['5/3', '6', '6/4']);
  eq('C triad slash basses', [0, 1, 2].map(i => T.inversion(cI, 3, i).slashBass), [null, 'E', 'G']);
  eq('Cmaj7 inv basses', [0, 1, 2, 3].map(i => T.inversion(cI, 4, i).bass.name), ['C', 'E', 'G', 'B']);
  eq('Cmaj7 figured bass', [0, 1, 2, 3].map(i => T.inversion(cI, 4, i).figured), ['7', '6/5', '4/3', '4/2']);
  // spelled enharmonic inversion: F#maj7 3rd inversion bass = E#
  const fsI = T.chordInfo(T.buildScale(note('F', 1), MAJOR), 0);
  eq('F#maj7 3rd inv bass = E#', T.inversion(fsI, 4, 3).bass.name, 'E♯');

  // 9. Suspended chords (built from scale; honest availability)
  const cMajScale = T.buildScale(note('C', 0), MAJOR);
  const sus = (d, t) => T.susChord(cMajScale, d, t);
  eq('Csus2 notes', sus(0, 'sus2').tones.map(t => t.name), ['C', 'D', 'G']);
  eq('Csus4 notes', sus(0, 'sus4').tones.map(t => t.name), ['C', 'F', 'G']);
  eq('Csus2 available', sus(0, 'sus2').available, true);
  eq('Esus2 NOT available (2nd is minor)', sus(2, 'sus2').available, false);
  eq('Esus4 available', [sus(2, 'sus4').available, sus(2, 'sus4').symbol], [true, 'Esus4']);
  eq('Fsus4 NOT available (4th is aug)', sus(3, 'sus4').available, false);
  eq('Fsus2 available', [sus(3, 'sus2').available, sus(3, 'sus2').symbol], [true, 'Fsus2']);
  eq('Bsus4 has flat-5', [sus(6, 'sus4').available, sus(6, 'sus4').symbol], [true, 'Bsus4♭5']);
  eq('Gsus4 notes', sus(4, 'sus4').tones.map(t => t.name), ['G', 'C', 'D']);
  // spelling: F# major Isus4 = F# B C#, Isus2 = F# G# C#
  const fsScale = T.buildScale(note('F', 1), MAJOR);
  eq('F#sus4 spelled', T.susChord(fsScale, 0, 'sus4').tones.map(t => t.name), ['F♯', 'B', 'C♯']);
  eq('F#sus2 spelled', T.susChord(fsScale, 0, 'sus2').tones.map(t => t.name), ['F♯', 'G♯', 'C♯']);

  // 10. New scales — correct spelling for non-7-note scales (the hard part)
  const sp = (tonic, name) => {
    for (const fam in T.SCALES) {
      const m = T.SCALES[fam].find(x => x.name === name);
      if (m) return T.buildScale(tonic, m.pattern, m.letterSteps).notes.map(T.noteName);
    }
    throw new Error('scale not found: ' + name);
  };
  eq('C major pentatonic', sp(note('C', 0), 'Major Pentatonic'), ['C', 'D', 'E', 'G', 'A']);
  eq('E♭ major pentatonic', sp(note('E', -1), 'Major Pentatonic'), ['E♭', 'F', 'G', 'B♭', 'C']);
  eq('A minor pentatonic', sp(note('A', 0), 'Minor Pentatonic'), ['A', 'C', 'D', 'E', 'G']);
  eq('C minor pentatonic', sp(note('C', 0), 'Minor Pentatonic'), ['C', 'E♭', 'F', 'G', 'B♭']);
  eq('C blues', sp(note('C', 0), 'Blues (Minor)'), ['C', 'E♭', 'F', 'G♭', 'G', 'B♭']);
  eq('C whole tone', sp(note('C', 0), 'Whole Tone'), ['C', 'D', 'E', 'F♯', 'G♯', 'A♯']);
  eq('D♭ whole tone', sp(note('D', -1), 'Whole Tone'), ['D♭', 'E♭', 'F', 'G', 'A', 'B']);
  eq('C dim W-H', sp(note('C', 0), 'Diminished (Whole–Half)'), ['C', 'D', 'E♭', 'F', 'G♭', 'A♭', 'A', 'B']);
  eq('C dim H-W', sp(note('C', 0), 'Diminished (Half–Whole)'), ['C', 'D♭', 'E♭', 'E', 'G♭', 'G', 'A', 'B♭']);
  // exotic heptatonic
  eq('C harmonic major', sp(note('C', 0), 'Harmonic Major'), ['C', 'D', 'E', 'F', 'G', 'A♭', 'B']);
  eq('C double harmonic', sp(note('C', 0), 'Double Harmonic (Byzantine)'), ['C', 'D♭', 'E', 'F', 'G', 'A♭', 'B']);
  eq('C hungarian minor', sp(note('C', 0), 'Hungarian Minor'), ['C', 'D', 'E♭', 'F♯', 'G', 'A♭', 'B']);

  // 11. chordable flag + degree intervals
  eq('major is chordable', T.analyzeScale(note('C', 0), MAJOR).chordable, true);
  const pent = T.SCALES['Pentatonic / Blues'][0];
  eq('pentatonic not chordable', T.analyzeScale(note('C', 0), pent.pattern, pent.letterSteps).chordable, false);
  const bluesM = T.SCALES['Pentatonic / Blues'][2];
  const bScale = T.buildScale(note('C', 0), bluesM.pattern, bluesM.letterSteps);
  eq('blues degree tokens', bScale.notes.map(n => T.degreeInterval(n.step, T.pitchClass(n) - T.pitchClass(bScale.notes[0])).token),
    ['1', '♭3', '4', '♭5', '5', '♭7']);

  // 12. Symmetric-scale characteristic chords
  const symScale = (name) => {
    const m = T.SCALES['Symmetric'].find(x => x.name === name);
    return { m, scale: T.buildScale(note('C', 0), m.pattern, m.letterSteps) };
  };
  const wh = symScale('Diminished (Whole–Half)');
  eq('C dim W-H chords = two dim7s',
    wh.m.chordSpec.map(c => T.scaleChord(wh.scale, c.deg, c.q).symbol), ['Cdim7', 'Ddim7']);
  eq('Cdim7 notes', T.scaleChord(wh.scale, 0, 'dim7').tones.map(t => t.name), ['C', 'E♭', 'G♭', 'A']);
  eq('Ddim7 notes', T.scaleChord(wh.scale, 1, 'dim7').tones.map(t => t.name), ['D', 'F', 'A♭', 'B']);
  const hw = symScale('Diminished (Half–Whole)');
  eq('C dim H-W chords',
    hw.m.chordSpec.map(c => T.scaleChord(hw.scale, c.deg, c.q).symbol),
    ['C7', 'E♭7', 'G♭7', 'A7', 'Cdim7', 'D♭dim7']);
  eq('C7 (from H-W) notes', T.scaleChord(hw.scale, 0, 'dom7').tones.map(t => t.name), ['C', 'E', 'G', 'B♭']);
  const wt = symScale('Whole Tone');
  eq('Whole tone chords = two aug triads',
    wt.m.chordSpec.map(c => T.scaleChord(wt.scale, c.deg, c.q).symbol), ['Caug', 'Daug']);
  eq('Caug notes', T.scaleChord(wt.scale, 0, 'aug').tones.map(t => t.name), ['C', 'E', 'G♯']);
  eq('dim7 interval names', T.scaleChord(wh.scale, 0, 'dim7').tones.map(t => t.intervalName), ['R', 'm3', 'd5', 'd7']);

  console.log('\n' + (fail === 0 ? 'ALL PASS' : 'SOME FAILED') + '  -  pass=' + pass + ' fail=' + fail);
  process.exit(fail === 0 ? 0 : 1);
}
