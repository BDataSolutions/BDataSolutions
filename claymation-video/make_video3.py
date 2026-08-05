"""BData Solutions claymation campaign video v2.
Hero: Belle, a Black woman in clay, rescues nonprofits/government/advocacy orgs
drowning in messy data, surrounded by vulnerable women who are lifted up."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio

W, H = 1280, 720
FPS = 12
TEAL = (38, 166, 154)
DEEP = (30, 60, 100)
ORANGE = (255, 138, 60)
PURPLE = (142, 88, 170)
CREAM = (246, 240, 228)
CLAYBG = (222, 213, 196)
SKIN = (121, 82, 57)        # warm brown clay
SKIN_D = (94, 62, 42)
WRAP = (178, 44, 38)        # headwrap orange
BLAZER = (240, 166, 65)     # teal blazer
GOLD = (233, 178, 70)

def font(sz):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", sz)
    except OSError:
        return ImageFont.load_default()
F64, F44, F34, F26, F22 = font(64), font(44), font(34), font(26), font(22)

def clay_blob(d, cx, cy, r, color, seed, wobble=0.09, points=24, squash=1.0):
    rr = random.Random(seed)
    pts = []
    for i in range(points):
        a = 2 * math.pi * i / points
        rad = r * (1 + wobble * (rr.random() - 0.5) * 2)
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a) * squash))
    d.polygon(pts, fill=color)

def speckle(img, seed, n=800):
    d = ImageDraw.Draw(img, "RGBA")
    rr = random.Random(seed)
    for _ in range(n):
        x, y = rr.randrange(W), rr.randrange(H)
        s = rr.choice([1, 1, 2])
        d.ellipse([x, y, x + s, y + s], fill=rr.choice([(0, 0, 0, 13), (255, 255, 255, 15)]))
    return img

def jitter(k, amp=2):
    rr = random.Random(k)
    return rr.randint(-amp, amp), rr.randint(-amp, amp)

def clay_text(d, text, cx, cy, fnt, color, k, drop=True):
    jx, jy = jitter(k * 31 + len(text), 2)
    b = d.textbbox((0, 0), text, font=fnt)
    x, y = cx - (b[2] - b[0]) // 2 + jx, cy - (b[3] - b[1]) // 2 + jy
    if drop:
        d.text((x + 3, y + 4), text, font=fnt, fill=(0, 0, 0, 55))
    d.text((x, y), text, font=fnt, fill=color)

def belle(d, cx, cy, s, k, arm="down"):
    """Belle: Black woman clay hero. s = scale (1.0 ~ 230px tall)."""
    jx, jy = jitter(k * 5, 2)
    cx, cy = cx + jx, cy + jy
    # skirt/blazer body
    clay_blob(d, cx, cy + 55 * s, 62 * s, BLAZER, k // 4 + 1, 0.07, squash=1.15)
    # arms
    if arm == "reach":  # reaching out to rescue
        d.line([cx + 30 * s, cy + 20 * s, cx + 105 * s, cy - 15 * s], fill=BLAZER, width=int(20 * s))
        clay_blob(d, cx + 108 * s, cy - 18 * s, 13 * s, SKIN, k // 4 + 7, 0.12)
    elif arm == "up":   # triumphant
        for sx in (-1, 1):
            d.line([cx + sx * 30 * s, cy + 20 * s, cx + sx * 78 * s, cy - 60 * s], fill=BLAZER, width=int(20 * s))
            clay_blob(d, cx + sx * 80 * s, cy - 64 * s, 13 * s, SKIN, k // 4 + 7 + sx, 0.12)
    else:
        for sx in (-1, 1):
            d.line([cx + sx * 28 * s, cy + 22 * s, cx + sx * 52 * s, cy + 85 * s], fill=BLAZER, width=int(20 * s))
            clay_blob(d, cx + sx * 54 * s, cy + 88 * s, 12 * s, SKIN, k // 4 + 7 + sx, 0.12)
    # head
    clay_blob(d, cx, cy - 42 * s, 40 * s, SKIN, k // 4 + 2, 0.06)
    # headwrap (crown-like)
    clay_blob(d, cx, cy - 72 * s, 34 * s, WRAP, k // 4 + 3, 0.10)
    clay_blob(d, cx - 20 * s, cy - 92 * s, 15 * s, WRAP, k // 4 + 4, 0.14)
    clay_blob(d, cx + 16 * s, cy - 95 * s, 13 * s, WRAP, k // 4 + 5, 0.14)
    # face
    for sx in (-1, 1):
        ex, ey = cx + sx * 15 * s, cy - 48 * s
        d.ellipse([ex - 8 * s, ey - 9 * s, ex + 8 * s, ey + 9 * s], fill=(255, 255, 255))
        if (k % 40) < 2:
            d.line([ex - 6 * s, ey, ex + 6 * s, ey], fill=(35, 25, 20), width=max(2, int(4 * s)))
        else:
            d.ellipse([ex - 4 * s, ey - 4 * s, ex + 4 * s, ey + 4 * s], fill=(35, 25, 20))
    d.arc([cx - 14 * s, cy - 36 * s, cx + 14 * s, cy - 18 * s], 15, 165, fill=(60, 30, 25), width=max(3, int(5 * s)))
    # gold earrings
    for sx in (-1, 1):
        d.ellipse([cx + sx * 36 * s - 5 * s, cy - 38 * s, cx + sx * 36 * s + 5 * s, cy - 28 * s], outline=GOLD, width=max(2, int(4 * s)))

def woman(d, cx, cy, s, k, color, mood="sad"):
    """Small clay woman figure (community member)."""
    jx, jy = jitter(k * 3 + int(cx), 2)
    cx, cy = cx + jx, cy + jy
    clay_blob(d, cx, cy + 26 * s, 30 * s, color, k // 4 + int(cx) % 9, 0.08, squash=1.15)
    clay_blob(d, cx, cy - 18 * s, 20 * s, SKIN, k // 4 + int(cx) % 9 + 1, 0.07)
    clay_blob(d, cx, cy - 34 * s, 16 * s, tuple(max(0, c - 60) for c in color), k // 4 + 2, 0.12)  # hair/scarf
    for sx in (-1, 1):
        ex, ey = cx + sx * 7 * s, cy - 21 * s
        d.ellipse([ex - 3 * s, ey - 3 * s, ex + 3 * s, ey + 3 * s], fill=(35, 25, 20))
    if mood == "sad":
        d.arc([cx - 8 * s, cy - 12 * s, cx + 8 * s, cy - 2 * s], 195, 345, fill=(60, 30, 25), width=3)
    else:
        d.arc([cx - 8 * s, cy - 14 * s, cx + 8 * s, cy - 4 * s], 15, 165, fill=(60, 30, 25), width=3)

def org(d, cx, cy, s, k, kind, sink=0.0, mood="sad"):
    """Org character: nonprofit (heart), government (building), advocacy (megaphone)."""
    jx, jy = jitter(k * 4 + int(cx), 2)
    cx, cy = cx + jx, cy + jy + int(sink * 55)
    col = {"np": PURPLE, "gov": DEEP, "adv": ORANGE}[kind]
    clay_blob(d, cx, cy, 55 * s, col, k // 4 + int(cx) % 7, 0.08)
    for sx in (-1, 1):
        ex, ey = cx + sx * 18 * s, cy - 10 * s
        d.ellipse([ex - 9 * s, ey - 11 * s, ex + 9 * s, ey + 11 * s], fill=(255, 255, 255))
        d.ellipse([ex - 4 * s, ey - 4 * s, ex + 4 * s, ey + 4 * s], fill=(40, 40, 40))
    if mood == "sad":
        d.arc([cx - 16 * s, cy + 14 * s, cx + 16 * s, cy + 32 * s], 195, 345, fill=(40, 30, 30), width=4)
    else:
        d.arc([cx - 16 * s, cy + 8 * s, cx + 16 * s, cy + 26 * s], 15, 165, fill=(40, 30, 30), width=4)
    # badge
    if kind == "np":  # heart
        d.polygon([(cx, cy - 48 * s), (cx - 14 * s, cy - 62 * s), (cx - 7 * s, cy - 72 * s), (cx, cy - 64 * s),
                   (cx + 7 * s, cy - 72 * s), (cx + 14 * s, cy - 62 * s)], fill=(220, 70, 90))
    elif kind == "gov":  # building
        d.rectangle([cx - 16 * s, cy - 72 * s, cx + 16 * s, cy - 48 * s], fill=CREAM, outline=DEEP, width=3)
        d.polygon([(cx - 20 * s, cy - 72 * s), (cx + 20 * s, cy - 72 * s), (cx, cy - 86 * s)], fill=CREAM, outline=DEEP)
    else:  # megaphone
        d.polygon([(cx - 6 * s, cy - 56 * s), (cx + 20 * s, cy - 76 * s), (cx + 20 * s, cy - 44 * s)], fill=GOLD)
        d.rectangle([cx - 16 * s, cy - 64 * s, cx - 6 * s, cy - 52 * s], fill=GOLD)

def tangle(d, cx, cy, spread, k, n=9):
    rr = random.Random(k // 4)
    cols = [ORANGE, DEEP, (180, 90, 120), (120, 140, 60), PURPLE]
    for i in range(n):
        pts = []
        x, y = cx + rr.randint(-spread, spread), cy + rr.randint(-40, 40)
        for _ in range(6):
            x += rr.randint(-80, 80); y += rr.randint(-40, 40)
            pts.append((x, y))
        d.line(pts, fill=cols[i % len(cols)], width=12, joint="curve")

def dashboard(d, cx, cy, w, h, k, grow=1.0):
    w, h = int(w * grow), int(h * grow)
    if w < 10:
        return
    d.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], 20, fill=CREAM, outline=DEEP, width=5)
    if grow > 0.55:
        for i, bh in enumerate([0.5, 0.8, 0.4, 0.95, 0.7]):
            bw = w // 9
            bx = cx - w // 2 + int(w * 0.1) + i * int(bw * 1.4)
            top = cy + h // 2 - 20 - int((h - 55) * bh * min(1, (grow - 0.55) / 0.45))
            jx, _ = jitter(k + i, 2)
            d.rounded_rectangle([bx + jx, top, bx + bw + jx, cy + h // 2 - 20], 7,
                                fill=[TEAL, ORANGE, PURPLE][i % 3])

def base_frame(k):
    img = Image.new("RGB", (W, H), CLAYBG)
    d = ImageDraw.Draw(img, "RGBA")
    clay_blob(d, W // 2, H + 250, 620, (204, 194, 176), k // 6 + 99, 0.05, 30)
    return img, d

frames = []
def scene(sec, painter):
    n = int(sec * FPS)
    for k in range(n):
        img, d = base_frame(k)
        painter(d, k, n)
        speckle(img, k % 6)
        frames.append(np.asarray(img))

# Scene 1 (6s): orgs sinking in messy data, vulnerable women around them, worried
def s1(d, k, n):
    t = k / n
    tangle(d, W // 2, 500, 420, k)
    sink = min(0.9, t * 1.2)
    org(d, 400, 430, 1.0, k, "np", sink)
    org(d, 660, 415, 1.0, k, "gov", sink * 0.8)
    org(d, 920, 435, 1.0, k, "adv", sink)
    for i, (x, col) in enumerate([(210, (150, 60, 90)), (540, (90, 110, 160)),
                                  (790, (170, 120, 50)), (1090, (100, 130, 90))]):
        woman(d, x, 560, 0.9, k + i, col, "sad")
    clay_text(d, "You can count who you served...", W // 2, 80, F44, DEEP, k)
    if t > 0.4:
        clay_text(d, "...but can you show funders they got safer, housed, stable?", W // 2, 150, F26, (120, 60, 40), k)
scene(6, s1)

# Scene 2 (6s): Belle arrives and reaches out to rescue
def s2(d, k, n):
    t = k / n
    tangle(d, 850, 520, int(300 * (1 - t * 0.5)), k, n=7)
    org(d, 900, 460, 1.0, k, "np", 0.6 * (1 - t), "sad" if t < 0.7 else "happy")
    for i, (x, col) in enumerate([(1080, (150, 60, 90)), (700, (90, 110, 160))]):
        woman(d, x, 570, 0.9, k + i, col, "sad" if t < 0.7 else "happy")
    bx = int(-180 + (330 + 180) * min(1, t * 2.5))
    belle(d, bx, 400, 1.0, k, arm="reach" if t > 0.35 else "down")
    if t > 0.35:  # rescue rope of clean data dots
        for i in range(10):
            p = i / 9
            x = bx + 110 + (900 - bx - 110) * p
            y = 385 + math.sin(p * math.pi) * -40
            d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=TEAL)
    clay_text(d, "Meet BData Solutions", W // 2, 80, F64, DEEP, k)
    if t > 0.5:
        clay_text(d, "Barakatou pulls your data — and your mission — out of the mess.", W // 2, 165, F26, TEAL, k)
scene(6, s2)

# Scene 3 (6s): transformation — dashboard rises, women lifted & smiling
def s3(d, k, n):
    t = k / n
    grow = min(1.0, t / 0.55)
    dashboard(d, 880, 330, 500, 300, k, grow)
    org(d, 700, 560, 0.8, k, "np", 0, "happy")
    org(d, 880, 575, 0.8, k, "gov", 0, "happy")
    org(d, 1060, 560, 0.8, k, "adv", 0, "happy")
    lift = int(min(1, t * 1.5) * 40)
    for i, (x, col) in enumerate([(180, (150, 60, 90)), (330, (90, 110, 160)), (480, (170, 120, 50))]):
        woman(d, x, 590 - lift - (i % 2) * 12, 0.95, k + i, col, "happy")
    belle(d, 300, 380, 1.0, k, arm="up")
    clay_text(d, "Turn program data into proof of impact", W // 2, 80, F44, DEEP, k)
    if t > 0.6:
        clay_text(d, "Google Sheets · Looker Studio · Power BI", W // 2, 150, F26, PURPLE, k)
scene(6, s3)

# Scene 4 (8s): offers & pricing cards stamp in
OFFERS = [
    ("Data Health Check", "$250-$500", "60-90 min review,\ngaps & quick wins\n1 week", TEAL),
    ("Impact Dashboard", "$3,000-$8,000", "Dashboard + KPIs +\ntraining & handover\n4 weeks", ORANGE),
    ("Reporting Support", "from $800/mo", "Board & funder reports\nkept accurate\nmonthly", PURPLE),
]
def s4(d, k, n):
    t = k / n
    clay_text(d, "Services built for nonprofit realities", W // 2, 70, F44, DEEP, k)
    cw, ch, gap = 340, 340, 40
    x0 = (W - 3 * cw - 2 * gap) // 2
    for i, (title, price, desc, col) in enumerate(OFFERS):
        start = 0.08 + i * 0.2
        if t < start:
            continue
        p = min(1, (t - start) / 0.1)
        sq = 1 + (1 - p) * 0.5
        cx = x0 + i * (cw + gap) + cw // 2
        cy = 400
        jx, jy = jitter(k * 9 + i, 2)
        w2, h2 = int(cw * (2 - sq) / 2), int(ch * sq / 2) if p < 1 else ch // 2
        d.rounded_rectangle([cx - cw // 2 + jx, cy - h2 + jy, cx + cw // 2 + jx, cy + h2 + jy], 18,
                            fill=CREAM, outline=col, width=6)
        if p >= 1:
            clay_text(d, title, cx, cy - 105, F22, col, k)
            clay_text(d, price, cx, cy - 45, F34, DEEP, k)
            for li, line in enumerate(desc.split("\n")):
                clay_text(d, line, cx, cy + 25 + li * 34, F22, (90, 80, 70), k, drop=False)
        belle(d, 90, 640, 0.55, k, arm="up")
scene(8, s4)

# Scene 5 (7s): CTA
def s5(d, k, n):
    t = k / n
    items = [("BData Solutions", F64, TEAL, 170, 0.05),
             ("Turn Your Program Data Into Proof of Impact", F26, PURPLE, 250, 0.22),
             ("Book a Free 20-Minute Discovery Call", F34, DEEP, 330, 0.38),
             ("www.barakabelle.ca  ·  hello@barakabelle.ca", F34, ORANGE, 410, 0.55),
             ("hellobdatasolutions@gmail.com  ·  Edmonton, AB", F26, (120, 90, 60), 480, 0.68)]
    for text, fnt, col, y, start in items:
        if t >= start:
            clay_text(d, text, W // 2, y, fnt, col, k)
    belle(d, W // 2, 620, 0.8, k, arm="up")
    for i, (x, col) in enumerate([(320, (150, 60, 90)), (960, (90, 110, 160))]):
        woman(d, x, 640, 0.8, k + i, col, "happy")
scene(7, s5)

out = "/tmp/claude-0/-home-user-BDataSolutions/e8b5f2ae-3431-5d77-9233-5ca80f105b1a/scratchpad/bdata-proof-of-impact.mp4"
w = imageio.get_writer(out, fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p")
for f in frames:
    w.append_data(f)
w.close()
print("wrote", out, len(frames) / FPS, "s")
