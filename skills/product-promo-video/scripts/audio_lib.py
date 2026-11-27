"""Self-synthesised music bed + sound-effect palette for product promo videos.

Everything is generated from oscillators and noise: no samples, no third-party audio, so the
result needs no licence. A video's own audio.py imports this module, builds the music bed from
the video's section times, places SFX cues at the timeline's event times, and calls
mix_and_write(). See templates/mcp-video/audio.py for a complete example.

Needs: numpy, scipy (pip install numpy scipy).
"""
import hashlib
import os
import numpy as np
from scipy.signal import butter, sosfilt, sawtooth, fftconvolve
from scipy.io import wavfile

SR = 48000
rng = np.random.default_rng(11)


class Bus:
    """A stereo buffer with a length in seconds (plus 3 s of tail for reverbs)."""
    def __init__(self, dur):
        self.dur = dur
        self.n = int(SR * (dur + 3))
        self.x = np.zeros((2, self.n))

    def add(self, t, sig, g=1.0, pan=0.0):
        i = int(t * SR)
        if i >= self.n or i < 0:
            print(f"WARNING: cue at {t:.2f}s is outside the bus (0 to {self.n / SR:.2f}s), dropped")
            return
        s = sig[: self.n - i] * g
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        self.x[0, i:i + len(s)] += s * l * 1.414
        self.x[1, i:i + len(s)] += s * r * 1.414


def T(d): return np.arange(int(d * SR)) / SR
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def filt(x, fc, kind="low", order=2): return sosfilt(butter(order, fc, kind, fs=SR, output="sos"), x)
def rms(x): return np.sqrt(np.mean(x ** 2) + 1e-12)


def reverb(x, size=2.2, damp=5000, wet=0.3):
    t = T(size)
    out = np.empty_like(x)
    for c in range(2):
        ir = rng.standard_normal(len(t)) * np.exp(-t / (size / 5))
        ir = filt(ir, damp)
        ir /= np.sqrt(np.sum(ir ** 2))
        out[c] = fftconvolve(x[c], ir)[: x.shape[1]]
    return x + out * wet


# ------------------------------------------------------------------ music bed
# Every video gets its own arrangement: key, progression, tempo, arp pattern, lead sound and drum
# feel are drawn from these palettes with the video's seed (its slug), so a rerun is identical
# and two videos rarely match. The tempo is fitted to the video's section times. I-V-vi-IV at
# 120 BPM, the bed this engine started with and shares with other brands, is left out on purpose.
SCALE = [0, 2, 4, 5, 7, 9, 11]
KEY_NAMES = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
PROGRESSIONS = {  # scale degrees, 0 = I; each chord is played as a diatonic seventh chord
    "I-IV-vi-V": [0, 3, 5, 4],
    "I-vi-IV-V": [0, 5, 3, 4],
    "vi-V-IV-V": [5, 4, 3, 4],
    "I-iii-vi-IV": [0, 2, 5, 3],
    "ii-IV-I-V": [1, 3, 0, 4],
}
ARP_PATTERNS = {
    "climb": [0, 1, 2, 3, 0, 1, 2, 3],
    "leap": [0, 2, 1, 3, 0, 3, 1, 2],
    "pulse": [0, 0, 2, 0, 1, 0, 3, 2],
    "cascade": [3, 2, 1, 0, 3, 2, 1, 2],
}
LEADS = ("bell", "marimba", "keys")
FEELS = {"four": (0, 1, 2, 3), "bounce": (0, 1.5, 2, 3.5)}  # kick positions in beats per bar
AVOID_BPM = (118.5, 121.5)


def lowest(pc, floor):
    """Lowest MIDI note >= floor with pitch class pc."""
    return floor + (pc - floor) % 12


def chord(degree, key):
    """(bass note, pad voicing, arp notes) for a diatonic seventh chord on a scale degree."""
    pcs = [(key + SCALE[(degree + k) % 7]) % 12 for k in (0, 2, 4, 6)]
    pad = sorted(lowest(pc, 52) for pc in pcs)
    return lowest(pcs[0], 33), pad, [m + 12 for m in pad]


