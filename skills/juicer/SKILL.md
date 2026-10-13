---
name: juicer
description: Social media data and feed API to search posts, brand mentions, hashtags, subreddits and profiles, and to aggregate, moderate and embed social feeds on any website, across 15+ platforms Reddit, X, Instagram, Facebook, TikTok, YouTube, LinkedIn, Pinterest, Bluesky, Tumblr, Vimeo, Flickr, Giphy and more
homepage: https://developers.juicer.io
metadata: {"openclaw":{"emoji":"🧃","requires":{"bins":["curl","jq"],"env":[]}}}
---

# Juicer

Read BEFORE calling any Juicer tool or writing curl against `api.juicer.io`,
and whenever the user mentions Juicer, wants posts, mentions, hashtags or a
handle's content from one or more social platforms, wants to monitor brand or
competitor mentions, or wants a social feed, social wall or social media embed
on a website.

Do NOT use for publishing or scheduling posts to social networks, for a
platform's own native API, or for scraping.

## Two ways to call it, one API

- **Juicer connector (MCP, preferred).** 33 tools, one per API operation,
  served from `https://api.juicer.io/mcp`. Works in claude.ai, Cowork and
  Claude Code. Auth is OAuth in the browser; you never handle a key.
- **curl + jq (Claude Code fallback).** Same operations against
  `https://api.juicer.io/v1` with a Bearer key. Use it only when the connector
  is not connected, or for shell loops over many pages.

Everything below names the tool first and the curl equivalent second.

- OpenAPI spec (authoritative for every schema): https://developers.juicer.io/openapi/v1.yaml
- Tool catalog: https://developers.juicer.io/mcp-tools
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

## ⚠️ Five Hard Rules (Read First)

**Rule 1 — Every Data API call spends credits. Check the balance before a
loop.** `get_account` (`GET /account`) returns `credits.balance` and
`credits.cost_per_call`. A free account starts with 30 credits that never
refill; Facebook costs 6 per platform per call, Instagram, TikTok and LinkedIn
3, everything else 1. When the balance cannot cover a call the API answers
402 `insufficient_credits` with `error.action.checkout_url`. Show that link to
the user; do not retry.

**Rule 2 — Pagination cursors are per platform, not top level.** One call
returns one page per platform (page size varies: Reddit 25–125, YouTube 50,
Instagram ~12, X ~11). The next cursor lives at `.meta.platforms[].next_cursor`,
only for entries with `has_more: true`. There is no top-level cursor. To page
several platforms in one call, pass their cursors comma-separated in the same
order as `platforms`.

```bash
jq -r '.meta.platforms[] | select(.success and .has_more) | .next_cursor'
```

**Rule 3 — `mentions` matching is loose; re-filter on your side.** The keyword
matcher can return "himself sighted" for `elfsight`. Always apply a
word-boundary regex to `message` before counting or reporting anything. X
messages contain HTML (`<a href=...>`), so strip tags first.

**Rule 4 — Discover platform capabilities at runtime; never hardcode them.**
`list_platforms` (`GET /platforms`) lists every platform, its `term_types`, a
`data_api` flag per term type, and which Integration-API sources need a
connected social account. Trust `data_api: true` over any table in this file.
A source that needs a missing connection fails with
`error.code = "social_account_required"` and an `error.action` carrying the
`connection_url` to send the user to. Surface it, do not guess.

**Rule 5 — An error is a tool result with `isError: true`, not an exception.**
The text is the API's `{ "error": { "code", "message", "action" } }` envelope.
Read `error.code`, show `error.message` and any `error.action` link to the
user, and stop. The codes you will meet: `insufficient_credits` (402),
`email_confirmation_required`, `social_account_required`, `invalid_term_type`,
`unknown_platform`, `feed_limit_reached`, `forbidden` (plan gate), `not_found`.

---

## Authentication

### Connector (preferred)

