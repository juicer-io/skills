# Lessons

Each of these cost a render or a re-think. Add your own lessons at the bottom as they come up.

## Tooling

- **No Remotion.** Its licence is free only for companies up to 3 employees. The stack here is
  plain HTML + JS driven by `seek(t)`, captured frame by frame with `puppeteer-core` in the
  installed Chrome, piped into `ffmpeg-static` (brings its own ffmpeg binary).
- **Deterministic animation only.** No CSS transitions, keyframes, `setTimeout` or
  `requestAnimationFrame`: every visual property is computed from `t` in `seek(t)`. That makes
  any frame reproducible and lets you render stills at arbitrary times for review.
- Render speed: ~3 s of wall-clock per second of video at 1080p (52 s video ≈ 2.5 min).
  Run full renders with a 10-minute timeout.
- Measure layout only after `document.fonts.ready`, then set `window.ready = true`; the
  renderer waits for it. Font loading from `file:///` works with `--allow-file-access-from-files`.
- Use `url.pathToFileURL()` for file URLs rather than string-replacing slashes (already done in
  `scripts/render.js`).

## Layout bugs that stills caught

- `:nth-of-type` counts element *types*, not classes: `.task:nth-of-type(1)` matched nothing
  because all children are `div`s. Use `:scope>:nth-child(n)`.
- A container with a border (a table) was visible and empty before its rows animated in.
  Animate the container together with its first child.
- Labels under tiles wrapped onto two lines. Give them `white-space:nowrap` and more width.
- The third answer overflowed the chat area and scrolled the user's question out of view.
  Shorten content (stats inline instead of on a second line, shorter text) before relying on
  auto-scroll.

→ Always render stills at every scene's busiest moment **and** at every transition, tile them
with `scripts/contact_sheet.py`, and look at the sheet before the full render.

## Audio

- You can't listen. Check with numbers instead: the `report()` output of `audio_lib.py`.
- The first mix was bass-heavy (75 % of energy below 250 Hz) and the SFX sat 15–20 dB under the
  music. On laptop speakers that sounds dull and the effects get lost. Fixed values are now the
  defaults in `audio_lib.py` (kick 0.36, bass 0.14, pad lowpass 2600 Hz, SFX gain 1.0,
  typing clicks 0.22–0.32, impact 0.32). Target: under ~65 % below 250 Hz, mix RMS −15 to −17 dBFS,
  no clipping.
- Every SFX cue time is copied from the animation timeline. If the page uses seeded randomness
  (the flurry), replicate the same generator in Python so pops match cards and pan with
  their x position.
- Always tell the user the audio is unheard and ask them to check it on headphones and laptop
  speakers.

## Content

- Don't name AI clients or partners a feature doesn't officially support yet, and mark
  fictional data.
- Show only what the product really does. A scene about automation ends on a result the user
  confirms, unless the feature really acts by itself. Check whether a feature is still labelled
  beta before showing or hiding the label.

## Brand Listening video

- A screen that switches off with `visibility:hidden` still shows children that `pop()` set to
  `visibility:visible`, so the report bled through the search screen. Switch whole screens with
  `display:none` (the `screen()` helper in the Brand Listening build does this).
- `.h1:nth-of-type(1)` matched a decorative `div` placed before the headlines. Select headline
  lines by index (`$$('#s1 .h1')[0].children`) instead.
- Flurry cards spread over the full frame covered the left caption column. Keep them at
  x ≥ 730 while a caption is on screen.
- A six-word headline at 112 px ran wider than 1920 px. Break kinetic headlines at three or four
  words per line.

## Music that stays our own

- The engine started with one fixed bed (I-V-vi-IV at 120 BPM) that other brands' videos built
  on the same engine share, so every video sounded alike. `music_bed()` now draws key,
  progression, tempo, arp pattern, lead sound and drum feel from the video's `seed` (its slug)
  and fits the tempo so the drop sits on a bar line and the other section changes on beats.
  That bed and 118.5-121.5 BPM are excluded. Never pass settings that recreate it, and give
  every video its own seed.
- Section times have no defaults any more: take them from the video's own timeline, and check
  the "offset from nearest beat" line the bed prints (the fit aims for under 0.06 s).

## Hotel Solenne round

- `contact_sheet.py` tiles every PNG in the folder, so stills from an earlier round showed the
  old brand next to the new one. Delete `stills/` before re-rendering stills for a new round.
- Adding one character to a typed prompt (one more click) moved the mix RMS by about 1 dB,
  because the mix is peak-normalized. Re-read the level report after any SFX change, however
  small, and nudge `music_rms_db` if it leaves the -15 to -17 dBFS window.
- Off-topic posts in a listening flurry work best as real collisions with the brand name
  ("Solenne album review", "Baby names like Solenne"), not random noise.


## Vertical Reels/TikTok cut

- `render.js` had a fixed 1920×1080 viewport, `contact_sheet.py` squashed every still into a
  16:9 tile and `deliverables.py` always made a 1280×720 thumbnail. All three now follow the
  page's `<meta name="video-size">`. Look at a vertical sheet, not a squashed one, before
  judging layout.
- A 15 s cut leaves ~1 s per beat: one story (type the website → report → one mention), captions
  of 3–6 words, and the hook visible on frame 1 (start the first words at a negative time).
- 27 flurry cards at random positions buried the vertical UI card. 15 cards on a jittered
  two-column grid read as "a lot of posts" and leave the UI legible.
- A scroll that stops mid-block leaves a half-cut label at the top of the window. Scroll to a
  block's top edge (or drop the label) and fade out what scrolls away.
- The system scipy stopped loading after a macOS update (dlopen `__thread_bss` error). A venv
  in the build folder with a fresh scipy fixed it.


## Real posts and example brands

- One cut used a real, well-known brand's posts and had to be rebuilt with a made-up brand
  before it could go on public channels: a recognisable person's photo, other people's
  pictures and private handles were on screen, and the story read as if that brand were a
  customer. Ask where the video will be published before building (stage 1, step 3).
- Another cut went the other way: made-up posts where the requester wanted real ones for an
  internal demo. Settle the data source in the storyboard, not after the render.
- A popular brand fills one page of results in minutes. "Today" was the honest window, and the
  count is what the search returned, not the brand's daily total. Say that when you hand over.
- A hashtag search on a big brand returns mostly reseller listings. Quote the posts that read
  as opinions and say that you picked them.
- A platform whose search fails on the day is left out of the video, not estimated.

## Music bed

- `fit_tempo` needs a bar line at or before `soft_start`. With `soft_start=0` no tempo
  qualifies; a video with no quiet intro uses about 1 s.
