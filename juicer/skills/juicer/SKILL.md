---
name: juicer
description: Social media data and feed API to search posts, brand mentions, hashtags, subreddits and profiles, and to aggregate, moderate and embed social feeds on any website, across 15+ platforms Reddit, X, Instagram, Facebook, TikTok, YouTube, LinkedIn, Pinterest, Bluesky, Tumblr, Vimeo, Flickr, Giphy and more
homepage: https://developers.juicer.io
metadata: {"openclaw":{"emoji":"🧃","requires":{"bins":["curl","jq"],"env":[]}}}
---

# Juicer API

Read BEFORE writing any code or curl against `api.juicer.io`, and whenever the
user mentions Juicer, wants posts, mentions, hashtags or a handle's content from
one or more social platforms, wants to monitor brand or competitor mentions, or
wants a social feed, social wall or social media embed on a website.

Do NOT use for publishing or scheduling posts to social networks, for a
platform's own native API, or for scraping.

## No install needed

Everything is `curl` + `jq` against `https://api.juicer.io/v1` with Bearer auth.
No CLI, no SDK, no dashboard required.

- OpenAPI spec (authoritative for every schema): https://developers.juicer.io/openapi/v1.yaml
- Docs: https://developers.juicer.io (append `.md` to any docs URL for markdown)
- Product page: https://www.juicer.io/api
- Skills repo: https://github.com/juicer-io/skills

---

| Property | Value |
|----------|-------|
| **name** | juicer |
| **description** | Social media data and feed API across 15+ platforms |
| **allowed-tools** | Bash(curl:*), Bash(jq:*) |

---

## ⚠️ Four Hard Rules (Read First)

**Rule 1 — Get a key before anything, and never mint a second one to escape a
confirmation gate.** Use `JUICER_API_KEY` if set, otherwise `POST /authorize`
with just an email. If a data call returns
`error.code = "email_confirmation_required"`, the user must click the
confirmation email. The SAME key unlocks after confirmation. A new
`/authorize` call does not help.

**Rule 2 — Pagination cursors are per platform, not top level.** One request
returns one page (~20–25 posts) per platform. The next cursor lives at
`.meta.platforms[].next_cursor`, only for platforms with `has_more: true`.
Reading a top-level cursor is the #1 mistake with this API.

```bash
jq -r '.meta.platforms[] | select(.success and .has_more) | .next_cursor'
```

**Rule 3 — `mentions` matching is loose; re-filter on your side.** The keyword
matcher can return "himself sighted" for `elfsight`. Always apply a
word-boundary regex to `message` before counting or reporting anything. X
messages contain HTML (`<a href=...>`), so strip tags first.

**Rule 4 — Discover platform capabilities at runtime; never hardcode them.**
`GET /platforms` says which `term_type` each platform supports and which
Integration-API sources need a connected social account. A source that needs a
missing connection fails with `error.code = "social_account_required"` and an
`error.action` telling you what to do. Surface it, do not guess.

---

## ⚠️ Authentication Required

All requests: `Authorization: Bearer jcr_...`

**Option 1: Permanent key (recommended for anything long-lived)**

From the Developer page in the Juicer dashboard.

```bash
export JUICER_API_KEY=jcr_...
```

**Option 2: Email-only signup, no dashboard**

```bash
curl -s -X POST https://api.juicer.io/v1/authorize \
  -H "Content-Type: application/json" \
  -d '{"email":"you@company.com","client_name":"My Tool"}'
```

- **201** (new or unconfirmed email): `api_key` returned immediately, 2h TTL,
  60 req/hr. Data endpoints return `email_confirmation_required` until the
  user clicks the confirmation email. After confirming, the same key extends
  to 12h and 300 req/hr.
- **202** (existing confirmed user): device flow. Show the user
  `authorization_url`, poll `poll_url` every 2s. 200 carries the key (returned
  exactly once), 410 means denied or expired. Requests expire in ~10 min.
- Every `/authorize` key is a 12h-max session key. It never revokes other keys.

Verify before doing anything else:

```bash
curl -s https://api.juicer.io/v1/account -H "Authorization: Bearer $JUICER_API_KEY"
```

**Rate limits:** 300 req/hr, 60 req/min on confirmed free keys. 429 on breach;
back off, the body includes an upgrade hint. Space requests ~1.2s apart in
loops.

---

## Core Workflow

Two surfaces, one key:

- **Data API** (`/data/*`): direct lookups with no feed required. Posts for a
  handle, hashtag, subreddit or keyword across platforms, plus canonical profile
  resolution. The research and ingestion surface. Works without OAuth on 13+
  platforms.
