"""Mounts Platane/snk's transparent contribution SVG on a paper card, like profile/ink-stats.svg.

    python tools/paper_snake.py dist/ink-snake.svg
"""
import re
import sys
from pathlib import Path

PAPER, LINE, MUTED = "#F4F1EA", "#DDD6C8", "#6B665C"
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Consolas, monospace"
PAD_X, PAD_TOP, PAD_BOTTOM = 24, 44, 8


def main(path):
    p = Path(path)
    s = p.read_text(encoding="utf-8")
    x, y, w, h = (float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split())
    x, y, w, h = x - PAD_X, y - PAD_TOP, w + 2 * PAD_X, h + PAD_TOP + PAD_BOTTOM
    s = re.sub(r'viewBox="[^"]+" width="[^"]+" height="[^"]+"',
               f'viewBox="{x:g} {y:g} {w:g} {h:g}" width="{w:g}" height="{h:g}"', s, count=1)
    card = (f'<rect x="{x + .5:g}" y="{y + .5:g}" width="{w - 1:g}" height="{h - 1:g}" rx="14" fill="{PAPER}" stroke="{LINE}"/>'
            f'<text x="{x + PAD_X + 12:g}" y="{y + 36:g}" font-family="{MONO}" font-size="11" letter-spacing="1.6" fill="{MUTED}">'
            f'CONTRIBUTIONS · THE LAST YEAR</text>')
    s = s.replace("</desc>", "</desc>" + card, 1) if "</desc>" in s else re.sub(r"(<svg[^>]*>)", r"\1" + card, s, count=1)
    p.write_text(s, encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
