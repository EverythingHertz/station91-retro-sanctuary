# Master Project Handoff: Station 91 Unified Channel

## Project Overview
This repository contains the complete architectural, creative, operational, and monetization framework for **Station 91: Retro Sanctuary** — the unified flagship YouTube channel combining:
1. **Viral AI Comedy Shorts:** High-retention 15-second retro mascot micro-sitcoms (Alf the Cat).
2. **Classic Nintendo & Chill Long-Form VODs:** Transformative 2–3 hour CRT nostalgic gameplay sessions backed by original in-house lofi/chiptunes.
3. **Autonomous 24/7 Headless Livestream:** Single-node circadian broadcast cell rotating through 4 mood archetypes on Hetzner CCX33.

---

## Core Documentation Index

| Blueprint File | Description |
|---|---|
| [UNIFIED_CHANNEL_MASTER_BLUEPRINT.md](./UNIFIED_CHANNEL_MASTER_BLUEPRINT.md) | The master strategic thesis, brand universe, algorithmic flywheel, and 12-month P&L model. |
| [CHANNEL_PACKAGING_AND_BRAND_BIBLE.md](./CHANNEL_PACKAGING_AND_BRAND_BIBLE.md) | Channel naming options, "About" copy, Higgsfield avatar & banner prompts, and thumbnail rules. |
| [CONTENT_PROGRAMMING_GRID_AND_CALENDAR.md](./CONTENT_PROGRAMMING_GRID_AND_CALENDAR.md) | The 3-tier programming grid, weekly upload schedule, and 30-day YPP monetization launch plan. |
| [UNIFIED_TECHNICAL_PIPELINE.md](./UNIFIED_TECHNICAL_PIPELINE.md) | Docker single-cell 24/7 stream engine, decoupled AI generation pipeline, and GLSL CRT shader stack. |
| [VIRAL_SHORTS_SCRIPT_AND_PROMPT_VAULT.md](./VIRAL_SHORTS_SCRIPT_AND_PROMPT_VAULT.md) | 10 ready-to-produce 15-second viral AI Shorts scripts with ElevenLabs audio cues and visual prompts. |

---

## Operational Playbook & Invariants

### 1. The Day-30 Monetization Invariant
* Do not dilute efforts across secondary channels. Direct all viral Shorts traffic to that week's long-form VOD using YouTube's native **"Related Video"** button to cross 1,000 subscribers and 4,000 watch hours on Day 30.

### 2. The 100% Owned Music Invariant
* Never use raw copyrighted Nintendo audio or licensed commercial music. All audio beds must use Jonathan Hertz's original 5-layer analog/hybrid stem compositions. Distribute all stems to Spotify/Apple Music under the Station 91 artist moniker for dual-stream royalties.

### 3. The Single Broadcast Cell Invariant
* Run only **one single 24/7 stream** on Hetzner CCX33 to pool all concurrent viewers into one chatroom and avoid multi-server bill bloat. The circadian scene switcher automatically transitions:
  * **06:00 UTC:** Shinkai Solarium (Morning Focus)
  * **12:00 UTC:** Nintendo Retro Lounge (Nostalgic Chill)
  * **18:00 UTC:** 1991 Late-Night Officewave (Deep Coding)
  * **00:00 UTC:** Midnight Cyberpunk Penthouse (Insomniac Tech)
* Python Watchdog executes graceful daily recycles at 04:17 UTC and rotates video/audio assets every 72 hours.
