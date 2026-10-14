---
name: juicer
description: Social media data and feed API to search posts, brand mentions, hashtags, subreddits and profiles, and to aggregate, moderate and embed social feeds on any website, across 15+ platforms Reddit, X, Instagram, Facebook, TikTok, YouTube, LinkedIn, Pinterest, Bluesky, Tumblr, Vimeo, Flickr, Giphy and more
homepage: https://developers.juicer.io
metadata: {"openclaw":{"emoji":"🧃","requires":{"bins":[],"env":[]}}}
---

# Juicer

Read BEFORE calling any Juicer tool or writing curl against `api.juicer.io`,
and whenever the user mentions Juicer, wants posts, mentions, hashtags or a
handle's content from one or more social platforms, wants to monitor brand or
competitor mentions, or wants a social feed, social wall or social media embed
on a website.

Do NOT use for publishing or scheduling posts to social networks, for a
platform's own native API, or for scraping.

## Two products, one connector

Juicer is one API with two products. Decide which one the user needs before
calling anything.

| | **Integration API** | **Data API** |
|---|---|---|
| What it is | A **feed** Juicer keeps syncing for you: sources, collected posts, moderation, embed code, analytics, webhooks, team | A **lookup**: fresh posts or profiles for a term on one or more platforms, right now |
| State | Persistent. Posts accumulate over time and stay searchable | None. Nothing is stored; every call fetches again |
| Set-up | `create_feed` → `create_source` → wait for the first sync | Nothing. `get_data_posts {term, platforms}` |
| Social connection | Some source types need a connected social account (`requires_connection` on `list_platforms`) | Never. 14 platforms work with no connection |
| Cost | Free of credits. Gated by the feed plan (Free: 1 feed, 1 source per feed, 300 views/month, no team) | Metered: credits per platform per call (Sandbox: 30 credits, once) |
| Output | Posts with `moderation_status`, embed snippets, analytics, webhook events | Posts per platform with a per-platform `next_cursor`; canonical profiles |
| Use when | "Build a social wall", "embed our Instagram on the site", "moderate the feed", "what did our feed do last month", "ping me on new posts", "give my colleague access" | "What are people on Reddit saying about X", "pull #coffee from Instagram and X", "find the brand's handle on TikTok", "latest 5 posts from NASA" |

Rule of thumb: **ongoing, visible, moderated → Integration. One answer, now
→ Data.** Preview a term on the Data API (1 credit on most platforms) before
committing it as a feed source; search collected posts with `search_posts`
when the account already has feeds.

## How to call it

- **Juicer connector (MCP, preferred).** 33 tools, one per API operation,
  served from `https://api.juicer.io/mcp`. Works in claude.ai, Cowork and
  Claude Code. Auth is OAuth in the browser; you never handle a key.
- **curl + jq (Claude Code fallback).** Same operations against
  `https://api.juicer.io/v1` with a Bearer key. Use it only when the connector
  is not connected, or for shell loops over many pages. See the appendix.

Every tool result is the API's JSON body as text. Read the keys named in
each section below; fetch the OpenAPI spec for anything else.

- OpenAPI spec (authoritative for every schema): https://developers.juicer.io/openapi/v1.yaml
- Tool catalog: https://developers.juicer.io/mcp-tools
- Docs: https://developers.juicer.io (append `.md` to any docs URL for markdown)
- Product page: https://www.juicer.io/api
- Skills repo: https://github.com/juicer-io/skills

---

## ⚠️ Five Hard Rules (Read First)

**Rule 1 — Every Data API call spends credits. Check the balance before a
loop.** `get_account` (`GET /account`) returns `credits.balance` and
`credits.cost_per_call`. A free account starts with 30 credits that never
refill; Facebook costs 6 per platform per call, Instagram, TikTok and LinkedIn
3, everything else 1. When the balance cannot cover a call the API answers
402 `insufficient_credits` with `error.action.checkout_url`. Show that link to
the user; do not retry. Integration tools never spend credits.

**Rule 2 — Pagination cursors are per platform, not top level.** One Data API
call returns one page per platform (page size varies: Reddit 25–125, YouTube
50, Instagram ~12, X ~11). The next cursor lives at
`.meta.platforms[].next_cursor`, only for entries with `has_more: true`. There
is no top-level cursor. To page several platforms in one call, pass their
cursors comma-separated in the same order as `platforms`. Integration lists
paginate the ordinary way: `page`, `per_page` (max 100), `.meta.total_pages`.

