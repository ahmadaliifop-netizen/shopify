#!/usr/bin/env python3
"""score.py — fastroo 30 s: a synthesised music bed at 120 BPM (licence-free, written here) + SFX placed from events.json.

    python3 dump_events.py && python3 score.py      → mix.wav (48 kHz stereo, ~-16 LUFS, peak ≤ -4 dBFS)

Music: D major, D–Bm–G–A, bars from 3.25 s (the first hop). It stops for the leap's hang, lands with the box,
falls silent at the door, comes back with the pull-out, cuts to three stabs for the hits, builds through the
gather and resolves once, on the badge.
"""
import json, os, sys, wave
import numpy as np
from scipy import signal
sys.path.insert(0, os.path.expanduser("~/.claude/skills/onetake/scripts"))
from sfx_palette import Score, air, glass, wood, sub, bubble, SR, lp, hp, bp, sweep_bp, sat
import pyloudnorm as pyln

HERE = os.path.dirname(os.path.abspath(__file__))
EV = json.load(open(os.path.join(HERE, "events.json")))
DUR = EV["T"]
rng = np.random.default_rng(3)
tt = lambda n: np.arange(n) / SR
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)

# ── instruments ──────────────────────────────────────────────────────────────────────
def pluck(f, dur=0.9, bright=0.6, decay=0.996):
    """Karplus–Strong: a short noise burst through a tuned delay loop (one IIR)."""
    n = int(SR * dur); N = max(2, int(round(SR / f)))
    x = np.zeros(n); x[:N] = lp(rng.uniform(-1, 1, N), 1500 + 6000 * bright)
    a = np.zeros(N + 2); a[0] = 1; a[N] = -0.5 * decay; a[N + 1] = -0.5 * decay
    y = signal.lfilter([1.0], a, x)
    return y / (np.abs(y).max() + 1e-9) * np.exp(-tt(n) * 2.2)
def bass(f, dur=0.42):
    n = int(SR * dur); t = tt(n); ph = 2 * np.pi * f * t
    saw = 2 * ((f * t) % 1) - 1
    y = np.sin(ph) * 0.9 + lp(saw, 380) * 0.5
    return sat(y * np.exp(-t * 5.5) * np.minimum(1, t / 0.004), 1.4)
def kick(dur=0.38):
    n = int(SR * dur); t = tt(n); ph = np.cumsum(2 * np.pi * (46 + 110 * np.exp(-t * 32)) / SR)
    return sat(np.sin(ph) * np.exp(-t * 9) + lp(rng.standard_normal(n), 3000) * np.exp(-t * 300) * 0.25, 1.6)
def hat(dur=0.05, open_=False):
    n = int(SR * (0.22 if open_ else dur)); t = tt(n)
    return hp(rng.standard_normal(n), 7000) * np.exp(-t * (14 if open_ else 90))
def clap(dur=0.25):
    n = int(SR * dur); t = tt(n); env = np.zeros(n)
    for d in (0.0, 0.011, 0.022): env += np.exp(-np.clip(t - d, 0, None) * 160) * (t >= d)
    env += np.exp(-t * 22) * 0.5
    return bp(rng.standard_normal(n), 1300, 0.9) * env
def pad(freqs, dur, attack=0.6, release=1.2, cut=1400):
    n = int(SR * dur); t = tt(n); y = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.11):
            ff = f * 2 ** (det / 12); y += 2 * ((ff * t + rng.uniform()) % 1) - 1
    y = lp(y, cut, 2) / (len(freqs) * 3)
    env = np.minimum(1, t / attack) * np.minimum(1, (dur - t) / release).clip(0, 1)
    return y * env
def riser(dur, f0=300, f1=6000):
    n = int(SR * dur); x = sweep_bp(rng.standard_normal(n), f0, f1, 1.2, blocks=48)
    return x / (np.abs(x).max() + 1e-9) * (tt(n) / dur) ** 2.2
def crash(dur=1.6):
    n = int(SR * dur); t = tt(n); return hp(rng.standard_normal(n), 5000) * np.exp(-t * 3.2) * 0.6

CH = {"D": [62, 66, 69], "Bm": [59, 62, 66], "G": [55, 59, 62], "A": [57, 61, 64]}
ROOT = {"D": 38, "Bm": 35, "G": 31, "A": 33}
PROG = ["D", "Bm", "G", "A"]
B0, BEAT, BAR = 3.25, 0.5, 2.0

