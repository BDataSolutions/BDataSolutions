# Video 9 — Production Plan (ready to run)

**Title:** AI Won't Save Messy Data. It Just Makes It Look Confident.
*(retitled from "Your Nonprofit's AI Problem Is Actually a Data Problem")*
**Publish:** Tuesday, August 11, 2026 · **Category:** Nonprofits & Activism
**Script runtime estimate:** 6:11 at 150 wpm — expect ~9:20 actual at BK's ~99 wpm pace.

## Status

| Item | State |
|---|---|
| Script | ✅ final (provided Aug 3) |
| Scene images | ⏳ 5 exist · **2 to generate** when credits reset (Aug 4, ~1:27 pm MT) |
| Narration audio | ❌ **blocking** — not yet provided |
| Assembly pipeline | ✅ built (`assemble_video.py`, `plan_beats.py`) |
| YouTube block | ✅ drafted below |

## Avatar rule (new, applies from Video 9 onward)

The avatar appears **when BK introduces herself**, not from 0:00. Every script
opens with a hook first, so beat 01 is always a non-avatar hook image and the
avatar enters on "I am Barakatou…". Videos 7 and 8 predate this rule and are
published/scheduled as-is — do not re-cut them.

## Scene plan

| # | Beat | Script cue | Image |
|---|---|---|---|
| 01 | Hook — shiny tool, untouched mess | "Here is a pattern I keep running into" | **NEW #1** |
| 02 | Self-intro | "I am Barakatou — or BK" | **NEW #2** (fresh avatar, must differ from V7/V8 intro) |
| 03 | Who it's for + the research | "This video is for you if" | `aadc3dde` tangled yarn → AI funnel |
| 04 | AI amplifies the mess | "Here is the thing about AI tools" | `e1d0b251` messy grid → polished report |
| 05 | Composite example | "Let me give you a concrete" | `aeb9eb2e` two ledgers, mismatched IDs |
| 06 | Three foundations | "So what does AI-ready data" | `ee54c35c` three foundation stones |
| 07 | Foundation before tool | "I know that is a less exciting" | `4c358bfc` avatar + clean dashboard |
| 08 | Outro | "That is the wrap for this week" | `823eb3f3` standing outro |

### Prompts for the two new images

**NEW #1 — Hook** (no avatar):
> Painterly 2.5D digital illustration, rich oil and acrylic brushwork texture, warm analytical lighting, palette of deep forest green #123326, teal #0F766E, gold #B8860B, cream #F5F1E6, fine-art aesthetic, non-photorealistic, textured brushstrokes, no readable text, no watermark. A glowing, expensive-looking AI tool box on a pedestal in a nonprofit office, brand new and gleaming, while the floor beneath it is covered in tangled, disordered paperwork it does not touch — conveying a costly purchase that solves nothing.

**NEW #2 — Self-intro avatar** (fresh framing, not the V7/V8 desk pose):
> Painterly 2.5D digital illustration, rich oil and acrylic brushwork texture, warm analytical lighting, palette of deep forest green #123326, teal #0F766E, gold #B8860B, cream #F5F1E6, fine-art aesthetic, non-photorealistic, textured brushstrokes, no readable text, no watermark. Featuring a friendly Black woman with a red patterned headwrap tied with a small bow, gold blazer over a dark top, and a chunky teal-and-gold statement necklace. She stands relaxed beside a window in a warm office, one hand gesturing openly as if mid-conversation, a softly glowing dashboard and a small stack of policy books on the desk behind her.

## Run order once audio arrives

```bash
# 1. trim narration (silence only)
ffmpeg -i raw.mp3 -af silenceremove=start_periods=1:stop_periods=-1:\
stop_duration=0.8:stop_threshold=-38dB narration.mp3

# 2. compute beat durations against the real audio
python3 plan_beats.py scale beats.json narration.mp3 > plan.json   # or: align

# 3. render + upload
python3 assemble_video.py config.json
```

`config.json` = narration URL, music (`five-of-a-kind-density-time.mp3`),
logo, presigned upload URL, and the `beats` array from `plan.json`.

## YouTube Studio block

**Title:** AI Won't Save Messy Data. It Just Makes It Look Confident. (54 chars)
**Alternates:** "Your AI Tool Isn't the Problem. Your Data Is." · "63% of Orgs Aren't Ready for AI — Here's the Fix"
*(vidIQ scoring pending — credits reset Aug 4)*

**Description:**

```
A nonprofit buys a shiny AI tool expecting it to finally make sense of their data — and months later they're more confused than when they started. It's almost never the tool's fault. In this video: why AI amplifies messy data instead of fixing it, and the three unglamorous foundations that have to exist first (none of them require new software).

⏱️ Chapters
[fill from plan.json after assembly]

▶️ Watch Next: "92% of Nonprofits Use AI — 47% Have No Rules for It"

📚 Sources Referenced
• Gartner — 63% of organizations lack or are unsure of AI-ready data practices
• Gartner — prediction: 60% of AI projects without AI-ready data abandoned through 2026

👋 About BData Solutions
BData Solutions is a data and analytics consultancy built for nonprofits and public sector programs — the organizations working on domestic violence support, homelessness, and precarious status. Practical data guidance for teams without a data team. New video every week.
🌐 www.barakabelle.ca

#NonprofitTech #DataQuality #AIforNonprofits #DataForGood #NonprofitLeadership #TechForGood
```

**Tags:** AI ready data, nonprofit data quality, AI nonprofit, messy data, data cleanup nonprofit, Gartner AI data, nonprofit reporting, client record matching, BData Solutions
**Settings:** Standard YouTube License · not made for kids · comments allowed, hold inappropriate for review

---

## Audio — processed 2026-08-07

| Version | Length | Link |
|---|---|---|
| **⭐ Final (cuts + denoise)** | 7:32 | https://d2ol7oe51mr4n9.cloudfront.net/user_3GhPyAdR8OQeZpTFjDtc2ne0Fdt/b81d02d7-2f9f-4375-810c-67ee9ca5f96e.mp3 |
| Silence-trim only (no content cuts) | 8:31 | https://d2ol7oe51mr4n9.cloudfront.net/user_3GhPyAdR8OQeZpTFjDtc2ne0Fdt/2e9c64bd-c7f0-481f-8069-86af85a54050.mp3 |
| Raw as recorded | 10:09 | `video9/video9_raw.m4a` |

Processing chain: silence trim (-40 dB, 0.9 s) → remove three retakes
(0:00–0:23 duplicate opening, 3:42–3:46 false start, 3:56–4:28 flubbed
"bad spreadsheet" passage) → highpass 85 Hz → FFT denoise (-28 dB) →
gentle compression (2.5:1) → loudnorm to −16 LUFS / −1.5 dBTP (YouTube spec).

**Blocked:** Videos 11–14 illustrations. Higgsfield balance is 0.08 credits
(free plan); 22 new images need ≈3.3 credits.