**Rule 3 — `mentions` matching is loose; re-filter on your side.** The keyword
matcher is a substring match: `asana` also returns "Casanova". Always apply a
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
`unknown_platform`, `feed_limit_reached`, `source_limit_reached`,
`user_limit_reached`, `forbidden` (plan gate), `not_found`, `invalid_date`.
Plan gates carry `error.action = { type: "upgrade_plan", upgrade_url,
required_plan_display_name }`.

---

## Authentication

The Juicer connector is listed on this plugin's **Connectors** tab in claude.ai
and Cowork; in Claude Code it loads with the plugin and `/mcp` shows its state.
On first use Claude opens the browser: the user enters their email (a new
account is created on the spot, no dashboard needed), clicks the emailed link,
and approves. Claude holds the resulting key; nothing to paste. If a tool call
returns a 401 the connector re-runs that flow by itself. Never ask the user for
a key when the connector is available.

A brand-new email gets a Free feed plan and a Sandbox API plan (30 credits).
Confirm what the account can do with `get_account` before promising anything.

Without the connector (Claude Code only), see **Appendix: curl path**.

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
- At 0 credits every Integration tool keeps working; only `/data/*` is
  blocked.

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

## Account and platforms

**`get_account`** → `.data`: `plan`, `plan_display_name` (feed plan),
`usage.feeds {current, limit}`, `usage.views {current, limit}`,
`usage.sources_per_feed_limit`, `features {api_enabled, moderation, mentions}`,
`api_plan`, `api_plan_display_name`, `credits {…}` (see Credits). Call it first
in any session: it tells you whether a feed can be created, how many sources it
may hold, and how many Data API calls are affordable.

**`list_platforms`** → `.data[]`: `platform` (the exact string to pass
everywhere), `display_name`, `term_types[] {term_type, display_name, data_api,
requires_connection? {provider, description}}`; plus `.data_api_platforms[]`.
`Twitter` is the platform value for X (the Data API also accepts `X`).

---

## Data API

Direct lookups with no feed and no social-account connection. Costs credits
(Rule 1).

**`get_data_posts`** arguments: `term` (required), `platforms` (required,
comma-separated), `term_type` (optional), `cursor` (optional, Rule 2).

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
`post_created_at`, `like_count`, `comment_count`, `share_count`, `view_count`,
`poster {name, display_name, url, image}`, `media[] {type, url}`,
`referenced_post`) and `.meta.platforms[]` (`platform`, `success`, `count`,
`has_more`, `next_cursor`, or `error_code` + `message` when that platform
failed: `fetch_timeout`, `invalid_term_type`, `invalid_term`,
`unknown_platform`, `platform_error`, `invalid_cursor`). A failed platform
never fails the call; the others still return data. There is no `limit`
argument: take the newest N from the page yourself.

**`get_data_profiles`** arguments: `term` (up to 5 handles, comma-separated,
no hashtags), `platforms`. Response `.data[]` groups of `{platform, term,
exact_match, profiles[] {platform, platform_id, handle, display_name, url,
image, description, verified, metrics {follower_count, post_count,
recent_post_engagement}}}`. `exact_match: false` means the list is best-effort
candidates. For Google the "profiles" are places and `platform_id` is the Place
ID to pass to `get_data_posts` with `term_type: "reviews"`. Reddit, X and the
scrapers can take 10–15 s per platform; Instagram profiles occasionally hit
`fetch_timeout`, retry once.

---

## Feeds and sources

A feed is a container Juicer syncs on a schedule (`sync_interval`). Sources
are what it pulls: one handle, hashtag, page or URL per source.

**`create_feed {name}`** → `.data {id, name, slug, sources_count,
sync_interval, moderation {…}}`. Free plan: 1 feed (`feed_limit_reached` with
an `upgrade_plan` action beyond that).

**`get_feed {feed_id, include: "sources"}`** → the feed plus `.data.sources[]`
(same as **`list_sources {feed_id}`**). **`list_feeds {page, per_page}`** →
`.data[]`, `.meta.total_count`.

**`update_feed {feed_id, name?, queue?, allowed?, disallowed?, profanity?,
prevent_duplicates?, deduplication_strategy?}`**: only passed fields change.
`queue: true` turns on the moderation queue (new posts wait for approval);
`allowed`/`disallowed` are comma-separated word lists; `deduplication_strategy`
is `prioritize_top_source` or `distribute_across_sources`. The response
echoes `moderation {enabled, allowed, disallowed, profanity_filter,
prevent_duplicates, deduplication_strategy, ai_moderation_available, …}`.

