# Juicer

**Teach your AI agent to drive the Juicer social media API.**

The `juicer` skill gives Claude, Codex, Cursor and other agents working
knowledge of the [Juicer API](https://www.juicer.io/api)
([docs](https://developers.juicer.io)): one API over Reddit, X, Instagram,
Facebook, TikTok, YouTube, LinkedIn, Pinterest, Bluesky, Tumblr, Vimeo, Flickr,
Giphy and more. No per-platform OAuth, no scraping setup.

## What your agent can do with it

- **Look up social data without building anything:** posts for a keyword,
  hashtag, handle, subreddit or YouTube channel across several platforms in one
  call, plus canonical profiles per platform.
- **Build and run social feeds:** create feeds, add sources, moderate posts,
  pull analytics, and get embed codes (JavaScript, iframe, WordPress shortcode)
  for putting a social wall on any website.
- **Wire up the rest:** webhooks, OAuth connections for social accounts, and
  team users on multi-tenant accounts.
- **Avoid the mistakes that aren't in the docs:** per-platform pagination
  cursors, loose keyword matching that needs re-filtering, rate limits, and
  key lifetimes.

## Install

**Claude Code:**

```
/plugin marketplace add juicer-io/skills
/plugin install juicer@juicer-skills
```

**Any other agent** (Cursor, Codex, Gemini CLI, Copilot and more):

```bash
npx skills add juicer-io/skills
```

Or copy the folder straight into your agent's skills directory:

```bash
cp -r skills/juicer ~/.claude/skills/
```

**Then just ask:** "what are people on Reddit saying about Notion?", "embed
our Instagram and TikTok on the homepage", "pull last week's posts for
#coffee on Instagram and X". Invoke it directly with `/juicer` (`/juicer:juicer` when installed as a plugin).

## What it runs and sends

The skill is instructions only: no scripts, no binaries, no dependencies
beyond `curl` and `jq`. When you ask it to act, your agent calls
`https://api.juicer.io/v1` with your Juicer API key as a Bearer token and
nothing else. The key comes from `JUICER_API_KEY` if you set one, or from
Juicer's email-only signup (`POST /v1/authorize`), which sends only the email
address you give it and returns a free session key. No data goes anywhere
except the Juicer API.

## License

MIT. Built by the [Juicer](https://www.juicer.io) team.