def lead_tone(kind, f, t):
    if kind == "bell":
        return np.sin(2 * np.pi * f * t + 2.0 * np.exp(-t / 0.08) * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t / 0.22)
    if kind == "marimba":
        return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.02)) \
            * np.minimum(1, t / 0.002) * np.exp(-t / 0.14)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t) + 0.15 * np.sin(2 * np.pi * 3 * f * t)) \
        * (1 + 0.15 * np.sin(2 * np.pi * 5 * t)) * np.exp(-t / 0.2)


def fit_tempo(soft_start, drop, breakdown, final_hit, rng, lo=100, hi=128, tol=0.06):
    """Tempo and first bar line that put the drop on a bar line and the soft start, breakdown and
    end-card hit within `tol` seconds of a beat (the build is snapped to a bar line later, since
    only a shaker enters there). Picks one of the fitting tempos with the video's seed, or the
    closest fit if none is within `tol`."""
    fits = []
    for bpm in np.round(np.arange(lo, hi + 0.001, 0.1), 1):
        if AVOID_BPM[0] <= bpm <= AVOID_BPM[1]:
            continue
        beat = 60 / bpm
        bar = 4 * beat
        grid0 = drop % bar
        off = lambda t, u: abs((t - grid0 + u / 2) % u - u / 2)
        worst = max(off(breakdown, beat), off(final_hit, beat), off(soft_start, beat))
        if grid0 <= soft_start:
            fits.append((worst, float(bpm), float(grid0)))
    if not fits:
        raise ValueError(
            f"no tempo between {lo} and {hi} BPM puts a bar line at or before soft_start={soft_start} "
            f"with drop={drop}. Use a later soft_start (about 1 s for a video with no quiet intro)."
        )
    good = [f for f in fits if f[0] <= tol] or [min(fits)]
    _, bpm, grid0 = good[rng.integers(len(good))]
    return bpm, grid0