**`create_source {feed_id, platform, term, term_type, options?}`** with
`platform` and `term_type` exactly as `list_platforms` returns them. Response
`.data {id, platform, term, term_type, syncable, unsyncable_reason,
synced_at}`. The first sync starts at once; `list_feed_posts` usually shows
posts within seconds for Bluesky, Reddit and YouTube, longer for the rest.
`options` is platform-specific (`retweets`, `replies` for Twitter;
`only_reels`, `only_posts` for Instagram). Errors: `source_limit_reached`
(Free: 1 per feed), `social_account_required` (Pattern 6),
`validation_failed` with `details` (bad `term_type`), `invalid_platform`
(wrong spelling).

**`delete_source`**, **`delete_feed`**: destructive, confirm first.

---

## Posts and moderation

**`list_feed_posts {feed_id, status?, filter?, search?, starting_at?,
ending_at?, page?, per_page?}`** → `.data[]` of `{id, platform, url, message,
external_created_at, poster, media, like_count, comment_count, share_count,
moderation_status, pinned, ai_sentiment, ai_decision_reason}`, `.meta`
pagination. `status` is `public` (live in the feed, default), `moderated`
(waiting in the queue) or `rejected` (hidden). `filter` narrows by source term,
platform name or source id; `search` matches message, poster name and
description; dates must parse or the call is `invalid_date`.

**`get_feed_post {feed_id, post_id}`** → one post with the same shape.

**`moderate_post {feed_id, post_id, action}`** with `action` = `approve`
(publish from the queue), `reject` (hide), `pin`, `unpin`, `delete` (soft
delete, destructive). Returns the updated post.

**`bulk_moderate_posts {feed_id, action_type, post_ids? | tab?,
excluded_post_ids?}`** with `action_type` = `approve`, `reject`, `soft_delete`
or `hard_delete` (irreversible), applied either to `post_ids` or to every post
in `tab` = `public`, `moderation_queue` or `trash`, minus `excluded_post_ids`.
Returns an empty object on success.

A moderation pass is: `update_feed {queue: true}` once → `list_feed_posts
{status: "moderated"}` → `moderate_post` per post, or `bulk_moderate_posts`
with the ids the user approved → `list_feed_posts {status: "public"}` to
confirm.

---

## Embed

**`get_feed_embed {feed_id}`** → `.data {feed_url, javascript, iframe,
wordpress_shortcode, wordpress_php}`. Give the user the snippet for their
stack: `javascript` for any site, `iframe` where scripts are not allowed,
`wordpress_shortcode` or `wordpress_php` for WordPress. The feed renders
whatever is `public`; moderation changes show on the next load.

---

## Search across feeds

**`search_posts {query, feed_ids?, platforms?, starting_at?, ending_at?,
page?, per_page?}`** searches posts already collected into the account's feeds
(free). `query` terms separated by `,` are OR, by `+` are AND; spaces are
stripped. Response `.data[]` posts, `.meta` pagination with `total_count`.
On accounts with many feeds a query without `feed_ids` can time out; scope to
the feeds you mean. For posts that are not in any feed, use `get_data_posts`.

---

## Analytics

**`get_feed_analytics {feed_id, start?, end?}`** (`YYYY-MM-DD`, default last
30 days) → `.data {period {start, end}, summary {total_posts, total_likes,
total_comments, total_engagement, page_views, clicks}, sources[] {id,
platform, term, posts_count, total_likes, total_comments}, top_posts[]}`.
`page_views` and `clicks` come from the embed; the rest from the posts
collected in the window. Compare two windows with two calls.

---

## Webhooks

**`create_webhook {url, subscribed_events}`** with events from
`post.created`, `social_account.expiring`, `social_account.expired`. The
response carries `secret` **once**: show it to the user to store; payloads
are signed with HMAC-SHA256 over the raw body in the `X-Juicer-Signature`
header. `post.created` delivers `{posts[], feed {id, name}, source {id,
platform}}`.

**`test_webhook {webhook_id}`** sends `{test: true, message, timestamp}` to
the endpoint so the user can verify their receiver. **`update_webhook`**
changes `url`, `subscribed_events` or `status` (`active` / `paused`).
`list_webhooks` shows `status` and `consecutive_failures`; a webhook that
keeps failing is paused by Juicer. **`delete_webhook`** removes it for good;
prefer `paused` when the user may want it back.

---

## Social connections

