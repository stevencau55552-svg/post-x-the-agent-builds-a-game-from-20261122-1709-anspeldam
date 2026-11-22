#!/usr/bin/env python3
"""Build the ORBIT DODGE video frames (1080x1920, 30fps, raw RGB to stdout).

Renders, in this session, every scene of the bounty video:
  S1 hook (0-4s)      — "I gave my AI agent ONE prompt. It built me a GAME."
  S2 the prompt (4-15s) — the single prompt typed out in a terminal card
  S3 agent working (15-23s) — build log lines appearing, BUILD COMPLETE
  S4 gameplay (23-45s) — ORBIT DODGE running: same ship, asteroids, stars,
                         score and lives rules as game.html (mirrored sim)
  S5 CTA (45-51s)     — "The game is REAL. Come build on make.fun"
The referral end card is appended afterwards by ffmpeg (see render notes).

Usage: python3 video/build_frames.py | ffmpeg -f rawvideo -pix_fmt rgb24 \
  -s 1080x1920 -r 30 -i - -c:v libx264 -pix_fmt yuv420p -crf 20 -an part1.mp4
"""
import math
import random
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30

INK = (7, 4, 13)
BG2 = (16, 8, 28)
MAGENTA = (196, 28, 131)
CYAN = (34, 211, 238)
GOLD = (255, 209, 102)
WHITE = (255, 255, 255)
GRAY = (154, 147, 168)
GREEN = (124, 252, 154)
CARD = (21, 11, 36)
CARD_BORDER = (58, 35, 88)
ORANGE = (255, 159, 28)

DJVU = "/usr/share/fonts/truetype/dejavu/"
F_BIG = ImageFont.truetype(DJVU + "DejaVuSans-Bold.ttf", 120)
F_H1 = ImageFont.truetype(DJVU + "DejaVuSans-Bold.ttf", 84)
F_H2 = ImageFont.truetype(DJVU + "DejaVuSans-Bold.ttf", 66)
F_H3 = ImageFont.truetype(DJVU + "DejaVuSans-Bold.ttf", 54)
F_MED = ImageFont.truetype(DJVU + "DejaVuSans.ttf", 38)
F_SMALL = ImageFont.truetype(DJVU + "DejaVuSans.ttf", 32)
F_MONO = ImageFont.truetype(DJVU + "DejaVuSansMono.ttf", 33)
F_MONO_B = ImageFont.truetype(DJVU + "DejaVuSansMono-Bold.ttf", 30)
F_MONO_S = ImageFont.truetype(DJVU + "DejaVuSansMono.ttf", 26)
F_SCORE = ImageFont.truetype(DJVU + "DejaVuSansMono-Bold.ttf", 64)


def gradient_bg():
    """Vertical gradient INK -> BG2 -> INK, precomputed once."""
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    top = (13, 6, 22)
    mid = (7, 4, 13)
    for y in range(H):
        t = y / H
        if t < 0.5:
            k = t / 0.5
            c = tuple(int(top[i] + (mid[i] - top[i]) * k) for i in range(3))
        else:
            k = (t - 0.5) / 0.5
            c = tuple(int(mid[i] + (top[i] - mid[i]) * k) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    return img


BASE_BG = gradient_bg()
_rng = random.Random(7)
BG_STARS = [( _rng.randint(0, W), _rng.randint(0, H), _rng.uniform(0.6, 2.2),
              _rng.uniform(0, 6.28)) for _ in range(80)]


def bg_with_stars(t):
    img = BASE_BG.copy()
    d = ImageDraw.Draw(img)
    for (x, y, r, ph) in BG_STARS:
        a = 0.35 + 0.65 * abs(math.sin(t * 1.5 + ph))
        v = int(255 * a)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(v, v, v))
    return img


def center(d, y, text, font, fill):
    d.text(((W - font.getlength(text)) / 2, y), text, font=font, fill=fill)


def fade_paste(base, layer, alpha):
    """Composite an RGBA layer onto base with extra alpha 0..1."""
    if alpha <= 0:
        return base
    if alpha >= 1:
        return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")
    r, g, b, a = layer.split()
    a = a.point(lambda v: int(v * alpha))
    layer = Image.merge("RGBA", (r, g, b, a))
    return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")