def music_bed(dur, *, seed, soft_start, drop, build, breakdown, final_hit, fade_start=None,
              bpm=None, grid0=None, key=None, progression=None, arp=None, lead=None, feel=None):
    """Upbeat, calm electronic bed that follows the video's structure.

    seed       the video slug; picks key, progression, arp, lead, feel and (with the section
               times) the tempo. Same seed = same music. Pass any of those to override.
    soft_start half-time kick + bass come in (e.g. when the concept scene starts)
    drop       full groove (e.g. when the product UI first appears); always lands on a bar line
    build      16th shaker adds energy (e.g. from the second use case on)
    breakdown  drums stop, pad + arp only (e.g. when the UI leaves for the outro)
    final_hit  riser into a final chord + impact (logo / end card)
    fade_start final fade to silence at dur (default: 1.25 s after final_hit)
    """
    pick = np.random.default_rng(int(hashlib.sha256(seed.encode()).hexdigest()[:12], 16))
    key = int(pick.integers(12)) if key is None else key
    progression = progression or list(PROGRESSIONS)[pick.integers(len(PROGRESSIONS))]
    arp = arp or list(ARP_PATTERNS)[pick.integers(len(ARP_PATTERNS))]
    lead = lead or LEADS[pick.integers(len(LEADS))]
    feel = feel or list(FEELS)[pick.integers(len(FEELS))]
    if bpm is None:
        bpm, fitted_grid0 = fit_tempo(soft_start, drop, breakdown, final_hit, pick)
        grid0 = fitted_grid0 if grid0 is None else grid0
    grid0 = (drop % (240 / bpm)) if grid0 is None else grid0
    assert not AVOID_BPM[0] <= bpm <= AVOID_BPM[1], f"{bpm} BPM is too close to the shared 120 BPM bed"

    beat = 60 / bpm
    bar = 4 * beat
    chord_len = 2 * bar
    fade_start = fade_start if fade_start is not None else final_hit + 1.25
    times = (grid0, soft_start, drop, build, breakdown, final_hit, fade_start, dur)
    assert 0 <= grid0 and times == tuple(sorted(times)), (
        "need 0 <= grid0 <= soft_start <= drop <= build <= breakdown <= final_hit <= fade_start <= dur, "
        f"got grid0={grid0} soft_start={soft_start} drop={drop} build={build} breakdown={breakdown} "
        f"final_hit={final_hit} fade_start={fade_start} dur={dur}")
    prog = [chord(d, key) for d in PROGRESSIONS[progression]]
    chord_at = lambda t: prog[int(max(0, t - grid0) // chord_len) % len(prog)]
    off = lambda t, u=bar: (t - grid0 + u / 2) % u - u / 2
    build = min(max(build - off(build), drop), breakdown)
    print(f"music: {KEY_NAMES[key]} major, {progression}, {bpm:g} BPM (first bar {grid0:.2f} s), "
          f"arp {arp}, lead {lead}, feel {feel}")
    print("  offset from nearest beat (s):",
          {n: round(off(t, beat), 2) for n, t in (("soft_start", soft_start), ("drop", drop), ("breakdown", breakdown), ("final_hit", final_hit))})

    pad, arps, bass, drums = Bus(dur), Bus(dur), Bus(dur), Bus(dur)
    n = pad.n

    # pad: detuned saws, one chord every 2 bars; the first chord fades in from 0 s
    k = 0
    while True:
        s = 0.0 if k == 0 else grid0 + chord_len * k
        if s >= final_hit:
            break
        e = min(grid0 + chord_len * (k + 1), final_hit)
        d = e - s + 1.2
        t = T(d)
        env = np.minimum(1, t / (1.2 if k == 0 else 0.5)) * np.clip((d - t) / 1.2, 0, 1)
        for m in prog[k % len(prog)][1]:
            for det, pan in ((-8, -0.5), (0, 0), (8, 0.5)):
                f = mtof(m) * 2 ** (det / 1200)
                pad.add(s, filt(sawtooth(2 * np.pi * f * t + rng.uniform(0, 6)), 2600) * env, 0.05, pan)
        k += 1

    # arp: 8th-note notes with ping-pong delay; darker before the drop and in the breakdown
    pat = ARP_PATTERNS[arp]
    t8 = T(0.4)
    for i in range(int((final_hit - grid0) / (beat / 2))):
        s = grid0 + i * beat / 2
        tone = lead_tone(lead, mtof(chord_at(s + 0.01)[2][pat[i % 8]]), t8)
        tone = filt(tone, 1800 if (s < drop or s >= breakdown) else 4200)
        g = 0.11 if s < drop else (0.085 if s >= breakdown else 0.13)
        arps.add(s, tone, g, -0.25)
        arps.add(s + 0.75 * beat, tone, g * 0.35, 0.6)
        arps.add(s + 1.5 * beat, tone, g * 0.14, -0.6)

    # kick + sidechain envelope; half-time (beats 1 and 3) between soft_start and drop
    kicks = [grid0 + b * bar + p * beat for b in range(int((breakdown - grid0) / bar) + 2) for p in FEELS[feel]]
    kicks = sorted(q for q in kicks if soft_start - 1e-6 <= q < breakdown - 1e-6)
    kicks = [q for q in kicks if q >= drop - 1e-6 or round((q - grid0) / beat, 3) % 4 in (0, 2)]
    sc = np.ones(n)
    for q in kicks:
        i = int(q * SR); tt = T(0.35)
        sc[i:i + len(tt)] = np.minimum(sc[i:i + len(tt)], 1 - 0.55 * np.exp(-tt / 0.09))
    tk = T(0.45)
    kick = np.sin(2 * np.pi * np.cumsum(45 + 110 * np.exp(-tk / 0.035)) / SR) * np.exp(-tk / 0.16)
    kick[:200] += rng.standard_normal(200) * np.linspace(0.4, 0, 200)
    for q in kicks:
        drums.add(q, kick, 0.36 if q >= drop else 0.24)

    # clap on 2 and 4, offbeat hats, 16th shaker from `build`
    tc = T(0.25)
    clap = filt(rng.standard_normal(len(tc)), [900, 3500], "band") * np.exp(-tc / 0.05)
    th = T(0.08)
    hat = filt(rng.standard_normal(len(th)), 7000, "high") * np.exp(-th / 0.018)
    b = 0
    while grid0 + b * beat < breakdown - 1e-6:
        s = grid0 + b * beat
        if s >= drop - 1e-6:
            if b % 2 == 1:
                for dd, gg in ((0, 1), (0.012, 0.7), (0.024, 0.5)):
                    drums.add(s + dd, clap, 0.16 * gg, 0.05)
            drums.add(s + beat / 2, hat, 0.09, 0.3)
            if s >= build:
                for qq in (0.25, 0.75):
                    drums.add(s + qq * beat, hat, 0.035, -0.35)
        b += 1

    # bass: 8th pulses on the chord root
    tb = T(0.24)
    s = soft_start
    while s < breakdown - 1e-6:
        f = mtof(chord_at(s + 0.01)[0] + 12)
        tone = (np.sin(2 * np.pi * f * tb) + 0.3 * filt(sawtooth(2 * np.pi * f * tb), 900)) \
            * np.minimum(1, tb / 0.005) * np.exp(-tb / 0.14)
        bass.add(s, tone, 0.14 if s >= drop else 0.09)
        s += beat / 2

    pad.x *= sc * 0.7 + 0.3
    bass.x *= sc
    out = Bus(dur)
    out.x = reverb(pad.x + arps.x, 2.6, 4500, 0.45) + bass.x + reverb(drums.x, 1.0, 6000, 0.12)

    # riser into the final tonic chord + its ring-out
    tr = T(2.0)
    out.add(final_hit - 2.0, filt(rng.standard_normal(len(tr)), 3000) * (tr / 2) ** 2.5, 0.18)
    tf = T(3.2)
    fin = np.zeros(len(tf))
    r = lowest(key, 40)
    for m in (r, r + 12, r + 16, r + 19, r + 26, r + 31, r + 36):
        for det in (-7, 0, 7):
            fin += filt(sawtooth(2 * np.pi * mtof(m) * 2 ** (det / 1200) * tf + rng.uniform(0, 6)), 2200)
    out.add(final_hit, fin * np.minimum(1, tf / 0.02) * np.exp(-tf / 1.4) * 0.03)
    out.x *= fade_curve(out.n, fade_start, dur)
    return out


def fade_curve(n, start, end):
    f = np.ones(n); a, b = int(start * SR), int(end * SR)
    f[a:b] = np.linspace(1, 0, b - a) ** 1.5
    f[b:] = 0
    return f


# ------------------------------------------------------------------ SFX palette
def whoosh(d=0.7, f0=400, f1=4000, rise=0.6):
    """Band-passed noise sweep. f0 < f1 = whoosh in, f0 > f1 = whoosh out."""
    n = int(d * SR); x = rng.standard_normal(n)
    fc = f0 * (f1 / f0) ** (np.arange(n) / n)
    g = 2 * np.sin(np.pi * fc / SR)
    y = np.zeros(n); lo = bp = 0.0
    for i in range(n):
        hi = x[i] - lo - 0.6 * bp; bp += g[i] * hi; lo += g[i] * bp; y[i] = bp
    t = np.arange(n) / n
    env = np.where(t < rise, (t / rise) ** 2, ((1 - t) / (1 - rise)) ** 1.5)
    return y * env / (np.max(np.abs(y)) + 1e-9)


def pop(f0=900, f1=300, d=0.12):
    """Bubbly UI pop: element appears. Higher f0 = lighter."""
    t = T(d); f = f1 + (f0 - f1) * np.exp(-t / 0.018)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.03)


def click():
    """One keystroke. Call per character; vary gain for a human feel."""
    t = T(0.03)
    nz = filt(rng.standard_normal(len(t)), 2500, "high") * np.exp(-t / 0.0035)
    th = np.sin(2 * np.pi * rng.uniform(160, 220) * t) * np.exp(-t / 0.008)
    return nz * 0.6 + th * 0.5


def ding(notes=(84, 88), d=1.2):
    """Soft two-note success chime: data loaded / task done."""
    t = T(d); s = np.zeros(len(t))
    for k, m in enumerate(notes):
        tt = np.clip(t - k * 0.07, 0, None)
        s += (np.sin(2 * np.pi * mtof(m) * tt) + 0.25 * np.sin(2 * np.pi * mtof(m) * 2.01 * tt)) \
            * np.exp(-tt / 0.35) * (t >= k * 0.07)
    return s * np.minimum(1, t / 0.003)


def sparkle():
    """Quick high arpeggio: highlight / insight moment."""
    t = T(0.9); s = np.zeros(len(t))
    for k, m in enumerate((91, 96, 100, 103)):
        tt = np.clip(t - k * 0.045, 0, None)
        s += np.sin(2 * np.pi * mtof(m) * tt) * np.exp(-tt / 0.18) * (t >= k * 0.045)
    return s


def impact():
    """Sub boom + air: logo / end card."""
    t = T(2.5)
    sub = np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-t / 0.08)) / SR) * np.exp(-t / 0.6)
    return sub + filt(rng.standard_normal(len(t)), 6000, "high") * np.exp(-t / 0.5) * 0.25