Only the Integration API needs these, and only for the term types whose
`list_platforms` entry has `requires_connection`. **`get_social_account_status`**
→ `.data[] {platform, provider, connected, allows_multiple}`; the `provider`
string (`facebook`, `instagram_login`, `tiktok`, …) is what
**`create_social_account_connect_url {provider}`** takes. It returns
`.data.connection_url`, a 30-minute magic link the user opens to authorise
the account; no Juicer login is needed. **`list_social_accounts`** lists what
is connected with `expired` and `expires_at`; subscribe to
`social_account.expiring` to hear about it early. **`delete_social_account
{social_account_id}`** disconnects one and stops every source that relied on
it syncing; confirm first.

---

## Team

**`create_user {email, role, feed_ids?, skip_invitation_email?}`** with `role`
= `manager` (all feeds) or `collaborator` (assigned feeds only; pass
`feed_ids`). Needs the Team or Enterprise plan, otherwise
`user_limit_reached` with an `upgrade_plan` action. **`assign_user_feed`** and
**`unassign_user_feed`** adjust a collaborator's feeds; unassigning their last
feed is refused (`last_feed_removal_blocked`), delete the user instead.
`list_users` → `.data[] {id, email, role, invitation_pending, feed_ids}`.

---

## Common Patterns

### Pattern 1: What are people saying about a brand on Reddit (2–3 pages, filtered)

`get_account` (check `credits.balance` ≥ 3) → `get_data_posts
{term:"Notion", platforms:"Reddit", term_type:"mentions"}` → read
`meta.platforms[0].next_cursor` → repeat with `cursor` while `has_more` and
the posts are still on-topic → word-boundary filter (Rule 3) → report with
`url` on every finding.

Brand corpora are small: 2–3 pages of `mentions` usually exhaust years of
history. Do not over-page; every page costs credits.

### Pattern 2: Cross-platform brand monitor

`get_data_posts {term:"Notion", platforms:"Reddit,Twitter,TikTok",
term_type:"mentions"}` is one call, 3 credits, one page per platform. Check
each `meta.platforms[]` entry: a `fetch_timeout` on one platform is normal,
retry only that platform.

Everyday-word terms (like "juicer") return an ambient firehose. A full page
spanning ≤3 days is the tell. Prefer the distinctive brand word; avoid dotted
domains (`notion.so` returns unrelated results, use `notion`).

### Pattern 3: A brand's latest posts across every network

"Give me Juicer's last 5 posts on all social networks" is one `get_data_posts`
call, but a bare handle means different people on different platforms:
`juicer` is the brand on LinkedIn and TikTok, a hairstyle seller on
Pinterest, an unrelated person on X. Never pass one handle to every platform.

1. Ask the user for the handle per platform, or resolve with
   `get_data_profiles {term, platforms}` and keep only matches whose
   `display_name` is the brand (`exact_match` only says the handle exists).
2. Call `get_data_posts {term:<handle>, platforms:<that platform>,
   term_type:"username"}` for the confirmed platforms only; a wrong handle
   still costs credits and returns a stranger's feed. Group several platforms
   in one call only when they share the handle.
3. There is no `limit` parameter: take the newest N per platform from each
   page (`post_created_at`), or merge and sort across platforms.
4. Bluesky needs the full handle (`juicer.bsky.social`); Instagram and
   Facebook fail with `invalid_term` when the account does not exist.

Twelve platforms in one call cost about 19 credits. On a Sandbox key that is
most of the lifetime budget, so confirm the platforms before calling.

### Pattern 4: What a community is talking about

`get_data_posts {term:"webdev", platforms:"Reddit", term_type:"channel"}` or
`{term:"nasa", platforms:"YouTube"}` (channel auto-detected). Sort by
`comment_count` or `like_count` on your side.

### Pattern 5: Set up a social wall from scratch

1. `get_account`: confirm `usage.feeds` has room and note
   `usage.sources_per_feed_limit`.
2. `list_platforms`: pick the exact `platform` and `term_type` per source; note
   any `requires_connection`.
3. `get_social_account_status` for those providers; if one is not connected,
   Pattern 6 first.
4. `create_feed {name}` → `create_source` once per handle or hashtag.
5. `list_feed_posts {feed_id}` after a few seconds to show the first posts;
   `update_feed {queue: true}` if the user wants to approve before publishing.
6. `get_feed_embed {feed_id}` → hand over the snippet for their stack.

### Pattern 6: Handle a missing social connection

