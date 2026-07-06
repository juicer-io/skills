# Juicer API Reference

**Install this and your agent knows how to drive the
[Juicer API](https://www.juicer.io/api).**

A knowledge skill (no workflow): whenever your agent writes code or curl
against `api.juicer.io` — pulling social data, building a feed, wiring
webhooks, embedding a social wall — it loads this reference first instead of
guessing.

## What's inside

- **Both API surfaces**: the Integration API (feeds, sources, moderation,
  embed codes, analytics, webhooks) and the Data API (posts and profiles for
  any handle/hashtag/subreddit/keyword — no feed required, no per-platform
  OAuth for public data).
- **Email-only signup**: `POST /authorize` gets a key with no dashboard —
  including the device flow for existing users.
- **The full endpoint map**, the `term_type` × platform matrix, and working
  curl recipes.
- **The gotchas that aren't in the docs**: per-platform pagination cursors,
  loose keyword matching (and how to re-filter), homonym tells, the
  email-confirmation gate, HTML embedded in X messages.
- Pointers to the authoritative sources for schemas: the
  [OpenAPI spec](https://developers.juicer.io/openapi/v1.yaml) and
  [developers.juicer.io](https://developers.juicer.io) (every docs page is
  fetchable as markdown by appending `.md`).

## Install

**Claude Code:**

```
/plugin marketplace add juicer-io/skills
/plugin install juicer@juicer-skills
```

**Manual (any agent):** copy `skills/juicer/` into your agent's skills
directory.

Then just build: "pull the last 100 Reddit posts mentioning my brand",
"create a Juicer feed for our Instagram and give me the embed code", "set up
a webhook for new posts" — the agent knows the way.

---

Built by the [Juicer](https://www.juicer.io) team. Sibling skills in this
marketplace put the API to work out of the box:
[topic-scout](../topic-scout) (find what to write) and
[mention-scout](../mention-scout) (find where to reply).
