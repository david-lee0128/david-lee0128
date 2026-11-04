"""Write the animated SVG header and footer for David's GitHub profile: space behind the words
(a drifting dot grid, twinkling stars, a shooting star) and planets that turn, some with a ring
or a moon. The header has one large planet with faint orbits around it; the footer a few small ones.

Run: python scripts/make-banners.py   (writes assets/header.svg and assets/footer.svg; needs the
internet, for the fonts)
"""
import base64
import html
import random
import re
import urllib.parse
import urllib.request

# A README image cannot load web fonts, so each banner carries its own: Sora for the display
# lines and Inter for the rest (the fonts of storyloomai.art), cut down by Google Fonts to just
# the letters the banner uses, which keeps each one to a few KB.
STACK = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read()


def fonts_css(words):
    """@font-face rules for every (family, weight) the words use, subset to their letters."""
    need = {}
    for m in re.finditer(r"<text\b([^>]*)>(.*?)</text>", words, re.S):
        fam = re.search(r'font-family="(\w+)', m[1])[1]
        wt = re.search(r'font-weight="(\d+)"', m[1])[1]
        need.setdefault((fam, wt), set()).update(html.unescape(re.sub(r"<[^>]+>", "", m[2])))
    rules = []
    for (fam, wt), chars in sorted(need.items()):
        q = urllib.parse.urlencode({"family": f"{fam}:wght@{wt}", "text": "".join(sorted(chars))})
        css = get(f"https://fonts.googleapis.com/css2?{q}").decode()
        data = base64.b64encode(get(re.search(r"url\((https://[^)]+)\)", css)[1])).decode()
        rules.append(f"@font-face {{ font-family: '{fam}'; font-weight: {wt}; src: url(data:font/woff2;base64,{data}) format('woff2'); }}")
    return "\n    ".join(rules)


# each planet: sea (light, mid, dark), its land colours, its glow
PALETTES = {
    "violet": (("#b4a6ff", "#7a66f0", "#2c2170"), ("#ff7a59", "#ff8f62", "#ffb36b", "#ff7a59", "#ff9a66"), "#a08bff"),
    "coral": (("#ffc2a8", "#ff7a59", "#6e2618"), ("#ffd9b0", "#ffb36b", "#ffe6c8", "#ffc48a", "#ffd9b0"), "#ff8a6b"),
    "gold": (("#ffe6bd", "#ffb36b", "#7a4417"), ("#ff8f62", "#ff7a59", "#ffd29a", "#ff8f62", "#ffa070"), "#ffc27e"),
    "ice": (("#f1eeff", "#b9b0d6", "#3d3654"), ("#d9d2ff", "#ffffff", "#c9bcff", "#e8e2ff", "#ffffff"), "#d9d2ff"),
    "plum": (("#f0b8ff", "#a86bf0", "#331b66"), ("#ffb36b", "#ff9fd0", "#ffd0a8", "#ff8fb8", "#ffb36b"), "#c08bff"),
}
CONTINENTS = [
    (0.15, -0.30, [(0, 0, .30, .15, -20), (.22, .10, .22, .13, 15), (-.12, .14, .16, .10, 30), (.08, -.12, .12, .08, 0)]),
    (0.85, 0.20, [(0, 0, .34, .20, 10), (.25, -.16, .20, .12, -25), (-.20, .16, .18, .12, 20), (.12, .26, .14, .08, 0)]),
    (1.65, -0.35, [(0, 0, .24, .12, 25), (.18, .12, .16, .10, -10), (-.16, -.06, .12, .08, 0)]),
    (2.35, 0.30, [(0, 0, .30, .18, -15), (-.24, -.12, .18, .11, 20), (.22, .14, .18, .09, 0), (.05, -.20, .12, .07, 0)]),
    (2.90, -0.50, [(0, 0, .18, .09, 0), (.14, .06, .12, .07, 20)]),
]