def text_layer(draw_fn):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d)
    return layer


def wrap(text, font, max_w):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- S1: hook
def scene_hook():
    cards = []

    def card1(d):
        center(d, 800, "I gave my AI agent", F_H2, WHITE)
        center(d, 890, "ONE prompt.", F_BIG, MAGENTA)

    def card2(d):
        center(d, 800, "It built me a", F_H2, WHITE)
        center(d, 880, "GAME.", ImageFont.truetype(DJVU + "DejaVuSans-Bold.ttf", 150), CYAN)

    def card3(d):
        center(d, 830, "Watch it happen.", F_H2, WHITE)
        center(d, 950, "no edits. no second try.", F_MED, GRAY)

    for fn in (card1, card2, card3):
        layer = text_layer(fn)
        cards.append(layer)
    for f in range(120):
        idx = 0 if f < 42 else (1 if f < 84 else 2)
        local = f - (0 if idx == 0 else (42 if idx == 1 else 84))
        alpha = min(1.0, local / 8.0)
        img = bg_with_stars(f / FPS)
        img = fade_paste(img, cards[idx], alpha)
        yield img


# ---------------------------------------------------------------- S2: prompt
PROMPT_TEXT = (
    "Build a tiny browser game in one HTML file: ORBIT DODGE, a neon space "
    "dodger. I pilot a small ship with arrow keys, mouse or touch. Asteroids "
    "fall from the top \u2014 dodge them. Glowing stars fall too \u2014 collect them "
    "for points. 3 lives, faster as I score. Particles and screen shake on a "
    "hit, game-over screen with restart. Canvas 2D, dark starfield, magenta "
    "and cyan neon, WebAudio bleeps. No libraries, no network, everything inline."
)
PROMPT_LINES = wrap(PROMPT_TEXT, F_MONO, 860)
PROMPT_FULL = "\n".join(PROMPT_LINES)
CARD_BOX = (70, 380, 1010, 1560)


def scene_prompt():
    # static terminal chrome (header + tag pill drawn separately at the end)
    def chrome(d):
        d.rounded_rectangle(CARD_BOX, radius=28, fill=CARD, outline=CARD_BORDER, width=3)
        d.ellipse([110, 420, 134, 444], fill=(255, 95, 86))
        d.ellipse([150, 420, 174, 444], fill=(255, 189, 46))
        d.ellipse([190, 420, 214, 444], fill=(39, 201, 63))
        d.text((240, 416), "PROMPT.md \u2014 the one prompt", font=F_MONO_S, fill=GRAY)
        d.text((110, 500), "agent@makefun:~$ cat PROMPT.md", font=F_MONO, fill=CYAN)

    chrome_layer = text_layer(chrome)
    n_chars = len(PROMPT_FULL)
    for f in range(330):
        img = bg_with_stars(f / FPS)
        img = fade_paste(img, chrome_layer, 1.0)
        d = ImageDraw.Draw(img)
        n = min(n_chars, 2 * f)
        revealed = PROMPT_FULL[:n]
        d.multiline_text((110, 570), revealed, font=F_MONO, fill=WHITE, spacing=17)
        # blinking block cursor after the last revealed char
        if n < n_chars or (f % 30) < 20:
            lines = revealed.split("\n")
            last = lines[-1] if lines else ""
            cx = 110 + F_MONO.getlength(last)
            cy = 570 + (len(lines) - 1) * 50
            d.rectangle([cx + 4, cy, cx + 22, cy + 40], fill=MAGENTA)
        # tag pill once typing is done
        if n >= n_chars:
            tag = "1 prompt \u00b7 0 edits \u00b7 0 follow-ups"
            tw = F_MONO_B.getlength(tag)
            x0 = (W - tw) / 2 - 28
            d.rounded_rectangle([x0, 1400, x0 + tw + 56, 1472], radius=36,
                                outline=MAGENTA, width=3)
            d.text(((W - tw) / 2, 1418), tag, font=F_MONO_B, fill=WHITE)
        yield img


