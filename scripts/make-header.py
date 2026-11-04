"""Write the animated SVG header for David's GitHub profile: his name in a small solar system."""
# Run: python scripts/make-header.py  (writes assets/header.svg)
import random
import sys

random.seed(7)
W, H = 960, 300
PX, PY, PR = 742, 152, 78  # the planet

stars = []
for _ in range(70):
    x, y = random.uniform(8, W - 8), random.uniform(8, H - 8)
    if (x - PX) ** 2 + (y - PY) ** 2 < (PR + 6) ** 2:
        continue
    r = random.choice([0.6, 0.8, 1.0, 1.0, 1.3, 1.7])
    dur = random.uniform(2.2, 5.5)
    begin = random.uniform(0, 4)
    lo = random.uniform(0.15, 0.4)
    col = random.choice(["#ffffff", "#ffffff", "#ffe2c4", "#d9d2ff"])
    stars.append(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}">'
        f'<animate attributeName="opacity" values="{lo:.2f};1;{lo:.2f}" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/></circle>'
    )

# a few bright stars with spikes
sparkles = []
for x, y, s, d in [(96, 52, 7, 3.4), (452, 40, 6, 4.1), (590, 262, 8, 3.0), (905, 58, 6, 4.6), (300, 250, 5, 3.8)]:
    sparkles.append(
        f'<g transform="translate({x} {y})" opacity="0.9">'
        f'<path d="M0 -{s} L{s*0.18:.2f} -{s*0.18:.2f} L{s} 0 L{s*0.18:.2f} {s*0.18:.2f} L0 {s} L-{s*0.18:.2f} {s*0.18:.2f} L-{s} 0 L-{s*0.18:.2f} -{s*0.18:.2f} Z" fill="#fff6ec"/>'
        f'<animateTransform attributeName="transform" type="scale" additive="sum" values="0.55;1.1;0.55" dur="{d}s" repeatCount="indefinite"/>'
        f'</g>'
    )

# continents on a strip twice the planet's width, slid sideways forever: the planet turns
blobs = []
for k in range(2):
    off = k * PR * 2 * 1.6
    # each continent is a cluster of overlapping shapes, so it reads as land and not as dots
    for cx0, cy0, c, parts in [
        (0.15, -0.30, "#ff7a59", [(0, 0, .30, .15, -20), (.22, .10, .22, .13, 15), (-.12, .14, .16, .10, 30), (.08, -.12, .12, .08, 0)]),
        (0.85, 0.20, "#ff8f62", [(0, 0, .34, .20, 10), (.25, -.16, .20, .12, -25), (-.20, .16, .18, .12, 20), (.12, .26, .14, .08, 0)]),
        (1.65, -0.35, "#ffb36b", [(0, 0, .24, .12, 25), (.18, .12, .16, .10, -10), (-.16, -.06, .12, .08, 0)]),
        (2.35, 0.30, "#ff7a59", [(0, 0, .30, .18, -15), (-.24, -.12, .18, .11, 20), (.22, .14, .18, .09, 0), (.05, -.20, .12, .07, 0)]),
        (2.90, -0.50, "#ff9a66", [(0, 0, .18, .09, 0), (.14, .06, .12, .07, 20)]),
    ]:
        for dx, dy, rx, ry, rot in parts:
            x = PX - PR + off + (cx0 + dx) * PR
            y = PY + (cy0 + dy) * PR
            blobs.append(
                f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx * PR:.1f}" ry="{ry * PR:.1f}" transform="rotate({rot} {x:.1f} {y:.1f})" fill="{c}" opacity="0.9"/>'
            )
