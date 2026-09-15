---
name: mention-scout
description: Find live conversations where your brand can genuinely join in — across Reddit, X and more via the Juicer Data API. Surfaces fresh recommendation-asks ("best tool for…?"), competitor complaints and outage threads, comparison discussions, and unanswered mentions of your own brand, then ranks them by how answerable they are. Built for disclosed, helpful engagement — it flags competitor-seeded (astroturf) threads as traps to avoid, never as opportunities. Every opportunity carries its source URL. Needs only curl + jq.
---

# Mention Scout

Find the conversations your brand should be part of — and how to show up
well. Powered by the [Juicer Data API](https://www.juicer.io/api)
([docs](https://developers.juicer.io)) — one API over Reddit, X, Instagram,
TikTok, YouTube, LinkedIn, and more, no per-platform OAuth.

Core principle: **engage, don't astroturf.** This skill finds places where a
disclosed, genuinely useful reply earns attention. It will not help you seed
fake questions or drop undisclosed links — its sibling skill (topic-scout)
literally detects that behavior, and so do Reddit moderators.

State lives in `./mention-scout-data/` in the working directory:
`brand.json`, `session.json` (gitignore it), `registry.json` (anchor
verdicts), `pulls/` (raw API pages — never edit or delete),
`mention-report-<date>.md` (deliverables). **If `./topic-scout-data/brand.json`
exists (sibling skill), reuse it instead of re-interviewing** — same schema.

## Auth — no dashboard

Key resolution: `JUICER_API_KEY` env/`.env` → unexpired key in
`mention-scout-data/session.json` (or the sibling's `topic-scout-data/session.json`).
None? Sign the user up with just their email:

```bash
curl -s -X POST https://api.juicer.io/v1/authorize \
  -H "Content-Type: application/json" \
  -d '{"email":"USER_EMAIL","client_name":"Mention Scout"}'
```

- **201** (new email): save `api_key` + `expires_at` to `session.json`; the
  user must click the confirmation email before data calls work (same key,
  limits rise automatically).
- **202** (existing user): show `authorization_url`, poll `poll_url` every
  2s until 200 (key inside) or 410 (denied/expired).

Session keys last 12 hours. A data call returning
`error.code = "email_confirmation_required"` means click the email, not get
a new key.

## First-run interview

If no brand config exists (check `topic-scout-data/brand.json` first), ask
conversationally: product one-liner · who buys it · 3–10 competitor brand
names · niche subreddits (2–8) · what the product can honestly claim and
must never claim. Save as `mention-scout-data/brand.json`. Additionally, for
this skill, ask:

- **Who replies?** The account that will post (founder, brand account,
  devrel) — recommendations are framed for that voice.
- **Disclosure line** — e.g. "(I work at Acme)". Every suggested reply
  includes it.

## The API

```bash
curl -s "https://api.juicer.io/v1/data/posts?term=TERM&term_type=TYPE&platforms=PLATFORM" \
  -H "Authorization: Bearer $KEY"
```

- `mentions` (keyword search): Reddit, Twitter (X), TikTok.
- `channel` (subreddit feed): Reddit. `hashtag`: IG/FB/TikTok/X/LinkedIn/YouTube.
- Posts in `.data[]`: `message`, `url`, `post_created_at`, `poster.name`,
  `comment_count`. X messages embed HTML tags — strip before quoting.
- Pagination cursor is per-platform:
  `jq -r '.meta.platforms[] | select(.success and .has_more) | .next_cursor'`
  → pass back as `&cursor=...`.
- Word-boundary match terms in `message` before trusting any hit (the API
  matches loosely). Sleep ~1.2s between calls; 60/min, 300/hr.
- Save pages to
  `mention-scout-data/pulls/<date>-<type>-<term-slug>-<platform>.p<N>.json`.

Probe every new anchor term × platform with ONE page before relying on it
(word-boundary hit rate; ≥15 hits spanning ≤3 days = everyday-word homonym —
unusable; record verdicts in `registry.json`). Reddit and X are the default
platforms; TikTok only if its probe is clean.

## The sweep (discover mode)

Pull, newest-first — **recency is the point here** (unlike topic research,
old threads are worthless):

1. **Competitor anchors** via `mentions` on Reddit + X, 1–2 pages each:
   comparison asks ("anyone used X?", "is X worth it?"), complaints, outage
   reports.
2. **Your own brand** via `mentions` (if the probe says the token is clean):
   unanswered mentions, questions, misconceptions — the highest-priority
   replies of all.
3. **Niche subreddits** via `channel`, 1–2 pages: fresh question posts
   ("how do I…", "what tool…", "recommend…") where the product is an honest
   answer. Ambient feeds are the right tool here — you want live, answerable
   threads, not demand statistics.
4. Optionally X `hashtag` pulls on 1–2 category tags for live discussions.

Digest to one line per post before reading (keep context for judgment):

```bash
jq -r '.data[] | [(.post_created_at[:10]), (.poster.name // "?"), (.url),
  ((.comment_count // 0) | tostring),
  ((.message // "") | gsub("\\s+"; " ") | .[:240])] | @tsv' FILE1 FILE2 ... \
  | sort -u -t$'\t' -k3,3 | sort -r
```

## Scoring an opportunity

Rank every candidate thread on:

- **Freshness** — ≤30 days is prime; 30–90 days only if the thread is still
  getting comments; **never suggest replying to anything older than 90 days**
  (necro-posting reads as spam).
- **Intent** — direct recommendation-ask > competitor complaint/outage >
  open comparison > relevant discussion. A thread that *asks* is worth ten
  that merely mention.
- **Answerability** — comment_count sweet spot ~0–30: enough silence to be
  seen, not a graveyard. Skip locked/archived threads (Reddit archives at
  ~6 months).
- **Honest fit** — per `capabilities`/`never_claim`: can the brand's reply
  actually solve the asker's problem? If the honest answer is a competitor,
  skip the thread.
- **Venue safety** — flag subreddits known to ban self-promo; the report
  tells the user to check each sub's rules before posting.

**Astroturf check**: apply the sibling detection signals (same author
posting near-identical brand-dropping posts across subs; answer-shaped
openers with links; brand-named posters). A thread seeded by a competitor's
sock account is a **trap, not an opportunity** — engaging legitimizes it and
invites scrutiny. List these separately as "seeded threads — do not engage."

## Report format

Write `mention-scout-data/mention-report-<date>.md`:

```markdown
# Mention Report — <brand> — <date>
_Powered by the Juicer Data API (juicer.io/api)_

## Reply-worthy now (ranked)
### 1. [<thread title/ask>](url) — r/sub, <date>, <n> comments
- Why: <intent + fit in one line>
- Suggested angle: <2-3 sentences: what a genuinely helpful reply covers,
  where the product fits IF it does, ending with the disclosure line>
- Watch out: <sub rules / competing replies / anything>

## Your own mentions needing a response
<unanswered brand mentions, questions, misconceptions — linked>

## Seeded threads — do not engage
<astroturf-flagged threads with the vendor and tell-tale signs — linked>

## House rules
Always disclose affiliation. One reply per thread. Answer the question
first; mention the product only where it genuinely fits. Check each
subreddit's self-promotion rules before posting. Never reply to threads
older than 90 days.
```

## Reporting back to the user

The chat message is the deliverable — never just "report written". Final
message: one-line run summary (sources swept, threads read, opportunities
found) → top 3–5 opportunities each as one line (linked thread, date, the
ask, your angle) → own-mentions needing response → one "do not engage" note
if any → link the full report and ask which replies to draft. Offer to draft
replies — in the user's voice, disclosure included — as the natural next step.

## Hard rules

- **Every opportunity carries its source URL.** No unlinked claims.
- Disclosure line in every suggested reply. No exceptions, no "subtle" mode.
- Never suggest fake questions, sock accounts, or undisclosed promotion —
  if asked for that, decline and explain why it backfires (detection is
  trivial; this repo ships the detector).
- Never recommend necro-posting (>90 days) or engaging seeded threads.
- Word-boundary matching before counting or quoting anything.
- Raw pulls are never edited or deleted; keep `session.json` gitignored.
- Rate limits: ~1.2s between calls, 60/min, 300/hr.
