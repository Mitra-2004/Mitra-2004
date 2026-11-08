#!/usr/bin/env python3
"""Keep GitHub contribution cells static and animate a snake through the gutters."""
from pathlib import Path
import re

ROOT = Path("dist")
FILES = (
    "github-contribution-grid-snake.svg",
    "github-contribution-grid-snake-dark.svg",
)

for filename in FILES:
    path = ROOT / filename
    source = path.read_text(encoding="utf-8")

    svg_match = re.search(r"<svg\b([^>]*)>", source)
    if not svg_match:
        raise SystemExit(f"Could not find SVG root in {path}")

    root_attrs = svg_match.group(1)
    cells = re.findall(r'<rect class="c(?: [a-z0-9]+)?"[^>]*/>', source)
    if not cells:
        raise SystemExit(f"Could not find contribution cells in {path}")

    style_match = re.search(r"<style>(.*?)</style>", source, re.S)
    style = style_match.group(1) if style_match else ""
    vars_match = re.search(r":root\{(.*?)\}", style)
    variables = vars_match.group(1) if vars_match else "--cb:#1b1f230a;--cs:#a855f7;--ce:#ebedf0;--c0:#ebedf0;--c1:#9be9a8;--c2:#40c463;--c3:#30a14e;--c4:#216e39"

    # Preserve every original contribution level, but remove the generator's
    # temporary cell-fading animation so no contribution ever disappears.
    cell_rules = re.findall(
        r"\.c\.([a-z0-9]+)\{fill:var\(--([a-z0-9]+)\);animation-name:[a-z0-9]+\}",
        style,
    )
    static_rules = "".join(f".c.{cls}{{fill:var(--{var})}}" for cls, var in cell_rules)

    route = "M16 16 H848 V32 H16 V48 H848 V64 H16 V80 H848 V96 H16"
    css = (
        f":root{{{variables}}}"
        ".c{shape-rendering:geometricPrecision;fill:var(--ce);stroke:var(--cb);stroke-width:1px}"
        + static_rules
        + ".trail{fill:none;stroke:#a855f7;stroke-linecap:round;stroke-linejoin:round}"
    )
    output = (
        f"<svg{root_attrs}>"
        f"<style>{css}</style>"
        + "".join(cells)
        + f'<path d="{route}" class="trail" stroke-width="5" opacity=".22"/>'
        + f'<path d="{route}" class="trail" stroke-width="2.4" stroke-dasharray="2 4">'
          '<animate attributeName="stroke-dashoffset" from="0" to="-12" dur="1s" repeatCount="indefinite"/>'
          '</path>'
        + f'<path id="snake-route" d="{route}" fill="none" stroke="none"/>'
        + '<circle r="3.4" fill="#c084fc" stroke="#7e22ce" stroke-width="1">'
          '<animateMotion dur="24s" repeatCount="indefinite" rotate="auto">'
          '<mpath href="#snake-route"/>'
          '</animateMotion></circle>'
        + "</svg>"
    )
    path.write_text(output, encoding="utf-8")
    print(f"Updated {path}: {len(cells)} contribution cells preserved")
