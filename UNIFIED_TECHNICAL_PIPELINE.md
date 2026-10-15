# Unified Technical Pipeline: Station 91

## Architecture Overview

The technical architecture unifies two distinct production systems into a lean, automated workflow:
1. **The Autonomous 24/7 Broadcast Engine:** A single Dockerized server running headless Chromium, Xvfb, and FFmpeg NVENC to stream the Circadian Day/Night cycle to YouTube Live without downtime.
2. **The Decoupled Generative AI Production Pipeline:** A rapid-batch pipeline creating 15-second viral comedy shorts and 3-hour transformative Nintendo ambient VODs using Higgsfield AI, Midjourney, Kling/Runway, and ElevenLabs.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        24/7 HEADLESS BROADCAST NODE (Hetzner)                          │
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ Circadian Cron Dispatcher (06:00, 12:00, 18:00, 00:00 UTC)                     │   │
│   │ [Solarium] ──► [Retro Lounge] ──► [Officewave] ──► [Cyberpunk]                │   │
│   └───────────────────────────────┬────────────────────────────────────────────────┘   │
│                                   ▼                                                    │
│   ┌───────────────────────┐  ┌───────────────────────┐  ┌──────────────────────────┐   │
│   │ 4K Seamless Video     │  │ Xvfb Virtual Display  │  │ Multi-Stem Audio Bed     │   │
│   │ Loops (ProRes/H.265)  │  │ Chromium Kiosk (HUD)  │  │ 320kbps AAC Original Bed │   │
│   └───────────┬───────────┘  └───────────┬───────────┘  └────────────┬─────────────┘   │
│               │                          │                           │                 │
│               └──────────────────────────┼───────────────────────────┘                 │
│                                          ▼                                             │
│                     ┌────────────────────────────────────────┐                         │
│                     │ FFmpeg Stream Pipeline (stream.sh)      │                         │
│                     │ NVENC Hardware Encoding (1440p30/4K30) │                         │
│                     └───────────────────┬────────────────────┘                         │
│                                         │                                              │
└─────────────────────────────────────────┼──────────────────────────────────────────────┘
                                          ▼ RTMP Ingest
                       ┌─────────────────────────────────────┐
                       │ YouTube Live Broadcast: Station 91  │
                       └──────────────────┬──────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     ┌────────────────────────┐                     ┌────────────────────────┐
     │ Python Watchdog Daemon │                     │ Live Concierge Bot     │
     │ • Health & Stalls      │                     │ • YouTube Chat API     │
     │ • 72h Asset Rotation   │                     │ • Night Receptionist   │
     │ • Auto-Restart         │                     │ • Ephemeral Unlock Code│
     └────────────────────────┘                     └────────────────────────┘
```

---

## 1. The Autonomous 24/7 Broadcast Engine

### Docker Compose Configuration (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  broadcast-node:
    image: station91/broadcast-cell:latest
    container_name: station91-broadcast
    restart: always
    runtime: nvidia
    environment:
      - DISPLAY=:99
      - RESOLUTION=2560x1440x24
      - YT_STREAM_KEY=${YOUTUBE_STREAM_KEY}
      - CURRENT_SCENE=officewave
    volumes:
      - ./assets/plates:/app/plates:ro
      - ./assets/audio:/app/audio:ro
      - ./config:/app/config
    devices:
      - /dev/nvidia0:/dev/nvidia0
      - /dev/nvidiactl:/dev/nvidiactl
      - /dev/nvidia-uvm:/dev/nvidia-uvm
    command: /app/start_broadcast.sh

  watchdog:
    build: ./watchdog
    container_name: station91-watchdog
    restart: always
    environment:
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
      - BROADCAST_ID=${YOUTUBE_BROADCAST_ID}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

### The Seamless Circadian Scene Switcher (`switch_scene.sh`)
To switch scenes without breaking the live RTMP connection or resetting stream keys:
1. FFmpeg reads video plates from a named FIFO pipe (`/tmp/video_pipe`) or local loopback relay.
2. At scheduled hour marks (06:00, 12:00, 18:00, 00:00 UTC), a cron task sends an IPC signal to Chromium to update the HUD parameter (`?scene=retro_lounge`).
3. The video pipe smoothly crossfades the next 4K ProRes loop while maintaining continuous PTS timestamps, ensuring zero stream buffering for viewers.

### Hardware Encoding Flags (`stream.sh`)
```bash
#!/usr/bin/env bash
set -e

