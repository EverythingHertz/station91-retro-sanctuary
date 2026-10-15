import wave
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WORKSPACE = Path(r"c:\Users\jhert\OneDrive\Desktop\Youtube")
EP1_DIR = WORKSPACE / "assets" / "episodes" / "ep01"
EP1_DIR.mkdir(parents=True, exist_ok=True)

W, H = 720, 1280
SAMPLE_RATE = 44100
DURATION = 15.0


def generate_pavlovian_audio(wav_path: Path):
    """Synthesizes the 15.0s Master Audio Skeleton (80s FM synth + Tape-Stop + Crash + Escalation + Tag)."""
    n_samples = int(SAMPLE_RATE * DURATION)
    t = np.linspace(0.0, DURATION, n_samples, endpoint=False, dtype=np.float32)
    audio = np.zeros(n_samples, dtype=np.float32)

    # 1. 0.0s - 2.4s: Upbeat 135 BPM 1980s FM Synth-Pop Aerobics Hook
    mask_hook = (t >= 0.0) & (t < 2.4)
    t_h = t[mask_hook]
    beat_freq = 135.0 / 60.0
    notes = np.array([261.63, 329.63, 392.00, 523.25, 392.00, 329.63, 440.00, 523.25], dtype=np.float32)
    note_idx = (np.floor(t_h * beat_freq * 2) % len(notes)).astype(int)
    freqs = notes[note_idx]
    fm_mod = np.sin(2 * np.pi * freqs * 2.0 * t_h) * 1.8
    synth = 0.35 * np.sin(2 * np.pi * freqs * t_h + fm_mod)
    kick_env = np.exp(-((t_h * beat_freq) % 1.0) * 14.0)
    kick = 0.45 * np.sin(2 * np.pi * (110.0 * kick_env + 45.0) * t_h) * kick_env
    audio[mask_hook] = synth + kick

    # 2. 2.4s - 2.7s: Hard Tape-Stop / Vinyl Scratch into Silence
    mask_stop = (t >= 2.4) & (t < 2.65)
    t_s = (t[mask_stop] - 2.4) / 0.25
    pitch_drop = 440.0 * (1.0 - 0.88 * t_s)
    audio[mask_stop] = 0.5 * np.sin(2 * np.pi * pitch_drop * (t[mask_stop] - 2.4)) * (1.0 - t_s)

    # 3. 2.7s - 3.8s: Protocol 13 Ominous HUD Beep + "Alf?!" Pitch Inflection
    for beep_t in [2.75, 2.90]:
        m_b = (t >= beep_t) & (t < beep_t + 0.08)
        audio[m_b] += 0.35 * np.sin(2 * np.pi * 1760.0 * t[m_b])
    m_alf = (t >= 3.05) & (t < 3.65)
    t_a = (t[m_alf] - 3.05) / 0.60
    f_alf = 210.0 + 160.0 * t_a
    audio[m_alf] += 0.30 * (np.sin(2 * np.pi * f_alf * t[m_alf]) + 0.5 * np.sin(2 * np.pi * f_alf * 2 * t[m_alf])) * np.sin(np.pi * t_a)

    # 4. 3.8s - 9.5s: Primary Chaos (Massive Sub-Bass Impact + Wrecking Ball Glass Shatter)
    m_crash = (t >= 3.8) & (t < 9.5)
    t_c = t[m_crash] - 3.8
    rng = np.random.default_rng(91)
    noise = rng.normal(0, 1, len(t_c)).astype(np.float32)
    sub_boom = 0.75 * np.sin(2 * np.pi * (65.0 * np.exp(-t_c * 1.5) + 32.0) * t_c) * np.exp(-t_c * 0.65)
    shatter_env = np.exp(-t_c * 0.55) * (0.6 + 0.4 * np.sin(2 * np.pi * 7.0 * t_c))
    audio[m_crash] += np.clip(sub_boom + 0.42 * noise * shatter_env, -0.95, 0.95)

    # 5. 9.5s - 13.0s: Secondary Escalation (Firework Glitter Cannons + Siren + Sprinkler Hiss)
    m_esc = (t >= 9.5) & (t < 13.0)
    t_e = t[m_esc] - 9.5
    siren_freq = 680.0 + 240.0 * np.sin(2 * np.pi * 2.5 * t_e)
    siren = 0.25 * np.sin(2 * np.pi * siren_freq * t_e)
    pop_noise = rng.normal(0, 1, len(t_e)).astype(np.float32) * (np.sin(2 * np.pi * 6.0 * t_e) > 0.4).astype(np.float32) * 0.45
    audio[m_esc] += np.clip(siren + pop_noise, -0.9, 0.9)

    # 6. 13.0s - 13.5s: Pre-Tag Silence + Single Tiny Gym Bell Ding
    m_ding = (t >= 13.08) & (t < 13.48)
    t_d = t[m_ding] - 13.08
    audio[m_ding] += 0.40 * np.sin(2 * np.pi * 2093.0 * t_d) * np.exp(-t_d * 8.0)

    # 7. 13.5s - 15.0s: Alf Deadpan Baritone Tag ("Feel the burn.")
    m_tag = (t >= 13.55) & (t < 14.80)
    t_tg = t[m_tag] - 13.55
    f_baritone = 85.0 - 8.0 * (t_tg / 1.25)
    env_syllables = (np.sin(2 * np.pi * 2.4 * t_tg) > -0.2).astype(np.float32)
    baritone = 0.45 * (
        np.sin(2 * np.pi * f_baritone * t_tg)
        + 0.6 * np.sin(2 * np.pi * f_baritone * 2.0 * t_tg)
        + 0.3 * np.sin(2 * np.pi * f_baritone * 3.0 * t_tg)
    ) * env_syllables * np.exp(-t_tg * 0.5)
    audio[m_tag] += baritone

    pcm16 = (np.clip(audio, -0.98, 0.98) * 32767.0).astype(np.int16)
    stereo = np.column_stack([pcm16, pcm16]).flatten()

    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(stereo.tobytes())