mus = Score(dur=DUR, T60=1.3)
def M(sig, t, g, pan=0.0, send=0.2):
    if 0 <= t < DUR: mus.place(sig, t, g, pan, send)

def groove(t0, t1, full=False):
    t = t0
    while t < t1 - 1e-6:
        i = int(round((t - B0) / BEAT)); ch = PROG[(i // 4) % 4]; beat = i % 4
        M(kick(), t, 0.85, 0, 0.05)
        M(hat(), t + BEAT / 2, 0.16, 0.25, 0.1)
        if full: M(hat(), t + BEAT / 4, 0.08, -0.25, 0.1); M(hat(), t + 3 * BEAT / 4, 0.08, -0.25, 0.1)
        if beat in (1, 3): M(clap(), t, 0.3, 0.05, 0.35)
        # bass: root on the beat, an octave pop on the off-beat
        M(bass(mtof(ROOT[ch])), t, 0.55, 0, 0.02); M(bass(mtof(ROOT[ch] + 12), 0.2), t + 0.25, 0.3, 0, 0.02)
        # plucked chord on the off-beats, a little strum
        if beat in (0, 2):
            for k, m in enumerate(CH[ch]): M(pluck(mtof(m + 12), 0.5, 0.5), t + 0.25 + k * 0.012, 0.15, -0.3 + 0.3 * k, 0.35)
        if beat == 3 and full:
            M(pluck(mtof(CH[ch][2] + 24), 0.4, 0.8), t + 0.375, 0.09, 0.4, 0.4)
        t += BEAT

def stab(ch, t, g=0.3, oct_=12):
    for k, m in enumerate(CH[ch]): M(pluck(mtof(m + oct_), 1.2, 0.7), t + k * 0.008, g, -0.4 + 0.4 * k, 0.4)
    M(bass(mtof(ROOT[ch]), 0.7), t, 0.6, 0, 0.05)

# the run: two bars and a bit, from the first hop to the leap's crouch
groove(B0, 7.75)
M(riser(1.0, 400, 3000), 7.75, 0.12, 0, 0.4)
# the leap: drums out, a pad that hangs with the box, a riser into the landing
M(pad([mtof(m) for m in CH["G"]], 2.6, 0.4, 0.4), 8.75, 0.32, 0, 0.5)
M(riser(2.4, 300, 7000), 8.85, 0.22, 0, 0.4)
# the landing: one big downbeat, then quiet for the door
M(kick(0.6), 11.25, 1.0, 0, 0.05); M(crash(), 11.25, 0.3, 0, 0.5); stab("D", 11.25, 0.32)
M(pad([mtof(m) for m in CH["D"]], 2.4, 0.05, 2.0, 900), 11.25, 0.18, 0, 0.6)
# the pull-out: the pad comes back, then the groove on the bar
M(pad([mtof(m) for m in CH["Bm"]], 1.4, 0.9, 0.2), 13.95, 0.2, 0, 0.5)
M(riser(1.25, 250, 4000), 14.0, 0.1, 0, 0.4)
groove(15.25, 17.25)
# the hits: three stabs, nothing between
for (t, c) in zip((17.75, 18.25, 18.75), ("Bm", "G", "A")):
    M(kick(), t, 0.95, 0, 0.05); stab(c, t, 0.34); M(clap(), t, 0.28, 0, 0.3)
# the gather: fuller, building
groove(19.25, 23.25, full=True)
M(riser(1.8, 400, 8000), 21.45, 0.16, 0, 0.4)
# the resolve, once, on the badge
M(kick(0.6), 24.25, 0.95, 0, 0.05); stab("D", 24.25, 0.38); stab("D", 24.25, 0.2, 24); M(crash(2.4), 24.25, 0.22, 0, 0.6)
M(pad([mtof(m) for m in CH["D"] + [74]], 4.6, 0.08, 3.4, 1100), 24.25, 0.3, 0, 0.6)
M(pluck(mtof(81), 1.4, 0.6), 25.55, 0.08, 0.2, 0.6)

# ── sound effects, from the picture ─────────────────────────────────────────────────
fx = Score(dur=DUR, T60=1.0)
P = fx.place
def zip_(dur):
    n = int(SR * dur); t = tt(n); x = bp(rng.standard_normal(n), 2600, 1.6) * (0.6 + 0.4 * np.sin(2 * np.pi * 46 * t)) ** 2
    return x / (np.abs(x).max() + 1e-9) * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.5
merges = 0
for e in EV["events"]:
    t, k, pn, v, d = e["t"], e["kind"], e.get("pan", 0) * 0.7, e.get("v", 1), e.get("dur", 0.4)
    if k == "tape": P(zip_(d), t, 0.42, -0.2, 0.2, pan_to=0.25); P(wood(260, 0.08), t + d, 0.25, 0.25, 0.2)
    elif k == "word": P(glass(988 if t < 20 else 784, 0.7, 0.5), t, 0.10 * v, 0, 0.5)
    elif k == "hop": P(air(min(0.35, d * 0.6), 280, 2000, 1.4, 0.3), t - 0.02, 0.22 * v, pn, 0.3, pan_to=min(0.7, pn + 0.1))
    elif k == "land":
        P(wood(150 + rng.uniform(-10, 10), 0.12), t, 0.5 * v, pn, 0.15); P(sub(85, 0.25), t, 0.22 * v, pn, 0.1)
    elif k == "leap": P(air(d * 0.95, 200, 2600, 1.1, 0.42), t - 0.05, 0.55, pn, 0.5, pan_to=0.2)
    elif k == "bigland": P(sub(52, 1.0), t, 0.9, pn, 0.2); P(wood(110, 0.16), t, 0.7, pn, 0.2)
    elif k == "bell": P(glass(1318, 1.4, 0.6), t, 0.32, pn, 0.55); P(glass(1046, 1.7, 0.6), t + 0.34, 0.3, pn, 0.55)
    elif k == "pull": P(air(d, 1800, 260, 1.0, 0.35), t, 0.32, 0, 0.6)
    elif k == "hit": P(sub(60, 0.5), t, 0.5, 0, 0.1)
    elif k == "fly": P(air(d, 300, 2400, 1.3, 0.55), t, 0.10, pn, 0.4, pan_to=0.0)
    elif k == "merge":
        merges += 1
        if merges % 2: P(bubble(360 + 30 * (merges % 5), 0.2), t, 0.16, 0, 0.3)
    elif k == "dive": P(air(d, 220, 2400, 1.0, 0.85), t, 0.22, 0, 0.5)
    elif k == "iris": P(air(0.6, 400, 3200, 1.2, 0.2), t, 0.28, 0, 0.5)
    elif k == "lid": P(wood(300, 0.08), t, 0.5, 0, 0.2); P(bubble(480, 0.24), t + 0.03, 0.28, 0, 0.3)
    elif k == "markhop": P(air(d, 400, 2600, 1.4, 0.4), t, 0.24, 0, 0.4)
    elif k == "markland": P(sub(58, 0.8), t, 0.55, 0, 0.2); P(wood(170, 0.12), t, 0.4, 0, 0.2)
    elif k == "flat": P(air(0.45, 2400, 500, 1.3, 0.3), t, 0.2, 0, 0.4)
    elif k == "letter": P(wood(330 + rng.uniform(-30, 30), 0.07), t, 0.13, pn, 0.25)

# ── master ──────────────────────────────────────────────────────────────────────────
m_mus, m_fx = mus.mix(peak_db=0), fx.mix(peak_db=0)
mix = m_fx * 1.0 + m_mus * 0.62
meter = pyln.Meter(SR)
for _ in range(3):                                         # loudness to -16 LUFS, soft ceiling below -4 dBFS
    gain = 10 ** ((-16 - meter.integrated_loudness(mix)) / 20); mix = mix * gain
    ceil = 10 ** (-4.2 / 20); mix = np.tanh(mix / ceil) * ceil
fade = np.ones(len(mix)); nf = int(SR * 0.6); fade[-nf:] = np.linspace(1, 0, nf) ** 2; mix *= fade[:, None]
out = os.path.join(HERE, "mix.wav")
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print(f"{out}: {meter.integrated_loudness(mix):.1f} LUFS, peak {20 * np.log10(np.abs(mix).max()):.1f} dBFS")
