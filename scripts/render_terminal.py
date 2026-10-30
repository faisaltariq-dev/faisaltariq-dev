#!/usr/bin/env python3
"""Generate a self-contained GitHub-profile terminal SVG. Python stdlib only."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import sys
from urllib.request import Request, urlopen

USERNAME = "faisaltariq-dev"
OUT = Path(__file__).resolve().parents[1] / "assets" / "terminal-profile.svg"
API = "https://api.github.com"


def api(path: str):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "faisaltariq-profile-readme"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    with urlopen(Request(API + path, headers=headers), timeout=25) as response:
        return json.load(response)


def fetch_stats():
    user = api(f"/users/{USERNAME}")
    repos = []
    page = 1
    while True:
        chunk = api(f"/users/{USERNAME}/repos?per_page=100&type=owner&page={page}")
        repos.extend(r for r in chunk if r["owner"]["login"].lower() == USERNAME.lower())
        if len(chunk) < 100:
            break
        page += 1
    originals = [r for r in repos if not r["fork"] and not r["archived"]]
    languages = Counter()
    for repo in originals:
        # GitHub's language byte counts reflect code volume, not proficiency.
        languages.update(api(f"/repos/{USERNAME}/{repo['name']}/languages"))
    return {
        "repos": user["public_repos"],
        "stars": sum(r["stargazers_count"] for r in repos if not r["fork"]),
        "followers": user["followers"],
        "originals": len(originals),
        "languages": languages,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }


def build_svg(data):
    C = {"bg":"#07100e", "panel":"#0c1915", "panel2":"#0e211a", "border":"#244e3b", "green":"#57f49d", "muted":"#8ba99a", "white":"#eefbf2", "cyan":"#74dbe9", "amber":"#ffcf75", "purple":"#b9a0ff"}
    p = []
    p.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" role="img" aria-labelledby="title desc">')
    p.append('<title id="title">Faisal: an agentic software developer terminal profile</title>')
    p.append('<desc id="desc">Terminal-inspired developer dashboard displaying GitHub statistics, focus areas, featured projects, and GitHub language breakdown.</desc>')
    p.append('''<defs>
      <linearGradient id="back" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#0b2018"/><stop offset="1" stop-color="#050a09"/></linearGradient>
      <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#57f49d"/><stop offset="1" stop-color="#5ecfda"/></linearGradient>
      <filter id="glow"><feGaussianBlur stdDeviation="11"/></filter>
      <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M 32 0 L 0 0 0 32" fill="none" stroke="#25533e" opacity="0.15"/></pattern>
    </defs>''')

    def box(x,y,w,h,fill=None,stroke=None,r=12,sw=1):
        p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill or C["panel"]}" stroke="{stroke or C["border"]}" stroke-width="{sw}"/>')

    def label(x,y,s,size=18,color=None,weight=500,anchor=None,opacity=None):
        opt = f' text-anchor="{anchor}"' if anchor else ''
        if opacity is not None: opt += f' opacity="{opacity}"'
        p.append(f'<text x="{x}" y="{y}" fill="{color or C["white"]}" font-size="{size}" font-weight="{weight}" font-family="DejaVu Sans Mono, Menlo, Consolas, monospace"{opt}>{escape(str(s))}</text>')

    def line(x1,y1,x2,y2,color=None,op=1,width=1):
        p.append(f'<path d="M {x1} {y1} L {x2} {y2}" stroke="{color or C["border"]}" stroke-width="{width}" opacity="{op}"/>')

    p.append('<rect width="1200" height="800" fill="url(#back)"/>')
    p.append('<rect width="1200" height="800" fill="url(#grid)"/>')
    p.append('<ellipse cx="1020" cy="110" rx="240" ry="180" fill="#1e8654" opacity="0.11" filter="url(#glow)"/>')
    box(17,17,1166,765,C["bg"],"#306e4f",19,2)
    p.append('<path d="M 18 80 H 1182" stroke="#306e4f"/>')
    for x,c in [(46,"#fc6a68"),(68,"#ffc860"),(90,"#4ed590")]:
        p.append(f'<circle cx="{x}" cy="48" r="8" fill="{c}"/>')
    label(135,54,"faisaltariq-dev / profile.sh",20,C["white"],600)
    label(1149,54,"● LIVE PROFILE",16,C["green"],650,"end")
    label(49,123,"➜  ~  $ neofetch --github --focus=agentic-systems",20,C["green"],600)
    box(45,147,405,334,C["panel"],"#2c6346")
    box(467,147,686,334,C["panel"],"#2c6346")
    label(70,182,"/usr/local/bin/identity",16,C["muted"],500)
    label(489,182,"SYSTEM INFORMATION",16,C["green"],650)

    # Original pixel-F mark with no fonts or external image dependencies.
    pattern = [
        '1111111111111',
        '1111111111111',
        '1110000000000',
        '1110000000000',
        '1111111111000',
        '1111111111000',
        '1110000000000',
        '1110000000000',
        '1110000000000',
        '1110000000000',
    ]
    for y,row in enumerate(pattern):
        for x,v in enumerate(row):
            if v == '1':
                color = C["cyan"] if (x+y)%7 == 0 else C["green"]
                p.append(f'<rect x="{112+x*17}" y="{207+y*17}" width="14" height="14" rx="2" fill="{color}" opacity="{0.75 + (x%4)*0.07:.2f}"/>')
    label(244,421,"FAISAL.T",21,C["white"],700,"middle")
    label(244,451,"ENGINEER  //  BUILDER",12,C["muted"],600,"middle")
    line(489,201,1131,201,C["border"])
    fields = [
        ("user", "Faisal"),
        ("handle", "@faisaltariq-dev"),
        ("role", "Computer Engineer / Developer"),
        ("focus", "Agents, RAG, backends, cloud"),
        ("principle", "Deterministic core + AI workflows"),
        ("based", "Saudi Arabia"),
        ("mode", "Building  •  Testing  •  Learning"),
    ]
    for i,(key,value) in enumerate(fields):
        y=234+i*31
        label(495,y,key,16,C["muted"],500)
        label(650,y,":",16,C["border"])
        label(670,y,value,16,C["white"] if i<5 else C["green"],550)
    line(489,460,1131,460,C["border"])

    # Actual GitHub statistics, never invented or hard-coded.
    cards=[("PUBLIC REPOS", data["repos"]),("SOURCE REPOS", data["originals"]),("TOTAL STARS", data["stars"]),("FOLLOWERS",data["followers"])]
    for i,(key,value) in enumerate(cards):
        x=45+i*280
        box(x,499,265,108,C["panel2"],"#2c6346")
        label(x+19,531,key,14,C["muted"],650)
        label(x+18,579,value,38,C["cyan"] if i==3 else C["green"],750)
        line(x+18,590,x+246,590,C["border"])
    box(45,625,735,117,C["panel"],"#2c6346")
    box(796,625,357,117,C["panel"],"#2c6346")
    label(66,651,"LANGUAGE FOOTPRINT",15,C["green"],700)
    label(814,651,"SIGNAL / NOISE",15,C["green"],700)
    language_colors=[C["green"],C["cyan"],C["purple"],C["amber"],"#fb9175"]
    lang_top=data["languages"].most_common(5)
    total=sum(data["languages"].values())
    if total:
        offset=0
        for i,(language,byte_count) in enumerate(lang_top):
            w=round((byte_count/total)*670)
            if w>0:
                p.append(f'<rect x="{66+offset}" y="667" width="{w}" height="16" rx="2" fill="{language_colors[i]}"/>')
            offset+=w
        for i,(language,byte_count) in enumerate(lang_top):
            x=68 + (i%3)*228
            y=709+(i//3)*23
            p.append(f'<circle cx="{x}" cy="{y-5}" r="5" fill="{language_colors[i]}"/>')
            label(x+12,y,f'{language} {byte_count/total:.0%}',13,C["white"])
    else:
        label(68,704,"No public language data available",16,C["muted"])
    label(815,688,"NAVIGATION  >",16,C["white"],650)
    label(815,713,"RETENTION",20,C["green"],750)
    label(815,731,"less collecting, more building",11,C["muted"])
    label(48,765,"github.com/faisaltariq-dev",13,C["muted"],550)
    label(1150,765,"SYNC " + data["updated"],12,C["muted"],500,"end")
    p.append('</svg>')
    return '\n'.join(p) + '\n'


def main():
    if "--preview" in sys.argv:
        # Layout-only preview, never used by the published Action.
        stats={"repos":"--", "originals":"--", "stars":"--", "followers":"--", "languages":Counter({"Python":35,"Go":25,"JavaScript":20,"Shell":10,"HTML":5}), "updated":"preview only"}
    else:
        stats=fetch_stats()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(build_svg(stats),encoding="utf-8")
    print(f"Generated {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
