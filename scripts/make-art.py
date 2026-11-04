"""Write the animated SVG art for David's GitHub profile, all in one look: space (a drifting dot
grid, twinkling stars) and planets that turn, with Sora and Inter for the words.

- assets/header.svg, assets/footer.svg: the banners at the top and bottom. The header has one large
  planet with faint orbits around it; the footer a few small ones.
- assets/main-app.svg: the strip that links to the main app, storyloomai.com.
- assets/card-previs.svg, card-design.svg, card-comic.svg: the three module cards, side by side.
- assets/path.svg: Unreal Engine -> Visualization -> AI Art.
- assets/now.svg: what he is working on and learning.

GitHub will not let a README set its own fonts or backgrounds, which is why these are images.

Run: python scripts/make-art.py   (needs the internet, for the fonts)
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
    960, 140,
    [
        (206, 72, 25, "violet", {"moon": True, "spin": 16}),
        (84, 46, 15, "coral", {"ring": True, "tilt": -22, "spin": 13}),
        (330, 38, 9, "gold", {"spin": 10}),
        (370, 100, 13, "plum", {"ring": True, "tilt": 18, "spin": 14}),
        (118, 110, 7, "ice", {"spin": 9}),
        (540, 26, 4, "gold", {"spin": 8}),
    ],
    None, (0.22, 0.5),
    [(40, 96, 5, 3.6), (274, 122, 4, 4.2), (468, 20, 4, 3.1), (932, 120, 5, 4.4), (620, 126, 4, 3.7)],
    ((300, 14), (540, 40)),
    '''    <text x="904" y="44" fill="#ffb36b" font-family="Inter" font-size="12" font-weight="600" letter-spacing="3.2" text-anchor="end">THANKS FOR STOPPING BY</text>
    <text x="904" y="86" fill="#f4eee6" font-family="Sora" font-size="34" font-weight="700" letter-spacing="-1.2" text-anchor="end">See you in <tspan fill="url(#word)">another world.</tspan></text>
    <text x="904" y="114" fill="#a59eb3" font-family="Inter" font-size="14" font-weight="400" letter-spacing="0.1" text-anchor="end">storyloomai.com · Previs · Scene Studio · SLA Comic</text>''',
    "Thanks for stopping by. See you in another world. Story Loom AI: Previs, Scene Studio, SLA Comic",
    11,
)

# ---- the panels inside the README: same space, quieter -------------------------------------------

def panel(W, H, body, words, label, x0=0, x1=None, glow=("#8f7bff", 0.0, 0.0), planets=(), stars=24, seed=1, rx=18):
    """A dark card from x0 to x1 (the rest is clear, the gap to its neighbour), a dot grid, a glow
    in one corner, a few stars, optional small planets, and the words."""
    x1 = W if x1 is None else x1
    rnd = random.Random(seed)
    words = words.replace('font-family="Sora"', f'font-family="Sora, {STACK}"').replace('font-family="Inter"', f'font-family="Inter, {STACK}"')
    gc, gx, gy = glow
    st = []
    for _ in range(stars):
        x, y = rnd.uniform(x0 + 10, x1 - 10), rnd.uniform(10, H - 10)
        dur, begin, lo = rnd.uniform(2.4, 5.5), rnd.uniform(0, 4), rnd.uniform(0.1, 0.35)
        st.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.choice([0.6, 0.8, 1.0, 1.2])}" fill="#fff">'
                  f'<animate attributeName="opacity" values="{lo:.2f};0.9;{lo:.2f}" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/></circle>')
    pd, pb = zip(*(planet(i, *p[:4], **(p[4] if len(p) > 4 else {})) for i, p in enumerate(planets))) if planets else ((), ())
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{html.escape(label)}">
  <style>
    {fonts_css(words)}
  </style>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#120f1b"/><stop offset="1" stop-color="#191226"/></linearGradient>
    <radialGradient id="corner" gradientUnits="userSpaceOnUse" cx="{x0 + (x1 - x0) * gx:.0f}" cy="{H * gy:.0f}" r="{max(x1 - x0, H) * 0.75:.0f}">
      <stop offset="0" stop-color="{gc}" stop-opacity="0.30"/><stop offset="1" stop-color="{gc}" stop-opacity="0"/>
    </radialGradient>
    <pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse">
      <circle cx="9" cy="9" r="0.8" fill="#d9d2ff" fill-opacity="0.18"/>
      <animateTransform attributeName="patternTransform" type="translate" values="0 0;18 18" dur="30s" repeatCount="indefinite"/>
    </pattern>
    <radialGradient id="shade" cx="0.32" cy="0.3" r="0.85">
      <stop offset="0.45" stop-color="#0d0b12" stop-opacity="0"/><stop offset="1" stop-color="#0d0b12" stop-opacity="0.78"/>
    </radialGradient>
    <linearGradient id="word" x1="0" x2="1"><stop offset="0" stop-color="#8f7bff"/><stop offset="0.5" stop-color="#ff7a59"/><stop offset="1" stop-color="#ffb36b"/></linearGradient>
    {"".join(pd)}
    <clipPath id="card"><rect x="{x0}" width="{x1 - x0}" height="{H}" rx="{rx}"/></clipPath>
  </defs>
  <g clip-path="url(#card)">
    <rect x="{x0}" width="{x1 - x0}" height="{H}" fill="url(#bg)"/>
    <rect x="{x0}" width="{x1 - x0}" height="{H}" fill="url(#corner)"/>
    <rect x="{x0}" width="{x1 - x0}" height="{H}" fill="url(#dots)"/>
    {"".join(st)}
    {body}
    {"".join(pb)}
{words}
  </g>
  <rect x="{x0 + 0.5}" y="0.5" width="{x1 - x0 - 1}" height="{H - 1}" rx="{rx}" fill="none" stroke="#ffffff" stroke-opacity="0.09"/>
</svg>
'''


ARROW = '<path d="M0 8 L8 0 M2 0 H8 V6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'


def pill(x, y, text, color, size=12.5, anchor_right=False):
    """A rounded outline around a domain, with an arrow; width from a rough Inter measure."""
    w = len(text) * size * 0.56 + 40
    left = x - w if anchor_right else x
    return (f'<rect x="{left:.1f}" y="{y - 15}" width="{w:.1f}" height="26" rx="13" fill="{color}" fill-opacity="0.10" stroke="{color}" stroke-opacity="0.45"/>'
            f'<text x="{left + 14:.1f}" y="{y + 2.5}" fill="{color}" font-family="Inter" font-size="{size}" font-weight="500">{text}</text>'
            f'<g transform="translate({left + w - 22:.1f} {y - 6})" color="{color}" style="color:{color}">{ARROW}</g>')


def lines(x, y, rows, size, color, lead, weight=400):
    return "\n".join(f'    <text x="{x}" y="{y + i * lead:.1f}" fill="{color}" font-family="Inter" font-size="{size}" font-weight="{weight}">{html.escape(r)}</text>' for i, r in enumerate(rows))


# the main app: a slim strip across the page
main_app = panel(
    960, 96, "",
    f'''    <text x="104" y="40" fill="#ffb36b" font-family="Inter" font-size="12" font-weight="600" letter-spacing="3">THE MAIN APP</text>
    <text x="104" y="68" fill="#f4eee6" font-family="Sora" font-size="25" font-weight="700" letter-spacing="-0.6">Story Loom AI, <tspan fill="url(#word)">where the story is written</tspan></text>
    {pill(928, 50, "storyloomai.com", "#ff7a59", 14, anchor_right=True)}''',
    "The main app: Story Loom AI, where the story is written. storyloomai.com",
    glow=("#ff7a59", 0.05, 0.5), planets=[(56, 48, 22, "coral", {"ring": True, "tilt": -18, "spin": 14})], stars=30, seed=3, rx=16,
)

# the three modules, each its own image so each can be its own link. Each is 300 wide with the
# card set inside it so that, laid edge to edge, the outer edges meet the page and the gaps are equal.
CW, CH = 300, 282
cards = {}
for n, (key, pal, color, eyebrow, title, dom, desc) in enumerate([
    ("previs", "violet", "#a08bff", "RENDERING", "Previs", "previs.storyloomai.art",
     ["Pre-visualization: scenes lit, framed", "and rendered like a film set before", "anything is final, using real-time", "techniques from game engines."]),
    ("design", "coral", "#ff8a6b", "IMAGE TO 3D WORLD", "Scene Studio", "design.storyloomai.art",
     ["A single photo is read for depth,", "shape and light, then rebuilt as a", "3D world you can move through", "and share."]),
    ("comic", "gold", "#ffb36b", "STORY ART", "SLA Comic", "comic.storyloomai.art",
     ["Type a title, meet your characters,", "pick a story, and it is written and", "drawn as a webtoon or a printed", "comic book."]),
]):
    x0, x1 = 4 * n, CW - 8 + 4 * n
    cards[key] = panel(
        CW, CH, "",
        f'''    <text x="{x0 + 24}" y="104" fill="{color}" font-family="Inter" font-size="11" font-weight="600" letter-spacing="2.6">{eyebrow}</text>
    <text x="{x0 + 23}" y="134" fill="#f4eee6" font-family="Sora" font-size="25" font-weight="700" letter-spacing="-0.7">{title}</text>
{lines(x0 + 24, 162, desc, 13, "#a59eb3", 19.5)}
    {pill(x0 + 24, 254, dom, color, 12)}''',
        f"{title}: {' '.join(desc)} {dom}",
        x0=x0, x1=x1, glow=(color, 0.15, 0.1), planets=[(x0 + 50, 50, 22, pal, {"ring": key == "comic", "moon": key == "previs", "spin": 12 + 2 * n})],
        stars=8, seed=20 + n,
    )

# Unreal Engine -> Visualization -> AI Art, with a light running along the path
steps = [("UNREAL ENGINE", "Real-time 3D", "#a08bff"), ("VISUALIZATION", "Image to 3D worlds", "#ff8a6b"), ("AI ART", "Now", "#ffb36b")]
path_body, path_words = [], []
xs = [150, 480, 810]
# a flat line has no height, so its gradient is set in page units, not the line's own box
path_body.append(f'<linearGradient id="pathline" gradientUnits="userSpaceOnUse" x1="{xs[0]}" x2="{xs[-1]}" y1="0" y2="0"><stop offset="0" stop-color="#a08bff"/><stop offset="0.5" stop-color="#ff8a6b"/><stop offset="1" stop-color="#ffb36b"/></linearGradient>')
path_body.append(f'<line x1="{xs[0]}" y1="40" x2="{xs[-1]}" y2="40" stroke="url(#pathline)" stroke-width="2" stroke-dasharray="3 7" opacity="0.8">'
                 f'<animate attributeName="stroke-dashoffset" values="0;-100" dur="5s" repeatCount="indefinite"/></line>')
path_body.append(f'<circle r="4" cy="40" fill="#fff"><animate attributeName="cx" values="{xs[0]};{xs[-1]}" dur="3.6s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.9;1" dur="3.6s" repeatCount="indefinite"/></circle>')
for x, (a, b, c) in zip(xs, steps):
    path_body.append(f'<circle cx="{x}" cy="40" r="15" fill="#120f1b" stroke="{c}" stroke-width="2"/>'
                     f'<circle cx="{x}" cy="40" r="6" fill="{c}"><animate attributeName="r" values="4.5;7;4.5" dur="2.6s" repeatCount="indefinite"/></circle>')
    path_words.append(f'    <text x="{x}" y="82" fill="{c}" font-family="Inter" font-size="12" font-weight="600" letter-spacing="2.6" text-anchor="middle">{a}</text>')
    path_words.append(f'    <text x="{x}" y="104" fill="#f4eee6" font-family="Sora" font-size="17" font-weight="600" letter-spacing="-0.3" text-anchor="middle">{b}</text>')
path = panel(960, 126, "".join(path_body), "\n".join(path_words), "Unreal Engine, real-time 3D, then visualization and image to 3D worlds, and now AI art",
             glow=("#8f7bff", 0.5, 0.0), stars=36, seed=5, rx=16)

# working on / learning, two halves of one panel
work = [
    ["Building Story Loom AI, an AI-driven storytelling", "platform: its art, its rendering and its 3D worlds."],
    ["Turning single images into 3D worlds you can explore."],
    ["Real-time visualization of story scenes, on the web", "with three.js and in Unreal Engine 5."],
    ["Crafting procedural, hyper-realistic environments", "that react to stories dynamically."],
    ["Merging advanced game AI with cinematic,", "player-driven storytelling."],
]
learn = [
    ["Generative AI for art: keeping characters and style", "consistent from one scene to the next."],
    ["Reading depth and shape from a single image and", "rebuilding it in 3D."],
    ["Integrating real-time AI generation pipelines", "directly into Unreal Engine 5."],
    ["Coaxing Nanite and Lumen into rendering", "trillion-polygon worlds."],
]


def column(x, eyebrow, title, items, color):
    out = [f'    <text x="{x}" y="50" fill="{color}" font-family="Inter" font-size="12" font-weight="600" letter-spacing="2.8">{eyebrow}</text>',
           f'    <text x="{x}" y="80" fill="#f4eee6" font-family="Sora" font-size="22" font-weight="700" letter-spacing="-0.5">{title}</text>']
    dots, y = [], 118
    for item in items:
        dots.append(f'<circle cx="{x + 4}" cy="{y - 5}" r="3.2" fill="{color}"/>')
        out.append(lines(x + 20, y, item, 14.5, "#c9c2d6", 21))
        y += 21 * len(item) + 14
    return out, dots, y


wl, wd, wy = column(48, "CURRENTLY WORKING ON", "What I am building", work, "#ff8a6b")
ll, ld, ly = column(528, "CURRENTLY LEARNING", "What I am learning", learn, "#a08bff")
NH = max(wy, ly) + 16
now = panel(960, NH, '<line x1="480" y1="36" x2="480" y2="' + str(NH - 36) + '" stroke="#ffffff" stroke-opacity="0.08"/>' + "".join(wd + ld),
            "\n".join(wl + ll), "What I am working on and learning: " + " ".join(" ".join(i) for i in work + learn),
            glow=("#ff7a59", 0.0, 0.0), stars=40, seed=9, rx=18)

for name, svg in [("assets/header.svg", header), ("assets/footer.svg", footer), ("assets/main-app.svg", main_app),
                  ("assets/card-previs.svg", cards["previs"]), ("assets/card-design.svg", cards["design"]), ("assets/card-comic.svg", cards["comic"]),
                  ("assets/path.svg", path), ("assets/now.svg", now)]:
    open(name, "w", encoding="utf-8", newline="\n").write(svg)
    print("wrote", name, len(svg) // 1024, "KB")