def bake_vhs_beat_card(src_path: Path, dst_path: Path, badge: str, caption: str, accent=(255, 64, 180), tint=None):
    img = Image.open(src_path).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    arr = np.array(img, dtype=np.uint8)

    if tint is not None:
        arr = np.clip(arr.astype(np.int16) + np.array(tint, dtype=np.int16), 0, 255).astype(np.uint8)

    # CRT scanlines every 4 rows
    arr[::4, :, :] = (arr[::4, :, :].astype(np.uint16) * 82 // 100).astype(np.uint8)

    out_img = Image.fromarray(arr)
    draw = ImageDraw.Draw(out_img)
    try:
        font_lg = ImageFont.truetype("arialbd.ttf", 36)
        font_sm = ImageFont.truetype("consolab.ttf", 22)
    except Exception:
        font_lg = ImageFont.load_default()
        font_sm = ImageFont.load_default()

    # Top VHS HUD badge
    draw.rectangle([32, 42, W - 32, 96], fill=(12, 14, 22), outline=accent, width=3)
    draw.text((48, 56), badge, fill=(74, 222, 128), font=font_sm)

    # Center-safe bottom caption box
    draw.rectangle([36, 960, W - 36, 1060], fill=(10, 10, 16), outline=accent, width=3)
    draw.text((56, 988), caption, fill=(255, 255, 255), font=font_lg)

    out_img.save(dst_path)


def render_episode_1():
    wav_path = EP1_DIR / "ep01_audio_master.wav"
    out_mp4 = EP1_DIR / "Episode_01_The_Wrecking_Ball_15s_Master.mp4"
    generate_pavlovian_audio(wav_path)

    b1 = EP1_DIR / "_beat1.png"
    b2 = EP1_DIR / "_beat2.png"
    b3 = EP1_DIR / "_beat3.png"
    b4 = EP1_DIR / "_beat4.png"
    b5 = EP1_DIR / "_beat5.png"

    bake_vhs_beat_card(
        EP1_DIR / "chad_aerobics_setup.png", b1,
        "VHS PLAY ▶ 1987-08-14 | INCIDENT #01",
        "CHAD: \"And step, two, three, PUMP!\"",
        accent=(255, 64, 180),
    )
    bake_vhs_beat_card(
        EP1_DIR / "alf_crane_reveal.png", b2,
        "⚠ PROTOCOL 13: GRAVITY OVERRIDE",
        "CHAD: \"Wait... Alf?!\"",
        accent=(251, 191, 36),
    )
    bake_vhs_beat_card(
        EP1_DIR / "wrecking_ball_chaos.png", b3,
        "CRITICAL IMPACT // MIRROR WALL BREACH",
        "CHAD: \"ALF! NOOOOOOO—!\"",
        accent=(239, 68, 68),
    )
    bake_vhs_beat_card(
        EP1_DIR / "wrecking_ball_chaos.png", b4,
        "SECONDARY ESCALATION // GLITTER + GATORADE",
        "CHAD: \"WHY IS THERE GLITTER?!\"",
        accent=(56, 189, 248),
        tint=(15, -10, 35),
    )
    bake_vhs_beat_card(
        EP1_DIR / "alf_closeup_tag.png", b5,
        "STATION 91 // ALF STATUS: UNBOTHERED",
        "ALF: \"Feel the burn.\"",
        accent=(74, 222, 128),
    )

    concat_txt = EP1_DIR / "_concat.txt"
    concat_txt.write_text(
        f"file '{b1.as_posix()}'\nduration 2.4\n"
        f"file '{b2.as_posix()}'\nduration 1.4\n"
        f"file '{b3.as_posix()}'\nduration 5.7\n"
        f"file '{b4.as_posix()}'\nduration 3.5\n"
        f"file '{b5.as_posix()}'\nduration 2.0\n"
        f"file '{b5.as_posix()}'\n",
        encoding="utf-8",
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-i", str(wav_path),
        "-vf", "fps=24,format=yuv420p",
        "-c:v", "libx264", "-threads", "2", "-preset", "ultrafast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out_mp4),
    ]
    subprocess.run(cmd, check=True)

    for tmp in [b1, b2, b3, b4, b5, concat_txt]:
        if tmp.exists():
            tmp.unlink()

    print(f"[PASS] Rendered Episode 1 15s Master Short: {out_mp4} ({out_mp4.stat().st_size:,} bytes)")


if __name__ == "__main__":
    render_episode_1()
