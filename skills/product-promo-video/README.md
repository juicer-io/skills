# product-promo-video

A skill that makes short motion-graphics product videos from a storyboard, with no video
editor. Built by the [Juicer](https://www.juicer.io) team. Licence: MIT.

## This skill runs code on your computer

Read this before you install it. Unlike the `juicer` plugin in this repository, which is text
only, this skill contains scripts:

| File | What it does |
|---|---|
| `scripts/render.js` | Opens the video page in your local Chrome and saves it frame by frame |
| `scripts/audio_lib.py` | Synthesizes the music and sound effects on your machine |
| `scripts/deliverables.py` | Cuts the formats, subtitles and thumbnail with ffmpeg |
| `scripts/contact_sheet.py` | Lays out still frames on one sheet for review |
| `templates/*/audio.py`, `templates/*/index.html` | The two worked examples |

- The scripts make no network calls and send nothing anywhere.
- They read and write only the files and folders you point them at.
- You install two npm packages yourself in that folder: `puppeteer-core` and `ffmpeg-static`.
- It does not need a Juicer account or an API key.

Read the scripts before you run them. They are short.

## Install

```bash
cp -r skills/product-promo-video ~/.claude/skills/
```

Then ask your agent for a promo video. The skill starts with "Make it yours first": swap the
Juicer colours, logo and fonts for your own before the first render.