- **Integration API**: feeds you configure once and embed on a website. Create
  feeds, add sources, moderate posts, get embed code, analytics, webhooks. The
  product surface.

**Data workflow (research, monitoring):**

```bash
# 1. Authenticate
curl -s https://api.juicer.io/v1/account -H "Authorization: Bearer $JUICER_API_KEY"

# 2. Discover what each platform supports
curl -s https://api.juicer.io/v1/platforms -H "Authorization: Bearer $JUICER_API_KEY"

# 3. Query
curl -s "https://api.juicer.io/v1/data/posts?term=Flockler&term_type=mentions&platforms=Reddit,Twitter" \
  -H "Authorization: Bearer $JUICER_API_KEY"

# 4. Page (per platform, Rule 2)
curl -s "https://api.juicer.io/v1/data/posts?term=Flockler&term_type=mentions&platforms=Reddit&cursor=$CURSOR" \
  -H "Authorization: Bearer $JUICER_API_KEY"

# 5. Filter (Rule 3), then report with source URLs
```

**Integration workflow (feeds on a website):**

```bash
# 1. Authenticate
# 2. Check connections
curl -s https://api.juicer.io/v1/social_accounts/status -H "Authorization: Bearer $JUICER_API_KEY"
# 3. Create feed
# 4. Add sources
# 5. Moderate posts
# 6. Get embed code
# 7. Optional: webhooks, analytics
```

---

## Essential Commands

Every example below assumes `H='Authorization: Bearer '"$JUICER_API_KEY"` and
`J='Content-Type: application/json'`.

### Account and discovery

```bash
curl -s https://api.juicer.io/v1/ -H "$H"                # index
curl -s https://api.juicer.io/v1/account -H "$H"         # plan, usage, limits
curl -s https://api.juicer.io/v1/platforms -H "$H"       # platforms × term types × connection requirements
```

### Data API

```bash
# Posts for a term, no feed needed
curl -s "https://api.juicer.io/v1/data/posts?term=<T>&term_type=<TYPE>&platforms=<P1,P2>" -H "$H"

# Next page for one platform
curl -s "https://api.juicer.io/v1/data/posts?term=<T>&term_type=<TYPE>&platforms=<P1>&cursor=<CURSOR>" -H "$H"

# Canonical profile per platform
curl -s "https://api.juicer.io/v1/data/profiles?term=<HANDLE>&platforms=<P1,P2>" -H "$H"
```

`term_type` by platform (verify with `GET /platforms`):

| term_type | Platforms | Notes |
|---|---|---|
| `mentions` (keyword search) | Reddit, Twitter, TikTok | Loose matching, re-filter (Rule 3). Multi-word phrases are noisy |
| `channel` | Reddit (subreddit), YouTube | Ambient feed of the community |
| `hashtag` | Instagram, Facebook, TikTok, Twitter, LinkedIn, YouTube, Pinterest, Tumblr, Bluesky | |
| `username` | nearly all platforms | A handle's own posts |

Platform param value for X is `Twitter`.

### Feeds and sources

```bash
curl -s https://api.juicer.io/v1/feeds -H "$H"                                   # list
curl -s -X POST https://api.juicer.io/v1/feeds -H "$H" -H "$J" -d '{"name":"My Wall"}'
curl -s https://api.juicer.io/v1/feeds/<id> -H "$H"                              # get
curl -s -X PATCH https://api.juicer.io/v1/feeds/<id> -H "$H" -H "$J" -d '{...}'  # update (see spec)
curl -s -X DELETE https://api.juicer.io/v1/feeds/<id> -H "$H"

curl -s https://api.juicer.io/v1/feeds/<feed_id>/sources -H "$H"
curl -s -X POST https://api.juicer.io/v1/feeds/<feed_id>/sources -H "$H" -H "$J" \
  -d '{"platform":"Instagram","term":"myhandle","term_type":"username"}'
curl -s -X DELETE https://api.juicer.io/v1/feeds/<feed_id>/sources/<id> -H "$H"
```

### Posts and moderation

```bash
curl -s https://api.juicer.io/v1/feeds/<feed_id>/posts -H "$H"
curl -s https://api.juicer.io/v1/feeds/<feed_id>/posts/<id> -H "$H"
curl -s -X DELETE https://api.juicer.io/v1/feeds/<feed_id>/posts/<id> -H "$H"
curl -s -X POST https://api.juicer.io/v1/feeds/<feed_id>/posts/<id>/approve -H "$H"
curl -s -X POST https://api.juicer.io/v1/feeds/<feed_id>/posts/<id>/reject -H "$H"
curl -s -X POST https://api.juicer.io/v1/feeds/<feed_id>/posts/<id>/pin -H "$H"
curl -s -X POST https://api.juicer.io/v1/feeds/<feed_id>/posts/<id>/unpin -H "$H"
curl -s -X POST https://api.juicer.io/v1/feeds/<feed_id>/posts/bulk -H "$H" -H "$J" -d '{...}'   # see spec
```

