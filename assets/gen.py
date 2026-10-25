# Generates assets/banner.svg and assets/terminal.svg. Edit the text here, then from the repo root: python assets/gen.py
import html, math

MONO = 'ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace'
G, GB, DIM, FG, BG = "#39d353", "#7ee787", "#6e7681", "#c9d1d9", "#0a0d0a"
esc = lambda s: html.escape(s, quote=False)


def typed(id_, x, y, text, cw, begin, dur, cls):
    # textLength pins the width so the discrete clip reveals exactly one char per step in any font
    w = len(text) * cw
    vals = ";".join(str(round(i * cw, 2)) for i in range(len(text) + 1))
    return (f'<clipPath id="{id_}"><rect x="{x}" y="{y - 20}" width="0" height="28">'
            f'<animate attributeName="width" values="{vals}" calcMode="discrete" begin="{begin}s" dur="{dur}s" fill="freeze"/></rect></clipPath>'
            f'<text class="{cls} typed" x="{x}" y="{y}" textLength="{w}" lengthAdjust="spacingAndGlyphs" clip-path="url(#{id_})" xml:space="preserve">{esc(text)}</text>')


def show(t, inner):
    return f'<g class="ln" opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>{inner}</g>'


def pinned(x, y, text, cw, cls, extra=""):
    return f'<text class="{cls}" x="{x}" y="{y}" textLength="{len(text) * cw}" lengthAdjust="spacingAndGlyphs" xml:space="preserve"{extra}>{esc(text)}</text>'


BASE_CSS = f"""
text {{ font-family: {MONO}; white-space: pre; }}
.g {{ fill: {G}; }} .gb {{ fill: {GB}; }} .d {{ fill: {DIM}; }} .f {{ fill: {FG}; }}
.cur {{ animation: blink 1s step-end infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{
  .ln {{ opacity: 1 !important; }} .typed {{ clip-path: none !important; }}
  .scan {{ display: none; }} * {{ animation: none !important; }}
}}"""

FONT = {  # 11x11 angular glyphs: chamfered corners, Λ-style A
    "Z": ["##########.", "###########", ".......####", "......####.", ".....####..", "....####...",
          "...####....", "..####.....", ".####......", "###########", ".##########"],
    "A": ["....###....", "...#####...", "...#####...", "..###.###..", "..###.###..", ".###...###.",
          ".#########.", "###########", "###.....###", "###.....###", "###.....###"],
    "C": ["...########", "..#########", ".####......", "####.......", "###........", "###........",
          "###........", "####.......", ".####......", "..#########", "...########"],
}


