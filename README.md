# Juicer Agent Skills

**Marketing skills for AI agents, powered by live social data.**

Skills in this repo teach your coding agent (Claude Code and compatible
harnesses) to do real marketing work using the
[Juicer Data API](https://www.juicer.io/api) ([docs](https://developers.juicer.io))
— one API over Reddit, X, Instagram, TikTok, Facebook, YouTube, LinkedIn, and
more. No per-platform OAuth, no scraping setup. Skills sign you up for a free API key in-flow with just your email —
you never open a dashboard.

## Skills

| Skill | What it does |
|---|---|
| [**topic-scout**](./topic-scout) | Finds blog topics your buyers are actually asking for. Mines competitor brand mentions across Reddit and X — years of real questions in buyers' own words, plus live complaints and outage reports — detects vendor astroturfing (and shows you which keywords competitors seed), and flags "changing right now" events (deprecations, breakage, pricing changes) before search volume exists. Every finding carries its source URL. |

| [**mention-scout**](./mention-scout) | Finds live conversations where your brand can genuinely join in: fresh "best tool for…?" asks, competitor complaints and outages, and unanswered mentions of your own brand — ranked by freshness and answerability, with a suggested angle for each reply. Disclosed engagement only; astroturfed threads are flagged as traps, not opportunities. |

More coming: brand monitoring (change detection on competitors and your own
mentions), idea validation as a standalone quick check.

## Install

**Claude Code (recommended):**

```
/plugin marketplace add juicer-io/skills
/plugin install topic-scout@juicer-skills
```

**Any other agent** — each skill is a self-contained folder of instructions
(no runtime, no dependencies beyond `curl` + `jq`). Copy it into your agent's
skills directory:

```bash
cp -r topic-scout/skills/topic-scout ~/.claude/skills/
```

**Then just ask.** Once installed, say "find me blog topic ideas" (first run
interviews you about your brand and signs you up for a free API key with your
email), or "should we write about \<idea\>?" to validate a specific one. You
can also invoke it directly: `/topic-scout:topic-scout`.

## What you'll get

See a real output: [topic-scout example report](./topic-scout/example-report.md)
— a live run for our own brand, including the moment it caught a competitor's
29-post astroturf network.

## Principles

- **Evidence, linked.** Every claim in every report carries its source URL.
- **Signal nominates, never decides.** Outputs end with a validation
  checklist, not a publish button.
- **Real voices only.** Distinct authors over years — never engagement sums,
  never astroturf.

## License

MIT. Built by the [Juicer](https://www.juicer.io) team.
