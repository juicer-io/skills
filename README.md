# Juicer

**Teach your AI agent to drive the Juicer social media API.**

The `juicer` plugin gives Claude, Codex, Cursor and other agents working
knowledge of the [Juicer API](https://www.juicer.io/api)
([docs](https://developers.juicer.io)): one API over Reddit, X, Instagram,
Facebook, TikTok, YouTube, LinkedIn, Pinterest, Bluesky, Tumblr, Vimeo, Flickr,
Giphy and more. No per-platform OAuth, no scraping setup.

It ships two parts: the **Juicer connector**, a remote MCP server at
`https://api.juicer.io/mcp` with 33 tools (one per API operation, OAuth sign-in
in the browser), and the **`juicer` skill**, which teaches the agent when and
how to use them: credits, per-platform pagination, loose keyword matching,
what needs a connected social account.

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

**claude.ai, Cowork and Claude Code:** add **Juicer** from the Claude
directory, then connect the Juicer connector from the plugin's Connectors tab
(claude.ai, Cowork) or let `/mcp` open the sign-in (Claude Code). You enter
your email, click the link, approve. No API key to copy.

**Claude Code from this repo:**

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

The plugin contains no scripts or binaries: a skill (Markdown) and a one-line
reference to the connector URL. Nothing in it holds a secret.

- **Connector path:** your agent calls `https://api.juicer.io/mcp`. Sign-in is
  OAuth 2.1 in your browser; Juicer issues an API key that Claude stores and
  sends as a Bearer token on each tool call. Tool arguments (search terms,
  handles, feed settings) are the only data sent. You can revoke the key from
  the Juicer dashboard at any time.
- The skill never reads a key from your environment or files, and never
  calls the API outside the connector.

No data goes anywhere except the Juicer API. Privacy policy:
https://www.juicer.io/privacy. Terms: https://www.juicer.io/terms.

## License

MIT. Built by the [Juicer](https://www.juicer.io) team.
