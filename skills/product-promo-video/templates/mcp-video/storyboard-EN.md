# Juicer MCP video · Storyboard (EN)

**Status:** reference template. It renders, but its content has not been reviewed with anyone.
Treat it as a starting point, not an approved video.

**Format:** 52 s · 1920×1080 MP4 · motion graphics, no voiceover, no presenter · on-screen text carries the story · no setup steps
**Look:** navy `#102738`, coral highlights, white-text Juicer logo top-left
**UI:** neutral "AI assistant" chat window (no Claude/ChatGPT branding), "Juicer connected"
**Data:** fictional hotel (Hotel Solenne, #stayatsolenne) with guest posts and Google reviews, "Example data" pill bottom-right
**Use cases:** the three customer MCP tools with the clearest payoff: `get_feed_analytics`,
`bulk_moderate_posts`, `search_posts`

---

## Scene 1 · Hook (0–3.6 s)
Kinetic headline, words rise in with blur.
**On screen:** What if you could just **ask** your social feeds?

## Scene 1b · Name (3.3–5.2 s)
**On screen:** Meet the Juicer **MCP**

## Scene 2 · The idea (5–9 s)
Two white tiles pop in: Juicer mark ("Your Juicer feeds") and an AI spark ("Your AI assistant"),
joined by a dashed line with travelling dots.
**On screen:** Your social feeds, **right inside your AI assistant.**

## Scene 3 · Use case 1: Feed analytics (9–22 s)
Chat window flies in. The prompt types itself:
> Which posts got the most engagement this month?

Tool chip: `Juicer · Feed analytics`. Answer builds row by row:

| Post | Source | Engagements (likes + comments) |
|---|---|---|
| Sunset from our rooftop | Instagram | 1,324 |
| A slow morning at the spa | TikTok | 1,012 |
| Meet our concierge team | LinkedIn | 437 |

Row 1 lights up. **Worth knowing:** your two best posts are videos from Instagram and TikTok.
**Caption:** See which posts people **engage with most**.

## Scene 4 · Use case 2: Moderation (22–36 s)
> Tidy up our lobby wall before check-in

Tool chip: `Juicer · Moderation`. Dozens of incoming post cards (platform colour dots) pile up
across the frame, a coral counter counts to 186 "posts waiting for review", then everything
collapses into the chip and the sorted queue appears:
1. `Approve` 171 guest photos look good · Approve them all in one go?
2. `Review` 9 posts mention another hotel
3. `Reject` 6 posts contain blocked words

**Caption:** Clear your moderation queue **in one go**.
(Ends on the sorted queue the user confirms, not on posts disappearing by themselves.)

## Scene 5 · Use case 3: Search posts (36–46 s)
> What are guests saying about our new rooftop bar?

Tool chip: `Juicer · Search posts`. Two post cards:
- "Best view in the city!" · Google Reviews · 5 stars
- "Cocktails worth the trip" · Instagram · 214 likes

Callout: **42 posts** mention the rooftop bar so far, most of them on Instagram.
**Caption:** Hear what people **say about you**.

## Scene 6 · Outro (46–52 s)
**On screen:** Ask in plain language. Get answers you can **act on.**
End card: **Juicer MCP** · Your social feeds, one question away.

---

## Open for review
- `get_feed_analytics` ranks top posts by likes + comments; clicks exist only as a feed total, so
  the table shows engagements, not per-post clicks.
- `search_posts` searches posts already collected into the account's feeds, so the rooftop bar
  example only works if those sources are in a feed.
- Google Reviews sources fetch up to 5 reviews per sync (Places API limit), so the "42 posts"
  callout credits Instagram, not Google.
- The outline "juicer" lettering in the background is texture, not a brand-book element.
- Outro avoids naming specific AI clients.
