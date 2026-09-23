#!/usr/bin/env python3
"""Generate the doodle background tiles for the night theme.

The doodles are stroke-only: fill is always none, so the black page shows
through the middle of every shape and only the outline is visible.

Usage:
    python3 tools/make_doodles.py                     # defaults
    python3 tools/make_doodles.py --set nature --ink white --density 12

Writes images/doodles-a.svg and images/doodles-b.svg. Two tiles at different
sizes are layered in CSS so the repeat is hard to spot.
"""

import argparse
import os

BOX = 240

SETS = {
    "nature":    ["leaf", "cloud", "drop", "wave", "mountain", "tree", "wind", "flower"],
    "science":   ["molecule", "flask", "chart", "pin", "satellite", "grid", "beaker", "wave"],
    "celestial": ["star4", "star5", "moon", "sun", "orbit", "spark", "cloud", "wind"],
}
SETS["mixed"] = ["leaf", "cloud", "drop", "molecule", "star4", "mountain",
                 "pin", "sun", "wind", "flask", "wave", "tree"]

# Each doodle is drawn inside a 0..20 box.
D = {
    "leaf":      '<path d="M10 1c6 4 6 12 0 18C4 13 4 5 10 1z"/><path d="M10 3v15"/>',
    "cloud":     '<path d="M4 14a3.2 3.2 0 0 1 .4-6.4A4.6 4.6 0 0 1 13 6.6 3.4 3.4 0 0 1 16 14z"/>',
    "drop":      '<path d="M10 2c4 5.5 5.6 8 5.6 10.4A5.6 5.6 0 0 1 4.4 12.4C4.4 10 6 7.5 10 2z"/>',
    "wave":      '<path d="M1 12c2.5-4 5-4 7.5 0s5 4 7.5 0"/><path d="M1 7c2.5-4 5-4 7.5 0s5 4 7.5 0"/>',
    "mountain":  '<path d="M1 16l6-9 4 5.5 2.5-3L19 16z"/>',
    "tree":      '<path d="M10 18v-6"/><circle cx="10" cy="8" r="5.5"/>',
    "wind":      '<path d="M2 7h9a2.6 2.6 0 1 0-2.6-2.6"/><path d="M2 12h12a2.6 2.6 0 1 1-2.6 2.6"/>',
    "flower":    '<circle cx="10" cy="10" r="2.4"/><circle cx="10" cy="4.6" r="2.7"/>'
                 '<circle cx="10" cy="15.4" r="2.7"/><circle cx="4.6" cy="10" r="2.7"/>'
                 '<circle cx="15.4" cy="10" r="2.7"/>',
    "molecule":  '<circle cx="4" cy="15" r="2.6"/><circle cx="16" cy="14" r="2.2"/>'
                 '<circle cx="10" cy="4.5" r="2.8"/><path d="M6 13.5l3-6.5M12.2 12.6L11.6 7"/>',
    "flask":     '<path d="M8 2v6L3.5 16.5A1.4 1.4 0 0 0 4.8 18.5h10.4a1.4 1.4 0 0 0 1.3-2L12 8V2z"/>'
                 '<path d="M7 2h6"/>',
    "beaker":    '<path d="M5 3h10v13a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2z"/><path d="M5 12h10"/>',
    "chart":     '<path d="M2 18V6M2 18h16"/><path d="M5 15l4-5 3.5 3L18 7"/>',
    "grid":      '<rect x="3" y="3" width="14" height="14" rx="1"/>'
                 '<path d="M3 8h14M3 13h14M8 3v14M13 3v14"/>',
    "pin":       '<path d="M10 19s6-6.4 6-10.6a6 6 0 1 0-12 0C4 12.6 10 19 10 19z"/>'
                 '<circle cx="10" cy="8.2" r="2.3"/>',
    "satellite": '<rect x="8" y="7.5" width="5" height="5" rx=".6"/><path d="M8 10H2M13 10h5"/>'
                 '<rect x="1" y="7.6" width="2.4" height="4.8" rx=".5"/>'
                 '<rect x="17" y="7.6" width="2.4" height="4.8" rx=".5"/>',
    "star4":     '<path d="M10 1c.9 5.6 3.5 8.2 9 9-5.5.9-8.1 3.5-9 9-.9-5.5-3.5-8.1-9-9 5.5-.8 8.1-3.4 9-9z"/>',
    "star5":     '<path d="M10 1.6l2.5 5.6 6 .6-4.5 4 1.3 5.9L10 14.7 4.7 17.7 6 11.8 1.5 7.8l6-.6z"/>',
    "moon":      '<path d="M14.5 2.6a8.6 8.6 0 1 0 3.2 12.2A9 9 0 0 1 14.5 2.6z"/>',
    "sun":       '<circle cx="10" cy="10" r="4.4"/><path d="M10 1v2.6M10 16.4V19M1 10h2.6M16.4 10H19'
                 'M3.6 3.6l1.9 1.9M14.5 14.5l1.9 1.9M16.4 3.6l-1.9 1.9M5.5 14.5l-1.9 1.9"/>',
    "orbit":     '<circle cx="10" cy="10" r="3"/><ellipse cx="10" cy="10" rx="9" ry="4.2"/>',
    "spark":     '<path d="M10 3v14M3 10h14"/><path d="M5.4 5.4l9.2 9.2M14.6 5.4l-9.2 9.2"/>',
}

