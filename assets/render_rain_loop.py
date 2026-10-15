import subprocess
import numpy as np
from PIL import Image

plate_path = r"C:\Users\jhert\OneDrive\Desktop\Youtube\assets\iter14_coder_loft_clean_rain.jpg"
output_path = r"C:\Users\jhert\OneDrive\Desktop\Youtube\assets\iter14_coder_loft_rain_loop.mp4"

img = Image.open(plate_path)
arr = np.array(img, dtype=np.float32) / 255.0
H, W, _ = arr.shape

# 1. Build precise window mask
mask = np.zeros((H, W), dtype=np.float32)
mask[35:630, 970:1376] = 1.0   # Right main window
mask[35:260, 620:970] = 1.0    # Upper level window

lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
# Exclude steel muntins
mask[lum < 0.11] = 0.0
# Exclude brass sousaphone
is_brass = (lum > 0.25) & (arr[:, :, 0] > 0.38) & (arr[:, :, 2] < 0.22)
mask[is_brass] = 0.0

# 2. Terminal screen region for blinking cursor & telemetry
# Terminal is on right screen around x: 585-700, y: 540-670
term_x = (585, 700)
term_y = (540, 670)

# 3. Setup video parameters
fps = 24
duration = 6.0  # 6 seconds seamless loop
n_frames = int(fps * duration)

# 4. Generate seamless rain streaks and droplets
np.random.seed(42)
n_streaks = 250
streak_x0 = np.random.uniform(970, 1376, n_streaks)
streak_y0 = np.random.uniform(0, H, n_streaks)
streak_len = np.random.uniform(15, 35, n_streaks)
streak_speed = np.random.uniform(180, 320, n_streaks) # pixels per loop
streak_alpha = np.random.uniform(0.15, 0.4, n_streaks)

# Rivulets sliding down glass
n_rivulets = 18
riv_x = np.random.uniform(980, 1360, n_rivulets)
riv_speed = np.random.uniform(60, 120, n_rivulets)
riv_phase = np.random.uniform(0, 1, n_rivulets)

# Setup FFmpeg pipe
cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{W}x{H}",
    "-pix_fmt", "rgb24",
    "-r", str(fps),
    "-i", "-",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-crf", "18",
    "-preset", "fast",
    output_path
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

print(f"Rendering {n_frames} frames ({duration}s @ {fps}fps) to {output_path}...")

for f in range(n_frames):
    t_norm = f / n_frames  # 0 to 1
    t_sec = f / fps
    frame = arr.copy()
    
    # Layer A: Rain streaks on windows
    streak_overlay = np.zeros((H, W), dtype=np.float32)
    for i in range(n_streaks):
        y_curr = (streak_y0[i] + streak_speed[i] * t_norm) % H
        x_curr = streak_x0[i] - 0.25 * (streak_speed[i] * t_norm) # slight wind slant
        x_int = int(x_curr) % W
        y_int = int(y_curr)
        l = int(streak_len[i])
        y1 = max(0, y_int - l)
        y2 = min(H, y_int)
        if 0 <= x_int < W and y2 > y1:
            streak_overlay[y1:y2, x_int] = np.maximum(streak_overlay[y1:y2, x_int], streak_alpha[i])
    
    # Layer B: Rivulets running down glass
    riv_overlay = np.zeros((H, W), dtype=np.float32)
    for j in range(n_rivulets):
        ry = (riv_speed[j] * (t_norm + riv_phase[j])) % 1.0 * H
        rx = int(riv_x[j] + 4.0 * np.sin(ry * 0.03))
        if 970 <= rx < 1370:
            y_start = max(0, int(ry) - 25)
            y_end = min(H, int(ry))
            for k in range(-1, 2):
                if 0 <= rx + k < W:
                    riv_overlay[y_start:y_end, rx + k] = 0.35 * (1.0 - abs(k) * 0.4)
    
    # Combine rain into window area only
    total_rain = (streak_overlay + riv_overlay) * mask
    
    # Apply rain to frame (brightening highlights and slight refraction blur)
    for c in range(3):
        frame[:, :, c] = np.clip(frame[:, :, c] + total_rain * (0.6 + 0.4 * (c == 2)), 0.0, 1.0)
    
    # Layer C: Coder terminal blinking cursor at 1.0 Hz
    cursor_on = (np.sin(2.0 * np.pi * t_sec * 1.5) > 0.0)
    if cursor_on:
        # Cursor block around x: 672, y: 642
        frame[642:648, 672:676, :] = [0.2, 0.9, 0.3] # bright terminal green
    
    # Convert to 8-bit RGB
    out_frame = (frame * 255.0).astype(np.uint8)
    proc.stdin.write(out_frame.tobytes())

proc.stdin.close()
proc.wait()
print(f"Successfully generated video: {output_path}")
