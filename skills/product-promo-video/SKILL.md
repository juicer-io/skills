---
name: product-promo-video
description: >
  Produce a short, on-brand product promo video (a motion-graphics "SaaS launch video": kinetic
  text, animated product UI, 2-3 use cases, under a minute, no voiceover) as a rendered MP4,
  from storyboard through a silent v1 to a v2 with self-synthesized, licence-free music and
  sound effects. No video editor, no stock music, no screen recording: the video is a web page
  filmed frame by frame. Use whenever someone wants a video that shows what a product feature
  does: "promo video", "launch video", "motion-graphics video", "explainer video", "animated
  feature video", "a short video for the help article / feature page / LinkedIn / Reels".
  Also use for follow-up rounds on a video this skill made ("shorten this scene", "different
  music", "German version", "v3"). Not for narrated walkthroughs cut from a real screen
  recording, webinar run sheets, still images or lists of video ideas.
license: MIT
---

# Product promo video

**Built by the [Juicer](https://www.juicer.io) team.** This is the skill we use for our own
product videos. It ships with the Juicer brand as the worked example: colours, logo files and
two finished templates. Licence: MIT, use and adapt it freely. Feedback and fixes are welcome
as issues or pull requests on the repository this skill came from.

Build a motion-graphics product video in three reviewed stages: storyboard → review → silent
v1 → review → v2 with music and SFX. The reference implementation is the Juicer MCP video in
`templates/mcp-video/` (storyboard, `index.html`, `audio.py`). Start from it; don't reinvent the
engine.

**What this skill is for:** it animates a mocked-up UI with on-screen text and synthesized
music (no recording, no voice). A narrated "how to set it up" walkthrough cut from a real screen
recording is a different job and needs different tooling. If the requester is unsure, a promo
for a feature page or a social feed is this skill.

**Reply in the user's language and keep replies short.** On-screen text is **American English**
by default; other languages only on request. No em dashes in on-screen text.

## Make it yours first

Before the first video for another brand, do this once and keep the result in the project:

1. Replace the three files in `assets/` with the brand's logo (a version for dark backgrounds,
   one for light backgrounds and the mark alone).
2. Rewrite `references/brand-video-spec.md` with the brand's colours, fonts and logo rules.
   Keep the sections on frame sizes, safe zones, text sizes and motion: they are not brand
   specific.
3. In the template `index.html` you start from, change the colours, the font names in the
   `@font-face` block, the logo and the background lettering.
4. Pick a made-up example brand for demo data and keep it for every video.

Never deliver a video for another company in the Juicer look.

## Requirements

- Node.js and Google Chrome (or `CHROME_PATH` pointing at a Chromium-based browser)
- Python 3 with `numpy`, `scipy`, `pillow` (`pip3 install numpy scipy pillow`). If
  `import scipy.signal` fails (a system scipy built for an older macOS fails with a dlopen
  `__thread_bss` error), make a venv in the build folder instead:
  `python3 -m venv .venv && .venv/bin/pip install numpy scipy pillow`, then run the Python
  scripts with `.venv/bin/python`.
- The brand font installed locally. The bundled example uses **Proxima Nova** or the free
  **Montserrat**
  (`~/Library/Fonts/Montserrat-{Regular,SemiBold,Bold}.ttf`). See
  `references/brand-video-spec.md`.
- No Remotion (company licence required) and no system ffmpeg needed: `ffmpeg-static` brings its
  own.

## Where the work lives

Each video gets `workspace/<slug>-video-build/` in the project you are working in. Storyboard, `index.html`, scripts, assets, stills and every delivered
MP4 stay there, so later rounds never depend on a temp directory.

## The three stages and their stops

The user reviews twice. Stop after stages 1 and 2 and wait. Don't run ahead into the next stage
"to save time". A storyboard change is cheap, a re-render costs minutes, a changed script after
audio costs both.

### Stage 1 · Storyboard → STOP

1. **Collect context before writing.** Read what exists: the feature page, the help article,
   the ticket or brief, customer requests, the requester's note and a screenshot of where the
   video goes. Pull use cases from real demand rather than inventing them.
2. **Know the placement.** It decides length, aspect ratio and text size (see
   `references/brand-video-spec.md` → readability). A help-article or dashboard embed is watched
   at ~640 px.
3. **Decide where the on-screen data comes from, before writing.** Ask where the video will be
   published. This decides whether the finished video can be used at all, so get the answer
   before building.
   - **Public channels:** use the brand's own accounts, a customer who agreed in writing, or a
     made-up example brand with invented posts and handles and pictures without recognisable
     people, labelled "Example brand · example data" on screen. Never build a public video on
     a third party's posts, photos or handles: it reads as if that brand were a customer.
   - **Internal demos and sales calls:** real public posts are fine.
   - **When you use real social posts,** pull them fresh for this video. With the Juicer MCP
     server connected (the `juicer` skill in the same repository), `get_data_posts` returns
     posts for a handle, hashtag or keyword, one call per platform; each call spends API
     credits, so the first page per platform is enough. Save the raw results to `data/` and
     the pictures to `media/` the same day, because media links expire within days.
   - Pick one time window that every platform's page covers ("this week", "today"), count only
     the posts inside it and name the window on screen.
   - On-screen numbers are counts from the pull, nothing else. A platform whose call failed is
     left out, not estimated; say so in the reply.
   - Write `sources.md` in the build folder: each search, returned vs counted, the link of
     every quoted post and what was left out.
4. **Write the storyboard** with `references/storyboard-template.md`: scenes with timings, the
   exact on-screen text, the prompt/action per use case, the example data, and an "Open for
   review" list. Save it as `workspace/<slug>-video-build/storyboard-EN.md`.
5. **Defaults** (state them in the reply so the user can overrule; don't ask about each one):
   - ~50 s, never over 60 s · 16:9 1920×1080 MP4 · no voiceover, no presenter. Another frame
     when the placement asks for it (9:16 for Reels/TikTok/Shorts, 1:1 or 4:5 for feeds; see
     `references/brand-video-spec.md` → Frame). A 15 s social cut carries one idea, not 2–3
     use cases
   - show the value by showing it: **2–3 use cases, no setup instructions**
   - example data from a made-up brand with an "Example data" pill, unless step 3 settled on
     real posts. The bundled example brand is **Hotel Solenne** (`hotelsolenne.com`,
     `@hotelsolenne`, `#stayatsolenne`); keep every example name and handle made up. Never
     show customer data or internal numbers
   - neutral UI (e.g. an "AI assistant" chat window without Claude/ChatGPT branding); for
     dashboard features, a simplified mockup in the product's dashboard style; for embed features,
     a simplified feed on a fictional website
   - English, no music in v1
6. **On-screen copy** is friendly, plain and benefit-first. Use the product's official feature
   names. Check every claim against the product itself (its code, its documentation or the
   live app) before it goes in the storyboard:
   - a feature, platform or option is shown only where it really exists
   - code on screen is checked line by line against the API documentation: paths, parameter
     names, id types and the exact spelling of values
   - never show prices or plan limits on screen (they change; point to the pricing page) and
     never imply a paid feature is on every plan
   - label beta or early-access features as such, or leave them out
   - scenes that show automation end on a result the user controls, unless the feature really
     acts by itself
   - don't name AI clients or partners a feature doesn't officially support
   - don't use internal code names
7. Reply: the file, the scene list in 5 bullets, the defaults in one line, and ask whether it
   fits. Then stop.

### Stage 2 · Silent v1 → STOP

1. **Set up the build folder** (tell the user in one line that you install two npm packages):
   ```bash
   cd workspace/<slug>-video-build
   npm init -y && npm install puppeteer-core ffmpeg-static
   ```
   Copy `scripts/render.js`, `scripts/contact_sheet.py`, `assets/` and
   `templates/mcp-video/index.html` from this skill into it.
2. **Write `index.html`** by adapting the template: same stage, background, logo, caption
   column, `seek(t)` engine and helpers (`pop`, `words`, `useCase`, `cap`), new scenes and UI.
   Set `window.DURATION`, `window.FPS`, and `window.ready = true` after `document.fonts.ready`.
   Follow `references/brand-video-spec.md` (colors, type, logo rules, text sizes, motion).
   Keep the timeline times in one place: the audio in stage 3 copies them.

   **Use the brand, never a generic look.** In the bundled Juicer example: navy background, coral as the one accent,
   white-text logo top-left, all text in the brand font family `G` (Proxima Nova or Montserrat).
   The Helvetica fallback only keeps a render from breaking; a video in it is not deliverable.
   `render.js` prints `WARNING: brand font not loaded` when that happens: install the font, then
   render again.
3. **Check stills before the full render.** Render the busiest moment of every scene plus every
   transition, then tile them:
   ```bash
   node render.js index.html stills stills 1.5,4.5,7.5,11,17.5,26.5,28.3,32,43,47.8,51
   python3 contact_sheet.py stills
   ```
   Look at the sheet. Typical faults are in `references/lessons.md` (empty containers showing
   early, overflow, wrapped labels, wrong selectors). Fix, re-check the affected frames.
4. **Render** `node render.js index.html video <slug>-video-v1.mp4` (≈ 3 s per video second;
   allow a 10-minute timeout). Render a second set of stills at the transitions to catch
   glitches, fix, re-render if needed.
5. **Write the transcript.** A video needs a text alternative (WCAG 1.2.1 / 1.2.3). Save `<slug>-video-transcript.md`: every on-screen
   line in order plus a one-sentence description per scene. It goes next to the video wherever
   it's embedded (below the player in the help article, or in a `<details>` on the page).
6. Reply: what's in it, what you checked (stills, not a real-time viewing), what you changed
   from the storyboard, and where it will need hosting (help articles and marketing pages
   usually embed from YouTube, Vimeo or Wistia).
   Ask for changes to pacing, text or scenes. Then stop.

### Stage 3 · v2 with music and sound effects

1. **Audio is synthesized, not downloaded.** `scripts/audio_lib.py` generates a calm, upbeat
   electronic bed that is different for every video and an SFX palette (whooshes, pops, typing clicks, success
   ding, sparkle, impact) from oscillators and noise. No samples, no third-party tracks, so no
   licence question. If the user prefers a real track, offer to lay one they supply from a
   licensed library under the video; don't fetch stock music yourself.
2. **Write `audio.py`** for the video by adapting `templates/mcp-video/audio.py`; copy
   `scripts/audio_lib.py` next to it:
   - `music_bed()` takes `seed` (the video slug) and the section times from the video, none of
     them defaulted: `soft_start` (concept scene), `drop` (product UI appears), `build` (second
     use case), `breakdown` (UI leaves for the outro), `final_hit` (end card). `soft_start` must be later than the first bar line: a video with
     no quiet intro uses about 1 s, not 0. The seed picks
     key, chord progression, arp pattern, lead sound and drum feel; the tempo is fitted so the
     drop sits on a bar line and the other changes land close to one. Read the line it prints
     (style + offsets from the nearest beat) and put the style in your reply. If the user wants a
     different feel, change the seed or override one setting (`key`, `progression`, `arp`,
     `lead`, `feel`, `bpm`); never reuse another video's seed.
   - one SFX cue per visual event, at the exact timeline time: word pops on pills, whoosh on
     scene changes, `typing()` with the prompt's exact character count and rate, whoosh+pop on
     send, `ding()` when data arrives, small pops per answer item, `sparkle()` on the highlight,
     `impact()` on the end card. Pan cues with where they happen on screen.
3. **Run and read the report** (`python3 audio.py .`, a few seconds). You can't listen, so
   the numbers are your ears: no clipping, mix RMS −15 to −17 dBFS, energy below 250 Hz under
   ~65 %, SFX audible over the music at event times. Adjust gains before muxing.
4. **Mux** the finished silent video with the mix (no re-render):
   ```bash
   "$(node -e "console.log(require('ffmpeg-static'))")" -y -i <slug>-video-v1.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart <slug>-video-v2.mp4
   ```
5. **Deliver** `<slug>-video-v2.mp4`; keep `audio.py`, `music.wav`, `sfx.wav` (stems for anyone
   who wants to re-mix) in the build folder. Say plainly that the audio hasn't been heard and
   ask the user to check it on headphones and laptop speakers. Embeds must not autoplay with
   sound (WCAG 1.4.2).
6. **Thumbnail and subtitles** go with every delivered version. Write `cues.json` from the
   timeline: one `[start, end, "text"]` cue per piece of on-screen text a viewer reads
   (headlines, captions, typed prompts, key answers), at most two lines of 42 characters, no
   overlaps. Pick the thumbnail frame: a use-case moment with its caption and the UI filled in,
   rendered as a still. Then run
   ```bash
   python3 deliverables.py cues.json <slug>-video-v2 stills/<frame>.png
   ```
   It writes `<slug>-video-v2.srt` (YouTube, most players), `.vtt` (Wistia, Vimeo, web
   players) and a 1280×720 `-thumbnail.jpg`. Check the subtitle files load:
   `"$(node -e "console.log(require('ffmpeg-static'))")" -loglevel error -y -i <slug>-video-v2.srt /tmp/check.ass`.
   Mark any cue that isn't literal on-screen text in your reply.

## Later rounds

Version every delivery (`v3`, `v4`) and never overwrite a version the user has already seen.
Text or timing changes: edit `index.html`, re-check stills, re-render, then shift the matching
cues in `audio.py`, re-mux, and update the transcript, `cues.json`, subtitles and thumbnail. Language versions: translate the
on-screen text, then check line breaks in stills. German runs ~30 % longer.

## Files in this skill

- `references/brand-video-spec.md`: frame, background, logo rules, colors, type, text sizes for
  small embeds, layout, motion vocabulary. Read before stage 2.
- `references/lessons.md`: what went wrong before and how it was fixed. Read before stage 2 and
  before stage 3; add new lessons at the bottom.
- `references/storyboard-template.md`: storyboard structure and scene budget.
- `templates/vertical-15s/`: 15 s 9:16 Brand Listening cut for Reels/TikTok (storyboard,
  `index.html` with the safe zone and a `T` timeline object, `audio.py`, `cues.json`). Start a
  vertical or short social video from it.
- `templates/mcp-video/`: Juicer MCP example (storyboard, `index.html`, `audio.py`). It renders
  and its audio checks pass, but its content hasn't been reviewed with anyone yet.
- `scripts/render.js`: stills and MP4 renderer. `scripts/contact_sheet.py`: still sheet.
  `scripts/audio_lib.py`: music bed, SFX palette, mix and level report.
  `scripts/deliverables.py`: `.srt` + `.vtt` subtitles and the thumbnail.
- `assets/wordmark.svg` (white-text logo for navy), `assets/logo-dark.svg` (navy-text logo for
  white), `assets/icon.svg` (the mark alone).