def banner():
    import random
    random.seed(360)
    W, H, T, step, skew = 900, 320, 7, 7.4, 0.35
    rows = ["...".join(FONT[c][r] for c in "ZAAC") for r in range(11)]
    gw, gh = (len(rows[0]) * 2 + 21 * skew) * step, 22 * step
    x0, y0 = (W - gw) / 2, 60
    cx, cy = W / 2, y0 + gh / 2
    greens = ["#39d353"] * 4 + ["#56d364"] * 3 + ["#7ee787", "#2ea043", "#aff5b4"]
    dots = []
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c != "#":
                continue
            for sx in (0, 1):  # 2x2 dots per glyph pixel
                for sy in (0, 1):
                    j = 2 * y + sy
                    # italic slant, plus one glyph row knocked 2 dots right as a glitch slice
                    tx = x0 + (2 * x + sx + 0.5 + (21 - j) * skew + 2 * (y == 5)) * step
                    ty = y0 + (j + 0.5) * step
                    fx, fy = random.uniform(-150, W + 150) - tx, random.uniform(-120, H + 120) - ty
                    a = math.atan2(ty - cy, tx - cx) + random.uniform(-0.5, 0.5)
                    d = random.uniform(250, 600)
                    delay = (tx - x0) / gw * 0.9 + random.uniform(0, 0.35)  # assembles as a left-to-right wave
                    dots.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="2.7" fill="{random.choice(greens)}" '
                                f'style="--x:{fx:.0f}px;--y:{fy:.0f}px;--ex:{math.cos(a) * d:.0f}px;--ey:{math.sin(a) * d:.0f}px;'
                                f'animation-delay:{delay:.2f}s"/>')

    sub = "> read the source. write the polyfill. ship it."
    sx = (W - len(sub) * 9.6) / 2
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">ZAAC</title>
<desc id="d">Hundreds of glowing dots fly in from everywhere and assemble into the word ZAAC, hold, then burst apart and reform. read the source. write the polyfill. ship it.</desc>
<style>{BASE_CSS}
.dots {{ filter: url(#glow); }}
.dots circle {{ transform-box: fill-box; transform-origin: center; opacity: 0;
  transform: translate(var(--x), var(--y)) scale(.3); animation: fly {T}s infinite, shine {T}s infinite; }}
@keyframes fly {{
  0% {{ transform: translate(var(--x), var(--y)) scale(.3); opacity: 0; animation-timing-function: cubic-bezier(.16, 1, .3, 1); }}
  38%, 80% {{ transform: translate(0, 0) scale(1); opacity: 1; }}
  80% {{ animation-timing-function: cubic-bezier(.7, 0, .84, 0); }}
  100% {{ transform: translate(var(--ex), var(--ey)) scale(.3); opacity: 0; }}
}}
@keyframes shine {{ 0%, 52%, 60%, 100% {{ fill-opacity: 1; }} 55% {{ fill: #ffffff; }} }}
.scan {{ animation: scan 7s linear infinite; }}
@keyframes scan {{ from {{ transform: translateY(-60px); }} to {{ transform: translateY({H}px); }} }}
.hud {{ font-size: 12px; fill: {DIM}; }} .sub {{ font-size: 16px; fill: {FG}; }}
@media (prefers-reduced-motion: reduce) {{ .dots circle {{ transform: none !important; opacity: 1 !important; }} }}
</style>
<defs>
<clipPath id="win"><rect width="{W}" height="{H}" rx="10"/></clipPath>
<filter id="glow" x="-5%" y="-10%" width="110%" height="120%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="grid" x="{x0}" y="{y0}" width="{step}" height="{step}" patternUnits="userSpaceOnUse"><circle cx="{step / 2}" cy="{step / 2}" r="1" fill="#1b2a1b"/></pattern>
<linearGradient id="sb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset=".5" stop-color="{G}" stop-opacity=".05"/><stop offset="1" stop-color="{G}" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#win)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
<g class="dots">{"".join(dots)}</g>
{typed("sub", round(sx, 1), H - 34, sub, 9.6, 2.4, 2.2, "sub")}
{show(4.6, f'<rect class="cur" x="{sx + len(sub) * 9.6 + 4:.1f}" y="{H - 48}" width="9" height="18" fill="{G}"/>')}
<text class="hud" x="20" y="24">ZaaC360://root</text>
<text class="hud" x="{W - 20}" y="24" text-anchor="end">sys.status: ONLINE <tspan class="g cur">●</tspan></text>
<rect class="scan" width="{W}" height="60" fill="url(#sb)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" stroke="#1f2d1f"/>
</svg>"""


CUBE = [
    "     +----------+",
    "    /          /|",
    "   /          / |",
    "  +----------+  |",
    "  |          |  |",
    "  |   ZAAC   |  +",
    "  |          | /",
    "  |          |/",
    "  +----------+",
]
INFO = [  # (key, value); key None = raw line
    (None, "zaac@github"),
    (None, "-----------"),
    ("role", "full-stack developer"),
    ("uptime", "since jun 2022, still compiling"),
    ("langs", "javascript · typescript · python · c++"),
    ("stack", "next.js · react native · node · postgres · redis"),
    ("shipped", "meeti · cardevo · apexindexer"),
    ("internals", "Promise.all · debounce — from scratch"),
    ("debug", "logs → debugger → read the source"),
    ("editor", "vs code, too many tabs"),
    ("mode", "NOT NOT a vibeCoder"),
]


def terminal():
    W, H, cw = 900, 455, 9
    prompt = lambda y: pinned(30, y, "zaac@github:~$", cw, "gb")
    out, t = [], 1.2
    for i, r in enumerate(CUBE):
        out.append(show(t + i * 0.06, f'<text class="g" x="30" y="{122 + i * 22}" xml:space="preserve">{esc(r)}</text>'))
    for i, (k, v) in enumerate(INFO):
        y = 100 + i * 22
        line = (f'<text x="300" y="{y}" class="{"gb" if i == 0 else "d"}">{esc(v)}</text>' if k is None else
                f'<text x="300" y="{y}" xml:space="preserve"><tspan class="g">{k:<11}</tspan><tspan class="f">{esc(v)}</tspan></text>')
        out.append(show(t + i * 0.06, line))
    colors = ["#0d1117", "#ff7b72", G, "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", FG]
    out.append(show(1.95, "".join(f'<rect x="{300 + i * 28}" y="336" width="26" height="14" fill="{c}"/>' for i, c in enumerate(colors))))

    bar_t = 4.0
    out.append(show(2.4, prompt(380) + typed("c2", 165, 380, "./ship --prod meeti", cw, 2.6, 1.2, "f")))
    out.append(show(bar_t, pinned(30, 405, "[", cw, "d") + pinned(39, 405, "░" * 30, cw, "d") + pinned(309, 405, "]", cw, "d")
                    + typed("bar", 39, 405, "█" * 30, cw, bar_t, 1.8, "g")))
    out.append(show(bar_t + 1.9, f'<text x="327" y="405"><tspan class="f">100%  </tspan><tspan class="g">✓ live in prod</tspan></text>'))
    out.append(show(bar_t + 2.3, prompt(435) + f'<rect class="cur" x="165" y="421" width="9" height="18" fill="{FG}"/>'))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">zaac@github: neofetch</title>
<desc id="d">neofetch for zaac: full-stack developer since 2022. javascript, typescript, python, c++. next.js, react native, node, postgres, redis. shipped meeti, cardevo, apexindexer. NOT NOT a vibeCoder.</desc>
<style>{BASE_CSS}
text {{ font-size: 15px; }}
</style>
<clipPath id="win"><rect width="{W}" height="{H}" rx="10"/></clipPath>
<g clip-path="url(#win)">
<rect width="{W}" height="{H}" fill="#0d1117"/>
<rect width="{W}" height="36" fill="#161b22"/>
<circle cx="22" cy="18" r="6" fill="#ff5f56"/><circle cx="42" cy="18" r="6" fill="#ffbd2e"/><circle cx="62" cy="18" r="6" fill="#27c93f"/>
<text x="{W / 2}" y="23" text-anchor="middle" class="d" style="font-size:13px">zaac@github: ~ — bash</text>
{show(0.3, prompt(68) + typed("c1", 165, 68, "neofetch", cw, 0.4, 0.6, "f"))}
{"".join(out)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" stroke="#30363d"/>
</svg>"""


if __name__ == "__main__":
    assert banner().count("<circle") > 800  # 2x2 dots per lit glyph pixel
    for name, svg in (("banner", banner()), ("terminal", terminal())):
        open(f"assets/{name}.svg", "w", encoding="utf-8").write(svg)
        print(name, len(svg.encode()), "bytes")