# Target: 1440p30 at 9,000 kbps (optimal quality-to-bandwidth ratio on YouTube Live)
ffmpeg -re \
  -stream_loop -1 -i "/app/plates/${CURRENT_SCENE}_loop.mp4" \
  -f x11grab -video_size 2560x1440 -framerate 30 -i :99.0 \
  -stream_loop -1 -i "/app/audio/${CURRENT_SCENE}_playlist.m3u8" \
  -filter_complex "[0:v][1:v]overlay=0:0:shortest=1[outv]" \
  -map "[outv]" -map 2:a \
  -c:v h264_nvenc -preset p4 -tune hq -b:v 9000k -maxrate 10000k -bufsize 18000k \
  -g 60 -keyint_min 60 \
  -c:a aac -b:a 320k -ar 48000 \
  -f flv "rtmp://a.rtmp.youtube.com/live2/${YT_STREAM_KEY}"
```

---

## 2. The Decoupled AI Shorts Pipeline

Solo creators fail when they attempt to generate animal characters, actors, and explosions in a single text-to-video prompt. Our pipeline completely **decouples** character consistency from physics destruction.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        DECOUPLED AI SHORTS ASSEMBLY LINE                               │
│                                                                                        │
│  [ STEP 1: AUDIO TRACK FIRST (ElevenLabs + Synth Bed) ]                                │
│  • Pacing locked at 15.00s. Chad screaming + deadpan Alf tag + punchline SFX.          │
│                                   │                                                    │
│                                   ▼                                                    │
│  [ STEP 2: CHARACTER BASE ]                [ STEP 3: DESTRUCTION VIDEO ]               │
│  • Midjourney v6 / Higgsfield              • Runway Gen-3 Alpha / Kling AI             │
│  • Fixed seed & character bible            • Pure environment physics only             │
│  • Alf transparent PNG library             • "Wrecking ball crashes, glass debris"     │
│                                   │                                                    │
│                                   ▼                                                    │
│  [ STEP 4: COMPOSITING & SELLING THE SHOT (CapCut / Premiere) ]                        │
│  • Drop transparent Alf layer over background physics plate                            │
│  • Apply camera shake at impact frame (t = 0:04.2)                                     │
│  • Apply VHS tracking noise and color grading overlay                                  │
│  • Export 9:16 vertical 1080x1920 60fps                                               │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Character Consistency Bible: Alf
* **Prompt Descriptor:** `chubby fluffy orange tabby cat, neon pink sweatband on forehead, tiny neon green legwarmers, deadpan unblinking facial expression, retro 1980s VHS screengrab --ar 9:16 --v 6.0`
* **Maintain Consistency:** Use Midjourney's `--cref [URL]` referencing the master approved portrait or Higgsfield Nano Banana character consistency engine.

### Environment Destruction Prompting (No Animals in Prompt)
* **Prompt Formula:** `Static wide shot of a 1980s mirrored aerobics gym. At second 2, a massive iron wrecking ball violently crashes through the center mirrors. Heavy shattered glass explosions, flying drywall debris, rigid body physics, dust clouds. No people, no animals, photorealistic 1980s film quality --motion 7`

---

## 3. Classic Nintendo Capture & Transformative CRT Shader Pipeline

### Legal & Transformative Packaging
1. **Zero-Audio Gameplay Capture:** Capture 60fps HDMI gameplay from original hardware or open-source software (RetroArch) with all native audio muted.
2. **Transformative Canvas Composition:**
   * Frame gameplay at 4:3 native ratio inside an asset layer of a vintage Sony Trinitron PVM monitor.
   * Apply GLSL CRT shader passes:
     * `scanlines.glsl`: Subtle scanline mask and phosphorus aperture grille.
     * `bloom.glsl`: Warm phosphorus glow on bright highlights.
     * `curvature.glsl`: Subtle 2.5% spherical barrel distortion simulating curved glass.
3. **Ambient Room Layer:** The CRT monitor sits on a teak desk next to a steaming mug of black coffee, rain trickling down the windowpane, and an animated loop of Alf snoozing gently next to the console.
4. **Mastering Audio:** Lay original in-house chiptune/lofi audio beds at **−14 LUFS integrated** for YouTube long-form standards.