The Juicer connector is listed on this plugin's **Connectors** tab in claude.ai
and Cowork; in Claude Code it loads with the plugin and `/mcp` shows its state.
On first use Claude opens the browser: the user enters their email (a new
account is created on the spot, no dashboard needed), clicks the emailed link,
and approves. Claude holds the resulting key; nothing to paste. If a tool call
returns a 401 the connector re-runs that flow by itself. Never ask the user for
a key when the connector is available.

### Claude Code without the connector: curl with a key

All requests: `Authorization: Bearer jcr_...`. Hold the key in a shell variable
for the session; never read one from the user's environment or files.

**Option 1: the user pastes a permanent key** (Developer page in the Juicer
dashboard):

```bash
KEY=jcr_...   # pasted by the user this session
```

**Option 2: email-only signup, no dashboard.** Ask the user for their email:

```bash
RESP=$(curl -s -X POST https://api.juicer.io/v1/authorize \
  -H "Content-Type: application/json" \
  -d '{"email":"you@company.com","client_name":"My Tool"}')
echo "$RESP" | jq .
KEY=$(echo "$RESP" | jq -r '.api_key // empty')
```

- **201** (new or unconfirmed email): `status: "issued"`, `api_key` returned,
  so `KEY` is set. 2h TTL, 60 req/hr. Data calls return
  `email_confirmation_required` until the user clicks the confirmation email;
  the SAME key then extends to 12h and 300 req/hr. Never mint a second key to
  escape that gate.
- **202** (existing confirmed user): `status: "pending_authorization"`, no key
  yet. Show the user `authorization_url`, then poll `poll_url` every 2s. The
  key is returned exactly once; 410 means denied, expired or already delivered.

```bash
echo "Open this to approve: $(echo "$RESP" | jq -r '.authorization_url')"
POLL=$(echo "$RESP" | jq -r '.poll_url')
while :; do
  R=$(curl -s -w '\n%{http_code}' "$POLL"); CODE=${R##*$'\n'}; BODY=${R%$'\n'*}
  case $CODE in
    200) KEY=$(echo "$BODY" | jq -r '.api_key'); break ;;
    202) sleep 2 ;;
    *)   echo "$BODY" | jq .; exit 1 ;;   # 410 denied/expired/already delivered
  esac
done
```

- `422 invalid_email` means the address was rejected; ask again.
- Every `/authorize` key is a 12h-max session key and never revokes others.

Verify before doing anything else:

```bash
curl -s https://api.juicer.io/v1/account -H "Authorization: Bearer $KEY"
```

**Rate limits:** 300 req/hr, 60 req/min on confirmed free keys. 429 on breach;
back off, the body includes an upgrade hint. Space loop requests ~1.2s apart.

---

## Credits

| Platform per call | Credits |
|---|---|
| Facebook | 6 |
| Instagram, TikTok, LinkedIn | 3 |
| Every other platform | 1 |

- Charged per platform that succeeds, per call, on `get_data_posts` and
  `get_data_profiles` (`/data/*`). Integration API calls (feeds, sources,
  moderation, embed, analytics, webhooks, users) are free.
- Free Sandbox tier: 30 credits once, no refill, no expiry. Paid API plans get
  a monthly allowance plus top-ups; `credits.refills_on` says when.
- `get_account` → `credits.balance`, `credits.allowance_remaining`,
  `credits.top_up_balance`, `credits.refills_on`, `credits.sandbox`,
  `credits.cost_per_call`. Read it before any multi-call plan and tell the
  user what the plan will cost.
- A single Instagram + TikTok + X sweep costs 7 credits per page. Three pages
  on a Sandbox key is most of its lifetime budget. Prefer one platform per
  question, and stop paging when `has_more` is false.

---

## Tool map

