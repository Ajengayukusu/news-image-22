#!/usr/bin/env python3
"""Draw the 22 November 2026 front page into assets/entry.png.

A one-page newspaper rendered with Pillow: a navy masthead naming the
day, a lead story on the Iranian strike on Bahrain with a burst motif,
six further stories in a two-column grid, and a footer strip of shorter
items. Every fact comes from news reported on Sunday 22 November 2026
by the live sources gathered while building this entry (Reuters via
Google News, Al Jazeera, The Washington Post, BBC Sport, and the
Paris Eye / AppiSToS wires). Output is 1024x1024 PNG, under 1 MiB.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
PAPER = (252, 252, 246)
INK = (18, 18, 18)
NAVY = (16, 30, 58)
CRIMSON = (172, 30, 30)
GOLD = (196, 156, 36)
GREY = (96, 96, 90)
RULE = (200, 200, 190)
CARD_BG = (246, 246, 238)

FONTS = Path("/usr/share/fonts/truetype/dejavu")


def load(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


SERIF_B = lambda s: load("DejaVuSerif-Bold.ttf", s)  # noqa: E731
SERIF = lambda s: load("DejaVuSerif.ttf", s)  # noqa: E731
SANS_B = lambda s: load("DejaVuSans-Bold.ttf", s)  # noqa: E731
SANS = lambda s: load("DejaVuSans.ttf", s)  # noqa: E731


def wrap(d, text, fnt, width):
    out = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            trial = (line + " " + word).strip()
            if d.textlength(trial, font=fnt) <= width or not line:
                line = trial
            else:
                out.append(line)
                line = word
        if line:
            out.append(line)
    return out


def para(d, text, fnt, width, x, y, fill=INK, gap=5):
    for line in wrap(d, text, fnt, width):
        d.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + gap
    return y


def burst(d, cx, cy, r_outer, r_inner, spikes=12):
    """A starburst: the strike motif for the lead panel."""
    pts = []
    for i in range(spikes * 2):
        r = r_outer if i % 2 == 0 else r_inner
        a = math.pi * i / spikes - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=GOLD)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(255, 255, 255))


def story_card(d, x, y, w, h, kicker, head, body):
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG)
    d.rectangle([x, y, x + w, y + 4], fill=NAVY)
    d.text((x + 14, y + 14), kicker, font=SANS_B(17), fill=CRIMSON)
    yy = para(d, head, SERIF_B(25), w - 28, x + 14, y + 42, gap=2)
    para(d, body, SERIF(19), w - 28, x + 14, yy + 4, gap=4)


def main():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead: paper name and the day it sums up.
    d.rectangle([0, 0, PAGE, 118], fill=NAVY)
    d.text((512, 22), "THE WORLD IN ONE PAGE", font=SERIF_B(56),
           fill=(255, 255, 255), anchor="ma")
    d.text((512, 90), "SUNDAY  \u00b7  22 NOVEMBER 2026",
           font=SANS_B(23), fill=GOLD, anchor="ma")
    d.rectangle([0, 118, PAGE, 124], fill=GOLD)

    # Lead story: the Iranian strike on Bahrain.
    d.text((48, 146), "BAHRAIN  \u2014  GULF ESCALATION",
           font=SANS_B(21), fill=CRIMSON)
    y = para(d, "Iran strikes Bahrain\nin Gulf escalation",
             SERIF_B(46), 660, 48, 186, gap=3)
    y += 6
    para(d,
         "Iranian missiles and drones hit an industrial facility in "
         "Bahrain, the kingdom said, as its air defences intercepted "
         "other attacks \u2014 the sharpest escalation yet in the Gulf "
         "crisis, with US assets in the island state in the line of fire.",
         SERIF(22), 660, 48, y, gap=5)
    # Burst motif panel on the right of the lead.
    d.rectangle([742, 146, 976, 398], fill=NAVY)
    burst(d, 859, 248, 78, 34)
    d.text((859, 338), "BAHRAIN", font=SANS_B(22),
           fill=(255, 255, 255), anchor="ma")
    d.text((859, 368), "22 NOVEMBER", font=SANS(17), fill=GOLD, anchor="ma")
    d.line([48, 430, 976, 430], fill=RULE, width=2)

    # Six stories, two columns by three rows.
    stories = [
        ("MEXICO  \u2014  DRUG WAR",
         "Mexico captures \u2018El Chapo Isidro\u2019",
         "Troops seized the Sinaloa drug lord after a decade on the "
         "run, the latest in a string of high-profile arrests."),
        ("BRUSSELS  \u2014  TRADE",
         "EU and Indonesia sign trade deal",
         "After ten years of talks the two sides signed deals scrapping "
         "tariffs on 98.5% of goods between them."),
        ("TURIN  \u2014  TENNIS",
         "Alcaraz to face Zverev for the title",
         "Carlos Alcaraz fought back past Ben Shelton to reach the ATP "
         "Finals decider against world No. 1 Alexander Zverev."),
        ("GAZA  \u2014  AID",
         "Four nations urge Israel to open Gaza aid",
         "Australia, Canada, Italy and Britain jointly called for "
         "immediate aid access as floods add to Gaza\u2019s suffering."),
        ("JERUSALEM  \u2014  POLITICS",
         "Eisenkot tapped to form government",
         "Israel\u2019s president asked ex-army chief Gadi Eisenkot to "
         "try to form the next government, bypassing Netanyahu."),
        ("LVIV  \u2014  UKRAINE",
         "Russian strike hits Lviv",
         "At least two people were killed and ten injured as Russian "
         "missiles hit the western Ukrainian city."),
    ]
    gx, gy, cw, ch, gap = 48, 446, 452, 168, 12
    for i, (kicker, head, body) in enumerate(stories):
        x = gx + (i % 2) * (cw + gap)
        yy = gy + (i // 2) * (ch + 14)
        story_card(d, x, yy, cw, ch, kicker, head, body)

    # Footer strip: shorter items from the same day.
    fy = gy + 3 * ch + 2 * 14 + 14
    d.line([48, fy, 976, fy], fill=RULE, width=2)
    para(d,
         "Also: France protests enter a fourth weekend  \u00b7  24 dead "
         "in Nigeria boat capsize  \u00b7  Hong Kong votes",
         SANS(17), 928, 48, fy + 12, fill=GREY, gap=3)

    out = Path(__file__).resolve().parent / "assets" / "entry.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
