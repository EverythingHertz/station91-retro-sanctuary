import os
import sys
import subprocess
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

def create_photoreal_rain_composite(
    plate_path=r"C:\Users\jhert\OneDrive\Desktop\Youtube\assets\iter14_coder_loft_clean_rain.jpg",
    rain_video_path=r"C:\Users\jhert\OneDrive\Desktop\Youtube\assets\seedance_rain_window_source.mp4",
    output_video_path=r"C:\Users\jhert\OneDrive\Desktop\Youtube\assets\iter14_coder_loft_actual_rain_loop.mp4",
    fps=24
):
    print(f"Loading master plate: {plate_path}")
    base_img = Image.open(plate_path).convert("RGB")
    base_arr = np.array(base_img, dtype=np.float32) / 255.0
    H, W, _ = base_arr.shape

    # 1. Build precise window mask
    mask = np.zeros((H, W), dtype=np.float32)
    # Right main warehouse window
    mask[35:630, 970:1376] = 1.0   
    # Upper mezzanine level window
    mask[35:260, 620:970] = 1.0    

    # Exclude dark steel muntins and interior frames
    lum = 0.299 * base_arr[:, :, 0] + 0.587 * base_arr[:, :, 1] + 0.114 * base_arr[:, :, 2]
    mask[lum < 0.115] = 0.0

    # Exclude brass sousaphone bell (warm golden tones on right edge)
    is_brass = (lum > 0.25) & (base_arr[:, :, 0] > 0.38) & (base_arr[:, :, 2] < 0.22)
    mask[is_brass] = 0.0

    # Soft feather on edges to avoid harsh matte lines
    mask = gaussian_filter(mask, sigma=0.8)

    # 2. Extract frames from rain video
    # Main right window dimensions:
    rw_x1, rw_x2 = 965, 1376
    rw_y1, rw_y2 = 30, 630
    rw_w = rw_x2 - rw_x1
    rw_h = rw_y2 - rw_y1

    # Upper window dimensions:
    uw_x1, uw_x2 = 620, 970
    uw_y1, uw_y2 = 35, 260
    uw_w = uw_x2 - uw_x1
    uw_h = uw_y2 - uw_y1

    print(f"Extracting frames from actual rain video: {rain_video_path}")
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
    rain_frames_rw = []
    while True:
        raw = proc_ext.stdout.read(frame_bytes)
        if not raw or len(raw) < frame_bytes:
            break
        f_arr = np.frombuffer(raw, dtype=np.uint8).reshape((rw_h, rw_w, 3)).astype(np.float32) / 255.0
        rain_frames_rw.append(f_arr)
    proc_ext.stdout.close()
    proc_ext.wait()
    print(f"Loaded {len(rain_frames_rw)} rain frames.")

    # Crossfade end into start for 100% seamless repeated loop
    total_raw = len(rain_frames_rw)
    overlap = int(fps * 0.75) # 0.75s crossfade
    loop_frames = []
    effective_len = total_raw - overlap
    for i in range(effective_len):
        loop_frames.append(rain_frames_rw[i].copy())
    for j in range(overlap):
        alpha = j / float(overlap)
        idx_tail = effective_len + j
        blended = (1.0 - alpha) * rain_frames_rw[idx_tail] + alpha * loop_frames[j]
        loop_frames[j] = blended

    n_loop = len(loop_frames)
    print(f"Constructed seamless loop with {n_loop} frames ({n_loop / fps:.2f}s).")

    # Precompute resized frames for upper window as well
    rain_frames_uw = []
    for f in loop_frames:
        img_f = Image.fromarray((f * 255).astype(np.uint8))
        img_uw = img_f.resize((uw_w, uw_h), Image.Resampling.BILINEAR)
        rain_frames_uw.append(np.array(img_uw, dtype=np.float32) / 255.0)

    # 3. Setup FFmpeg output stream
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
        output_video_path
    ]
    proc_out = subprocess.Popen(cmd_out, stdin=subprocess.PIPE)

    print(f"Compositing {n_loop} frames into {output_video_path}...")

    for f_idx in range(n_loop):
        t_sec = f_idx / float(fps)
        composite = base_arr.copy()

        # Place rain video onto the full frame buffer
        rain_canvas = np.zeros((H, W, 3), dtype=np.float32)
        rain_canvas[rw_y1:rw_y2, rw_x1:rw_x2] = loop_frames[f_idx]
        rain_canvas[uw_y1:uw_y2, uw_x1:uw_x2] = rain_frames_uw[f_idx]

        # Blend rain video onto background window panes:
        # Screen blend adds the bright highlights of water droplets and sliding rivulets
        # while keeping city lights and dark night tones rich
        mask_3d = np.repeat(mask[:, :, np.newaxis], 3, axis=2)
        
        # Screen blend: 1 - (1 - a)*(1 - b*gain)
        blended_window = 1.0 - (1.0 - composite) * (1.0 - rain_canvas * 0.85)
        
        # Apply composite only where mask allows
        composite = composite * (1.0 - mask_3d) + blended_window * mask_3d

        # Micro-animation: Classic Coder terminal cursor blink (1.5 Hz green block)
        # Position: right monitor command line (x: 672, y: 642)
        cursor_active = (np.sin(2.0 * np.pi * t_sec * 1.5) > 0.0)
        if cursor_active:
            composite[642:648, 672:676, :] = [0.2, 0.95, 0.35]

        out_uint8 = (np.clip(composite, 0.0, 1.0) * 255.0).astype(np.uint8)
        proc_out.stdin.write(out_uint8.tobytes())

    proc_out.stdin.close()
    proc_out.wait()
    print(f"Successfully generated photoreal rain composite: {output_video_path}")

if __name__ == "__main__":
    create_photoreal_rain_composite()