# ---------------------------------------------------------------- S3: agent working
LOG_LINES = [
    ("$ agent build orbit-dodge", CYAN, F_MONO_B),
    ("\u2713 prompt read \u2014 1 prompt, 0 edits", GREEN, F_MONO_B),
    ("\u2713 game.html \u2014 canvas 960\u00d7540, starfield", GREEN, F_MONO_B),
    ("\u2713 ship + controls \u2014 keys, mouse, touch", GREEN, F_MONO_B),
    ("\u2713 asteroids falling, stars +10", GREEN, F_MONO_B),
    ("\u2713 3 lives \u00b7 speed ramp \u00b7 particles", GREEN, F_MONO_B),
    ("\u2713 WebAudio bleeps wired", GREEN, F_MONO_B),
    ("\u2713 node --check \u2014 syntax OK", GREEN, F_MONO_B),
    ("\u2713 main.ts \u2014 POST.json copies clean", GREEN, F_MONO_B),
    ("BUILD COMPLETE \u2014 359 lines, 0 libraries", MAGENTA, F_MONO_B),
]


def scene_working():
    def chrome(d):
        d.rounded_rectangle(CARD_BOX, radius=28, fill=CARD, outline=CARD_BORDER, width=3)
        d.ellipse([110, 420, 134, 444], fill=(255, 95, 86))
        d.ellipse([150, 420, 174, 444], fill=(255, 189, 46))
        d.ellipse([190, 420, 214, 444], fill=(39, 201, 63))
        d.text((240, 416), "agent@makefun:~$ build orbit-dodge", font=F_MONO_S, fill=GRAY)

    chrome_layer = text_layer(chrome)
    for f in range(240):
        img = bg_with_stars(f / FPS)
        img = fade_paste(img, chrome_layer, 1.0)
        d = ImageDraw.Draw(img)
        for i, (text, color, font) in enumerate(LOG_LINES):
            if f >= 12 * (i + 1):
                d.text((110, 540 + i * 62), text, font=font, fill=color)
        if f >= 132:
            pulse = 0.85 + 0.15 * math.sin(f / 6.0)
            label = "\u25b6 PLAYING NOW"
            tw = F_H3.getlength(label)
            x0 = (W - tw) / 2 - 40
            d.rounded_rectangle([x0, 1290, x0 + tw + 80, 1390], radius=48, fill=CYAN)
            d.text(((W - tw) / 2, 1312), label, font=F_H3,
                   fill=(int(7 * pulse), int(4 * pulse), int(13 * pulse)))
        yield img


# ---------------------------------------------------------------- S4: gameplay
GW, GH = 960, 540          # game coords, as in game.html
SCALE = 1080 / GW          # 1.125
WIN_Y0 = 320               # game window top on the 1080x1920 frame
WIN_H = int(GH * SCALE)    # 607


