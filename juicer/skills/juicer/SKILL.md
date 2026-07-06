---
name: juicer
description: Reference for the Juicer API — read BEFORE writing any code or curl against api.juicer.io, or when the user mentions Juicer, social feed embeds, social media aggregation, or cross-platform social data (Reddit, Instagram, TikTok, X, YouTube, LinkedIn and more). Covers both API surfaces (Integration API for feeds/moderation/embeds/webhooks; Data API for keyword/handle/hashtag lookups with no feed required), the email-only signup flow that needs no dashboard, the full endpoint map, and the gotchas that aren't in the docs (per-platform pagination cursors, loose keyword matching, email-confirmation gates).
---

# Juicer API

One API over 15+ social platforms — Reddit, Instagram, Facebook, X/Twitter,
TikTok, YouTube, LinkedIn, Pinterest, Bluesky, Tumblr, Vimeo, Flickr, Giphy
and more. Base URL `https://api.juicer.io/v1`, Bearer auth.

**Two surfaces, one key:**

- **Integration API** — feeds you configure once and embed on a website:
  create feeds, add sources, moderate posts, get embed code, analytics,
  webhooks. This is the product surface (social walls on websites).
- **Data API** (`/data/*`) — direct lookups with **no feed required**: posts
  for a handle, hashtag, subreddit, or keyword across platforms, plus
  canonical profile resolution. This is the research/ingestion surface.

