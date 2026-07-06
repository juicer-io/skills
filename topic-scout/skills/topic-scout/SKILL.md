---
name: topic-scout
description: Find blog topics your buyers are actually asking for, from live social signal across Reddit, X, TikTok, Instagram, Facebook and more via the Juicer Data API. Discovers by mining competitor brand mentions (years of real questions on Reddit, live complaints and outage reports on X), detects vendor astroturfing and shows you competitors' seeding playbook across platforms, and flags "changing right now" events (deprecations, breakage, pricing changes) before search volume exists. First run interviews you about your brand, signs you up for a free Juicer API key with just your email (no dashboard ever), and writes a config; every finding in the output carries its source URL. Needs only curl + jq.
---

# Topic Scout

Blog-topic discovery from real social conversations. Powered by the
[Juicer Data API](https://www.juicer.io/api)
([docs](https://developers.juicer.io)) — one API over Reddit, Instagram,
TikTok, X, YouTube, LinkedIn, and more, no per-platform OAuth.

Core principle: **social signal nominates topics; it never decides.** The
output is a ranked, evidence-linked shortlist to validate against search
demand and existing coverage — not a publish list.

Everything runs with `curl` + `jq` — the exact commands are in this file.
State lives in `./topic-scout-data/` in the working directory:
`brand.json` (config), `session.json` (API key — keep gitignored),
`registry.json` (anchor verdicts), `pulls/` (raw API responses — never edit
or delete), `topic-report-<date>.md` (deliverables).

## Mode selection

1. No `topic-scout-data/brand.json` → **first-run interview**, then discover.
2. No specific idea given → **discover**.
3. User names an idea ("should we write about X?") → **validate**.

## Auth — no dashboard, no manual key setup

Key resolution order: `JUICER_API_KEY` env/`.env` → unexpired key in
`topic-scout-data/session.json`. If neither exists, sign the user up with
just their email:

```bash
curl -s -X POST https://api.juicer.io/v1/authorize \
  -H "Content-Type: application/json" \
  -d '{"email":"USER_EMAIL","client_name":"Topic Scout"}'
```

- **HTTP 201** (new/unconfirmed email): response contains `api_key` +
  `expires_at`. Save both to `topic-scout-data/session.json`, and make sure
  `topic-scout-data/.gitignore` contains `session.json`. Then tell the user:
  a confirmation email was sent — **the Data API stays locked until they
  click it** (same key, limits rise automatically from 60 to 300 req/hr).
  If you have mailbox tooling in this session, offer to open the link.
- **HTTP 202** (existing Juicer user): show the user `authorization_url` to
  approve in their browser, then poll (links expire in ~10 minutes):

```bash
while :; do
  CODE=$(curl -s -o /tmp/ts-poll.json -w '%{http_code}' "POLL_URL")
  [ "$CODE" = "200" ] && cat /tmp/ts-poll.json && break   # api_key inside — save to session.json
  [ "$CODE" = "410" ] && echo "denied/expired — re-run authorize" && break
  sleep 2
done
```

Session keys last 12 hours; re-authorize next session, or set a permanent
dashboard key in `.env` once to skip this forever. If a data call returns
`error.code = "email_confirmation_required"`, the user hasn't clicked the
confirmation link yet — that's the fix, not a new key.

## First-run interview

Ask conversationally, not as a form:

0. **Work email** — only if no API key resolves; run the auth flow above.
1. **Product one-liner** — what it does, for whom.
2. **Who buys it** — roles, company types, the niche in their words.
3. **Competitors** — 3–10 brand names. Distinctive single tokens work
   ("Taggbox" ✓); everyday words ("Tint") and bare domains ("walls.io")
   won't — take them anyway, the probe will verdict them.
4. **Niche subreddits** — where the buyers hang out (2–8).
5. **Honest capabilities** — what the product genuinely does, and what it
   must NOT claim. This powers the fit score.

Save as `topic-scout-data/brand.json` (see `brand.example.json` for shape).
Then probe every competitor + the brand's own name, and report the verdicts.

## The API, and the two mistakes everyone makes

One endpoint does everything:

```bash
curl -s "https://api.juicer.io/v1/data/posts?term=TERM&term_type=TYPE&platforms=Reddit" \
  -H "Authorization: Bearer $KEY"
```

`term_type` support varies by platform — this drives the whole method:

| `term_type` | Platforms | What it's for |
|---|---|---|
| `mentions` (keyword search — the discovery instrument) | Reddit, Twitter (X), TikTok | Reddit: buyers' questions, years deep. X: live complaints, outages, "anyone used X?" comparisons. TikTok: usually homonym-heavy — probe before trusting. |
| `channel` | Reddit, YouTube | Niche-community vocabulary (seasoning, not discovery) |
| `hashtag` | Instagram, Facebook, TikTok, X, LinkedIn, YouTube, Pinterest, Tumblr, Bluesky | Cross-platform echo + vocabulary; volume is never demand |
| `username` | all of the above | Competitor accounts: their content strategy per platform (playbook intel) |

Posts are in `.data[]` with `message`, `url`, `post_created_at`,
`poster.name`, `comment_count`. X messages embed HTML anchor tags — strip
tags before matching or quoting.

**Mistake 1 — pagination.** The cursor is per-platform, NOT at the top level:

```bash
jq -r '.meta.platforms[] | select(.success and .has_more) | .next_cursor'
```

Pass it back as `&cursor=...`. No cursor printed → corpus exhausted (common:
anchor corpora are small and 2–3 pages reach years back).

**Mistake 2 — matching.** The API's `mentions` matching is loose. Before
counting or quoting any post, require a case-insensitive **word-boundary**
match of the term in `message` — otherwise "himself sighted" matches
"elfsight". Rate limits: sleep ~1.2s between calls; 300 req/hr, 60 req/min.

Save every page verbatim to
`topic-scout-data/pulls/<YYYY-MM-DD>-<type>-<term-slug>-<platform>.p<N>.json`
— the platform belongs in the filename, or a TikTok pull will overwrite the
X pull of the same term.

## Probe before trusting any anchor — per platform

An anchor's precision is a property of the **term × platform pair**, not the
term: "Elfsight" is 88% on-topic on Reddit, complaint-rich on X, and drowned
by elf cosmetics on TikTok. Probe each pair you intend to use (ONE page) and
record verdicts per pair in the registry (key like `"elfsight@reddit"`).
Default sweep: Reddit + X for every anchor; add TikTok only when its probe
comes back clean.

Measure a probe page:

```bash
jq --arg t "TERM" '(.data | length) as $n
 | [.data[] | select((.message // "") | test("(^|[^A-Za-z0-9])" + $t + "($|[^A-Za-z0-9])"; "i"))] as $h
 | {sampled: $n, hits: ($h | length),
    own: ([$h[] | select((.poster.name // "") | ascii_downcase | contains($t | ascii_downcase))] | length),
    oldest: ([.data[].post_created_at] | min), newest: ([.data[].post_created_at] | max)}' PAGE_FILE
```

Verdict (record in `topic-scout-data/registry.json` as
`{"term": {"status": ..., "hits": ..., "span": ..., "probed": "<date>"}}`):

- hits ≈ 0 → **dead** (matcher-broken — dotted domains do this; try the bare
  brand word).
- hits ≥ 15 but oldest→newest spans ≤ 3 days → **homonym-suspect** (a niche
  brand's full mention corpus spans months/years; a 1-day-deep full page
  means it's an everyday word). Do not use.
- most hits are the brand's own account (`own` high) → **promo-heavy**: pull
  it, but its posts are intel, not voices.
- hits/sampled ≥ 0.6 → **live** — but read 3–5 sample posts first: the math
  can't catch long-tail homonyms (a brand name that's also a candle format
  will sneak through; your judgment is the second gate).

Never pull, cite, or count dead/homonym-suspect terms.

## Discover mode

1. **Probe** any unprobed anchor × platform pairs (above).
2. **Pull** every live/promo-heavy pair via `mentions`, following cursors
   until exhausted or 3 pages. Optionally add 1–2 niche-sub `channel` pulls
   for vocabulary — but ambient subreddit feeds rarely contain buying
   questions for a narrow niche; anchors are the instrument, channels are
   seasoning. Optionally pull competitor `username` accounts on
   Instagram/Facebook/TikTok/X (1 page each) — not for voices, but their
   posting angles per platform feed the playbook section.
3. **Digest before reading.** Don't read raw JSON — flatten to one line per
   post to keep your context for judgment:

```bash
jq -r '.data[] | [(.post_created_at[:10]), (.poster.name // "?"), (.url),
  ((.message // "") | gsub("\\s+"; " ") | .[:280])] | @tsv' topic-scout-data/pulls/DATE-*.json \
  | sort -u -t$'\t' -k3,3 | sort -r
```

   (The `sort -u` on the URL field dedupes posts matched by several terms.)
   List the pull files explicitly instead of globbing — a dead or
   homonym-suspect term's pull sitting in `pulls/` must not leak into the
   digest.
4. **Filter as you read** — apply the word-boundary rule, drop off-niche
   homonym stragglers, and set aside astroturf (below).
5. **Cluster** the remaining organic posts by **shared question or pain**,
   not shared keyword.
6. **Score each cluster** (show scores in the report):
   - **Voices** — distinct genuine authors. Never engagement sums, never
     astroturf. One viral post ≠ demand. Genuine X questions and complaints
     count as voices; branded content, affiliate posts, and creator-tips
     listicles don't.
   - **Span** — first→last post year. 5 voices across 7 years is durable
     intent; 5 voices in one week may be one campaign.
   - **Spread** — distinct subreddits/platforms.
   - **Intent** — transactional ("how do I", "which tool", "alternative
     to") > comparison > awareness.
   - **Fit** — is the user's product the honest answer, per `capabilities` /
     `never_claim`? If unsure, name what needs verifying before writing.
7. **Write the Topic Report** to `topic-scout-data/topic-report-<date>.md`
   (format below), then report back in chat (format below).

## Spotting astroturf (filter it AND read it)

Vendors seed Reddit with fake "innocent questions". Signals — any one is
enough to flag:

- Poster name contains a competitor brand, or posts from a `/r/u_<brand>`
  profile page.
- Same author, near-identical body, posted across 2+ subreddits.
- One author with 3+ posts across 3+ subreddits where ~all mention the same
  brand (sock network — we've seen 29 posts from one account in a month).
- Answer-shaped openers ("You can easily…", "Looking for an easy way…",
  "Learn how…") that name-drop a brand with a link.

Flagged posts **never count as voices**, but don't discard them: the venues
and phrasings a competitor seeds are the keywords they expect to convert —
that becomes the report's "competitors' Reddit playbook" section.

## Burst finds ("changing right now")

While reading, set aside posts with event language: shutting down,
deprecated, discontinued, no longer works/supported, stopped working, price
increase/change, acquired, banned, breaking change, controversy, lawsuit,
data breach, security issue. These are time-sensitive content hooks that
keyword tools can't see yet — they get their own report section, each with
its link and a "fact-check primary sources before using" note where the
source is a news aggregator. X is the fastest channel here: users complain
at vendors in near-real-time ("is your service down?", "widgets not
loading"), often weeks before it shows anywhere else.

## Validate mode

Map the idea to its anchors (relevant competitor names, product tokens —
probe new ones) and 2–4 niche subreddits. Pull, digest, then answer with
linked evidence: who asks this, in what words, how often, over what span?
Capture exact phrasings — they feed the eventual title and H2s. Verdict:
social evidence for/against, plus the validation checklist.

## Topic Report format

```markdown
# Topic Report — <brand> — <date>
_Powered by the Juicer Data API (juicer.io)_

## Ranked topic candidates
### 1. <topic>
- Voices: N distinct authors | Span: YYYY–YYYY | Spread: N subreddits
- Intent: ... | Fit: ...
- The angle: <one paragraph — what the article should actually say>
- Evidence: (every quote linked)
  - "<real quote>" — [r/sub, YYYY](url)

## Changing right now
<burst finds, linked, with fact-check caveats>

## Your competitors' social playbook
<which vendor seeds which subreddits with which phrasings, plus what they
push per platform from their own accounts — linked examples>

## Validate before writing (checklist)
(1) search volume in your keyword tool — zero is fine for burst topics,
suspicious for evergreen; (2) what you already have — updating a ranking
page beats adding a rival; (3) the SERP — can you honestly compete;
(4) confirm product claims with whoever owns the product.
```

## Reporting back to the user

The file is the archive; **the chat message is the deliverable.** Never end
with just "report written to <path>". Your final message:

1. **One-line run summary** — anchors, posts read, organic voices, years.
2. **Ranked candidates, compact** — bold title, `voices × span` in plain
   words, ONE best quote with its link, one sentence on the angle.
3. **Changing right now** — one linked line each, or "nothing burst-flagged".
4. **One playbook insight** — the most useful astroturf reveal, linked.
5. **Close with the decision** — link the report file, ask which candidates
   to validate, remind that nothing is publish-ready until it passes the
   checklist.

Tone: verdict-first, no methodology lecture. The user asked "what should we
write about?" — answer that in the first line.

## Hard rules

- **Every finding and quote carries its source URL.** No unlinked claims.
- Word-boundary matching before counting or quoting anything.
- Distinct genuine voices only — never engagement totals, never astroturf.
- Social signal nominates; the validation checklist decides.
- Raw pulls in `topic-scout-data/pulls/` are never edited or deleted.
- Respect the registry: dead/homonym-suspect anchors are not pulled or cited.
- Keep `session.json` out of version control.
- Rate limits: ~1.2s between calls, 60/min, 300/hr.