def planet(i, PX, PY, PR, pal, ring=False, moon=False, tilt=-16, spin=18):
    """One planet: glow, back of the ring, the globe with its land sliding past (it turns), front of the ring, a moon."""
    (s0, s1, s2), land, glow = PALETTES[pal]
    k = PR / 78  # the ring and the moon were drawn for a planet of radius 78
    defs = (
        f'<radialGradient id="sea{i}" cx="0.36" cy="0.32" r="0.8"><stop offset="0" stop-color="{s0}"/><stop offset="0.45" stop-color="{s1}"/><stop offset="1" stop-color="{s2}"/></radialGradient>'
        f'<radialGradient id="glow{i}" cx="0.5" cy="0.5" r="0.5"><stop offset="0.62" stop-color="{glow}" stop-opacity="0.55"/><stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="ball{i}"><circle cx="{PX}" cy="{PY}" r="{PR}"/></clipPath>'
    )
    blobs = []
    for n in range(2):
        off = n * PR * 2 * 1.6
        for (cx0, cy0, parts), c in zip(CONTINENTS, land):
            for dx, dy, rx, ry, rot in parts:
                x, y = PX - PR + off + (cx0 + dx) * PR, PY + (cy0 + dy) * PR
                blobs.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx * PR:.1f}" ry="{ry * PR:.1f}" transform="rotate({rot} {x:.1f} {y:.1f})" fill="{c}" opacity="0.9"/>')
    strip = PR * 2 * 1.6
    ra, rb, ma, mb = 138 * k, 34 * k, 160 * k, 44 * k
    sw = max(1.0, 2.6 * k ** 0.5)
    dash = f"{max(2.5, 7 * k):.1f} {max(3.5, 9 * k):.1f}"
    out = [
        f'<circle cx="{PX}" cy="{PY}" r="{PR * 1.45:.1f}" fill="url(#glow{i})"><animate attributeName="r" values="{PR * 1.40:.1f};{PR * 1.52:.1f};{PR * 1.40:.1f}" dur="5s" repeatCount="indefinite"/></circle>'
    ]
    if ring:
        out.append(
            f'<g transform="rotate({tilt} {PX} {PY})"><path d="M{PX - ra:.1f} {PY} A{ra:.1f} {rb:.1f} 0 0 1 {PX + ra:.1f} {PY}" fill="none" stroke="#ffb36b" stroke-width="{sw * 0.9:.2f}" stroke-dasharray="{dash}" opacity="0.55">'
            f'<animate attributeName="stroke-dashoffset" values="0;-160" dur="6s" repeatCount="indefinite"/></path></g>'
        )
    out.append(
        f'<circle cx="{PX}" cy="{PY}" r="{PR}" fill="url(#sea{i})"/>'
        f'<g clip-path="url(#ball{i})"><g>{"".join(blobs)}'
        f'<animateTransform attributeName="transform" type="translate" values="0 0; -{strip:.1f} 0" dur="{spin}s" repeatCount="indefinite"/></g>'
        f'<ellipse cx="{PX}" cy="{PY - PR + 8 * k:.1f}" rx="{PR * 0.7:.1f}" ry="{14 * k:.1f}" fill="#f2efff" opacity="0.85"/>'
        f'<circle cx="{PX}" cy="{PY}" r="{PR}" fill="url(#shade)"/></g>'
        f'<circle cx="{PX}" cy="{PY}" r="{PR}" fill="none" stroke="{s0}" stroke-opacity="0.5" stroke-width="{max(0.8, 1.5 * k ** 0.5):.2f}"/>'
    )
    if ring or moon:
        front = []
        if ring:
            front.append(
                f'<path d="M{PX + ra:.1f} {PY} A{ra:.1f} {rb:.1f} 0 0 1 {PX - ra:.1f} {PY}" fill="none" stroke="#ffb36b" stroke-width="{sw:.2f}" stroke-dasharray="{dash}">'
                f'<animate attributeName="stroke-dashoffset" values="0;-160" dur="6s" repeatCount="indefinite"/></path>'
            )
        if moon:
            front.append(
                f'<circle r="{max(2.2, 7 * k):.1f}" fill="#d8d2e6"><animateMotion dur="{6 + 3 * k:.1f}s" repeatCount="indefinite" '
                f'path="M{PX + ma:.1f} {PY} A{ma:.1f} {mb:.1f} 0 1 1 {PX - ma:.1f} {PY} A{ma:.1f} {mb:.1f} 0 1 1 {PX + ma:.1f} {PY}"/></circle>'
            )
        out.append(f'<g transform="rotate({tilt} {PX} {PY})">{"".join(front)}</g>')
    return defs, "".join(out)