**Where the truth lives** (fetch these; don't trust memory for schemas):

- OpenAPI spec: `https://developers.juicer.io/openapi/v1.yaml`
- Docs: `https://developers.juicer.io` — any docs page is fetchable as
  markdown by appending `.md` to its URL (LLM-friendly).
- Product page: `https://www.juicer.io/api`

## Auth

All requests: `Authorization: Bearer jcr_...`

Two ways to get a key:

1. **Permanent key** — Developer page in the Juicer dashboard. Use for
   anything long-lived.
2. **Email-only signup, no dashboard** — `POST /authorize` with
   `{"email": "...", "client_name": "Your App"}`:
   - **201** (new/unconfirmed email): `api_key` returned immediately, 2h TTL,
     60 req/hr — BUT data endpoints return
     `error.code = "email_confirmation_required"` until the user clicks the
     confirmation email. After confirming, the SAME key extends to 12h and
     300 req/hr.
   - **202** (existing confirmed user): device flow — show the user
     `authorization_url`, poll `poll_url` every 2s; 200 carries the key
     (returned exactly once), 410 = denied/expired. Requests expire ~10 min.
   - Every `/authorize` key is a 12h-max session key; it never revokes other
     keys.

Rate limits: 300 req/hr, 60 req/min on confirmed free keys (429 on breach —
back off; the body includes an upgrade hint). Space requests ~1.2s apart in
loops.

## Endpoint map

| Area | Endpoints |
|---|---|
| Auth | `POST /authorize`, `GET /authorize/{request_id}` (poll) |
| Account | `GET /account` (plan, usage, limits), `GET /` (index), `GET /platforms` (platforms × term types × connection requirements) |
| Social accounts (OAuth) | `GET /social_accounts`, `GET /social_accounts/status`, `POST /social_accounts/connect_url`, `DELETE /social_accounts/{id}` |
| Feeds | `GET/POST /feeds`, `GET/PATCH/DELETE /feeds/{id}` |
| Sources | `GET/POST /feeds/{feed_id}/sources`, `DELETE .../sources/{id}` |
| Posts & moderation | `GET /feeds/{feed_id}/posts`, `GET/DELETE .../posts/{id}`, `POST .../approve`, `.../reject`, `.../pin`, `.../unpin`, `POST .../posts/bulk` |
| Embed | `GET /feeds/{feed_id}/embed` (code snippets) |
| Search & analytics | `GET /search/posts` (across all feeds), `GET /feeds/{feed_id}/analytics` |
| Webhooks | `GET/POST /webhooks`, `PATCH/DELETE /webhooks/{id}`, `POST /webhooks/{id}/test`, `GET /webhook_events`, `GET /webhook_events/{id}`, `GET /webhooks/{id}/deliveries`, `POST .../redeliver` |
| **Data API** | `GET /data/posts` (term lookup, no feed), `GET /data/profiles` (canonical profile per platform) |
| Users | `GET/POST /users`, `GET/DELETE /users/{id}`, `PUT/DELETE /users/{user_id}/feeds/{feed_id}` |

## Data API essentials

```
GET /data/posts?term=<T>&term_type=<TYPE>&platforms=<P1,P2>[&cursor=...]
```

`term_type` support varies by platform:

| term_type | Platforms | Notes |
|---|---|---|
| `mentions` (keyword search) | Reddit, Twitter, TikTok | Loose matching — verify word-boundary matches in `message` yourself; multi-word phrases are noisy |
| `channel` | Reddit (subreddit), YouTube | Ambient feed of the community |
| `hashtag` | Instagram, Facebook, TikTok, Twitter, LinkedIn, YouTube, Pinterest, Tumblr, Bluesky | |
| `username` | nearly all platforms | A handle's own posts |

Posts come back in `.data[]`: `platform`, `platform_id`, `url`, `message`,
`post_created_at`, `like_count`, `comment_count`, `poster{name, url, ...}`,
`media[]`. One request serves one platform page (~20–25 posts).

**Pagination — the #1 mistake:** the cursor is per-platform, NOT top-level:

```bash
jq -r '.meta.platforms[] | select(.success and .has_more) | .next_cursor'
```

Pass it back via `&cursor=`. No cursor → that platform's corpus is exhausted.

## Social account connections

The Data API works **without** OAuth on 13+ platforms. Some Integration-API
source types need a connected social account — the `requires_connection`
flags in `GET /platforms` apply to the Integration API only. Discover at
runtime, never hardcode:

1. `GET /social_accounts/status` — what needs connecting
2. `POST /social_accounts/connect_url` `{"provider": "facebook"}` → magic
   link; the user clicks it (no Juicer login needed)
3. `GET /social_accounts` — verify connected

Creating a source that needs a missing connection fails with
`error.code = "social_account_required"` and an `error.action` telling you
what to do — surface it, don't guess.

## Gotchas (not in the docs)

- **X/Twitter `message` fields embed HTML** (`<a href=...>` around mentions
  and links) — strip tags before displaying or matching.
- **`mentions` matching is loose**: "himself sighted" can match "elfsight".
  Always re-filter with a word-boundary regex on your side. Everyday-word
  terms (e.g. "juicer") return ambient firehose — a full page spanning ≤3
  days is the tell.
- **Dotted terms** (bare domains like `walls.io`) tend to return unrelated
  results from the mentions matcher — use the bare brand word.
- **`email_confirmation_required`** on data calls means click the email —
  do NOT mint another key; the same key unlocks on confirmation.
- Platform param value for X is `Twitter`.
- Anchor-style brand corpora are small: 2–3 pages of `mentions` usually
  exhausts years of history. Don't over-page.

## Recipes

Key with just an email (then confirm via inbox):
```bash
curl -s -X POST https://api.juicer.io/v1/authorize \
  -H "Content-Type: application/json" \
  -d '{"email":"you@company.com","client_name":"My Tool"}'
```

Reddit keyword sweep with pagination:
```bash
curl -s "https://api.juicer.io/v1/data/posts?term=Flockler&term_type=mentions&platforms=Reddit" \
  -H "Authorization: Bearer $KEY"   # then follow meta.platforms[].next_cursor
```

Feed → source → embed (Integration API):
```bash
curl -s -X POST https://api.juicer.io/v1/feeds -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" -d '{"name":"My Wall"}'
curl -s -X POST https://api.juicer.io/v1/feeds/<id>/sources -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" -d '{"platform":"Instagram","term":"myhandle","term_type":"username"}'
curl -s https://api.juicer.io/v1/feeds/<id>/embed -H "Authorization: Bearer $KEY"
```

Check plan/usage before heavy pulls: `GET /account`.

For exact request/response schemas of any endpoint, fetch the OpenAPI spec —
it is authoritative and this file is not.