INKS = {
    "gold":  ["#c9a227"],
    "white": ["#ffffff"],
    "both":  ["#c9a227", "#ffffff", "#ffffff"],
    # for the light-ground whimsy theme
    "ink":   ["#232a33"],
    "warm":  ["#d9583c", "#2c8a79", "#c8901c", "#232a33", "#232a33"],
    # for the quiet theme — one ink, nearly invisible
    "faint": ["#1c1c1b"],
    # for the quiet theme on its black ground
    "pale":  ["#efeee9"],
}


def tile(glyphs, colors, size, count, opacity, seed):
    r = seed

    def rnd():
        nonlocal r
        r = (r * 1103515245 + 12345) & 0x7FFFFFFF
        return r / 0x7FFFFFFF

    parts = []
    for _ in range(count):
        g = glyphs[int(rnd() * len(glyphs))]
        x, y = rnd() * BOX, rnd() * BOX
        rot = int(rnd() * 360)
        s = (size * (0.75 + rnd() * 0.6)) / 20
        c = colors[int(rnd() * len(colors))]
        parts.append(
            '<g transform="translate(%.1f,%.1f) rotate(%d) scale(%.3f) translate(-10,-10)" '
            'stroke="%s">%s</g>' % (x, y, rot, s, c, D[g])
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
        '<g fill="none" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round" '
        'opacity="%s">%s</g></svg>' % (BOX, BOX, BOX, BOX, opacity, "".join(parts))
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--set", default="mixed", choices=sorted(SETS))
    p.add_argument("--ink", default="gold", choices=sorted(INKS))
    p.add_argument("--density", type=int, default=9)
    p.add_argument("--size", type=int, default=17)
    p.add_argument("--opacity", type=float, default=0.20)
    a = p.parse_args()

    glyphs, colors = SETS[a.set], INKS[a.ink]
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "images")
    os.makedirs(out, exist_ok=True)

    for name, sz, ct, op, seed in [
        ("doodles-a.svg", a.size, a.density, a.opacity, 8675309),
        ("doodles-b.svg", a.size * 0.72, max(3, round(a.density * 0.7)), a.opacity * 0.75, 24601),
    ]:
        path = os.path.join(out, name)
        with open(path, "w") as f:
            f.write(tile(glyphs, colors, sz, ct, round(op, 3), seed))
        print("wrote", path)

    print("settings: %s / %s / density %d / size %d / opacity %.2f"
          % (a.set, a.ink, a.density, a.size, a.opacity))


if __name__ == "__main__":
    main()
