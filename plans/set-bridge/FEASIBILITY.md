# Set bridge: feasibility test (2026-11-06, $0)

Idea (radar run 2026-11-06, producer-tools, "open" + own competitor check, rating B-):
keep sound and clock going while Ableton Live loads the next set, so a live act has no 10-15 s silence.

## What the desk check says

| Part | How it would work | Risk |
|---|---|---|
| 1. Sound during the load | A small helper app, OUTSIDE Live, plays the last 2-8 bars of the outgoing set while Live loads. A Max for Live device alone can't do it: it is unloaded with the set. | **Unknown, the key test.** A 2008 forum post says Live "grabs the audio outputs and refuses to share". That was Live 7 and probably Windows. On a Mac, Core Audio normally lets 2 apps play at once, and the Fireface can also keep them on separate channels mixed in TotalMix. |
| 2. Tempo and phase | The helper joins Ableton Link and keeps the beat while Live is gone. When the new set opens with Link on, Live re-aligns tempo and phase to the helper (Link aligns phase automatically when a peer joins). | Low. That is how Link is designed. Start/stop sync is opt-in in Live's Link settings. |
| 3. Handoff back | The helper crossfades out on the next downbeat once Live plays again (detected through Link start/stop sync). Hardware clock during the gap = the helper sends MIDI clock, or a Link-to-MIDI bridge. | Medium: needs a prototype. |
| How the bars get captured | The helper records Live's master the whole time through the Fireface's own loopback (TotalMix "Loopback"), or Live's master goes out through Loopback.app (also installed here). | Low on this Mac; for customers it is a setup step. |

Nothing found that already does this (AbleSet 3 at $129-269 still leaves a gap between set files).

## The 5-minute test (needs your hands and ears, no installs)

On the Mac mini with the Fireface:

1. Open Live 12, open any set, press play. Let it run.
2. In Terminal, start the test loop (120 BPM clicks plus a low hum, about 64 seconds):
   `cd "/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode" && for i in 1 2 3 4; do afplay plans/set-bridge/bridge-test-loop-120bpm.wav; done`
3. **Do you hear the test loop on top of Live?** (If not: Live holds the device, and the helper needs its own Fireface channels. Tell me and we try that next.)
4. While the loop plays, open ANOTHER set in Live (File > Open, don't save).
5. **Does the test loop keep playing through the whole load, without a drop or a crackle?** Roughly how many seconds did Live's own sound stop?

Two answers decide it:
- Q3 yes + Q5 yes = part 1 works. The rest (Link, crossfade) is normal building. Next step: a small prototype (needs 2 free Python packages; I will ask first).
- Q5 no = the idea needs a second machine or a hardware looper, and it drops back to C.