### Embed, search, analytics

```bash
curl -s https://api.juicer.io/v1/feeds/<feed_id>/embed -H "$H"       # code snippets
curl -s "https://api.juicer.io/v1/search/posts?q=<Q>" -H "$H"         # across all your feeds
curl -s https://api.juicer.io/v1/feeds/<feed_id>/analytics -H "$H"
```

### Social account connections (Integration API only)

```bash
curl -s https://api.juicer.io/v1/social_accounts -H "$H"
curl -s https://api.juicer.io/v1/social_accounts/status -H "$H"             # what needs connecting
curl -s -X POST https://api.juicer.io/v1/social_accounts/connect_url -H "$H" -H "$J" \
  -d '{"provider":"facebook"}'                                              # magic link, user clicks it
curl -s -X DELETE https://api.juicer.io/v1/social_accounts/<id> -H "$H"
```

### Webhooks

```bash
curl -s https://api.juicer.io/v1/webhooks -H "$H"
curl -s -X POST https://api.juicer.io/v1/webhooks -H "$H" -H "$J" -d '{...}'   # see spec for events/URL
curl -s -X PATCH https://api.juicer.io/v1/webhooks/<id> -H "$H" -H "$J" -d '{...}'
curl -s -X DELETE https://api.juicer.io/v1/webhooks/<id> -H "$H"
curl -s -X POST https://api.juicer.io/v1/webhooks/<id>/test -H "$H"
curl -s https://api.juicer.io/v1/webhook_events -H "$H"
curl -s https://api.juicer.io/v1/webhook_events/<id> -H "$H"
curl -s https://api.juicer.io/v1/webhooks/<id>/deliveries -H "$H"
curl -s -X POST https://api.juicer.io/v1/webhooks/<id>/deliveries/<id>/redeliver -H "$H"
```

### Users (multi-tenant)

```bash
curl -s https://api.juicer.io/v1/users -H "$H"
curl -s -X POST https://api.juicer.io/v1/users -H "$H" -H "$J" -d '{...}'
curl -s https://api.juicer.io/v1/users/<id> -H "$H"
curl -s -X DELETE https://api.juicer.io/v1/users/<id> -H "$H"
curl -s -X PUT https://api.juicer.io/v1/users/<user_id>/feeds/<feed_id> -H "$H"
curl -s -X DELETE https://api.juicer.io/v1/users/<user_id>/feeds/<feed_id> -H "$H"
```

---

## Common Patterns

### Pattern 1: Keyword sweep with pagination and word-boundary filter

```bash
#!/bin/bash
TERM="Flockler"; PLATFORM="Reddit"; MAX_PAGES=3
H="Authorization: Bearer $JUICER_API_KEY"
CURSOR=""; PAGE=0
> posts.jsonl
while :; do
  URL="https://api.juicer.io/v1/data/posts?term=$TERM&term_type=mentions&platforms=$PLATFORM"
  [ -n "$CURSOR" ] && URL="$URL&cursor=$CURSOR"
  RESP=$(curl -s "$URL" -H "$H")
  if [ "$(echo "$RESP" | jq -r '.error.code // empty')" = "email_confirmation_required" ]; then
    echo "Click the confirmation email, then rerun with the SAME key (Rule 1)"; exit 1
  fi
  # Rule 3: re-filter on a word boundary; strip HTML first
  echo "$RESP" | jq -c --arg t "$TERM" '
    .data[] | .message |= gsub("<[^>]*>";"")
    | select(.message | test("\\b" + $t + "\\b"; "i"))' >> posts.jsonl
  PAGE=$((PAGE+1))
  CURSOR=$(echo "$RESP" | jq -r '.meta.platforms[] | select(.success and .has_more) | .next_cursor' | head -1)
  [ -z "$CURSOR" ] || [ "$PAGE" -ge "$MAX_PAGES" ] && break
  sleep 1.2
done
jq -r '[.post_created_at, .poster.name, .url] | @tsv' posts.jsonl
```

Brand corpora are small: 2–3 pages of `mentions` usually exhaust years of
history. Do not over-page.

### Pattern 2: Cross-platform brand monitor

