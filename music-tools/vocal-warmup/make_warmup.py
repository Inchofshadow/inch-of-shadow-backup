"""Vocal warm-up MIDI: chord cue, then you sing 1-3-5 ("ah ah ahhh").

Each step = 2 bars of 4/4:
  bar 1: piano rolls the major triad: bass first, then root, 3rd, 5th about
         90 / 160 / 230 ms later (at 100 BPM), velocities slightly varied; held 1 bar
  bar 2: you sing 1-3-5 (quarter, quarter, half). In the "guide" file the
         piano plays those 3 notes softly with you; in "chords" it stays silent.
The next step starts a semitone higher, up to the top root, then back down.

Usage: python3 make_warmup.py [--low C2] [--high C3] [--bpm 100]
Defaults (Ableton names): roots C2 -> C3, top sung note G3 (the G above middle C).
No dependencies (raw MIDI writer).
"""
import argparse
import os
import random
import struct

TPQ = 480  # ticks per quarter note
NOTE_NAMES = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
              "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def note_number(name):
    """Ableton note names: Live labels MIDI 60 (middle C) as C3."""
    pitch, octave = name[:-1], int(name[-1])
    return NOTE_NAMES[pitch.upper()] + (octave + 2) * 12


def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)


def build(roots, bpm, guide):
    events = []  # (tick, order, bytes); order: note-off before note-on
    bar = 4 * TPQ
    t = 0
    rng = random.Random(135)  # fixed seed: same file every run
    for root in roots:
        # bar 1: chord cue, rolled like a hand on a piano: bass first, then
        # root, 3rd, 5th, each a little later and a little softer/louder
        roll = ((root - 12, 0, 78), (root, 70, 68), (root + 4, 130, 64), (root + 7, 185, 72))
        for n, delay, vel in roll:
            d = delay + rng.randint(-8, 8) if delay else 0
            v = max(1, min(127, vel + rng.randint(-5, 5)))
            events.append((t + d, 1, bytes([0x90, n, v])))
            events.append((t + bar - 20, 0, bytes([0x80, n, 0])))
        # bar 2: sing 1-3-5 (quarter, quarter, half)
        if guide:
            s = t + bar
            for n, start, length in ((root, 0, TPQ), (root + 4, TPQ, TPQ), (root + 7, 2 * TPQ, 2 * TPQ)):
                events.append((s + start, 1, bytes([0x90, n, 52 + rng.randint(-4, 4)])))
                events.append((s + start + length - 20, 0, bytes([0x80, n, 0])))
        t += 2 * bar
    events.sort(key=lambda e: (e[0], e[1]))

    track = bytearray()
    tempo = int(60_000_000 / bpm)
    track += vlq(0) + b"\xff\x51\x03" + tempo.to_bytes(3, "big")
    track += vlq(0) + b"\xff\x58\x04\x04\x02\x18\x08"  # 4/4
    last = 0
    for tick, _, data in events:
        track += vlq(tick - last) + data
        last = tick
    end = t  # end exactly on the last bar line so the clip loops cleanly
    track += vlq(end - last) + b"\xff\x2f\x00"
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, TPQ)
    return header + b"MTrk" + struct.pack(">I", len(track)) + bytes(track)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--low", default="C2", help="lowest root (Ableton names, C3 = middle C)")
    ap.add_argument("--high", default="C3", help="highest root; top sung note = this + a fifth")
    ap.add_argument("--bpm", type=float, default=100)
    a = ap.parse_args()
    lo, hi = note_number(a.low), note_number(a.high)
    up = list(range(lo, hi + 1))
    roots = up + up[-2::-1]  # up by semitones, then back down
    here = os.path.dirname(os.path.abspath(__file__))
    for guide, name in ((False, "chords"), (True, "guide")):
        path = os.path.join(here, f"warmup-135-{name}.mid")
        with open(path, "wb") as f:
            f.write(build(roots, a.bpm, guide))
        print(path, len(roots), "steps")


if __name__ == "__main__":
    main()