`create_source` answers `social_account_required` with
`error.action = { type: "connect_social_account", provider, connection_url,
expires_at }`. Send the user to `connection_url` (a 30-minute magic link, no
Juicer login needed), wait for them to confirm, then retry `create_source`.
`create_social_account_connect_url {provider}` returns the same link on demand
as `.data.connection_url`.

### Pattern 7: Morning moderation pass

`list_feed_posts {feed_id, status: "moderated", per_page: 50}` → summarise
what is waiting (poster, first line of `message`, `url`, any `ai_sentiment`)
→ the user says which to publish → `bulk_moderate_posts {feed_id,
action_type: "approve", post_ids: [...]}` and `reject` for the rest →
`moderate_post {action: "pin"}` for the one they want on top. Confirm with
`list_feed_posts {status: "public"}`. Never `hard_delete` without an explicit
ask.

### Pattern 8: Monthly feed report

`get_feed_analytics {feed_id, start: "2026-09-01", end: "2026-09-30"}` and the
same for the previous month → compare `summary` (`total_posts`,
`total_engagement`, `page_views`, `clicks`) → rank `sources[]` by
`posts_count` and engagement → list `top_posts[]` with `url`. One free call
per window per feed; `list_feeds` first when the user has several.

### Pattern 9: Tell me when new posts arrive

`create_webhook {url: <their HTTPS endpoint>, subscribed_events:
["post.created"]}` → show the user the one-time `secret` and the
`X-Juicer-Signature` rule → `test_webhook {webhook_id}` so they see a delivery
→ `update_webhook {status: "paused"}` to stop without deleting. Add
`social_account.expiring` when the feed depends on a connected account.

### Pattern 10: Give a colleague access to one feed

`create_user {email, role: "collaborator", feed_ids: [<feed>]}` →
`assign_user_feed` for more feeds later → `delete_user` to revoke. Expect
`user_limit_reached` on Free and Pro: surface `error.action.upgrade_url`.

---

## Common Gotchas

1. **Credits run out before rate limits do.** A Sandbox key has 30 credits for life. Check `get_account` first; a 402 carries `error.action.checkout_url`.
2. **Top-level cursor does not exist.** Use `.meta.platforms[].next_cursor` per platform; comma-join them for multi-platform paging.
3. **`mentions` matching is loose.** `asana` also matches "Casanova". Re-filter with a word-boundary regex.
4. **X `message` fields embed HTML.** Strip tags before displaying or matching.
5. **`mentions` is Reddit, Twitter/X and TikTok only** on the Data API, whatever `list_platforms` says for the Integration API.
6. **Dotted terms** (bare domains like `notion.so`) return unrelated results. Use the bare brand word.
7. **Everyday-word terms** ("juicer") return an ambient firehose. A full page spanning ≤3 days is the tell.
8. **Brand corpora are small.** 2–3 pages of `mentions` usually exhaust years of history. Don't over-page.
9. **`social_account_required`** carries an `error.action.connection_url`. Send the user there; don't guess a workaround.
10. **`requires_connection` is Integration-API only.** The Data API works without any social connection on 14 platforms.
11. **`fetch_timeout` on one platform** is a partial result, not a failure. Retry that platform alone.
12. **`/authorize` keys are session keys** (12h max) and never revoke other keys. Prefer the connector or a permanent key.
13. **`search_posts` `+` must be URL-encoded** as `%2B` in curl; a bare `+` becomes a space. The tool handles it.
14. **This file is not the schema.** Fetch the OpenAPI spec for exact request and response shapes.
15. **Spell platforms as `list_platforms` returns them** (`Bluesky`, `TikTok`, `X` or `Twitter`). Lowercase is `unknown_platform` on the Data API and an empty filter on `search_posts` until case-folding ships.
16. **Connection `provider` names are not platform names.** Read them from `get_social_account_status` (`facebook`, `instagram_login`, `tiktok`, …); `instagram` is `invalid_provider`.
17. **Free-plan limits are `isError` results with an `error.action` upgrade link**: `source_limit_reached` (1 source per feed), `user_limit_reached` (no team members), `last_feed_removal_blocked`. Show the link; do not retry.
18. **A feed shows nothing until its first sync lands.** Wait a few seconds and call `list_feed_posts` again before declaring a source empty; check `syncable` and `unsyncable_reason` on the source if it stays empty.

---

## Appendix: curl path (Claude Code without the connector)

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

| Key | TTL | Rate limit |
|---|---|---|
| Connector (OAuth) or dashboard | none | plan-dependent |
| `/authorize`, unconfirmed | 2h | 60 req/hr, data calls gated |
| `/authorize`, confirmed | 12h | 300 req/hr, 60 req/min |

