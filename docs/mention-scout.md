# Mention Scout

**Find the conversations your brand should be part of — and how to show up
well.**

A skill for Claude Code and compatible agents, powered by the
[Juicer Data API](https://www.juicer.io/api)
([docs](https://developers.juicer.io)).

## What it does

- **Finds reply-worthy threads** across Reddit and X: fresh
  recommendation-asks ("best tool for…?"), competitor complaints and outage
  reports, open comparison discussions — ranked by freshness, intent, and
  how answerable they still are.
- **Surfaces your own unanswered mentions** — questions and misconceptions
  about your brand that deserve a response, the highest-priority replies of
  all.
- **Suggests the angle, not just the link**: for each opportunity, what a
  genuinely helpful reply covers, where your product fits *if* it does, and
  your disclosure line.
- **Flags astroturfed threads as traps** — conversations seeded by a
  competitor's sock accounts are listed under "do not engage," with the
  tell-tale signs.

## What it deliberately does NOT do

Undisclosed promotion. Every suggested reply includes your affiliation
disclosure; the skill refuses fake-question seeding outright — its sibling,
[topic-scout](../topic-scout), ships the detector for exactly that behavior,
and so does every good moderator.

## Install

**Claude Code:**

```
/plugin marketplace add juicer-io/skills
/plugin install mention-scout@juicer-skills
```

**Manual (any agent):** copy `skills/mention-scout/` into your agent's
skills directory. Single instruction file, runs on `curl` + `jq` — no other
installs. No dashboard either: first run signs you up for a free Juicer API
key with just your email (one confirmation click in your inbox). If you
already use topic-scout, mention-scout reuses its brand config and key.

## Usage

- "Where can I mention my brand this week?" / "find threads we should reply
  to" — runs the sweep.
- Follow up with "draft the reply for #2" — it writes the reply in your
  voice, disclosure included.

Everything the skill collects lives in `./mention-scout-data/`.

---

Built by the [Juicer](https://www.juicer.io) team. The same API that powers
this skill powers embeddable social feeds and walls — if you ever need your
social content *on* your website, you know where the key works.
