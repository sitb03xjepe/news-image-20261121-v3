#!/usr/bin/env python3
"""Draw the dense v2 front page for news-image-20261121.

One-day newspaper: 38 stories from Saturday 21 November 2026 across
7 regions, with attribution. Drawn with Pillow only; run it once and it
writes entry.png (1024x1024) next to this file.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 241, 227)
INK = (22, 21, 19)
MUTED = (74, 70, 64)
RED = (143, 29, 29)
NAVY = (31, 58, 95)
PANEL = (255, 253, 246)
GREEN = (26, 110, 62)
GOLD = (176, 132, 30)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)

# ---------------------------------------------------------------- data

LEAD = [
    {
        "kicker": "EUROPE  ·  WAR IN UKRAINE",
        "title": "400 drones, 110 missiles hit Ukraine; three land in Poland",
        "sub": "Eight killed in Kyiv as bridges and rail are hit; NATO calls it a "
               "grave violation; Tusk: \u2018deliberate provocation\u2019.",
        "art": "missiles",
    },
    {
        "kicker": "MARKETS  ·  THE AI ROUT",
        "title": "Stocks plunge worldwide as the AI sell-off bites",
        "sub": "S&P 500 \u22123.7% into correction; Nasdaq \u22125.3%; Nikkei \u22125.1%; "
               "gold \u22124.6%.",
        "art": "bars",
    },
]

PANELS = [
    {
        "kicker": "THE HAGUE  ·  JUSTICE",
        "title": "Court: Myanmar guilty of Rohingya genocide",
        "sub": "The first time any court has found a state guilty of genocide.",
        "art": "scales",
    },
    {
        "kicker": "HEALTH  ·  LONDON",
        "title": "Cancer pill makes tumours vanish in 1 in 12",
        "sub": "Daraxonrasib, a daily pill, left pancreatic cancer undetectable "
               "on scans.",
        "art": "pill",
    },
    {
        "kicker": "BRUSSELS  ·  BREXIT",
        "title": "UK and EU sign three post-Brexit deals",
        "sub": "Food trade, carbon permits and youth mobility \u2014 the biggest "
               "step since Brexit.",
        "art": "flags",
    },
    {
        "kicker": "CLIMATE  ·  ANTALYA",
        "title": "COP31 deadlocked over fossil fuels",
        "sub": "Talks run past their deadline; the EU warns of a \u2018substantial "
               "step backwards\u2019.",
        "art": "flame",
    },
    {
        "kicker": "MIDDLE EAST  ·  HORMUZ",
        "title": "Tankers hit as US\u2013Iran talks stall",
        "sub": "Iran says it downed a US MQ-9 drone over the strait \u2014 its 58th.",
        "art": "tanker",
    },
    {
        "kicker": "MIDDLE EAST  ·  RIYADH",
        "title": "Houthis fire on Riyadh, third night running",
        "sub": "The coalition intercepts three missiles and strikes Yemen in reply.",
        "art": "streaks",
    },
]

# Three columns for the index: col 1, col 2, col 3 (kept in reading order).
INDEX_COLS = [
    [
        ("EUROPE", [
            "Denmark expels Russian diplomat over rapper plot",
            "Cost-of-living protests sweep 25 European countries",
            "France adopts police self-defence law; Villepin to run in 2027",
            "Estonia shuts Russia border; Latvia urges EU ban",
            "Alcaraz wins at ATP Finals; Zverev reaches the semis",
            "French police sentenced over beating of Zecler",
        ]),
        ("LATIN AMERICA", [
            "Strong quake shakes Peru\u2019s Andes, felt in Lima",
            "Bolsonaro hospitalised with intestinal obstruction",
            "Salvadoran troops lose soldiers fighting gangs in Haiti",
            "Argentina\u2019s country risk tops 1,000 points",
        ]),
    ],
    [
        ("AFRICA", [
            "Phumzile Mlambo-Ngcuka dies aged 71",
            "Uganda limits gatherings and travel over Ebola",
            "Kenya starts onshore crude drilling in Turkana",
            "Funeral boat capsizes in Nigeria; four dead",
        ]),
        ("NORTH AMERICA", [
            "FBI crime database and USDA hacked",
            "Palisades fire arsonist convicted in Los Angeles",
            "US loses measles elimination status",
            "Trump defends Putin, Xi ties; Zelensky: \u2018killer\u2019",
            "Anthropic mathematician claims AI Riemann proof",
            "Trump weighs new strikes on Iran as Israel presses",
            "Judge approves Bayer\u2019s $7.25bn Roundup settlement",
        ]),
    ],
    [
        ("MIDDLE EAST", [
            "Israeli fire kills Palestinians in Gaza",
            "Basra power plant fire kills four, injures 30",
            "Saudi Arabia and Japan agree oil stockpile deal",
            "Lewis Pugh swims Hormuz for war\u2019s wildlife toll",
        ]),
        ("ASIA", [
            "Japan sidelined as China ties hit record low",
            "Cyclone Akvan crosses India\u2019s Odisha coast",
            "Indonesia\u2019s forest fires burn 7.1m acres in 2026",
        ]),
        ("OCEANIA & SPACE", [
            "BepiColombo reaches Mercury orbit after eight years",
            "Voyager 1 now 24 light-hours from Earth",
        ]),
    ],
]

TOTAL_STORIES = 8 + sum(len(items) for col in INDEX_COLS
                        for _, items in col)
assert TOTAL_STORIES == 38, TOTAL_STORIES

# ---------------------------------------------------------------- helpers


def wrap(d, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, text, fnt, x, y, max_w, fill, leading):
    lines = wrap(d, text, fnt, max_w)
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(d, x0, x1, y, fill=INK, width=2):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- art


def art_missiles(d, x, y, w, h):
    """Three missile arcs converging on a burst."""
    cx, cy = x + w - 26, y + h - 18
    for i, (sx, top) in enumerate([(x + 8, y + 6), (x + 46, y + 16),
                                   (x + 84, y + 2)]):
        d.arc([sx, top, cx + 30, cy + 26], start=200, end=330,
              fill=RED, width=2)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
    for ang in range(0, 360, 45):
        import math
        r1, r2 = 5, 13
        a = math.radians(ang)
        d.line([(cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
                (cx + r2 * math.cos(a), cy + r2 * math.sin(a))],
               fill=GOLD, width=2)
    d.text((x + 4, y + h - 14), "KYIV  ·  POLAND", font=SANS_B(10),
           fill=MUTED)


def art_bars(d, x, y, w, h):
    """Market bars: four down (red), one up (green)."""
    vals = [("S&P", -3.7), ("Nasdaq", -5.3), ("Nikkei", -5.1),
            ("Gold", -4.6), ("Sensex", 2.3)]
    base = y + h - 24
    slot = w / len(vals)
    for i, (name, v) in enumerate(vals):
        cx = x + slot * i + slot / 2
        bh = abs(v) / 5.5 * (h - 34)
        if v < 0:
            d.rectangle([cx - 13, base - bh, cx + 13, base], fill=RED)
        else:
            d.rectangle([cx - 13, base - bh, cx + 13, base], fill=GREEN)
        d.text((cx - 24, base + 4), f"{name} {v:+.1f}%", font=SANS_B(10),
               fill=INK, anchor="ma")
    d.line([(x, base), (x + w, base)], fill=INK, width=1)


def art_scales(d, x, y, w, h):
    """Scales of justice, centred."""
    cx, cy = x + w // 2, y + h // 2 + 4
    d.line([(cx, cy - 22), (cx, cy + 16)], fill=INK, width=2)
    d.line([(cx - 24, cy - 14), (cx + 24, cy - 14)], fill=INK, width=2)
    for s in (-1, 1):
        px = cx + s * 24
        d.line([(px, cy - 14), (px - 9, cy + 2)], fill=INK, width=1)
        d.line([(px, cy - 14), (px + 9, cy + 2)], fill=INK, width=1)
        d.polygon([(px - 11, cy + 2), (px + 11, cy + 2), (px, cy + 12)],
                  fill=NAVY)
    d.ellipse([cx - 4, cy - 28, cx + 4, cy - 20], fill=GOLD)


def art_pill(d, x, y, w, h):
    """A two-half capsule, tilted by drawing on a small tile."""
    tile = Image.new("RGB", (76, 30), PANEL)
    td = ImageDraw.Draw(tile)
    td.rounded_rectangle([2, 6, 74, 24], radius=9, fill=RED)
    td.rounded_rectangle([38, 6, 74, 24], radius=9, fill=(255, 255, 255),
                         outline=INK, width=1)
    td.rounded_rectangle([2, 6, 74, 24], radius=9, outline=INK, width=1)
    tile = tile.rotate(18, expand=False, fillcolor=PANEL)
    d._image.paste(tile, (x + w // 2 - 38, y + h // 2 - 15))


def art_flags(d, x, y, w, h):
    """EU circle of stars beside a small Union Jack."""
    import math
    cx, cy = x + 34, y + h // 2
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=NAVY)
    for i in range(12):
        a = math.radians(i * 30 - 90)
        sx, sy = cx + 16 * math.cos(a), cy + 16 * math.sin(a)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=GOLD)
    fx, fy = x + w - 78, cy - 20
    d.rectangle([fx, fy, fx + 64, fy + 40], fill=(255, 255, 255),
                outline=INK, width=1)
    d.line([(fx, fy), (fx + 64, fy + 40)], fill=RED, width=3)
    d.line([(fx + 64, fy), (fx, fy + 40)], fill=RED, width=3)
    d.line([(fx + 32, fy), (fx + 32, fy + 40)], fill=RED, width=5)
    d.line([(fx, fy + 20), (fx + 64, fy + 20)], fill=RED, width=5)


def art_flame(d, x, y, w, h):
    """A flame over a leaf line."""
    cx, cy = x + w // 2, y + h // 2 + 6
    d.polygon([(cx, cy - 24), (cx + 12, cy - 2), (cx + 6, cy + 12),
               (cx - 6, cy + 12), (cx - 12, cy - 2)],
              fill=(214, 90, 20))
    d.polygon([(cx, cy - 12), (cx + 6, cy + 2), (cx, cy + 10),
               (cx - 6, cy + 2)], fill=GOLD)
    d.line([(x + 6, cy + 16), (x + w - 6, cy + 16)], fill=GREEN, width=3)


def art_tanker(d, x, y, w, h):
    """A tanker on waves."""
    cx, cy = x + w // 2, y + h // 2 + 2
    d.polygon([(cx - 34, cy), (cx + 34, cy), (cx + 26, cy + 14),
               (cx - 26, cy + 14)], fill=NAVY)
    d.rectangle([cx - 22, cy - 14, cx + 6, cy], fill=RED)
    d.rectangle([cx + 10, cy - 10, cx + 24, cy], fill=GOLD)
    for i, wy in enumerate((cy + 20, cy + 26)):
        d.arc([x + 4 + i * 8, wy - 5, x + w - 4 - i * 8, wy + 5],
              start=0, end=180, fill=NAVY, width=2)


def art_streaks(d, x, y, w, h):
    """Three incoming streaks met by an intercept burst."""
    import math
    for i, sy in enumerate((y + 10, y + 24, y + 38)):
        d.line([(x + 6, sy), (x + w - 30, sy + 12)], fill=RED, width=2)
        d.ellipse([x + w - 34, sy + 8, x + w - 26, sy + 16], fill=RED)
    cx, cy = x + w - 20, y + h // 2 + 8
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([(cx + 4 * math.cos(a), cy + 4 * math.sin(a)),
                (cx + 12 * math.cos(a), cy + 12 * math.sin(a))],
               fill=GOLD, width=2)


ART = {"missiles": art_missiles, "bars": art_bars, "scales": art_scales,
       "pill": art_pill, "flags": art_flags, "flame": art_flame,
       "tanker": art_tanker, "streaks": art_streaks}

# ---------------------------------------------------------------- page


def panel(d, x, y, w, h, item, headline_size, sub_size=12):
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=INK, width=1)
    ix, iy = x + 12, y + 10
    d.text((ix, iy), item["kicker"], font=SANS_B(11), fill=RED)
    iy += 20
    iy = draw_wrapped(d, item["title"], SERIF_B(headline_size), ix, iy,
                      w - 24, INK, headline_size + 4)
    iy += 4
    sub_end = draw_wrapped(d, item["sub"], SANS(sub_size), ix, iy, w - 24,
                           MUTED, sub_size + 4)
    art_h = y + h - sub_end - 8
    if art_h >= 34:
        ART[item["art"]](d, x + 10, sub_end + 2, w - 20, art_h)


def index_column(d, x, y, w, groups):
    """One column of region groups; returns the bottom y."""
    for region, items in groups:
        d.text((x, y), region, font=SANS_B(12), fill=NAVY)
        y += 17
        rule(d, x, x + w, y, fill=(180, 172, 156), width=1)
        y += 5
        for item in items:
            d.text((x + 9, y), "\u2022", font=SANS_B(11), fill=RED)
            y = draw_wrapped(d, item, SANS(11), x + 20, y, w - 20, INK, 13)
            y += 1
        y += 7
    return y


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 28  # side margin

    # Masthead
    d.text((W // 2, 18), "THE WORLD", font=SERIF_B(58), fill=INK,
           anchor="ma")
    d.text((W // 2, 84), "SATURDAY, 21 NOVEMBER 2026", font=SANS_B(19),
           fill=INK, anchor="ma")
    rule(d, mx, W - mx, 112, width=2)

    # Count banner
    d.rectangle([mx, 120, W - mx, 148], fill=RED)
    d.text((W // 2, 126), "38 STORIES  \u00b7  7 REGIONS  \u00b7  ONE DAY",
           font=SANS_B(17), fill=(255, 255, 255), anchor="ma")

    # Lead row: two wide panels
    lead_y, lead_h = 156, 176
    gap = 12
    lw = (W - 2 * mx - gap) // 2
    panel(d, mx, lead_y, lw, lead_h, LEAD[0], 22)
    panel(d, mx + lw + gap, lead_y, lw, lead_h, LEAD[1], 22)

    # Rows of three panels
    row_y, row_h = 342, 146
    pw = (W - 2 * mx - 2 * gap) // 3
    for i, item in enumerate(PANELS[:3]):
        panel(d, mx + i * (pw + gap), row_y, pw, row_h, item, 18)
    row_y2 = 498
    for i, item in enumerate(PANELS[3:]):
        panel(d, mx + i * (pw + gap), row_y2, pw, row_h, item, 18)

    # Index of the rest, in three columns
    idx_y = 662
    d.text((mx, idx_y), "AROUND THE WORLD \u2014 30 MORE STORIES",
           font=SANS_B(17), fill=INK)
    idx_y += 26
    rule(d, mx, W - mx, idx_y, width=2)
    idx_y += 10
    col_w = (W - 2 * mx - 2 * gap) // 3
    ends = [index_column(d, mx + i * (col_w + gap), idx_y, col_w,
                         INDEX_COLS[i]) for i in range(3)]
    idx_end = max(ends)
    assert idx_end <= 984, f"index overflows: ends at {idx_end}"

    # Footer: attribution
    rule(d, mx, W - mx, 988, width=1)
    d.text((W // 2, 994),
           "Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 Le Monde \u00b7 NYT \u00b7 ISW \u00b7 "
           "OneTurn daily brief \u2014 all stories from Saturday 21 November 2026",
           font=SANS(11), fill=MUTED, anchor="ma")
    return img


if __name__ == "__main__":
    build().save("entry.png", optimize=True)
    print("wrote entry.png")
