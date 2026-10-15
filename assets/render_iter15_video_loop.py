import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

def render_iter15_loop():
    plate_path = r"C:\Users\jhert\OneDrive\Desktop\Youtube\assets\iter15_coder_loft_art_synth_aquarium.jpg"
    rain_video_path = r"C:\Users\jhert\OneDrive\Desktop\Youtube\assets\seedance_rain_window_source.mp4"
    output_path = r"C:\Users\jhert\OneDrive\Desktop\Youtube\assets\iter15_coder_loft_actual_rain_loop.mp4"
    fps = 24

    print(f"Loading master plate: {plate_path}")
    base_img = Image.open(plate_path).convert("RGB")
    base_arr = np.array(base_img, dtype=np.float32) / 255.0
    H, W, _ = base_arr.shape

    # 1. Exact window glass polygon strictly bounded by steel frame:
    # Synthesizer, leather couch, brick sill, aquarium, and ceiling beam are 100% excluded.
    poly = [
        (1030, 200),   # Top-left corner of window glass under roller shade
        (1240, 0),     # Header line meets top ceiling edge
        (1348, 0),     # Top-right corner of window glass
        (1348, 385),   # Right edge down to above aquarium rim
        (1160, 385),   # Horizontal line across top of aquarium rim
        (1160, 438),   # Vertical step-down along aquarium left glass flank
        (1030, 438)    # Horizontal line along bottom steel sill frame (strictly above synth/sofa)
    ]

    mask_img = Image.new('L', (W, H), 0)
    draw = ImageDraw.Draw(mask_img)
    draw.polygon(poly, fill=255)

    # Exclude aquarium LED fixture & black mounting arm
    draw.rectangle([1215, 318, 1348, 345], fill=0)

    # Explicit safety zero-outs:
    # 1. Complete aquarium enclosure (water, corals, fish, glass, stand):
    draw.rectangle([1160, 385, 1376, 768], fill=0)
    # 2. Complete indoor room below window sill (modular synth, keys, couch, wall):
    draw.rectangle([0, 438, 1376, 768], fill=0)

    # Convert to float array
    mask = np.array(mask_img, dtype=np.float32) / 255.0

    # 2. Exclude all black steel muntins and frame bars
    # In the window area, the steel muntins are dark (lum < 0.12)
    lum = 0.299 * base_arr[:, :, 0] + 0.587 * base_arr[:, :, 1] + 0.114 * base_arr[:, :, 2]
    is_steel = (lum < 0.12) & (mask > 0)
    mask[is_steel] = 0.0

    # Slight 0.5px Gaussian feather for anti-aliasing without bleeding
    mask = gaussian_filter(mask, sigma=0.5)

    # 3. Extract and scale rain video frames
    # Bounding box of the window
    rw_x1, rw_x2 = 1030, 1348
    rw_y1, rw_y2 = 0, 438
    rw_w = rw_x2 - rw_x1
    rw_h = rw_y2 - rw_y1

    print(f"Extracting rain video frames from {rain_video_path}...")
    cmd_extract = [
        "ffmpeg", "-y",
        "-i", rain_video_path,
        "-r", str(fps),
        "-vf", f"scale={rw_w}:{rw_h}",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-"
    ]
    proc_ext = subprocess.Popen(cmd_extract, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    frame_bytes = rw_w * rw_h * 3
    raw_frames = []
    while True:
        raw = proc_ext.stdout.read(frame_bytes)
        if not raw or len(raw) < frame_bytes:
            break
        f_arr = np.frombuffer(raw, dtype=np.uint8).reshape((rw_h, rw_w, 3)).astype(np.float32) / 255.0
        raw_frames.append(f_arr)
    proc_ext.stdout.close()
    proc_ext.wait()

    # 4. Construct seamless loop with crossfade
    total_raw = len(raw_frames)
    overlap = int(fps * 0.75) # 0.75s crossfade
    loop_frames = []
    effective_len = total_raw - overlap
    for i in range(effective_len):
        loop_frames.append(raw_frames[i].copy())
    for j in range(overlap):
        alpha = j / float(overlap)
        idx_tail = effective_len + j
        blended = (1.0 - alpha) * raw_frames[idx_tail] + alpha * loop_frames[j]
        loop_frames[j] = blended

    n_loop = len(loop_frames)
    print(f"Constructed seamless loop with {n_loop} frames ({n_loop / fps:.2f}s).")

    # 5. Setup FFmpeg encode pipe
    cmd_out = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "17",
        "-preset", "medium",
        output_path
    ]
    proc_out = subprocess.Popen(cmd_out, stdin=subprocess.PIPE)

    print(f"Compositing into {output_path}...")
    mask_3d = np.repeat(mask[:, :, np.newaxis], 3, axis=2)

    for f_idx in range(n_loop):
        t_sec = f_idx / float(fps)
        composite = base_arr.copy()

        # Place rain video onto the window canvas
        rain_canvas = np.zeros((H, W, 3), dtype=np.float32)
        rain_canvas[rw_y1:rw_y2, rw_x1:rw_x2] = loop_frames[f_idx]

        # Screen blend: bright water droplet highlights & sliding streaks
        # applied strictly within the glass panes (behind the black steel muntins)
        blended_window = 1.0 - (1.0 - composite) * (1.0 - rain_canvas * 0.85)
        composite = composite * (1.0 - mask_3d) + blended_window * mask_3d

        # Micro-animation: Classic Coder terminal blinking cursor at 1.5 Hz
        cursor_active = (np.sin(2.0 * np.pi * t_sec * 1.5) > 0.0)
        if cursor_active:
            composite[508:514, 804:808, :] = [0.2, 0.95, 0.35]

        out_uint8 = (np.clip(composite, 0.0, 1.0) * 255.0).astype(np.uint8)
        proc_out.stdin.write(out_uint8.tobytes())

    proc_out.stdin.close()
    proc_out.wait()
    print(f"Photoreal rain composite rendered successfully: {output_path}")

if __name__ == "__main__":
    render_iter15_loop()