def typing(bus, start, n_chars, cps, pan=0.35):
    """Keystrokes matching a typewriter effect that shows floor((t-start)*cps) characters."""
    for i in range(n_chars):
        bus.add(start + i / cps + rng.uniform(-0.006, 0.006), click(), rng.uniform(0.22, 0.32), pan)


# ------------------------------------------------------------------ mix
def mix_and_write(music, sfx, out_dir, music_rms_db=-19, sfx_gain=1.0, sfx_reverb=0.15):
    """Level the music bed, add SFX, soft-limit, write music.wav / sfx.wav / mix.wav.
    Prints the checks you use instead of listening (see references/lessons.md)."""
    dur = music.dur
    L = int(dur * SR)
    os.makedirs(out_dir, exist_ok=True)
    fade = fade_curve(music.n, dur - 1.7, dur)
    s = reverb(sfx.x, 1.2, 7000, sfx_reverb) * fade * sfx_gain
    m = music.x * (10 ** (music_rms_db / 20) / rms(music.x[:, :L]))
    mix = np.tanh((m + s) * 1.2) / 1.2
    mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
    for name, x in (("music", m), ("sfx", s), ("mix", mix)):
        y = x[:, :L]
        y = y / max(1.0, np.max(np.abs(y)) / 0.99)
        wavfile.write(os.path.join(out_dir, f"{name}.wav"), SR, (y.T * 32767).astype(np.int16))
    report(mix[:, :L])


def report(x):
    """Level + spectral balance check. Aim: no clipping, mix RMS about -15 to -17 dBFS,
    energy below 250 Hz under ~65 % (more sounds muddy on laptop speakers)."""
    mono = x.mean(0)
    F = np.abs(np.fft.rfft(mono)) ** 2; f = np.fft.rfftfreq(len(mono), 1 / SR); tot = F.sum()
    if tot == 0:
        print("WARNING: mix is silent")
        return
    bands = [(20, 80), (80, 250), (250, 1000), (1000, 4000), (4000, 12000), (12000, 24000)]
    share = [round(100 * F[(f >= a) & (f < b)].sum() / tot, 1) for a, b in bands]
    per_s = [round(20 * np.log10(rms(mono[i * SR:(i + 1) * SR]) + 1e-9)) for i in range(len(mono) // SR)]
    print("peak", round(float(np.max(np.abs(x))), 3), "| mix RMS dB", round(20 * np.log10(rms(x)), 1))
    print("band energy % (20-80, 80-250, 250-1k, 1-4k, 4-12k, 12k+):", share)
    print("RMS dB per second:", per_s)