def banner(W, H, planets, orbit_around, nebula, sparkles, shoot, words, label, seed):
    rnd = random.Random(seed)
    words = words.replace('font-family="Sora"', f'font-family="Sora, {STACK}"').replace('font-family="Inter"', f'font-family="Inter, {STACK}"')
    keep_clear = [(p[0], p[1], p[2]) for p in planets]

    stars = []
    for _ in range(int(70 * W * H / (960 * 300))):
        x, y = rnd.uniform(8, W - 8), rnd.uniform(8, H - 8)
        if any((x - px) ** 2 + (y - py) ** 2 < (pr + 6) ** 2 for px, py, pr in keep_clear):
            continue
        r = rnd.choice([0.6, 0.8, 1.0, 1.0, 1.3, 1.7])
        dur, begin, lo = rnd.uniform(2.2, 5.5), rnd.uniform(0, 4), rnd.uniform(0.15, 0.4)
        col = rnd.choice(["#ffffff", "#ffffff", "#ffe2c4", "#d9d2ff"])
        stars.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}">'
            f'<animate attributeName="opacity" values="{lo:.2f};1;{lo:.2f}" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/></circle>'
        )

    spark = []
    for x, y, s, d in sparkles:
        q = s * 0.18
        spark.append(
            f'<g transform="translate({x} {y})" opacity="0.9">'
            f'<path d="M0 -{s} L{q:.2f} -{q:.2f} L{s} 0 L{q:.2f} {q:.2f} L0 {s} L-{q:.2f} {q:.2f} L-{s} 0 L-{q:.2f} -{q:.2f} Z" fill="#fff6ec"/>'
            f'<animateTransform attributeName="transform" type="scale" additive="sum" values="0.55;1.1;0.55" dur="{d}s" repeatCount="indefinite"/></g>'
        )

    # faint orbits around the main planet, one dashed and turning, one with a small body on it
    orbits = []
    if orbit_around is not None:
        OX, OY, OR = planets[orbit_around][:3]
        for n, f in enumerate([1.95, 2.75, 3.6, 4.55]):
            r, op = OR * f, 0.16 - n * 0.025
            if n == 1:
                orbits.append(
                    f'<g><circle cx="{OX}" cy="{OY}" r="{r:.1f}" fill="none" stroke="#8f7bff" stroke-opacity="{op:.3f}" stroke-dasharray="2 7"/>'
                    f'<animateTransform attributeName="transform" type="rotate" values="0 {OX} {OY};360 {OX} {OY}" dur="140s" repeatCount="indefinite"/></g>'
                )
            else:
                orbits.append(f'<circle cx="{OX}" cy="{OY}" r="{r:.1f}" fill="none" stroke="#a59eb3" stroke-opacity="{op:.3f}"/>')
        ro = OR * 3.6
        orbits.append(
            f'<circle r="2.2" fill="#ffb36b" opacity="0.8"><animateMotion dur="48s" repeatCount="indefinite" '
            f'path="M{OX - ro:.1f} {OY} a{ro:.1f} {ro:.1f} 0 1 1 {2 * ro:.1f} 0 a{ro:.1f} {ro:.1f} 0 1 1 -{2 * ro:.1f} 0"/></circle>'
        )

    pdefs, pbodies = zip(*(planet(i, *p[:4], **(p[4] if len(p) > 4 else {})) for i, p in enumerate(planets)))
    (sx0, sy0), (sx1, sy1) = shoot
    gx, gy = nebula

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{label}">
  <style>
    {fonts_css(words)}
  </style>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0d0b12"/><stop offset="0.6" stop-color="#140f22"/><stop offset="1" stop-color="#1c1230"/>
    </linearGradient>
    <radialGradient id="nebula" cx="{gx}" cy="{gy}" r="0.55">
      <stop offset="0" stop-color="#8f7bff" stop-opacity="0.38"/><stop offset="0.5" stop-color="#ff7a59" stop-opacity="0.10"/><stop offset="1" stop-color="#0d0b12" stop-opacity="0"/>
    </radialGradient>
    <!-- a fine dot grid that drifts slowly, clearest behind the planets and gone at the edges -->
    <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
      <circle cx="11" cy="11" r="0.85" fill="#d9d2ff" fill-opacity="0.32"/>
      <animateTransform attributeName="patternTransform" type="translate" values="0 0;22 22" dur="24s" repeatCount="indefinite"/>
    </pattern>
    <radialGradient id="gridfade" gradientUnits="userSpaceOnUse" cx="{gx * W:.0f}" cy="{gy * H:.0f}" r="{W * 0.5:.0f}" gradientTransform="translate({gx * W:.0f} {gy * H:.0f}) scale(1 {H / W * 1.6:.3f}) translate(-{gx * W:.0f} -{gy * H:.0f})">
      <stop offset="0" stop-color="#fff"/><stop offset="0.55" stop-color="#fff" stop-opacity="0.4"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
    <mask id="gridmask"><rect width="{W}" height="{H}" fill="url(#gridfade)"/></mask>
    <radialGradient id="shade" cx="0.32" cy="0.3" r="0.85">
      <stop offset="0.45" stop-color="#0d0b12" stop-opacity="0"/><stop offset="1" stop-color="#0d0b12" stop-opacity="0.78"/>
    </radialGradient>
    <linearGradient id="word" x1="0" x2="1">
      <stop offset="0" stop-color="#8f7bff"/><stop offset="0.5" stop-color="#ff7a59"/><stop offset="1" stop-color="#ffb36b"/>
    </linearGradient>
    <linearGradient id="trail" x1="0" x2="1">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0"/><stop offset="1" stop-color="#ffffff" stop-opacity="0.95"/>
    </linearGradient>
    {"".join(pdefs)}
    <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  </defs>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#nebula)">
      <animate attributeName="opacity" values="0.75;1;0.75" dur="7s" repeatCount="indefinite"/>
    </rect>
    <rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#gridmask)"/>
    {"".join(orbits)}
    {"".join(stars)}
    {"".join(spark)}

    <!-- a shooting star now and then -->
    <g opacity="0">
      <line x1="-86" y1="-26" x2="0" y2="0" stroke="url(#trail)" stroke-width="2" stroke-linecap="round"/>
      <animateTransform attributeName="transform" type="translate" values="{sx0} {sy0}; {sx1} {sy1}" dur="1.1s" begin="1.5s;shoot.end+5s" id="shoot" fill="freeze"/>
      <animate attributeName="opacity" values="0;1;0" dur="1.1s" begin="1.5s;shoot.end+5s"/>
    </g>

    <!-- the planets -->
    {"".join(pbodies)}

    <!-- the words -->
{words}
  </g>