strip = PR * 2 * 1.6

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="David Lee, developer at Story Loom AI: stories, rendered as worlds">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0d0b12"/><stop offset="0.6" stop-color="#140f22"/><stop offset="1" stop-color="#1c1230"/>
    </linearGradient>
    <radialGradient id="nebula" cx="0.76" cy="0.5" r="0.55">
      <stop offset="0" stop-color="#8f7bff" stop-opacity="0.38"/><stop offset="0.5" stop-color="#ff7a59" stop-opacity="0.10"/><stop offset="1" stop-color="#0d0b12" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="sea" cx="0.36" cy="0.32" r="0.8">
      <stop offset="0" stop-color="#b4a6ff"/><stop offset="0.45" stop-color="#7a66f0"/><stop offset="1" stop-color="#2c2170"/>
    </radialGradient>
    <radialGradient id="shade" cx="0.32" cy="0.3" r="0.85">
      <stop offset="0.45" stop-color="#0d0b12" stop-opacity="0"/><stop offset="1" stop-color="#0d0b12" stop-opacity="0.78"/>
    </radialGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0.62" stop-color="#a08bff" stop-opacity="0.55"/><stop offset="1" stop-color="#a08bff" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="word" x1="0" x2="1">
      <stop offset="0" stop-color="#8f7bff"/><stop offset="0.5" stop-color="#ff7a59"/><stop offset="1" stop-color="#ffb36b"/>
    </linearGradient>
    <linearGradient id="trail" x1="0" x2="1">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0"/><stop offset="1" stop-color="#ffffff" stop-opacity="0.95"/>
    </linearGradient>
    <clipPath id="ball"><circle cx="{PX}" cy="{PY}" r="{PR}"/></clipPath>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  </defs>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#nebula)">
      <animate attributeName="opacity" values="0.75;1;0.75" dur="7s" repeatCount="indefinite"/>
    </rect>
    {''.join(stars)}
    {''.join(sparkles)}

    <!-- a shooting star now and then -->
    <g opacity="0">
      <line x1="-86" y1="-26" x2="0" y2="0" stroke="url(#trail)" stroke-width="2" stroke-linecap="round"/>
      <animateTransform attributeName="transform" type="translate" values="140 24; 540 144" dur="1.1s" begin="1.5s;shoot.end+5s" id="shoot" fill="freeze"/>
      <animate attributeName="opacity" values="0;1;0" dur="1.1s" begin="1.5s;shoot.end+5s"/>
    </g>

    <!-- the world: glow, back of the ring, the planet turning, front of the ring, a moon -->
    <circle cx="{PX}" cy="{PY}" r="{PR * 1.45:.0f}" fill="url(#glow)">
      <animate attributeName="r" values="{PR * 1.40:.0f};{PR * 1.52:.0f};{PR * 1.40:.0f}" dur="5s" repeatCount="indefinite"/>
    </circle>
    <g transform="rotate(-16 {PX} {PY})">
      <path d="M{PX - 138} {PY} A138 34 0 0 1 {PX + 138} {PY}" fill="none" stroke="#ffb36b" stroke-width="2.4" stroke-dasharray="7 9" opacity="0.55">
        <animate attributeName="stroke-dashoffset" values="0;-160" dur="6s" repeatCount="indefinite"/>
      </path>
    </g>
    <circle cx="{PX}" cy="{PY}" r="{PR}" fill="url(#sea)"/>
    <g clip-path="url(#ball)">
      <g>
        {''.join(blobs)}
        <animateTransform attributeName="transform" type="translate" values="0 0; -{strip:.1f} 0" dur="18s" repeatCount="indefinite"/>
      </g>
      <ellipse cx="{PX}" cy="{PY - PR + 8}" rx="{PR * 0.7:.0f}" ry="14" fill="#f2efff" opacity="0.85"/>
      <circle cx="{PX}" cy="{PY}" r="{PR}" fill="url(#shade)"/>
    </g>
    <circle cx="{PX}" cy="{PY}" r="{PR}" fill="none" stroke="#c9bcff" stroke-opacity="0.5" stroke-width="1.5"/>
    <g transform="rotate(-16 {PX} {PY})">
      <path d="M{PX + 138} {PY} A138 34 0 0 1 {PX - 138} {PY}" fill="none" stroke="#ffb36b" stroke-width="2.8" stroke-dasharray="7 9">
        <animate attributeName="stroke-dashoffset" values="0;-160" dur="6s" repeatCount="indefinite"/>
      </path>
      <circle r="7" fill="#d8d2e6">
        <animateMotion dur="9s" repeatCount="indefinite" path="M{PX + 160} {PY} A160 44 0 1 1 {PX - 160} {PY} A160 44 0 1 1 {PX + 160} {PY}"/>
      </circle>
    </g>

    <!-- the words -->
    <g font-family="'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif">
      <text x="56" y="88" fill="#ffb36b" font-size="14" font-weight="700" letter-spacing="3.5">DEVELOPER AT STORY LOOM AI</text>
      <text x="52" y="160" fill="#f4eee6" font-size="66" font-weight="800" letter-spacing="-2">David <tspan fill="url(#word)">Lee</tspan></text>
      <text x="55" y="204" fill="#f4eee6" font-size="25" font-weight="700" letter-spacing="-0.5">Stories, <tspan fill="url(#word)">rendered</tspan> as worlds.</text>
      <text x="56" y="244" fill="#a59eb3" font-size="16">Unreal Engine · Real-time 3D · Visualization · AI Art</text>
    </g>
  </g>
</svg>
'''
out = sys.argv[1] if len(sys.argv) > 1 else "assets/header.svg"
open(out, "w", encoding="utf-8", newline="\n").write(svg)
print("wrote", out, len(svg), "bytes")