| Task | Tool | curl |
|---|---|---|
| Plan, limits, credit balance | `get_account` | `GET /account` |
| Platforms, term types, `data_api` flag, connection needs | `list_platforms` | `GET /platforms` |
| Posts for a keyword, hashtag, handle, subreddit, channel or Place ID, no feed | `get_data_posts` (`term`, `platforms`, `term_type?`, `cursor?`) | `GET /data/posts` |
| Canonical profile(s) for handle(s) | `get_data_profiles` (`term` comma list up to 5, `platforms`) | `GET /data/profiles` |
| Feeds | `list_feeds`, `get_feed` (`include="sources"`), `create_feed`, `update_feed`, `delete_feed` | `/feeds` |
| Sources in a feed | `list_sources`, `create_source` (`feed_id`, `platform`, `term`, `term_type`, `options?`), `delete_source` | `/feeds/{id}/sources` |
| Posts in a feed | `list_feed_posts` (`status` public/moderated/rejected, `filter`, `search`, dates), `get_feed_post` | `/feeds/{id}/posts` |
| Moderate | `moderate_post` (`action` approve/reject/pin/unpin/delete), `bulk_moderate_posts` (`action_type`, `post_ids` or `tab`) | `/posts/{id}/approve` etc., `/posts/bulk` |
| Embed code | `get_feed_embed` | `GET /feeds/{id}/embed` |
| Search collected posts | `search_posts` (`query`, `feed_ids?`, `platforms?`, dates, `page`) | `GET /search/posts?query=` |
| Analytics | `get_feed_analytics` (`start?`, `end?`) | `GET /feeds/{id}/analytics` |
| Social connections | `get_social_account_status`, `list_social_accounts`, `create_social_account_connect_url` (`provider`), `delete_social_account` | `/social_accounts` |
| Webhooks | `list_webhooks`, `create_webhook` (`url`, `subscribed_events`), `update_webhook`, `delete_webhook`, `test_webhook` | `/webhooks` |
| Team | `list_users`, `create_user` (`email`, `role` manager/collaborator), `delete_user`, `assign_user_feed`, `unassign_user_feed` | `/users` |

Destructive tools (`delete_*`, `moderate_post` with `delete`,
`bulk_moderate_posts` with `hard_delete`) are flagged `destructiveHint`;
confirm with the user before calling them.

---

## Data API

Direct lookups with no feed and no social-account connection. Costs credits
(Rule 1).

**Arguments:** `term` (required), `platforms` (required, comma-separated),
`term_type` (optional), `cursor` (optional, Rule 2).

**`term_type` is auto-detected when omitted**: `#tag` → `hashtag`, `@handle`
or bare word → `username` (YouTube: `channel`). Reddit and Google never
auto-detect; pass `term_type` explicitly. Pass it whenever you mean `mentions`.

Supported Data API term types (verify with `list_platforms`, Rule 4):

| Platform | `username` | `hashtag` | `mentions` (keyword) | other |
|---|---|---|---|---|
| Reddit | | | ✓ (all of Reddit) | `channel` = subreddit |
| Twitter (alias `X`) | ✓ | ✓ | ✓ | |
| TikTok | ✓ | ✓ | ✓ | |
| YouTube | ✓ | ✓ | | `channel` |
| Instagram | ✓ | ✓ | | |
| Facebook | ✓ | ✓ | | |
| LinkedIn | ✓ | ✓ | | |
| Bluesky | ✓ | ✓ | | |
| Pinterest | ✓ | ✓ | | |
| Tumblr | ✓ | ✓ | | |
| Vimeo, Flickr, Giphy | ✓ | | | |
| Google | | | | `reviews` (term = Place ID from `get_data_profiles`) |

`mentions` exists only on Reddit, Twitter/X and TikTok. LinkedIn, Facebook and
Instagram list `mentions` for the Integration API, but the Data API rejects it
with `invalid_term_type`. Soundcloud is not available on the Data API.

**Response:** `.data[]` posts (`platform`, `platform_id`, `url`, `message`,
`post_created_at`, `like_count`, `comment_count`, `share_count`, `poster{name,
display_name, url, image}`, `media[]`, `referenced_post`) and
`.meta.platforms[]` (`platform`, `success`, `count`, `has_more`, `next_cursor`,
or `error_code` + `message` when that platform failed: `fetch_timeout`,
`invalid_term_type`, `unknown_platform`, `platform_error`, `invalid_cursor`).
A failed platform never fails the call; the others still return data. Fetch
the OpenAPI spec for the full schema.

