# Generates assets/banner.svg and assets/terminal.svg. Edit the text here, then from the repo root: python assets/gen.py
# banner.svg is a tiny software 3D renderer: extruded voxel text -> rotate -> perspective -> z-buffer -> lambert -> ascii.
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
  .ln, .fr0 {{ opacity: 1 !important; }} .typed {{ clip-path: none !important; }}
  .scan, .fr:not(.fr0) {{ display: none; }} * {{ animation: none !important; }}
}}"""

FONT = {  # 9x11 pixel glyphs
    "Z": ["#########", "#########", "......###", ".....###.", "....###..", "...###...",
          "..###....", ".###.....", "###......", "#########", "#########"],
    "A": ["..#####..", ".#######.", "###...###", "##.....##", "##.....##", "#########",
          "#########", "##.....##", "##.....##", "##.....##", "##.....##"],
    "C": ["..#######", ".########", "###......", "##.......", "##.......", "##.......",
          "##.......", "##.......", "###......", ".########", "..#######"],
}
RAMP = ".,-~:;=!*#$@"


def voxel_points(word, depth=4, s=4):
    rows = ["..".join(FONT[c][r] for c in word) for r in range(11)]
    px = {(x, y) for y, row in enumerate(rows) for x, c in enumerate(row) if c == "#"}
    cx, cy = len(rows[0]) / 2, 11 / 2
    st = [(i + 0.5) / s for i in range(s)]
    ds = [-depth / 2 + (i + 0.5) * depth / (s * depth) for i in range(s * depth)]
    pts = []
    for x, y in px:
        X, Y = x - cx, cy - y  # voxel spans X..X+1, Y-1..Y (bitmap y grows down, world y grows up)
        for a in st:
            for b in st:
                pts.append((X + a, Y - b, -depth / 2, 0, 0, -1))
                pts.append((X + a, Y - b, depth / 2, 0, 0, 1))
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if (x + dx, y + dy) in px:
                continue
            for a in st:
                for d in ds:
                    if dx:
                        pts.append((X + (dx > 0), Y - a, d, dx, 0, 0))
                    else:
                        pts.append((X + a, Y - (dy > 0), d, 0, -dy, 0))
    return pts


def render(pts, ay, ax, C, R, K=214, z0=75, aspect=9 / 5.4):
    ca, sa, cb, sb = math.cos(ay), math.sin(ay), math.cos(ax), math.sin(ax)
    px_, py_, pz_ = -22, 16, -30  # point light, upper-left in front, so shading slides across faces as they turn
    zbuf = [[0.0] * C for _ in range(R)]
    out = [[" "] * C for _ in range(R)]
    for x, y, z, nx, ny, nz in pts:
        x1, z1 = x * ca + z * sa, -x * sa + z * ca
        n1x, n1z = nx * ca + nz * sa, -nx * sa + nz * ca
        y2, z2 = y * cb - z1 * sb, y * sb + z1 * cb
        n2y, n2z = ny * cb - n1z * sb, ny * sb + n1z * cb
        ooz = 1 / (z2 + z0)
        col, row = int(C / 2 + K * x1 * ooz), int(R / 2 - K * y2 * ooz / aspect)
        if 0 <= col < C and 0 <= row < R and ooz > zbuf[row][col]:
            zbuf[row][col] = ooz
            lx, ly, lz = px_ - x1, py_ - y2, pz_ - z2
            lum = (n1x * lx + n2y * ly + n2z * lz) / math.sqrt(lx * lx + ly * ly + lz * lz)
            out[row][col] = RAMP[min(11, int(lum ** 1.6 * 13))] if lum > 0 else "."
    return ["".join(r) for r in out]


def banner():
    W, H, C, R, N, T, cw, lh = 900, 384, 160, 32, 60, 6, 5.4, 9
    x0, y0 = (W - C * cw) / 2, 38
    pts = voxel_points("ZAAC")
    frames = []
    for i in range(N):
        t = 2 * math.pi * i / N
        ay, ax = 0.7 * math.sin(t), 0.2 * math.sin(2 * t)
        rows = []
        for r, line in enumerate(render(pts, ay, ax, C, R)):
            body = line.strip()
            if body:
                lead = len(line) - len(line.lstrip())
                rows.append(pinned(round(x0 + lead * cw, 1), y0 + r * lh + 7, body, cw, ""))
        hud = f"θy {math.degrees(ay):+06.1f}°  θx {math.degrees(ax):+05.1f}°  frame {i + 1:02d}/{N}"
        rows.append(f'<text class="hud" x="{W - 20}" y="{H - 16}" text-anchor="end">{hud}</text>')
        frames.append(f'<g class="fr fr{i}" style="animation-delay:{i * T / N:.2f}s">{"".join(rows)}</g>')

    sub = "> no webgl. no libraries. just math and characters."
    sx = (W - len(sub) * 9.6) / 2
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">ZAAC</title>
<desc id="d">The word ZAAC as a 3D object, rendered frame by frame into ASCII characters, swinging in space. no webgl. no libraries. just math and characters.</desc>
<style>{BASE_CSS}
.fr {{ opacity: 0; animation: fr {T}s step-end infinite; font-size: 9px; }}
@keyframes fr {{ 0% {{ opacity: 1; }} {100 / N:.4f}% {{ opacity: 0; }} 100% {{ opacity: 0; }} }}
.obj {{ fill: url(#gg); filter: url(#glow); }}
.scan {{ animation: scan 7s linear infinite; }}
@keyframes scan {{ from {{ transform: translateY(-60px); }} to {{ transform: translateY({H}px); }} }}
.hud {{ font-size: 12px; fill: {DIM}; }} .sub {{ font-size: 16px; fill: {FG}; }}
</style>
<defs>
<clipPath id="win"><rect width="{W}" height="{H}" rx="10"/></clipPath>
<filter id="glow" x="-5%" y="-10%" width="110%" height="120%"><feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<linearGradient id="gg" gradientUnits="userSpaceOnUse" x1="0" y1="{y0}" x2="0" y2="{y0 + R * lh}"><stop offset="0" stop-color="#b4ffbf"/><stop offset=".5" stop-color="{G}"/><stop offset="1" stop-color="#1a7f37"/></linearGradient>
<linearGradient id="sb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset=".5" stop-color="{G}" stop-opacity=".06"/><stop offset="1" stop-color="{G}" stop-opacity="0"/></linearGradient>
<pattern id="sl" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".3"/></pattern>
</defs>
<g clip-path="url(#win)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<g class="obj">{"".join(frames)}</g>
{typed("sub", round(sx, 1), H - 46, sub, 9.6, 0.6, 2.2, "sub")}
{show(2.8, f'<rect class="cur" x="{sx + len(sub) * 9.6 + 4:.1f}" y="{H - 60}" width="9" height="18" fill="{G}"/>')}
<text class="hud" x="20" y="26">zaac.c — software rasterizer → ascii</text>
<text class="hud" x="{W - 20}" y="26" text-anchor="end">sys.status: ONLINE <tspan class="g cur">●</tspan></text>
<text class="hud" x="20" y="{H - 16}">{len(pts):,} points · z-buffer · lambert</text>
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
    # self-check: the unrotated render must contain lit front faces and stay inside the frame
    flat = render(voxel_points("ZAAC"), 0, 0, 160, 32)
    assert any(c in "".join(flat) for c in "#$@") and not flat[0].strip() and not flat[-1].strip()
    for name, svg in (("banner", banner()), ("terminal", terminal())):
        open(f"assets/{name}.svg", "w", encoding="utf-8").write(svg)
        print(name, len(svg.encode()), "bytes")