def sim_gameplay():
    """Mirror of game.html logic; yields per-frame draw state."""
    rng = random.Random(42)
    ship_x = GW / 2
    score = 0
    lives = 3
    asteroids, stars, parts, popups = [], [], [], []
    ast_t, star_t = 0.4, 0.5
    shake_t, invuln_t = 0.0, 0.0
    elapsed = 0.0
    bg = [[rng.random() * GW, rng.random() * GH, rng.uniform(0.5, 2.0),
           rng.uniform(12, 52), rng.uniform(0, 6.28)] for _ in range(90)]

    def spawn_asteroid(x=None, y=None, vy=None):
        r = rng.uniform(14, 30)
        asteroids.append({"x": x if x is not None else rng.uniform(r, GW - r),
                          "y": y if y is not None else -r - 10, "r": r,
                          "vy": vy if vy is not None else (140 + score * 0.35) * rng.uniform(0.8, 1.3),
                          "rot": rng.uniform(0, 6.28), "vr": rng.uniform(-1.5, 1.5)})

    def spawn_star():
        stars.append({"x": rng.uniform(16, GW - 16), "y": -16, "r": 11,
                      "vy": 120, "phase": rng.uniform(0, 6.28)})

    def burst(x, y, color, n, speed):
        for _ in range(n):
            a = rng.uniform(0, 6.283)
            s = rng.uniform(speed * 0.3, speed)
            parts.append({"x": x, "y": y, "vx": math.cos(a) * s, "vy": math.sin(a) * s,
                          "life": rng.uniform(0.3, 0.8), "max": 0.8, "color": color,
                          "r": rng.uniform(2, 5)})

    for frame in range(660):
        dt = 1.0 / FPS
        elapsed += dt
        for s in bg:
            s[1] += s[3] * dt
            if s[1] > GH + 2:
                s[1] = -2
                s[0] = rng.random() * GW

        # --- autopilot: 3-way lookahead, dodge first, collect second
        def danger_at(x):
            worst = 1e9
            for a in asteroids:
                if 100 < a["y"] < 500:
                    worst = min(worst, abs(a["x"] - x) - a["r"])
            return worst

        if frame >= 378 and frame <= 402:  # scripted hit window: hold still
            pass
        elif danger_at(ship_x) < 46:
            step = 420 * dt
            cands = [max(30, min(GW - 30, c))
                     for c in (ship_x - step, ship_x, ship_x + step)]
            # most clearance wins; ties break toward the centre
            ship_x = max(cands, key=lambda c: (danger_at(c), -abs(c - GW / 2)))
        else:
            near = [s for s in stars if s["y"] < 460 and 120 < s["x"] < GW - 120]
            if near:
                tgt = min(near, key=lambda s: abs(s["x"] - ship_x))
                d = tgt["x"] - ship_x
                ship_x += max(-300 * dt, min(300 * dt, d))
            else:
                ship_x += (GW / 2 - ship_x) * 0.4 * dt
        ship_x = max(24, min(GW - 24, ship_x))
        if invuln_t > 0:
            invuln_t -= dt
        if shake_t > 0:
            shake_t -= dt

        ast_t -= dt
        if ast_t <= 0:
            spawn_asteroid()
            ast_t = max(0.28, 0.55 - score * 0.0004)
        star_t -= dt
        if star_t <= 0:
            spawn_star()
            star_t = 0.9

        # scripted hit at ~13s: an asteroid lands exactly on the ship
        if frame == 390:
            spawn_asteroid(x=ship_x, y=470, vy=60)

        for i in range(len(asteroids) - 1, -1, -1):
            a = asteroids[i]
            a["y"] += a["vy"] * dt
            a["rot"] += a["vr"] * dt
            if a["y"] - a["r"] > GH:
                asteroids.pop(i)
                continue
            rr = a["r"] + 18 - 6
            if invuln_t <= 0 and (a["x"] - ship_x) ** 2 + (a["y"] - 480) ** 2 < rr * rr:
                asteroids.pop(i)
                if lives > 0:
                    lives -= 1
                shake_t = 0.45
                invuln_t = 1.2
                burst(ship_x, 480, MAGENTA, 26, 260)
        for i in range(len(stars) - 1, -1, -1):
            s = stars[i]
            s["y"] += s["vy"] * dt
            s["phase"] += dt * 4
            if s["y"] - s["r"] > GH:
                stars.pop(i)
                continue
            rr = s["r"] + 18
            if (s["x"] - ship_x) ** 2 + (s["y"] - 480) ** 2 < rr * rr:
                stars.pop(i)
                score += 10
                popups.append({"x": s["x"], "y": s["y"], "text": "+10", "life": 0.8})
                burst(s["x"], s["y"], GOLD, 10, 140)
        for i in range(len(parts) - 1, -1, -1):
            p = parts[i]
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vx"] *= 0.98
            p["vy"] *= 0.98
            p["life"] -= dt
            if p["life"] <= 0:
                parts.pop(i)
        for i in range(len(popups) - 1, -1, -1):
            p = popups[i]
            p["y"] -= 40 * dt
            p["life"] -= dt
            if p["life"] <= 0:
                popups.pop(i)

        yield {"ship_x": ship_x, "score": score, "lives": lives, "elapsed": elapsed,
               "asteroids": [dict(a) for a in asteroids], "stars": [dict(s) for s in stars],
               "parts": [dict(p) for p in parts], "popups": [dict(p) for p in popups],
               "bg": [(x, y, r, ph) for (x, y, r, sp, ph) in bg],
               "shake": shake_t, "invuln": invuln_t, "frame": frame}