```bash
# tool: get_data_posts {term, platforms, term_type, cursor}
curl -s "https://api.juicer.io/v1/data/posts?term=<T>&term_type=<TYPE>&platforms=<P1,P2>" -H "$H"
curl -s "https://api.juicer.io/v1/data/posts?term=<T>&term_type=<TYPE>&platforms=<P1,P2>&cursor=<C1>,<C2>" -H "$H"
# tool: get_data_profiles {term, platforms}
curl -s "https://api.juicer.io/v1/data/profiles?term=<HANDLE1,HANDLE2>&platforms=<P1,P2>" -H "$H"
```

Profiles return `.data[]` of `{platform, term, exact_match, profiles[{platform,
platform_id, handle, display_name, url, image}]}`.

---

## Integration API

Feeds you configure once and embed on a website. Free of credits. Some source
types need a connected social account (`requires_connection` on
`list_platforms`); the Data API never does.

**Workflow:** `get_social_account_status` → `create_feed` → `create_source`
(one per handle/hashtag/page) → `list_feed_posts` + `moderate_post` →
`get_feed_embed` → optional `create_webhook`, `get_feed_analytics`.

```bash
H="Authorization: Bearer $KEY"; J="Content-Type: application/json"; B=https://api.juicer.io/v1
curl -s $B/feeds -H "$H"                                                    # list_feeds (paginated: page, per_page)
curl -s -X POST $B/feeds -H "$H" -H "$J" -d '{"name":"My Wall"}'            # create_feed → .data.id
curl -s -X PATCH $B/feeds/<id> -H "$H" -H "$J" -d '{"queue":true}'          # update_feed (see spec for all fields)
curl -s -X POST $B/feeds/<id>/sources -H "$H" -H "$J" \
  -d '{"platform":"Instagram","term":"myhandle","term_type":"username"}'   # create_source
curl -s "$B/feeds/<id>/posts?status=moderated" -H "$H"                      # list_feed_posts (status: public|moderated|rejected)
curl -s -X POST $B/feeds/<id>/posts/<pid>/approve -H "$H"                   # moderate_post (approve|reject|pin|unpin), DELETE for delete
curl -s -X POST $B/feeds/<id>/posts/bulk -H "$H" -H "$J" \
  -d '{"action_type":"approve","post_ids":[1,2]}'                           # bulk_moderate_posts (approve|reject|soft_delete|hard_delete; or "tab")
curl -s $B/feeds/<id>/embed -H "$H"                                         # get_feed_embed → .data.javascript / .iframe / feed_url
curl -s "$B/search/posts?query=<Q>&feed_ids=1,2" -H "$H"                     # search_posts (send + as %2B for AND; comma = OR)
curl -s "$B/feeds/<id>/analytics?start=2026-09-01&end=2026-09-30" -H "$H"   # get_feed_analytics
curl -s $B/social_accounts/status -H "$H"                                   # get_social_account_status
curl -s -X POST $B/social_accounts/connect_url -H "$H" -H "$J" -d '{"provider":"facebook"}'  # → .data.connection_url
curl -s -X POST $B/webhooks -H "$H" -H "$J" -d '{"url":"https://…","subscribed_events":["post.created"]}'
curl -s -X POST $B/users -H "$H" -H "$J" -d '{"email":"a@b.co","role":"collaborator","feed_ids":[1]}'
curl -s -X PUT $B/users/<uid>/feeds/<fid> -H "$H"                           # assign_user_feed; DELETE to unassign
```

Integration list endpoints paginate with `page` and `per_page` and return
`.meta.{page, per_page, total_count, total_pages}`.

---

## Common Patterns

### Pattern 1: What are people saying about a brand on Reddit (2–3 pages, filtered)

