# Topic Scout

**Find blog topics your buyers are actually asking for — from real social
conversations, with a source link on every finding.**

A Claude Code skill powered by the [Juicer Data API](https://www.juicer.io/api)
([docs](https://developers.juicer.io)): one API over Reddit, X, Instagram,
TikTok, Facebook, YouTube, LinkedIn, and more.

## What it does

- **Discovers topics** by mining mentions of your competitors across Reddit
  and X (and TikTok where the probe comes back clean) — a distinctive brand
  name is a topical filter, so every thread mentioning one is a conversation
  in your niche. Reddit corpora reach back years (real questions in buyers'
  own words); X adds live complaints, outages, and "anyone used X?"
  comparisons. Every post carries its URL.
- **Detects astroturfing** — vendor sock accounts seeding "innocent questions" —
  and turns it into intel: a map of which competitor invests in which keywords.
- **Flags "changing right now" events** — deprecations, breakage, pricing
  changes — content hooks that exist before search volume does.
- **Scores honestly**: distinct voices × years of recurrence × subreddit
  spread × intent × fit with what your product can truthfully claim. Never
  engagement totals.
- **Interviews you on first run** and saves a brand config — no setup files to
  hand-write.

## What it deliberately does NOT do

Publish decisions. Social signal nominates; every report ends with a validation
checklist (search demand, existing coverage, SERP reality, product truth). Don't
skip it — we learned that the hard way.

## Install

**Claude Code:**

```
/plugin marketplace add juicer-io/skills
/plugin install topic-scout@juicer-skills
```

**Manual (any agent):** copy `skills/topic-scout/` into your agent's skills
directory. The skill is a single instruction file — your agent runs
everything with `curl` and `jq`. No other installs.

Either way there's no dashboard and no manual key setup: on first run the
skill asks for your email, provisions a free Juicer API key on the spot
(you'll click one confirmation link in your inbox), and gets to work.
Already have a key? Set `JUICER_API_KEY` and the skill uses it.

See [example-report.md](./example-report.md) for a real run.

## Usage

- `/topic-scout` — first run interviews you, then discovers.
- `/topic-scout should we write about <idea>?` — validate a specific idea
  against live social evidence.

Everything the engine collects lives in `./topic-scout-data/` (raw pulls,
anchor registry, dated topic reports).

---

Built by the [Juicer](https://www.juicer.io) team. The same API that powers
this skill powers embeddable social feeds and walls — if you ever need your
social content *on* your website, you know where the key works.