```bash
H="Authorization: Bearer $JUICER_API_KEY"
for P in Reddit Twitter TikTok; do
  curl -s "https://api.juicer.io/v1/data/posts?term=juicer&term_type=mentions&platforms=$P" -H "$H" \
    | jq -c --arg p "$P" '.data[] | {p:$p, at:.post_created_at, likes:.like_count, url, msg:(.message|gsub("<[^>]*>";"")|.[0:140])}'
  sleep 1.2
done
```

Everyday-word terms (like "juicer") return an ambient firehose. A full page
spanning ≤3 days is the tell. Prefer the distinctive brand word; avoid dotted
domains (`walls.io` returns unrelated results, use `walls`).

### Pattern 3: What a community is talking about (subreddit or YouTube channel)

```bash
curl -s "https://api.juicer.io/v1/data/posts?term=webdev&term_type=channel&platforms=Reddit" -H "$H" \
  | jq -r '.data[] | [.comment_count, .like_count, .url, (.message|.[0:100])] | @tsv' | sort -rn | head -20
```

### Pattern 4: Feed → source → embed on a website

```bash
H="Authorization: Bearer $JUICER_API_KEY"; J="Content-Type: application/json"
FEED=$(curl -s -X POST https://api.juicer.io/v1/feeds -H "$H" -H "$J" -d '{"name":"My Wall"}' | jq -r '.id')
curl -s -X POST "https://api.juicer.io/v1/feeds/$FEED/sources" -H "$H" -H "$J" \
  -d '{"platform":"Instagram","term":"myhandle","term_type":"username"}'
curl -s "https://api.juicer.io/v1/feeds/$FEED/embed" -H "$H"
```

### Pattern 5: Handle a missing social connection

```bash
RESP=$(curl -s -X POST "https://api.juicer.io/v1/feeds/$FEED/sources" -H "$H" -H "$J" \
  -d '{"platform":"Facebook","term":"mypage","term_type":"username"}')
if [ "$(echo "$RESP" | jq -r '.error.code // empty')" = "social_account_required" ]; then
  echo "$RESP" | jq -r '.error.action'          # tell the user exactly this
  curl -s -X POST https://api.juicer.io/v1/social_accounts/connect_url -H "$H" -H "$J" \
    -d '{"provider":"facebook"}' | jq -r '.url'  # magic link, no Juicer login needed
fi
```

### Pattern 6: Rate-limit aware loop

```bash
for T in "${TERMS[@]}"; do
  for attempt in 1 2 3; do
    CODE=$(curl -s -o out.json -w '%{http_code}' \
      "https://api.juicer.io/v1/data/posts?term=$T&term_type=mentions&platforms=Reddit" -H "$H")
    [ "$CODE" = "429" ] && { sleep $((15 * attempt)); continue; }
    break
  done
  sleep 1.2
done
```

Check `GET /account` before heavy pulls to see remaining quota.

---

## Technical Concepts

### Post object (Data API `.data[]`)

`platform`, `platform_id`, `url`, `message`, `post_created_at`, `like_count`,
`comment_count`, `poster{name, url, ...}`, `media[]`. Fetch the OpenAPI spec
for the full schema; this list is not authoritative.

### Response metadata

`.meta.platforms[]` carries one entry per requested platform: `success`,
`has_more`, `next_cursor`. A platform with `success: false` failed
independently; the others still returned data. No cursor means that
platform's corpus is exhausted.

### Keys and lifetimes

| Key | TTL | Rate limit |
|---|---|---|
| Permanent (dashboard) | none | plan-dependent |
| `/authorize`, unconfirmed | 2h | 60 req/hr, data calls gated |
| `/authorize`, confirmed | 12h | 300 req/hr, 60 req/min |

### Connections

The Data API needs no OAuth. `requires_connection` flags from `GET /platforms`
apply only to Integration-API source types. Flow: `GET /social_accounts/status`
→ `POST /social_accounts/connect_url` → user clicks → `GET /social_accounts`.

---

## Platform-Specific Examples

### Reddit
```bash
# keyword across all of Reddit
curl -s "https://api.juicer.io/v1/data/posts?term=Elfsight&term_type=mentions&platforms=Reddit" -H "$H"
# one subreddit's feed
curl -s "https://api.juicer.io/v1/data/posts?term=SaaS&term_type=channel&platforms=Reddit" -H "$H"
```

### X (Twitter)
```bash
# platform value is Twitter, and message contains HTML
curl -s "https://api.juicer.io/v1/data/posts?term=Elfsight&term_type=mentions&platforms=Twitter" -H "$H" \
  | jq '.data[] | .message |= gsub("<[^>]*>";"")'
```

