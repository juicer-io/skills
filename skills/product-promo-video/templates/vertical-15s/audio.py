"""Audio for the vertical Brand Listening video. Every time below is copied from the T timeline in
index.html: when you change the animation, change the cue here too.
Usage: python3 audio.py <out-dir>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_lib import *  # noqa: E402,F401

DUR = 15.0
OUT = sys.argv[1] if len(sys.argv) > 1 else "."

music = music_bed(DUR, seed="brand-listening-vertical", soft_start=0.3, drop=2.4, build=6.45,
                  breakdown=12.8, final_hit=13.95, fade_start=14.3)
sfx = Bus(DUR)

W_IN, W_OUT = whoosh(0.6, 300, 5000, 0.75), whoosh(0.45, 3000, 500, 0.25)
W_BIG, W_SUCK = whoosh(0.8, 200, 6000, 0.7), whoosh(0.6, 400, 7000, 0.92)
W_DROP = whoosh(0.6, 2500, 250, 0.2)
W_CAP = whoosh(0.4, 900, 3500, 0.5)

# hook
sfx.add(0.0, W_IN, 0.2)
sfx.add(1.0, pop(1100, 380), 0.3)            # "listening?" pill
sfx.add(2.0, W_OUT, 0.18)

# card rises, website typed, generate
sfx.add(2.3, W_BIG, 0.26)
sfx.add(2.5, W_CAP, 0.08)                     # caption "Type your website."
typing(sfx, 3.0, 16, 26, pan=0.0)
sfx.add(3.75, whoosh(0.3, 1200, 5000, 0.4), 0.12)
sfx.add(3.8, pop(600, 900, 0.1), 0.2)         # Generate brand report
sfx.add(3.95, pop(900, 400, 0.08), 0.1)       # progress card

# flurry: same seeded random as the page, so each pop matches its card and pans with it
seed = 11
def rnd():
    global seed
    seed = (seed * 16807) % 2147483647
    return (seed - 1) / 2147483646
for i in range(15):
    x = (520 if i % 2 else 40) + (-30 + 60 * rnd())
    rnd(); rnd(); ra = rnd(); rnd()
    sfx.add(4.05 + i * 0.07 + ra * 0.05, pop(rng.uniform(700, 1300), rng.uniform(250, 450), 0.09),
            0.13, float(np.clip((x + 200) / 540 - 1, -0.6, 0.6)))
sfx.add(5.0, W_DROP, 0.18)                    # off-topic posts drop away
sfx.add(5.4, ding(), 0.1)                     # Reading 1,120 posts done
sfx.add(5.55, W_SUCK, 0.26)                   # real mentions fly into the card
sfx.add(6.1, ding(), 0.12)                    # Keeping 264 real mentions done

# report
sfx.add(6.25, W_OUT, 0.12)
sfx.add(6.6, W_CAP, 0.08)                     # caption "Every mention, in one report."
sfx.add(6.65, pop(1000, 500, 0.08), 0.22)     # mentions block
sfx.add(6.95, pop(1000, 500, 0.08), 0.22)     # sentiment block
for k in range(3):                            # sentiment bar segments
    sfx.add(7.1 + k * 0.25, pop(1400, 900, 0.05), 0.09)
sfx.add(7.8, sparkle(), 0.08)                 # counter lands on 264

# latest mention
sfx.add(10.1, whoosh(0.5, 2000, 600, 0.3), 0.12)
sfx.add(10.35, W_CAP, 0.08)                   # caption "Know how people feel"
sfx.add(10.45, pop(1300, 700, 0.06), 0.24)    # mention card
sfx.add(11.3, sparkle(), 0.11)                # coral ring

# end card
sfx.add(12.75, W_OUT, 0.2)
sfx.add(13.2, W_IN, 0.14)
sfx.add(13.6, pop(1200, 420), 0.3)            # "Act on it." pill
sfx.add(13.95, impact(), 0.32)                # Brand Listening
sfx.add(13.95, sparkle(), 0.12)

mix_and_write(music, sfx, OUT, music_rms_db=-18.6)