</svg>
'''


header = banner(
    960, 300,
    [(742, 152, 78, "violet", {"ring": True, "moon": True})], 0, (0.76, 0.5),
    [(96, 52, 7, 3.4), (452, 40, 6, 4.1), (590, 262, 8, 3.0), (905, 58, 6, 4.6), (300, 250, 5, 3.8)],
    ((140, 24), (540, 144)),
    '''    <text x="56" y="86" fill="#ffb36b" font-family="Inter" font-size="13" font-weight="600" letter-spacing="3.2">DEVELOPER AT STORY LOOM AI</text>
    <text x="52" y="156" fill="#f4eee6" font-family="Sora" font-size="62" font-weight="700" letter-spacing="-2.6">David <tspan fill="url(#word)">Lee</tspan></text>
    <text x="55" y="200" fill="#f4eee6" font-family="Sora" font-size="23" font-weight="600" letter-spacing="-0.6">Stories, <tspan fill="url(#word)">rendered</tspan> as worlds.</text>
    <text x="56" y="242" fill="#a59eb3" font-family="Inter" font-size="15" font-weight="400" letter-spacing="0.1">Unreal Engine · Real-time 3D · Visualization · AI Art</text>''',
    "David Lee, developer at Story Loom AI: stories, rendered as worlds",
    7,
)

# the footer: a shorter strip, the words on the right, a few small planets scattered on the left
footer = banner(
    960, 190,
    [
        (208, 104, 30, "violet", {"moon": True, "spin": 16}),
        (82, 62, 19, "coral", {"ring": True, "tilt": -22, "spin": 13}),
        (334, 52, 11, "gold", {"spin": 10}),
        (360, 140, 16, "plum", {"ring": True, "tilt": 18, "spin": 14}),
        (112, 150, 8, "ice", {"spin": 9}),
        (548, 34, 5, "gold", {"spin": 8}),
    ],
    None, (0.22, 0.5),
    [(42, 120, 5, 3.6), (270, 168, 4, 4.2), (470, 24, 5, 3.1), (930, 166, 5, 4.4), (640, 172, 4, 3.7)],
    ((300, 16), (560, 50)),
    '''    <text x="904" y="62" fill="#ffb36b" font-family="Inter" font-size="12" font-weight="600" letter-spacing="3.2" text-anchor="end">THANKS FOR STOPPING BY</text>
    <text x="904" y="110" fill="#f4eee6" font-family="Sora" font-size="36" font-weight="700" letter-spacing="-1.3" text-anchor="end">See you in <tspan fill="url(#word)">another world.</tspan></text>
    <text x="904" y="146" fill="#a59eb3" font-family="Inter" font-size="14" font-weight="400" letter-spacing="0.1" text-anchor="end">storyloomai.com · Previs · Scene Studio · SLA Comic</text>''',
    "Thanks for stopping by. See you in another world. Story Loom AI: Previs, Scene Studio, SLA Comic",
    11,
)

for name, svg in [("assets/header.svg", header), ("assets/footer.svg", footer)]:
    open(name, "w", encoding="utf-8", newline="\n").write(svg)
    print("wrote", name, len(svg) // 1024, "KB")