Tool flow: `get_account` (check `credits.balance` ≥ 3) → `get_data_posts
{term:"Flockler", platforms:"Reddit", term_type:"mentions"}` → read
`meta.platforms[0].next_cursor` → repeat with `cursor` while `has_more` and
the posts are still on-topic → word-boundary filter (Rule 3) → report with
`url` on every finding.

Shell version for Claude Code:

```bash
#!/bin/bash
TERM="Flockler"; PLATFORM="Reddit"; MAX_PAGES=3
H="Authorization: Bearer $KEY"
CURSOR=""; PAGE=0
> posts.jsonl
while :; do
  URL="https://api.juicer.io/v1/data/posts?term=$TERM&term_type=mentions&platforms=$PLATFORM"
  [ -n "$CURSOR" ] && URL="$URL&cursor=$CURSOR"
  RESP=$(curl -s "$URL" -H "$H")
  ERR=$(echo "$RESP" | jq -r '.error.code // empty')
  [ -n "$ERR" ] && { echo "$RESP" | jq .; exit 1; }     # Rule 5: insufficient_credits, email_confirmation_required, …
  echo "$RESP" | jq -c --arg t "$TERM" '
    .data[] | .message |= gsub("<[^>]*>";"")
    | select(.message | test("\\b" + $t + "\\b"; "i"))' >> posts.jsonl   # Rule 3
  PAGE=$((PAGE+1))
  CURSOR=$(echo "$RESP" | jq -r '.meta.platforms[] | select(.success and .has_more) | .next_cursor' | head -1)
  [ -z "$CURSOR" ] || [ "$PAGE" -ge "$MAX_PAGES" ] && break
  sleep 1.2
done
jq -r '[.post_created_at, .poster.name, .url] | @tsv' posts.jsonl
```

Brand corpora are small: 2–3 pages of `mentions` usually exhaust years of
history. Do not over-page; every page costs credits.

### Pattern 2: Cross-platform brand monitor

`get_data_posts {term:"elfsight", platforms:"Reddit,Twitter,TikTok",
term_type:"mentions"}` is one call, 3 credits, one page per platform. Check
each `meta.platforms[]` entry: a `fetch_timeout` on one platform is normal,
retry only that platform.

Everyday-word terms (like "juicer") return an ambient firehose. A full page
spanning ≤3 days is the tell. Prefer the distinctive brand word; avoid dotted
domains (`walls.io` returns unrelated results, use `walls`).

### Pattern 3: What a community is talking about

`get_data_posts {term:"webdev", platforms:"Reddit", term_type:"channel"}` or
`{term:"nasa", platforms:"YouTube"}` (channel auto-detected). Sort by
`comment_count` or `like_count` on your side.

### Pattern 4: Feed → source → embed on a website

`create_feed {name}` → `create_source {feed_id, platform:"Instagram",
term:"myhandle", term_type:"username"}` → `get_feed_embed {feed_id}` → give
the user `.data.javascript` (or `.iframe`, or the WordPress shortcode).

### Pattern 5: Handle a missing social connection

`create_source` answers `social_account_required` with
`error.action = { type: "connect_social_account", provider, connection_url,
expires_at }`. Send the user to `connection_url` (a 30-minute magic link, no
Juicer login needed), wait for them to confirm, then retry `create_source`.
`create_social_account_connect_url {provider}` returns the same link on demand
as `.data.connection_url`.

### Pattern 6: Rate-limit and credit aware loop (curl)

```bash
for T in "${TERMS[@]}"; do
  for attempt in 1 2 3; do
    CODE=$(curl -s -o out.json -w '%{http_code}' \
      "https://api.juicer.io/v1/data/posts?term=$T&term_type=mentions&platforms=Reddit" -H "$H")
    case $CODE in
      429) sleep $((15 * attempt)); continue ;;
      402) jq . out.json; exit 1 ;;          # out of credits: show error.action.checkout_url
    esac
    break
  done
  sleep 1.2
done
```