def star4(d, x, y, r, color):
    k = 0.28
    pts = [(x, y - r), (x + r * k, y - r * k), (x + r, y), (x + r * k, y + r * k),
           (x, y + r), (x - r * k, y + r * k), (x - r, y), (x - r * k, y - r * k)]
    d.polygon(pts, fill=color)


def heart_poly(cx, cy, s):
    """Filled-heart polygon (parametric curve); DejaVu's U+2665 renders
    hollow here, so hearts are drawn, not typed."""
    pts = []
    for i in range(41):
        t = 2 * math.pi * i / 40
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * s / 16.0, cy - y * s / 16.0))
    return pts


def draw_hearts(d, centers, s, lives):
    for i, (cx, cy) in enumerate(centers):
        if i < lives:
            d.polygon(heart_poly(cx, cy, s), fill=MAGENTA)
        else:
            d.polygon(heart_poly(cx, cy, s), outline=MAGENTA, width=2)


def scene_gameplay():
    for st in sim_gameplay():
        f = st["frame"]
        img = bg_with_stars(f / FPS)
        d = ImageDraw.Draw(img)
        # titles
        center(d, 70, "ORBIT DODGE", F_H3, WHITE)
        center(d, 140, "the finished game \u2014 running right now", F_SMALL, GRAY)
        # shake offsets (game-window space)
        ox = oy = 0
        if st["shake"] > 0:
            ox = random.uniform(-7, 7) * st["shake"] * 2 * SCALE
            oy = random.uniform(-7, 7) * st["shake"] * 2 * SCALE
        # game window
        d.rectangle([0, WIN_Y0, W, WIN_Y0 + WIN_H], fill=INK)
        d.rectangle([2, WIN_Y0 + 2, W - 2, WIN_Y0 + WIN_H - 2], outline=MAGENTA, width=3)
        for (x, y, r, ph) in st["bg"]:
            a = 0.35 + 0.65 * abs(math.sin(st["elapsed"] * 2 + ph))
            v = int(255 * a)
            sx, sy = x * SCALE + ox, WIN_Y0 + y * SCALE + oy
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(v, v, v))
        for s in st["stars"]:
            sx, sy = s["x"] * SCALE + ox, WIN_Y0 + s["y"] * SCALE + oy
            star4(d, sx, sy, s["r"] * SCALE * (1 + 0.15 * math.sin(s["phase"])), GOLD)
        for a in st["asteroids"]:
            ax, ay = a["x"] * SCALE + ox, WIN_Y0 + a["y"] * SCALE + oy
            ar = a["r"] * SCALE
            d.ellipse([ax - ar, ay - ar, ax + ar, ay + ar], fill=(91, 84, 112),
                      outline=(141, 134, 168), width=2)
            d.ellipse([ax - ar * 0.55, ay - ar * 0.45, ax - ar * 0.05, ay + ar * 0.05],
                      fill=(69, 62, 88))
        for p in st["parts"]:
            px, py = p["x"] * SCALE + ox, WIN_Y0 + p["y"] * SCALE + oy
            pr = p["r"] * SCALE
            d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=p["color"])
        # ship
        sx, sy = st["ship_x"] * SCALE + ox, WIN_Y0 + 480 * SCALE + oy
        if not (st["invuln"] > 0 and int(st["elapsed"] * 12) % 2 == 0):
            fl = 30 + random.uniform(0, 8)
            d.polygon([(sx - 8, sy + 18), (sx, sy + fl), (sx + 8, sy + 18)], fill=ORANGE)
            d.polygon([(sx, sy - 22), (sx + 18, sy + 16), (sx, sy + 9), (sx - 18, sy + 16)],
                      fill=CYAN, outline=WHITE)
            d.ellipse([sx - 6, sy - 10, sx + 6, sy + 2], fill=MAGENTA)
        for p in st["popups"]:
            px, py = p["x"] * SCALE + ox, WIN_Y0 + p["y"] * SCALE + oy
            d.text((px - 20, py - 12), p["text"], font=F_MONO_B, fill=GOLD)
        # in-window HUD (mirrors game.html)
        d.text((18 + ox, WIN_Y0 + 14 + oy), "SCORE " + str(st["score"]),
               font=F_MONO_B, fill=WHITE)
        hud_hearts = [(W - 32 - 32 * i, WIN_Y0 + 28) for i in (2, 1, 0)]
        draw_hearts(d, [(x + ox, y + oy) for (x, y) in hud_hearts], 11, st["lives"])
        # caption phases
        if f < 120:
            cap = "dodging asteroids\u2026"
        elif f < 270:
            cap = "collecting stars \u00b7 +10 each"
        elif f < 390:
            cap = "speed rising as the score grows"
        elif f < 450:
            cap = "HIT! \u22121 life \u2014 shake + particles"
        else:
            cap = "faster now. still flying."
        center(d, 1000, cap, F_MED, WHITE)
        center(d, 1120, "SCORE " + str(st["score"]), F_SCORE, WHITE)
        big_hearts = [(W / 2 - 72, 1245), (W / 2, 1245), (W / 2 + 72, 1245)]
        draw_hearts(d, big_hearts, 26, st["lives"])
        # chips: ONE PROMPT -> game.html -> PLAYING
        chip_y = 1420
        parts = [("ONE PROMPT", MAGENTA, WHITE), ("  \u2192  ", None, GRAY),
                 ("game.html", None, WHITE), ("  \u2192  ", None, GRAY),
                 ("PLAYING", CYAN, INK)]
        total = sum(F_MONO_B.getlength(t) + 56 if c else F_MONO_B.getlength(t)
                    for (t, c, _) in parts)
        x = (W - total) / 2
        for (t, bg, fg) in parts:
            tw = F_MONO_B.getlength(t)
            if bg:
                d.rounded_rectangle([x, chip_y, x + tw + 56, chip_y + 72], radius=36, fill=bg)
                d.text((x + 28, chip_y + 18), t, font=F_MONO_B, fill=fg)
                x += tw + 56
            else:
                d.text((x, chip_y + 18), t, font=F_MONO_B, fill=fg)
                x += tw
        center(d, 1780, "open game.html in any browser \u2014 no install, no network",
               F_SMALL, GRAY)
        yield img


