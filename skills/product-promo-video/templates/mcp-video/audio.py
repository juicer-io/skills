"""Audio for the Juicer MCP video (reference example). Every time below is copied from the
timeline in index.html: when you change the animation, change the cue here too.
Usage: python audio.py <out-dir>   (needs ../../scripts on the path, done below)"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
from audio_lib import (  # noqa: E402
    Bus, ding, impact, mix_and_write, music_bed, np, pop, rng, sparkle, typing, whoosh)

DUR = 52.0
OUT = sys.argv[1] if len(sys.argv) > 1 else "."

music = music_bed(DUR, seed="juicer-mcp", soft_start=5.0, drop=9.0, build=21.0,
                  breakdown=45.0, final_hit=49.05, fade_start=50.3)
sfx = Bus(DUR)

W_IN, W_OUT = whoosh(0.7, 300, 5000, 0.75), whoosh(0.5, 3000, 500, 0.25)
W_BIG, W_SUCK = whoosh(1.0, 200, 6000, 0.7), whoosh(0.9, 400, 7000, 0.92)

# scene 1 + 2: kinetic headline, concept tiles
sfx.add(0.15, W_IN, 0.22)
sfx.add(1.0, pop(1100, 380), 0.3)          # "ask" pill
sfx.add(3.0, W_OUT, 0.2)
sfx.add(3.35, W_IN, 0.16, 0.2)
sfx.add(3.79, pop(1200, 420), 0.32)        # "MCP" pill
sfx.add(5.0, pop(700, 250), 0.34, -0.5)    # Juicer tile
sfx.add(5.15, pop(900, 320), 0.34, 0.5)    # AI tile
sfx.add(5.6, whoosh(0.6, 800, 3000, 0.5), 0.1)
for k in range(3):                          # data pulses arriving at the AI tile
    for n in range(1, 4):
        tt = 6.1 + (n - k / 3) / 0.55
        if 6.1 < tt < 8.5:
            sfx.add(tt, ding((96,), 0.25), 0.05, 0.5)
sfx.add(8.35, W_BIG, 0.28, 0.4)            # chat window flies in

# three use cases: typing, send, tool done, answer items, highlights
for a, s, n, cps in [(9.7, 11.95, 47, 26), (22.3, 23.9, 38, 24), (36.2, 38.45, 49, 28)]:
    typing(sfx, a, n, cps)
    sfx.add(s - 0.05, whoosh(0.35, 1200, 5000, 0.4), 0.14, 0.3)
    sfx.add(s, pop(600, 900, 0.1), 0.18, 0.3)
for t in (13.7, 28.9, 39.9):
    sfx.add(t, ding(), 0.13, -0.1)
for t in (13.9, 14.25, 14.55, 14.85, 29.05, 29.4, 29.75, 30.1, 40.1, 40.45, 40.8):
    sfx.add(t, pop(1300, 700, 0.06), 0.12, 0.1)
for t in (15.7, 31.0, 41.4):
    sfx.add(t, sparkle(), 0.1, 0.2)
for t in (16.3, 42.0):
    sfx.add(t, pop(800, 500, 0.08), 0.12, 0.1)
for t in (21.25, 35.25):
    sfx.add(t, W_OUT, 0.16, 0.2)

# post flurry: replicate the page's seeded random so each pop matches its card and pans with it
seed = 7
def rnd():
    global seed
    seed = (seed * 16807) % 2147483647
    return (seed - 1) / 2147483646
for i in range(46):
    r1 = rnd()
    x = (40 + 1560 * r1) if i % 3 == 0 else (30 + 1470 * r1)
    rnd(); rnd(); ra = rnd(); rnd()
    sfx.add(24.9 + i * 0.05 + ra * 0.1, pop(rng.uniform(700, 1300), rng.uniform(250, 450), 0.09),
            0.13, float(np.clip(x / 960 - 1, -0.8, 0.8)))
sfx.add(24.8, pop(500, 200, 0.2), 0.3)     # queue counter card
sfx.add(27.95, W_SUCK, 0.3, 0.3)           # cards collapse into the chip

# outro + end card
sfx.add(45.85, W_OUT, 0.2)
sfx.add(46.3, W_IN, 0.14)
sfx.add(47.5, pop(1200, 420), 0.3)         # "act on." pill
sfx.add(48.6, W_OUT, 0.16)
sfx.add(49.05, impact(), 0.32)
sfx.add(49.05, sparkle(), 0.12)

mix_and_write(music, sfx, OUT)
