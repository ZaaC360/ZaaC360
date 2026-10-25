# Generates assets/banner.svg and assets/terminal.svg. Edit the text here, then from the repo root: python assets/gen.py
import html, random

random.seed(360)
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
  .rain, .scan, .gl {{ display: none; }} * {{ animation: none !important; }}
}}"""

LOGO = [  # ANSI Shadow "ZAAC", 32 cols each
    "███████╗ █████╗  █████╗  ██████╗",
    "╚══███╔╝██╔══██╗██╔══██╗██╔════╝",
    "  ███╔╝ ███████║███████║██║     ",
    " ███╔╝  ██╔══██║██╔══██║██║     ",
    "███████╗██║  ██║██║  ██║╚██████╗",
    "╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝",
]
assert all(len(r) == 32 for r in LOGO)


def banner():
    W, H, cw = 900, 300, 13
    x0 = (W - 32 * cw) / 2
    chars = "01アイウエオカキクケコサシスセソタチツテト<>/{}[]=+*#$%&"
    rain = []
    for i in range(46):
        x = 8 + i * 19.6
        col = [random.choice(chars) for _ in range(random.randint(10, 18))]
        tsp = "".join(f'<tspan x="{x:.1f}" dy="18"{" class=\"hd\"" if j == len(col) - 1 else ""}>{esc(c)}</tspan>'
                      for j, c in enumerate(col))
        rain.append(f'<text class="rain" style="animation-duration:{random.uniform(5, 12):.1f}s;'
                    f'animation-delay:-{random.uniform(0, 12):.1f}s">{tsp}</text>')

    def layer(cls, entrance):
        rows = [pinned(x0, 80 + i * 24, r, cw, "") for i, r in enumerate(LOGO)]
        if entrance:
            rows = [show(0.15 + i * 0.08, r) for i, r in enumerate(rows)]
        return f'<g class="{cls}">{"".join(rows)}</g>'

    sub = "> read the source. write the polyfill. ship it."
    sx = (W - len(sub) * 9.6) / 2
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">ZAAC</title>
<desc id="d">ASCII art ZAAC over falling matrix code. read the source. write the polyfill. ship it.</desc>
<style>{BASE_CSS}
.rain {{ font-size: 15px; fill: {G}; opacity: .28; animation: fall linear infinite; }}
.rain .hd {{ fill: #d7ffd9; }}
@keyframes fall {{ from {{ transform: translateY(-340px); }} to {{ transform: translateY({H + 20}px); }} }}
.logo text {{ font-size: 22px; }}
.main {{ fill: {G}; filter: url(#glow); animation: jit 5s infinite; }}
.gl {{ opacity: 0; animation: 5s infinite; }} .gr {{ fill: #ff2a6d; animation-name: gr; }} .gc {{ fill: #05d9e8; animation-name: gc; }}
@keyframes jit {{ 0%,86%,93%,100% {{ transform: none; }} 88% {{ transform: translateX(3px); }} 90% {{ transform: translateX(-2px); }} }}
@keyframes gr {{ 0%,86%,93%,100% {{ opacity: 0; transform: none; }} 87% {{ opacity: .8; transform: translate(-5px,1px); }} 90% {{ opacity: .7; transform: translate(4px,-2px); }} }}
@keyframes gc {{ 0%,86%,93%,100% {{ opacity: 0; transform: none; }} 87% {{ opacity: .8; transform: translate(5px,-1px); }} 90% {{ opacity: .7; transform: translate(-3px,2px); }} }}
.scan {{ animation: scan 7s linear infinite; }}
@keyframes scan {{ from {{ transform: translateY(-60px); }} to {{ transform: translateY({H}px); }} }}
.hud {{ font-size: 12px; fill: {DIM}; }} .sub {{ font-size: 16px; fill: {FG}; }}
</style>
<defs>
<clipPath id="win"><rect width="{W}" height="{H}" rx="10"/></clipPath>
<filter id="glow" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<radialGradient id="vig" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="{BG}" stop-opacity=".93"/><stop offset=".55" stop-color="{BG}" stop-opacity=".75"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
<linearGradient id="sb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset=".5" stop-color="{G}" stop-opacity=".07"/><stop offset="1" stop-color="{G}" stop-opacity="0"/></linearGradient>
<pattern id="sl" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".35"/></pattern>
</defs>
<g clip-path="url(#win)">
<rect width="{W}" height="{H}" fill="{BG}"/>
{"".join(rain)}
<rect width="{W}" height="{H}" fill="url(#vig)"/>
<g class="logo">{layer("gl gr", False)}{layer("gl gc", False)}{layer("main", True)}</g>
{typed("sub", round(sx, 1), 250, sub, 9.6, 1.0, 2.2, "sub")}
{show(3.2, f'<rect class="cur" x="{sx + len(sub) * 9.6 + 4:.1f}" y="236" width="9" height="18" fill="{G}"/>')}
<text class="hud" x="20" y="26">ZaaC360://root</text>
<text class="hud" x="{W - 20}" y="26" text-anchor="end">sys.status: ONLINE <tspan class="g cur">●</tspan></text>
<text class="hud" x="20" y="{H - 16}">full-stack · js internals · c++</text>
<text class="hud" x="{W - 20}" y="{H - 16}" text-anchor="end">since 2022</text>
<rect class="scan" width="{W}" height="60" fill="url(#sb)"/>
<rect width="{W}" height="{H}" fill="url(#sl)"/>
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
<desc id="d">neofetch for zaac: full-stack developer since 2022. javascript, typescript, python, c++. react, node.js, shopify. shipped meeti, headlessShopify, neon-rubiks-cube. NOT NOT a vibeCoder.</desc>
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


for name, svg in (("banner", banner()), ("terminal", terminal())):
    open(f"assets/{name}.svg", "w", encoding="utf-8").write(svg)
    print(name, len(svg.encode()), "bytes")