# ---------------------------------------------------------------- S5: CTA
def scene_cta():
    def l1(d):
        center(d, 700, "The game is REAL.", F_H1, WHITE)

    def l2(d):
        center(d, 820, "Play it in your browser.", F_H2, CYAN)

    def l3(d):
        label = "Come build on make.fun"
        tw = F_H2.getlength(label)
        x0 = (W - tw) / 2 - 40
        d.rounded_rectangle([x0, 990, x0 + tw + 80, 1096], radius=48, fill=MAGENTA)
        d.text(((W - tw) / 2, 1012), label, font=F_H2, fill=WHITE)

    def l4(d):
        center(d, 1180, "one prompt is all it takes.", F_MED, GRAY)

    layers = [text_layer(fn) for fn in (l1, l2, l3, l4)]
    starts = [0, 18, 36, 54]
    for f in range(180):
        img = bg_with_stars(f / FPS)
        for layer, s in zip(layers, starts):
            img = fade_paste(img, layer, min(1.0, max(0.0, (f - s) / 15.0)))
        yield img


def main():
    out = sys.stdout.buffer
    total = 0
    for scene in (scene_hook(), scene_prompt(), scene_working(), scene_gameplay(), scene_cta()):
        for img in scene:
            out.write(img.tobytes())
            total += 1
            if total % 300 == 0:
                print(f"frame {total}/1530", file=sys.stderr)
    print(f"done: {total} frames", file=sys.stderr)


if __name__ == "__main__":
    main()
