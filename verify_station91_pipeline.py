import os
import zipfile
from pathlib import Path

WORKSPACE = Path(r"c:\Users\jhert\OneDrive\Desktop\Youtube")
BRAIN_DIR = Path(r"C:\Users\jhert\.gemini\antigravity\brain\80dec2fd-bd26-48f3-829a-0eb4f6c9da9a")

ZIP_MANIFEST = {
    "youtube_part1.zip": [
        "ALF_PRODUCTION_EXECUTION_PACK.md",
        "alf_aerobics_production_plan.md",
        "research_mega_prompts.md",
        "research_algorithmic_hook.md",
        "research_audio_branding.md",
        "research_technical_workflow.md",
        "research_comedic_escalation.md",
        "research_franchise_strategy.md",
    ],
    "youtube_part2.zip": [
        "STATION91_OPENMEOW_INTEGRATION_ARCHITECTURE.md",
        "MASTER_PROJECT_HANDOFF.md",
        "UNIFIED_CHANNEL_MASTER_BLUEPRINT.md",
        "UNIFIED_TECHNICAL_PIPELINE.md",
        "CHANNEL_PACKAGING_AND_BRAND_BIBLE.md",
        "CONTENT_PROGRAMMING_GRID_AND_CALENDAR.md",
        "VIRAL_SHORTS_SCRIPT_AND_PROMPT_VAULT.md",
        "verify_station91_pipeline.py",
    ],
    "youtube_part3_legacy_tracks.zip": [
        "AMBIENT_SANCTUARY_MASTER_INDEX.md",
        "DEPENDENCY_MAPS_AND_SYSTEM_TOPOLOGY.md",
        "GROK46_TRACK_3_MONETIZATION_AND_BRAND_INCUBATION.md",
        "GROK46_TRACK_4_OMNICHANNEL_GROWTH_AND_LIVESTREAMS.md",
    ],
    "youtube_part4_ep01_wrecking_ball.zip": [
        "assets/render_episode1_wrecking_ball.py",
        "assets/episodes/ep01/chad_aerobics_setup.png",
        "assets/episodes/ep01/alf_crane_reveal.png",
        "assets/episodes/ep01/wrecking_ball_chaos.png",
        "assets/episodes/ep01/alf_closeup_tag.png",
        "assets/episodes/ep01/ep01_audio_master.wav",
        "assets/episodes/ep01/Episode_01_The_Wrecking_Ball_15s_Master.mp4",
    ],
}

REQUIRED_ASSETS = [
    "assets/iter15_coder_loft_art_synth_aquarium.jpg",
    "assets/iter15_coder_loft_actual_rain_loop.mp4",
    "assets/Suite_B_v2_1_meute_lockin.mp3",
    "assets/station91_live_preview.html",
    "assets/render_iter15_video_loop.py",
    "assets/episodes/ep01/chad_aerobics_setup.png",
    "assets/episodes/ep01/alf_crane_reveal.png",
    "assets/episodes/ep01/wrecking_ball_chaos.png",
    "assets/episodes/ep01/alf_closeup_tag.png",
    "assets/episodes/ep01/Episode_01_The_Wrecking_Ball_15s_Master.mp4",
]


def sync_brain_artifacts():
    for fname in ["research_algorithmic_hook.md", "ALF_PRODUCTION_EXECUTION_PACK.md"]:
        src = BRAIN_DIR / fname
        dst = WORKSPACE / fname
        if src.exists():
            dst.write_bytes(src.read_bytes())


def build_and_verify_zips():
    print("=== Building & Verifying Compliant Zip Archives (Max 10 files/zip) ===")
    for zip_name, file_list in ZIP_MANIFEST.items():
        assert len(file_list) <= 10, f"Violation: {zip_name} has {len(file_list)} files (>10)"
        zip_path = WORKSPACE / zip_name
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for rel_name in file_list:
                fpath = WORKSPACE / rel_name
                if not fpath.exists():
                    raise FileNotFoundError(f"Missing required file for {zip_name}: {fpath}")
                zf.write(fpath, arcname=Path(rel_name).name)

        with zipfile.ZipFile(zip_path, "r") as zf_check:
            names = zf_check.namelist()
            bad = zf_check.testzip()
            assert bad is None, f"Corrupt entry in {zip_name}: {bad}"
            assert len(names) <= 10, f"Zip {zip_name} exceeded 10-file limit: {len(names)}"
            print(f"[PASS] {zip_name}: {len(names)}/10 files verified ({zip_path.stat().st_size:,} bytes)")


def verify_production_assets():
    print("\n=== Verifying Station 91 Production & Broadcast Assets ===")
    for rel_asset in REQUIRED_ASSETS:
        apath = WORKSPACE / rel_asset
        assert apath.exists() and apath.stat().st_size > 0, f"Missing or empty asset: {apath}"
        print(f"[PASS] {rel_asset} ({apath.stat().st_size:,} bytes)")


if __name__ == "__main__":
    sync_brain_artifacts()
    build_and_verify_zips()
    verify_production_assets()
    print("\nALL STATION 91 x OPENMEOW QUALITY GATES PASSED.")
