# Visual spec (worked example: Juicer)

This is Juicer's video spec, kept as the worked example. For another brand, replace the
colours, fonts and logo rules below with that brand's and keep the sections on frame, safe
zones, readability and motion.

## Frame

- 30 fps, H.264 MP4 (yuv420p, CRF 17, faststart). The placement picks the frame; 16:9 is the
  default:

  | Placement | Frame | `<meta name="video-size">` |
  |---|---|---|
  | Feature page, help article, YouTube (default) | 16:9 | `1920x1080` |
  | Instagram Reels, TikTok, YouTube Shorts, Stories | 9:16 | `1080x1920` |
  | LinkedIn / Instagram feed | 1:1 or 4:5 | `1080x1080` / `1080x1350` |

  Set the size with `<meta name="video-size" content="WxH">` in `index.html` and match `html,body`
  width/height to it. `render.js`, `contact_sheet.py` and `deliverables.py` follow it.
- **9:16 safe zone.** Instagram and TikTok draw their own UI over the top ~220 px, the bottom
  ~400 px and a ~140 px strip on the right (like, comment, share). Keep text, the UI mockup and
  the logo inside x 72–940, y 240–1500. Logo at top 240 px, not in the corner; "Example data"
  pill bottom-left of the safe zone, not bottom-right. Put the caption above the UI card, not
  beside it, and open on text from frame 1 (viewers swipe in the first second).
- Background: solid dark navy `#102738`, **no gradients** (a Juicer brand rule). For
  depth, the template drifts a huge outline "juicer" lettering (white stroke at ~7 % opacity)
  sideways. It is optional texture, not a brand element: drop it if the requester wants a
  cleaner look.
- White-text Juicer logo (`assets/wordmark.svg`) small in the top-left corner for the whole
  video, like the social posts. Height ~46 px at 1080p.

## Logo rules that constrain the edit

- The logo is the coral/orange mark plus the "juicer" word. Never recolour the mark on navy,
  never stretch it, never put other words right next to it ("juicer MCP" as a lockup). Write
  product names as normal text ("Juicer MCP") and keep the logo in its corner.
- On navy use `assets/wordmark.svg` (white word). On white cards use `assets/logo-dark.svg`
  (navy word). The mark alone (`assets/icon.svg`) works on white tiles and chips.
- On a coral background the coral mark disappears: use an all-white logo there (recolour the
  mark to white), or avoid coral full-frame backgrounds.

## Colour

| Use | Colour |
|---|---|
| Background | `#102738` |
| Brand accent: highlight words, pills, buttons, focus rings | coral `#F05B4A` (hover/darker `#E04A39`) |
| Coral text on white (small text) | `#CC4232` (the only coral that clears 4.5:1 on white) |
| Dark text on white cards, dark UI | `#1B2A3D` |
| Secondary text | `#4D5A66`, subtle `#6A737C` |
| Borders | `#E2E6EB`, strong `#C7CDD4` |
| Light fills (user bubble, callouts) | `#FEF0EE`, `#F7F8FB`, `#EEF1F6` |
| Headline text on navy | `#FFFFFF`; secondary `#A0AEC0`, body `#CBD5E0` |
| Positive (connected, approved, done) | `#1E6B41` on `#E7F4EC` |
| Negative (rejected, blocked) | `#A6342A` on `#FBEBE9` |
| Neutral / needs review | `#4D5A66` on `#EEF1F6` |

Coral is the brand colour: use it for the one thing per frame that matters. Green only for
positive states.

## Type

Juicer's brand font is **Proxima Nova**. The free **Montserrat** is the accepted stand-in (Bold headlines, SemiBold subheads, Regular body), which is
installed locally at `~/Library/Fonts/Montserrat-*.ttf`. The template declares one family `G`
that tries Proxima Nova first and falls back to Montserrat through `local()`; either counts as
on-brand. `render.js` warns `brand font not loaded` only when neither is found: install
Montserrat, or point `@font-face` at the font files with `file:///` URLs. A render in
Helvetica/system fallback is not deliverable.

Montserrat has no Medium (500) installed: the template maps 500 to SemiBold. No italics in the
video. Highlight words with coral colour, bold weight, or a coral pill with white text.

## Readability at embed size

Videos are often watched small (a dashboard help panel, a help-center article, a LinkedIn feed
on a phone). Everything must survive being divided by three:

| Element | Size at 1080p | ≈ at 640 px |
|---|---|---|
| Kinetic headlines | 110–120 px, semibold | 38 px |
| Side captions | 70–72 px, medium, bold highlight | 24 px |
| Chat / UI text | 28–30 px minimum | 10 px |
| Tiny labels (chips, badges) | 21–24 px, never smaller | 7–8 px |

So a UI mockup shows far fewer items than the real dashboard: three rows, three tasks, two
post cards. Fewer, larger elements beat a faithful screenshot.

## Shapes

Radii scaled for video: cards 18–28 px, tiles 40 px, pills 999 px.
Shadows soft and navy-tinted, e.g. `0 50px 120px rgba(4,14,24,.55)` for the main window.
White cards on navy.

## Layout that worked

- Kinetic text scenes centered.
- Product scenes: caption column left (x 104–704: step label pill "1/3 · Feed analytics" +
  headline), UI window right (x 760–1820, y 100–980).
- "Example data" pill bottom-right while fictional data is on screen.

## Motion vocabulary

- Words enter with a stagger (0.09–0.13 s), rising 70 px, blur 12 px → 0, easeOutCubic.
- Pills and tiles pop with easeOutBack (slight overshoot).
- The UI window flies in with a 3D turn (perspective 1800 px, rotateY −26° → 0, from +760 px).
- Typing: a fixed characters-per-second rate (24–28) with a caret; the send button squashes.
- Tool call: a grey chip with spinner that turns into a green check, then the answer builds
  item by item (0.3–0.35 s apart).
- Emphasis: a coral ring fades in on the key item, the window zooms in by 3 %.
- "Overwhelm → order" beat: dozens of social post cards (one per platform colour dot) pop in
  across the whole frame, a dark counter card counts up, then everything collapses into the
  tool chip and a short, sorted answer appears. It fits Juicer naturally: many sources → one
  curated feed, a full moderation queue → a clear plan.
- Scene exits: fade + 30–40 px upward drift + blur; never hard cuts.
