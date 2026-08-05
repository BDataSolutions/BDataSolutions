"""Render a claymation-style promo video for BData Solutions."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio.v2 as imageio

W, H = 1280, 720
FPS = 12
rng = random.Random(7)

TEAL = (38, 166, 154)
DEEP = (30, 60, 100)
ORANGE = (255, 138, 60)
CREAM = (246, 240, 228)
CLAYBG = (222, 213, 196)

try:
    FONT_BIG = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    FONT_MED = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
    FONT_SM = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
except OSError:
    FONT_BIG = FONT_MED = FONT_SM = ImageFont.load_default()

def clay_blob(draw, cx, cy, r, color, seed, wobble=0.10, points=24):
    """Irregular blob outline = handmade clay look."""
    rr = random.Random(seed)
    pts = []
    for i in range(points):
        a = 2 * math.pi * i / points
        rad = r * (1 + wobble * (rr.random() - 0.5) * 2)
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a) * 0.95))
    draw.polygon(pts, fill=color)

def speckle(img, seed, n=900):
    d = ImageDraw.Draw(img, "RGBA")
    rr = random.Random(seed)
    for _ in range(n):
        x, y = rr.randrange(W), rr.randrange(H)
        s = rr.choice([1, 1, 2])
        shade = rr.choice([(0, 0, 0, 14), (255, 255, 255, 16)])
        d.ellipse([x, y, x + s, y + s], fill=shade)
    return img

def base_frame(bg=CLAYBG, seed=0):
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    # soft clay floor
    clay_blob(d, W // 2, H + 260, 620, tuple(max(0, c - 18) for c in bg), seed + 99, 0.05, 30)
    return img, d

def jitter(k, amp=3):
    """Per-frame stop-motion jitter."""
    rr = random.Random(k)
    return rr.randint(-amp, amp), rr.randint(-amp, amp)

def clay_text(d, text, cx, cy, font, color, fseed, drop=True):
    jx, jy = jitter(fseed * 31 + len(text), 2)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = cx - tw // 2 + jx, cy - th // 2 + jy
    if drop:
        d.text((x + 4, y + 5), text, font=font, fill=(0, 0, 0, 60))
    d.text((x, y), text, font=font, fill=color)

def eyes(d, cx, cy, r, fseed, mood="happy"):
    for sx in (-1, 1):
        ex, ey = cx + sx * r * 0.38, cy - r * 0.15
        d.ellipse([ex - 16, ey - 20, ex + 16, ey + 20], fill=(255, 255, 255))
        blink = (fseed % 36) < 2
        if blink:
            d.line([ex - 12, ey, ex + 12, ey], fill=(40, 40, 40), width=5)
        else:
            d.ellipse([ex - 7, ey - 8, ex + 7, ey + 8], fill=(45, 45, 45))
    if mood == "happy":
        d.arc([cx - r * 0.35, cy + r * 0.05, cx + r * 0.35, cy + r * 0.5], 15, 165, fill=(50, 40, 35), width=6)
    else:
        d.arc([cx - r * 0.3, cy + r * 0.3, cx + r * 0.3, cy + r * 0.65], 195, 345, fill=(50, 40, 35), width=6)

def blob_b(d, cx, cy, r, fseed, mood="happy"):
    """B: teal clay blob mascot with glasses."""
    sq = 1 + 0.04 * math.sin(fseed * 0.9)  # breathing squash
    clay_blob(d, cx + 6, cy + 10, r, (0, 0, 0, 40), fseed // 3, 0.08)  # shadow-ish
    clay_blob(d, cx, cy, r * sq, TEAL, fseed // 3, 0.09)
    eyes(d, cx, cy, r, fseed, mood)
    # glasses
    for sx in (-1, 1):
        ex, ey = cx + sx * r * 0.38, cy - r * 0.15
        d.ellipse([ex - 22, ey - 26, ex + 22, ey + 26], outline=(60, 50, 45), width=5)
    d.line([cx - r * 0.38 + 22, cy - r * 0.15, cx + r * 0.38 - 22, cy - r * 0.15], fill=(60, 50, 45), width=5)

def tangle(d, cx, cy, spread, fseed, colors, n=10):
    rr = random.Random(fseed // 4)
    for i in range(n):
        pts = []
        x, y = cx + rr.randint(-spread, spread), cy + rr.randint(-60, 60)
        for _ in range(6):
            x += rr.randint(-90, 90); y += rr.randint(-50, 50)
            pts.append((x, y))
        d.line(pts, fill=colors[i % len(colors)], width=14, joint="curve")

def dashboard(d, cx, cy, w, h, fseed, grow=1.0):
    w, h = int(w * grow), int(h * grow)
    d.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], 24, fill=CREAM, outline=DEEP, width=6)
    if grow > 0.55:
        bars = [0.5, 0.8, 0.35, 0.95, 0.65]
        bw = w // 8
        for i, bh in enumerate(bars):
            bx = cx - w // 2 + int(w * 0.12) + i * int(bw * 1.3)
            top = cy + h // 2 - 24 - int((h - 70) * bh * min(1, (grow - 0.55) / 0.45))
            jx, _ = jitter(fseed + i, 2)
            d.rounded_rectangle([bx + jx, top, bx + bw + jx, cy + h // 2 - 24], 8,
                                fill=[TEAL, ORANGE, DEEP][i % 3])

frames = []

def hold(img, sec):
    for k in range(int(sec * FPS)):
        frames.append(np.asarray(img))

def scene(n_frames, painter):
    for k in range(n_frames):
        img, d = base_frame(seed=k)
        d = ImageDraw.Draw(img, "RGBA")
        painter(d, k, n_frames)
        speckle(img, k % 6)
        frames.append(np.asarray(img))

# ---- Scene 1: the problem (5s)
def s1(d, k, n):
    t = k / n
    tangle(d, W // 2, H // 2 + 60, 320, k, [ORANGE, DEEP, (180, 90, 120), (120, 140, 60)])
    # stressed owner blob (orange, no glasses)
    clay_blob(d, 250, 470, 110, ORANGE, k // 3, 0.09)
    eyes(d, 250, 470, 110, k, "sad")
    # teetering spreadsheet tower
    lean = min(28, int(t * 55))
    for i in range(6):
        jx, jy = jitter(k * 7 + i, 2)
        d.rounded_rectangle([950 + i * lean // 3 + jx, 520 - i * 52 + jy,
                             1110 + i * lean // 3 + jx, 560 - i * 52 + jy], 10,
                            fill=CREAM, outline=DEEP, width=4)
    clay_text(d, "Drowning in spreadsheets?", W // 2, 110, FONT_MED, DEEP, k)
scene(5 * FPS, s1)

# ---- Scene 2: meet B (5s)
def s2(d, k, n):
    t = k / n
    bx = int(-150 + (W // 2 + 150) * min(1, t * 2.2))  # rolls in
    bounce = abs(math.sin(t * 14)) * 26 * max(0, 1 - t * 2)
    blob_b(d, bx, 430 - int(bounce), 130, k)
    if t > 0.45:
        clay_text(d, "Meet BData Solutions", W // 2, 110, FONT_BIG, DEEP, k)
    if t > 0.62:
        clay_text(d, "Dynamics 365  ·  Power Platform  ·  CRM", W // 2, 190, FONT_SM, ORANGE, k)
scene(5 * FPS, s2)

# ---- Scene 3: transformation (7s)
def s3(d, k, n):
    t = k / n
    if t < 0.4:
        shrink = 1 - t / 0.4
        tangle(d, 880, 380, int(280 * shrink), k, [ORANGE, DEEP, (180, 90, 120)], n=max(2, int(10 * shrink)))
    grow = max(0.0, min(1.0, (t - 0.25) / 0.55))
    if grow > 0:
        dashboard(d, 880, 380, 520, 330, k, grow)
    blob_b(d, 260, 460, 120, k)
    clay_text(d, "Messy data  →  smart CRM", W // 2, 90, FONT_MED, DEEP, k)
    if t > 0.7:
        clay_text(d, "Automated workflows · Real insights", W // 2, 640, FONT_SM, DEEP, k)
scene(7 * FPS, s3)

# ---- Scene 4: happy ending (5s)
def s4(d, k, n):
    t = k / n
    dashboard(d, 900, 360, 480, 300, k, 1.0)
    clay_blob(d, 300, 470, 105, ORANGE, k // 3, 0.09)
    eyes(d, 300, 470, 105, k, "happy")
    blob_b(d, 520, 480, 105, k)
    # confetti
    rr = random.Random(3)
    for i in range(60):
        x0, spd = rr.randrange(W), rr.uniform(120, 380)
        y = (rr.randrange(H) + t * spd * 5) % H
        d.ellipse([x0, y, x0 + 10, y + 10], fill=[TEAL, ORANGE, DEEP][i % 3])
    clay_text(d, "Less chaos. More growth.", W // 2, 100, FONT_BIG, DEEP, k)
scene(5 * FPS, s4)

# ---- Scene 5: CTA (6s)
def s5(d, k, n):
    t = k / n
    words = [("BData Solutions", FONT_BIG, TEAL, 260, 0.08),
             ("www.barakabelle.ca", FONT_MED, DEEP, 380, 0.38),
             ("hellobdatasolutions@gmail.com", FONT_SM, ORANGE, 470, 0.62)]
    for text, font, color, y, start in words:
        if t >= start:
            p = min(1, (t - start) / 0.12)
            squash = 1.6 - 0.6 * p  # stamp-in squash
            clay_text(d, text, W // 2, int(y * (2 - squash) / 1.0) if p < 1 else y, font, color, k)
    blob_b(d, W // 2, 600, 80, k)
scene(6 * FPS, s5)

out = "/tmp/claude-0/-home-user-BDataSolutions/e8b5f2ae-3431-5d77-9233-5ca80f105b1a/scratchpad/bdata-claymation.mp4"
w = imageio.get_writer(out, fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p")
for f in frames:
    w.append_data(f)
w.close()
print("wrote", out, len(frames), "frames =", len(frames) / FPS, "s")
