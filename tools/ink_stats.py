"""Draws profile/ink-stats.svg: one paper card with GitHub numbers and WakaTime languages.

Replaces the three github-readme-stats cards so colours and layout match the banner.
Runs daily in .github/workflows/stats.yml; GH_TOKEN (optional) lifts the API rate limit
and lets search count commits in private repos the token can see.

    python tools/ink_stats.py
"""
import json
import os
import urllib.request
from pathlib import Path

USER = "phoenixak"
WAKA_USER = "phoenixak"
OUT = Path(__file__).resolve().parent.parent / "profile" / "ink-stats.svg"

PAPER, INK, SOFT, MUTED, LINE, RED = "#F4F1EA", "#141310", "#4A463F", "#6B665C", "#DDD6C8", "#C2341B"
LANG_INK = [INK, RED, "#5C574E", "#8F887A", "#B5AE9F", "#D6CFC1"]
NOT_CODE = {"Markdown", "Other", "Text", "JSON", "YAML", "TOML", "CSV", "INI", "XML", "Git Config", "Image (svg)"}
SERIF = "'Shippori Mincho', 'Hiragino Mincho ProN', Georgia, 'Times New Roman', serif"
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Consolas, monospace"


def get(url, token=None):
    req = urllib.request.Request(url, headers={"User-Agent": "phoenixak-ink-stats", "Accept": "application/vnd.github+json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def graphql(token, query):
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": query}).encode(),
                                 headers={"User-Agent": "phoenixak-ink-stats", "Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]


def all_commits(token):
    # every year's commits, private ones included (what the old card's count_private showed)
    years = graphql(token, f'{{user(login:"{USER}"){{contributionsCollection{{contributionYears}}}}}}')
    years = years["user"]["contributionsCollection"]["contributionYears"]
    parts = " ".join(f'y{y}:contributionsCollection(from:"{y}-01-01T00:00:00Z",to:"{y}-12-31T23:59:59Z")'
                     f'{{totalCommitContributions restrictedContributionsCount}}' for y in years)
    data = graphql(token, f'{{user(login:"{USER}"){{{parts}}}}}')["user"]
    return sum(c["totalCommitContributions"] + c["restrictedContributionsCount"] for c in data.values())


def github(token):
    api = "https://api.github.com"
    repos = get(f"{api}/users/{USER}/repos?per_page=100&type=owner", token)
    commits = get(f"{api}/search/commits?q=author:{USER}&per_page=1", token)["total_count"]
    if token:
        commits = max(commits, all_commits(token))
    return [
        ("Commits", commits),
        ("Stars", sum(r["stargazers_count"] for r in repos if not r["fork"])),
        ("Pull requests", get(f"{api}/search/issues?q=author:{USER}+type:pr&per_page=1", token)["total_count"]),
        ("Issues", get(f"{api}/search/issues?q=author:{USER}+type:issue&per_page=1", token)["total_count"]),
    ]


def wakatime():
    d = get(f"https://wakatime.com/api/v1/users/{WAKA_USER}/stats")["data"]
    langs = [l for l in d["languages"] if l["name"] not in NOT_CODE][:6]
    total = sum(l["total_seconds"] for l in langs) or 1
    hours = round(d["total_seconds"] / 3600)
    return hours, [(l["name"], l["total_seconds"] / total * 100) for l in langs]


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(stats, hours, langs):
    W, H = 840, 236
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub and WakaTime stats">',
           f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{PAPER}" stroke="{LINE}"/>']

    # left: four numbers, 2 x 2
    out.append(f'<text x="36" y="44" font-family="{MONO}" font-size="11" letter-spacing="1.6" fill="{MUTED}">GITHUB</text>')
    for i, (label, n) in enumerate(stats):
        x, y = 36 + (i % 2) * 180, 104 + (i // 2) * 84
        out.append(f'<text x="{x}" y="{y}" font-family="{SERIF}" font-size="38" font-weight="700" fill="{INK}">{n:,}</text>')
        out.append(f'<text x="{x + 1}" y="{y + 22}" font-family="{MONO}" font-size="11" letter-spacing="1.2" fill="{MUTED}">{esc(label.upper())}</text>')

    # ink divider
    out.append(f'<path d="M412 34 C 414 90, 410 150, 413 202" stroke="{INK}" stroke-opacity=".18" stroke-width="2" fill="none" stroke-linecap="round"/>')

    # right: coding time and language bar
    x0, bw = 448, 356
    out.append(f'<text x="{x0}" y="44" font-family="{MONO}" font-size="11" letter-spacing="1.6" fill="{MUTED}">CODING TIME · WAKATIME</text>')
    out.append(f'<text x="{x0}" y="92" font-family="{SERIF}" font-size="38" font-weight="700" fill="{RED}">{hours:,}<tspan font-size="18" fill="{SOFT}" dx="8">hours</tspan></text>')
    out.append(f'<clipPath id="bar"><rect x="{x0}" y="112" width="{bw}" height="10" rx="5"/></clipPath><g clip-path="url(#bar)">')
    x = x0
    for i, (_, pct) in enumerate(langs):
        w = bw * pct / 100
        out.append(f'<rect x="{x:.1f}" y="112" width="{w + .6:.1f}" height="10" fill="{LANG_INK[i]}"/>')
        x += w
    out.append('</g>')
    for i, (name, pct) in enumerate(langs):
        lx, ly = x0 + (i % 2) * 180, 154 + (i // 2) * 24
        out.append(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{LANG_INK[i]}"/>')
        out.append(f'<text x="{lx + 18}" y="{ly}" font-family="{MONO}" font-size="12" fill="{INK}">{esc(name)} <tspan fill="{MUTED}">{pct:.0f}%</tspan></text>')

    out.append('</svg>')
    return "\n".join(out) + "\n"


def main():
    token = os.environ.get("GH_TOKEN") or None
    stats = github(token)
    hours, langs = wakatime()
    OUT.write_text(svg(stats, hours, langs), encoding="utf-8", newline="\n")
    print(OUT.name, stats, hours, [(n, round(p)) for n, p in langs])


if __name__ == "__main__":
    main()