### Instagram
```bash
curl -s "https://api.juicer.io/v1/data/posts?term=ugc&term_type=hashtag&platforms=Instagram" -H "$H"
curl -s "https://api.juicer.io/v1/data/posts?term=nasa&term_type=username&platforms=Instagram" -H "$H"
```

### TikTok
```bash
curl -s "https://api.juicer.io/v1/data/posts?term=Elfsight&term_type=mentions&platforms=TikTok" -H "$H"
```

### YouTube
```bash
curl -s "https://api.juicer.io/v1/data/posts?term=<channel>&term_type=channel&platforms=YouTube" -H "$H"
```

### Multi-platform in one call
```bash
curl -s "https://api.juicer.io/v1/data/posts?term=ugc&term_type=hashtag&platforms=Instagram,TikTok,Twitter,Bluesky" -H "$H" \
  | jq '.meta.platforms'
```

---

## Supporting Resources

- OpenAPI spec: https://developers.juicer.io/openapi/v1.yaml
- Docs (markdown by appending `.md`): https://developers.juicer.io
- Product page: https://www.juicer.io/api
- Sibling skills built on this API:
  - `topic-scout`: find blog topics from competitor mentions across Reddit and X
  - `mention-scout`: find live conversations your brand can join
  - https://github.com/juicer-io/skills

---

## Common Gotchas

1. **`email_confirmation_required`** on data calls means click the email. Do NOT mint another key; the same key unlocks on confirmation.
2. **Top-level cursor does not exist.** Use `.meta.platforms[].next_cursor` per platform.
3. **`mentions` matching is loose.** "himself sighted" matches `elfsight`. Re-filter with a word-boundary regex.
4. **X `message` fields embed HTML.** Strip tags before displaying or matching.
5. **Platform param for X is `Twitter`**, not X.
6. **Dotted terms** (bare domains like `walls.io`) return unrelated results. Use the bare brand word.
7. **Everyday-word terms** ("juicer") return an ambient firehose. A full page spanning ≤3 days is the tell.
8. **Brand corpora are small.** 2–3 pages of `mentions` usually exhaust years of history. Don't over-page.
9. **`social_account_required`** carries an `error.action`. Surface it verbatim; don't guess a workaround.
10. **`requires_connection` is Integration-API only.** The Data API works without OAuth on 13+ platforms.
11. **429** means back off; the body includes an upgrade hint. Space loop requests ~1.2s apart.
12. **`/authorize` keys are session keys** (12h max) and never revoke other keys. Use a permanent key for anything long-lived.
13. **This file is not the schema.** Fetch the OpenAPI spec for exact request and response shapes.

---

## Quick Reference

```bash
H="Authorization: Bearer $JUICER_API_KEY"; J="Content-Type: application/json"
B=https://api.juicer.io/v1

# ⚠️ AUTHENTICATE FIRST
curl -s -X POST $B/authorize -H "$J" -d '{"email":"you@co.com","client_name":"My Tool"}'   # email-only key
curl -s $B/account -H "$H"                                                                # verify, quota

# Discovery
curl -s $B/platforms -H "$H"                                                              # term types per platform
curl -s $B/social_accounts/status -H "$H"                                                 # connections needed

# Data API (no feed, no OAuth)
curl -s "$B/data/posts?term=<T>&term_type=mentions|channel|hashtag|username&platforms=<P1,P2>" -H "$H"
curl -s "$B/data/posts?...&cursor=<from .meta.platforms[].next_cursor>" -H "$H"           # next page
curl -s "$B/data/profiles?term=<handle>&platforms=<P>" -H "$H"                            # canonical profile

# Integration API
curl -s -X POST $B/feeds -H "$H" -H "$J" -d '{"name":"..."}'                              # create feed
curl -s -X POST $B/feeds/<id>/sources -H "$H" -H "$J" -d '{"platform":"...","term":"...","term_type":"..."}'
curl -s $B/feeds/<id>/posts -H "$H"                                                       # moderate: /approve /reject /pin /unpin
curl -s $B/feeds/<id>/embed -H "$H"                                                       # embed code
curl -s $B/feeds/<id>/analytics -H "$H"
curl -s "$B/search/posts?q=<Q>" -H "$H"                                                   # across all feeds
curl -s $B/webhooks -H "$H"                                                               # + /test, /deliveries, /redeliver
curl -s -X POST $B/social_accounts/connect_url -H "$H" -H "$J" -d '{"provider":"facebook"}'

# Schemas
curl -s https://developers.juicer.io/openapi/v1.yaml
```