### Quick reference

```bash
H="Authorization: Bearer $KEY"; J="Content-Type: application/json"
B=https://api.juicer.io/v1

# Discovery
curl -s $B/account -H "$H"                                                                # plan, limits, credits.balance
curl -s $B/platforms -H "$H"                                                              # term types, data_api flag
curl -s $B/social_accounts/status -H "$H"                                                 # connections needed

# Data API (no feed, no connection; costs credits)
curl -s "$B/data/posts?term=<T>&term_type=mentions|channel|hashtag|username|reviews&platforms=<P1,P2>" -H "$H"
curl -s "$B/data/posts?...&cursor=<C1>,<C2>" -H "$H"                                      # next page per platform
curl -s "$B/data/profiles?term=<h1,h2>&platforms=<P>" -H "$H"                             # canonical profiles

# Integration API (free)
curl -s $B/feeds -H "$H"                                                                  # list_feeds (page, per_page)
curl -s -X POST $B/feeds -H "$H" -H "$J" -d '{"name":"My Wall"}'                          # create_feed → .data.id
curl -s -X PATCH $B/feeds/<id> -H "$H" -H "$J" -d '{"queue":true}'                        # update_feed
curl -s -X POST $B/feeds/<id>/sources -H "$H" -H "$J" \
  -d '{"platform":"Instagram","term":"myhandle","term_type":"username"}'                 # create_source
curl -s "$B/feeds/<id>/posts?status=moderated" -H "$H"                                    # list_feed_posts (public|moderated|rejected)
curl -s -X POST $B/feeds/<id>/posts/<pid>/approve -H "$H"                                 # moderate_post (approve|reject|pin|unpin), DELETE for delete
curl -s -X POST $B/feeds/<id>/posts/bulk -H "$H" -H "$J" \
  -d '{"action_type":"approve","post_ids":[1,2]}'                                         # bulk_moderate_posts (or "tab")
curl -s $B/feeds/<id>/embed -H "$H"                                                       # get_feed_embed → .data.javascript / .iframe
curl -s "$B/search/posts?query=<Q>&feed_ids=1,2" -H "$H"                                   # search_posts (+ as %2B for AND; comma = OR)
curl -s "$B/feeds/<id>/analytics?start=2026-09-01&end=2026-09-30" -H "$H"                 # get_feed_analytics
curl -s -X POST $B/social_accounts/connect_url -H "$H" -H "$J" -d '{"provider":"facebook"}'  # → .data.connection_url
curl -s -X POST $B/webhooks -H "$H" -H "$J" -d '{"url":"https://…","subscribed_events":["post.created"]}'
curl -s -X POST $B/webhooks/<id>/test -H "$H"                                             # test_webhook
curl -s -X POST $B/users -H "$H" -H "$J" -d '{"email":"a@b.co","role":"collaborator","feed_ids":[1]}'
curl -s -X PUT $B/users/<uid>/feeds/<fid> -H "$H"                                         # assign_user_feed; DELETE to unassign

# Schemas
curl -s https://developers.juicer.io/openapi/v1.yaml
```

### Paged Data API loop (credit and rate-limit aware)

```bash
TERM="Notion"; PLATFORM="Reddit"; MAX_PAGES=3
H="Authorization: Bearer $KEY"; CURSOR=""; PAGE=0
> posts.jsonl
while :; do
  URL="https://api.juicer.io/v1/data/posts?term=$TERM&term_type=mentions&platforms=$PLATFORM"
  [ -n "$CURSOR" ] && URL="$URL&cursor=$CURSOR"
  CODE=$(curl -s -o out.json -w '%{http_code}' "$URL" -H "$H")
  case $CODE in
    429) sleep 15; continue ;;
    402|4*|5*) jq . out.json; exit 1 ;;    # Rule 5: insufficient_credits, email_confirmation_required, …
  esac
  jq -c --arg t "$TERM" '
    .data[] | .message |= gsub("<[^>]*>";"")
    | select(.message | test("\\b" + $t + "\\b"; "i"))' out.json >> posts.jsonl   # Rule 3
  PAGE=$((PAGE+1))
  CURSOR=$(jq -r '.meta.platforms[] | select(.success and .has_more) | .next_cursor' out.json | head -1)
  [ -z "$CURSOR" ] || [ "$PAGE" -ge "$MAX_PAGES" ] && break
  sleep 1.2
done
jq -r '[.post_created_at, .poster.name, .url] | @tsv' posts.jsonl
```