---

## Keys and lifetimes (curl path)

| Key | TTL | Rate limit |
|---|---|---|
| Connector (OAuth) or dashboard | none | plan-dependent |
| `/authorize`, unconfirmed | 2h | 60 req/hr, data calls gated |
| `/authorize`, confirmed | 12h | 300 req/hr, 60 req/min |

---

## Common Gotchas

1. **Credits run out before rate limits do.** A Sandbox key has 30 credits for life. Check `get_account` first; a 402 carries `error.action.checkout_url`.
2. **Top-level cursor does not exist.** Use `.meta.platforms[].next_cursor` per platform; comma-join them for multi-platform paging.
3. **`mentions` matching is loose.** "himself sighted" matches `elfsight`. Re-filter with a word-boundary regex.
4. **X `message` fields embed HTML.** Strip tags before displaying or matching.
5. **`mentions` is Reddit, Twitter/X and TikTok only** on the Data API, whatever `list_platforms` says for the Integration API.
6. **Dotted terms** (bare domains like `walls.io`) return unrelated results. Use the bare brand word.
7. **Everyday-word terms** ("juicer") return an ambient firehose. A full page spanning ≤3 days is the tell.
8. **Brand corpora are small.** 2–3 pages of `mentions` usually exhaust years of history. Don't over-page.
9. **`social_account_required`** carries an `error.action.connection_url`. Send the user there; don't guess a workaround.
10. **`requires_connection` is Integration-API only.** The Data API works without any social connection on 14 platforms.
11. **`fetch_timeout` on one platform** is a partial result, not a failure. Retry that platform alone.
12. **`/authorize` keys are session keys** (12h max) and never revoke other keys. Prefer the connector or a permanent key.
13. **`search_posts` `+` must be URL-encoded** as `%2B` in curl; a bare `+` becomes a space.
14. **This file is not the schema.** Fetch the OpenAPI spec for exact request and response shapes.

---

## Quick Reference (curl)

```bash
H="Authorization: Bearer $KEY"; J="Content-Type: application/json"
B=https://api.juicer.io/v1

# ⚠️ AUTHENTICATE FIRST (connector users skip this)
curl -s -X POST $B/authorize -H "$J" -d '{"email":"you@co.com","client_name":"My Tool"}'   # email-only key
curl -s $B/account -H "$H"                                                                # verify, credits.balance

# Discovery
curl -s $B/platforms -H "$H"                                                              # term types, data_api flag
curl -s $B/social_accounts/status -H "$H"                                                 # connections needed

# Data API (no feed, no connection; costs credits)
curl -s "$B/data/posts?term=<T>&term_type=mentions|channel|hashtag|username|reviews&platforms=<P1,P2>" -H "$H"
curl -s "$B/data/posts?...&cursor=<C1>,<C2>" -H "$H"                                      # next page per platform
curl -s "$B/data/profiles?term=<h1,h2>&platforms=<P>" -H "$H"                             # canonical profiles

# Integration API (free)
curl -s -X POST $B/feeds -H "$H" -H "$J" -d '{"name":"..."}'                              # create feed
curl -s -X POST $B/feeds/<id>/sources -H "$H" -H "$J" -d '{"platform":"...","term":"...","term_type":"..."}'
curl -s "$B/feeds/<id>/posts?status=moderated" -H "$H"                                    # then /approve /reject /pin /unpin
curl -s $B/feeds/<id>/embed -H "$H"                                                       # embed code
curl -s $B/feeds/<id>/analytics -H "$H"
curl -s "$B/search/posts?query=<Q>" -H "$H"                                               # across all feeds
curl -s $B/webhooks -H "$H"                                                               # + /test, /deliveries, /redeliver
curl -s -X POST $B/social_accounts/connect_url -H "$H" -H "$J" -d '{"provider":"facebook"}'  # → .data.connection_url

# Schemas
curl -s https://developers.juicer.io/openapi/v1.yaml
```
