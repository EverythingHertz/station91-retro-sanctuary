# Dependency Maps and System Topology

## High-Level Topology

```mermaid
graph TD
    subgraph "Infrastructure (Hetzner / AWS)"
        H[Hetzner CCX33 / RTX 4000] -->|Primary| C[Dockerized Broadcast Cells]
        A[AWS g4dn.xlarge] -->|Cold Standby| C
    end

    subgraph "Rendering Pipeline"
        C --> X[Xvfb Virtual Display]
        X --> K[Chromium Kiosk]
        K --> HUD[Web App HUD /broadcast?scene=]
        HUD --> F[FFmpeg stream.sh]
    end

    subgraph "YouTube Distribution"
        F -->|RTMP 4K30| YT1[Channel A: Officewave]
        F -->|RTMP 4K30| YT2[Channel B: Cyberpunk]
        F -->|RTMP 4K30| YT3[Channel C: Solarium]
    end

    subgraph "Control Plane"
        W[Python Watchdog] -->|Poll| YT1
        W -->|Poll| YT2
        W -->|Poll| YT3
        W -->|Self-Heal / Rotate| C
        B[Live Concierge Bot] -->|API| YT1
    end
```

## Core Dependencies
- **OS/Containerization:** Docker, Docker Compose
- **Graphics/Display:** Xvfb, Chromium (Kiosk Mode)
- **Encoding:** FFmpeg (NVENC hardware acceleration)
- **Audio:** 320 kbps AAC stem generators
- **Automation:** Python (Watchdog, YouTube Data API v3, Live Chat API)
