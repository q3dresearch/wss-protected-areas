#!/usr/bin/env python3
"""Render charts from derived/observations/*.csv.gz as SVG.

    python examples/visualize.py

  the-only-release.svg      what Protected Planet still serves, and what it has
                            already deleted — the case for this repository
  count-or-area.svg         territories plotted both ways at once. Counting
                            sites and measuring area produce different worlds
  where-the-area-is.svg     IUCN category by count and by km². The smallest
                            categories hold the most planet
  the-weight-of-a-realm.svg 2.1% of the sites hold 57.4% of the planet
  one-row-away.svg          the countries whose protected estate is mostly a
                            single site
  cannot-be-weighed.svg     the countries whose rows cannot be aged or measured
                            even while they are present

Reads the derived table, never the raw archive. Stdlib only, deterministic
output: the same observations always produce the same bytes.
"""

from __future__ import annotations

import collections
import csv
import gzip
import io
import math
from pathlib import Path
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "examples" / "charts"

# Validated reference palette, shared with the rest of the fleet.
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
HUE = "#2a78d6"
HUE_SOFT = "#9ec5f4"
ACCENT = "#eb6834"
DEAD = "#b8b6ad"
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'

# Every one of these was fetched on 2026-09-11, twice: once under /current/ and
# once under its own month prefix. Only the current month answers, at either
# path. These are recorded results, not an assumed pattern.
RELEASE_PROBE = [
    ("Sep 2026", 200), ("Aug 2026", 404), ("Jul 2026", 404),
    ("Jun 2026", 404), ("May 2026", 404), ("Apr 2026", 404),
    ("Mar 2026", 404), ("Feb 2026", 404), ("Jan 2026", 404),
]

ISO_NAME = {
    "USA": "United States", "SWE": "Sweden", "DEU": "Germany", "EST": "Estonia",
    "FIN": "Finland", "CAN": "Canada", "GBR": "United Kingdom", "AUS": "Australia",
    "CHE": "Switzerland", "NZL": "New Zealand", "RUS": "Russia", "UKR": "Ukraine",
    "FRA": "France", "BRA": "Brazil", "COK": "Cook Islands", "CHL": "Chile",
    "MEX": "Mexico", "ABNJ": "High seas (ABNJ)", "NGA": "Nigeria",
    "IDN": "Indonesia", "TZA": "Tanzania", "LTU": "Lithuania", "ALB": "Albania",
    "HRV": "Croatia", "ITA": "Italy", "IRL": "Ireland", "HUN": "Hungary",
    "SVN": "Slovenia", "MYS": "Malaysia", "ESP": "Spain", "NOR": "Norway",
    "ZMB": "Zambia", "LKA": "Sri Lanka", "KIR": "Kiribati", "NIU": "Niue",
    "DNK": "Denmark", "CAF": "Central African Rep.", "PLW": "Palau",
    "CRI": "Costa Rica", "PAN": "Panama", "SYC": "Seychelles",
    "ZAF": "South Africa", "PRT": "Portugal", "NER": "Niger", "DZA": "Algeria",
    "BEL": "Belgium", "JPN": "Japan", "VEN": "Venezuela", "ARG": "Argentina",
    "COL": "Colombia", "SJM": "Svalbard & Jan Mayen", "FSM": "Micronesia",
    "MCO": "Monaco", "SGP": "Singapore", "GUY": "Guyana", "LBY": "Libya",
    "ROU": "Romania", "LVA": "Latvia", "NLD": "Netherlands", "POL": "Poland",
    "CZE": "Czechia", "AUT": "Austria", "SVK": "Slovakia", "BGR": "Bulgaria",
}

IUCN_LABEL = {
    "Ia": "Ia  strict nature reserve", "Ib": "Ib  wilderness area",
    "II": "II  national park", "III": "III  natural monument",
    "IV": "IV  habitat management", "V": "V  protected landscape",
    "VI": "VI  sustainable use", "Not Reported": "Not Reported",
    "Not Assigned": "Not Assigned", "Not Applicable": "Not Applicable",
}


def _open(path: Path):
    if str(path).endswith(".gz"):
        return io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8", newline="")
    return open(path, encoding="utf-8", newline="")


def load():
    """(sites, countries, iucn, feed) — each {entity: {metric: value}}."""
    sites = collections.defaultdict(dict)
    countries = collections.defaultdict(dict)
    iucn = collections.defaultdict(dict)
    realms = collections.defaultdict(dict)
    feed = collections.defaultdict(dict)
    for part in sorted((REPO / "derived" / "observations").glob("*.csv*")):
        with _open(part) as fh:
            for r in csv.DictReader(fh):
                eid, metric, value = r["entity_id"], r["metric"], r["value"]
                if eid.startswith("pa:"):
                    sites[eid][metric] = value
                elif eid.startswith("country:"):
                    countries[eid[8:]][metric] = value
                elif eid.startswith("iucn:"):
                    iucn[eid[5:]][metric] = value
                elif eid.startswith("realm:"):
                    realms[eid[6:]][metric] = value
                else:
                    feed[eid][metric] = value
    return sites, countries, iucn, realms, feed


def territories(countries: dict) -> dict:
    """Only real single-country codes.

    PRNT_ISO3 holds 222 values and 25 are joint designations like
    "FRA;ITA;MCO" -- 28 sites between them. Treating those as countries makes
    22 of them look like territories holding exactly one protected area, which
    is nonsense: France holds 7,464. ABNJ (the high seas) is excluded for the
    same reason and named separately wherever it matters.
    """
    return {iso: m for iso, m in countries.items() if m.get("is_territory") == "yes"}


def T(x, y, text, size=12, fill=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family=\'{FONT}\' font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{escape(str(text))}</text>')


def R(x, y, w, h, fill, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" '
            f'height="{max(h, 0):.1f}" fill="{fill}" rx="{rx}"/>')


def C(cx, cy, r, fill, stroke=SURFACE, width=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{width}"/>')


def L(x1, y1, x2, y2, stroke=GRID, width=1, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}"{d}/>')


def head(w, h, title, sub, note=""):
    """`note` may be a string or a list of lines. SVG does not wrap text, so
    the caller breaks its own lines."""
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}">', R(0, 0, w, h, SURFACE),
         T(56, 48, title, 20, INK, weight="600"),
         T(56, 74, sub, 13, INK2)]
    lines = [note] if isinstance(note, str) else list(note)
    for i, line in enumerate(l for l in lines if l):
        p.append(T(56, 96 + i * 16, line, 12, MUTED))
    return p


def save(parts, name, w, h):
    OUT.mkdir(parents=True, exist_ok=True)
    svg = "\n".join(parts) + "\n</svg>\n"
    # Parse before writing. Two invalid SVGs have shipped from this fleet, both
    # from quoting mistakes that a browser hides and a parser does not.
    import xml.etree.ElementTree as ET
    ET.fromstring(svg)
    (OUT / name).write_text(svg, encoding="utf-8")
    print(f"  wrote examples/charts/{name}")


def km2(v) -> str:
    v = float(v)
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M km²"
    if v >= 1000:
        return f"{v/1000:,.0f}k km²"
    if v >= 10:
        return f"{v:,.0f} km²"
    if v >= 0.1:
        # Monaco's two sites total 0.2 km². Rounding that to "0 km²" would
        # print a zero next to a bar that is visibly not zero.
        return f"{v:.1f} km²"
    return f"{v:.2f} km²"


def name_of(iso: str) -> str:
    return ISO_NAME.get(iso, iso)


# --- charts ---------------------------------------------------------------

def chart_only_release(feed):
    """The case for the repository, drawn as what answers and what does not."""
    w, h = 940, 470
    p = head(w, h, "Nine months of the World Database on Protected Areas, asked for",
             "Every release lives at the same /current/ path. Only one of them is still there.",
             ["Each bar is one HTTP request made on 2026-09-11 to "
              "d1gam3xoknrgr2.cloudfront.net/current/WDPA_<month>_Public_csv.zip,",
              "and to the same filename under its own month prefix. Earlier "
              "releases are available on request — by email, from UNEP-WCMC."])
    x0, y0 = 210, 160
    row = 24
    for i, (label, status) in enumerate(RELEASE_PROBE):
        y = y0 + i * row
        live = status == 200
        p.append(T(x0 - 14, y + 11, label, 12, INK if live else MUTED, anchor="end",
                   weight="600" if live else "normal"))
        bw = 470 if live else 120
        p.append(R(x0, y, bw, 15, HUE if live else DEAD, rx=4))
        p.append(T(x0 + bw + 10, y + 11, "200 — 23,820,193 bytes" if live else "404",
                   12, INK if live else MUTED, weight="600" if live else "normal"))
    p.append(T(56, y0 + len(RELEASE_PROBE) * row + 34,
               "One month of the world's protected areas exists at a time. "
               "The other eight were published and are gone.",
               13, INK, weight="600"))
    sites = int(feed["feed:wdpa"]["sites_listed"])
    area = float(feed["feed:wdpa"]["area_listed_total"])
    p.append(T(56, y0 + len(RELEASE_PROBE) * row + 56,
               f"The surviving release holds {sites:,} sites and {area:,.0f} km². "
               f"Nothing in it records what left.", 12, INK2))
    save(p, "the-only-release.svg", w, h)


def chart_count_or_area(countries):
    """Two encodings of the same territories, because they disagree."""
    w, h = 940, 660
    terr = territories(countries)
    p = head(w, h, "Counting protected areas and measuring them are different questions",
             "Each bubble is one of 196 territories: how many sites it lists, "
             "against how much of the planet they cover.",
             ["Both axes are logarithmic; the spread is five orders of magnitude. "
              "A departure counted as one site in 312,943 says nothing, and the",
              "same departure measured in km\u00b2 is the finding. Blue labels are the "
              "ten largest by area. Orange is the three territories with the most",
              "sites per square kilometre — large records, small estates. Joint "
              "designations and the high seas are excluded."])
    L_, Rr, Tp, Bt = 160, 880, 190, 540
    pts = []
    for iso, m in terr.items():
        n = float(m.get("sites_listed", 0))
        a = float(m.get("area_listed", 0))
        if n > 0 and a > 0:
            pts.append((iso, n, a))
    xs = [math.log10(n) for _, n, _ in pts]
    ys = [math.log10(a) for _, _, a in pts]
    xlo, xhi = math.floor(min(xs)), math.ceil(max(xs))
    ylo, yhi = math.floor(min(ys)), math.ceil(max(ys))
    px = lambda n: L_ + (math.log10(n) - xlo) / (xhi - xlo) * (Rr - L_)
    py = lambda a: Bt - (math.log10(a) - ylo) / (yhi - ylo) * (Bt - Tp)

    for e in range(xlo, xhi + 1):
        x = px(10 ** e)
        p.append(L(x, Tp, x, Bt))
        p.append(T(x, Bt + 20, f"{10**e:,}", 11, MUTED, anchor="middle"))
    for e in range(ylo, yhi + 1):
        y = py(10 ** e)
        p.append(L(L_, y, Rr, y))
        p.append(T(L_ - 12, y + 4, km2(10 ** e), 11, MUTED, anchor="end"))
    p.append(L(L_, Bt, Rr, Bt, BASELINE, 2))
    p.append(L(L_, Tp, L_, Bt, BASELINE, 2))
    p.append(T(L_, Bt + 42, "sites listed (log scale)", 12, INK2))
    p.append(T(L_ - 12, Tp - 16, "reported area (log scale)", 12, INK2, anchor="end"))

    by_area = [t[0] for t in sorted(pts, key=lambda t: -t[2])[:10]]
    # Dense records over small estates: the argument for weighting by area.
    dense = [t[0] for t in sorted((t for t in pts if t[1] >= 1000),
                                  key=lambda t: t[2] / t[1])[:3]]
    # Sweden and the Cook Islands are the pair the caption argues over, so they
    # are labelled whether or not they fall out of the two rules above.
    label = set(by_area) | set(dense) | {"SWE", "COK"}

    for iso, n, a in sorted(pts, key=lambda t: -t[2]):
        r = 7 if iso in label else 4
        fill = ACCENT if iso in dense else (HUE if iso in label else HUE_SOFT)
        p.append(C(px(n), py(a), r, fill))
    # Labels, placed by trying eight offsets and taking the first that clears
    # everything already placed. SVG has no collision handling, and the first
    # draft overlapped Germany with Sweden and Russia with Canada.
    placed = []
    OFFSETS = [(0, -14), (0, 22), (14, 4), (-14, 4), (0, -26), (0, 34), (26, -10), (-26, -10)]
    for iso, n, a in sorted(pts, key=lambda t: -t[2]):
        if iso not in label:
            continue
        x, y = px(n), py(a)
        text = name_of(iso)
        half = 3.4 * len(text)
        for ox, oy in OFFSETS:
            lx, ly = x + ox, y + oy
            anchor = "middle"
            if ox > 0:
                anchor, lx = "start", x + 11
            elif ox < 0:
                anchor, lx = "end", x - 11
            left = lx - (half if anchor == "middle" else (0 if anchor == "start" else 2 * half))
            if left < 56 or left + 2 * half > w - 20:
                continue
            if all(abs(pl - left) > 2 * half or abs(pt - ly) > 13
                   for pl, pt, _ in placed):
                break
        p.append(T(lx, ly, text, 11, INK, anchor=anchor, weight="600"))
        placed.append((left, ly, text))

    swe = next((t for t in pts if t[0] == "SWE"), None)
    cok = next((t for t in pts if t[0] == "COK"), None)
    if swe and cok:
        p.append(T(56, 604,
                   f"Sweden lists {swe[1]:,.0f} sites covering {swe[2]:,.0f} km\u00b2. "
                   f"The Cook Islands lists {cok[1]:,.0f}, covering {cok[2]:,.0f} km\u00b2.",
                   13, INK, weight="600"))
        p.append(T(56, 626,
                   f"By count Sweden is {swe[1]/cok[1]:,.0f}\u00d7 the larger record. "
                   f"By area the Cook Islands is {cok[2]/swe[2]:.0f}\u00d7 the larger loss. "
                   f"Only one of those numbers is a fact about protection.",
                   12, INK2))
    save(p, "count-or-area.svg", w, h)


def chart_where_area_is(iucn):
    """IUCN category: the smallest counts hold the most planet."""
    w, h = 940, 590
    p = head(w, h, "The smallest IUCN categories hold the most planet",
             "Every protected area carries a management category. Sites and area "
             "rank it almost in reverse.",
             ["Two bars per category, each scaled to its own maximum — the "
              "question is the ORDERING, not a shared magnitude.",
              "Category VI is sustainable-use protected area: the weakest "
              "protection class, and the largest by area."])
    rows = sorted(iucn.items(), key=lambda kv: -float(kv[1].get("area_listed", 0)))
    max_n = max(float(m.get("sites_listed", 0)) for _, m in rows)
    max_a = max(float(m.get("area_listed", 0)) for _, m in rows)
    # The count bar tops out at 230px and its value label needs ~60px after it,
    # so the area group cannot start before x0+300 without the two colliding --
    # which is exactly what the first draft did to category IV ("95,6").
    x0, y0, row = 244, 182, 32
    bar_n, bar_a, gap = 230, 250, 310
    p.append(T(x0, y0 - 14, "sites listed", 11, MUTED))
    p.append(T(x0 + gap, y0 - 14, "reported area", 11, MUTED))
    for i, (cat, m) in enumerate(rows):
        y = y0 + i * row
        n = float(m.get("sites_listed", 0))
        a = float(m.get("area_listed", 0))
        p.append(T(x0 - 14, y + 12, IUCN_LABEL.get(cat, cat), 12, INK, anchor="end"))
        p.append(R(x0, y, bar_n * n / max_n, 16, HUE_SOFT, rx=4))
        p.append(T(x0 + bar_n * n / max_n + 8, y + 12, f"{n:,.0f}", 11, INK2))
        p.append(R(x0 + gap, y, bar_a * a / max_a, 16, HUE, rx=4))
        p.append(T(x0 + gap + bar_a * a / max_a + 8, y + 12, km2(a), 11, INK2))
    vi = iucn.get("VI", {})
    iv = iucn.get("IV", {})
    if vi and iv:
        p.append(T(56, y0 + len(rows) * row + 30,
                   f"Category VI is {float(vi['sites_listed']):,.0f} sites — "
                   f"{float(iv['sites_listed'])/float(vi['sites_listed']):.1f}× fewer than "
                   f"category IV — and {float(vi['area_listed'])/float(iv['area_listed']):.1f}× "
                   f"its area.", 13, INK, weight="600"))
        p.append(T(56, y0 + len(rows) * row + 50,
                   "Ranking departures by site count would report the loss of the "
                   "planet's largest protected estate as a rounding error.",
                   12, INK2))
    save(p, "where-the-area-is.svg", w, h)


def chart_realm_weight(realms, feed):
    """2.1% of the sites hold 57.4% of the planet. Two stacked shares, one row."""
    w, h = 940, 560
    total_n = int(feed["feed:wdpa"]["sites_listed"])
    total_a = float(feed["feed:wdpa"]["area_listed_total"])
    order = ["marine", "coastal", "terrestrial"]
    colour = {"marine": HUE, "coastal": ACCENT, "terrestrial": HUE_SOFT}
    rows = [(k, int(realms[k]["sites_listed"]), float(realms[k]["area_listed"]))
            for k in order if k in realms]
    p = head(w, h, "2.1% of protected areas hold 57.4% of the protected planet",
             "WDPA labels every site Marine, Coastal or Terrestrial. Counting "
             "sites and measuring them give opposite answers.",
             ["Both bars are the same 312,943 sites and the same 75,626,603 km2, "
              "split by the source's own REALM column.",
              "Coastal is a real third category and not a rounding of the other "
              "two: at 225 km2 a coastal site is nearer a terrestrial one."])
    x0, bar = 210, 640
    for i, (label, field, total) in enumerate((("by site count", 1, total_n),
                                               ("by reported area", 2, total_a))):
        y = 190 + i * 110
        p.append(T(x0 - 14, y + 26, label, 13, INK, anchor="end", weight="600"))
        x = x0
        for key, n, a in rows:
            v = (n if field == 1 else a)
            seg = bar * v / total
            p.append(R(x, y, max(seg - 2, 1), 40, colour[key], rx=4))
            if seg > 56:
                p.append(T(x + seg / 2 - 1, y + 25, f"{v/total:.1%}", 12, SURFACE,
                           anchor="middle", weight="600"))
            else:
                # Marine and Coastal are 2.1% and 3.3% of the count bar and their
                # labels overlapped at every width tried. Stagger them.
                dy = -8 if key == "marine" else -24
                p.append(T(x + seg / 2 - 1, y + dy, f"{v/total:.1%}", 11, colour[key],
                           anchor="middle", weight="600"))
                p.append(L(x + seg / 2 - 1, y + dy + 4, x + seg / 2 - 1, y,
                           colour[key], 1))
            x += seg
        p.append(T(x0, y + 60,
                   "   ·   ".join(f"{k.title()} {(n if field==1 else a):,.0f}"
                                  + ("" if field == 1 else " km\u00b2")
                                  for k, n, a in rows), 11, MUTED))
    ly = 190 + 2 * 110 + 40
    for i, (key, n, a) in enumerate(rows):
        x = x0 + i * 230
        p.append(R(x, ly, 14, 14, colour[key], rx=3))
        p.append(T(x + 22, ly + 12, f"{key.title()}", 12, INK, weight="600"))
        p.append(T(x + 22, ly + 28, f"mean {a/n:,.0f} km\u00b2", 11, MUTED))
    mar = next(r for r in rows if r[0] == "marine")
    ter = next(r for r in rows if r[0] == "terrestrial")
    p.append(T(56, ly + 74,
               f"The average marine site is {(mar[2]/mar[1])/(ter[2]/ter[1]):.0f}\u00d7 "
               f"the average terrestrial one.", 13, INK, weight="600"))
    p.append(T(56, ly + 96,
               "A departure counted as one site in 312,943 is not a measurement. "
               "Which realm it was in decides what was lost.", 12, INK2))
    save(p, "the-weight-of-a-realm.svg", w, h)


def chart_one_row_away(countries, sites):
    """The honest fragility measure: how much of a country is one site."""
    w, h = 940, 700
    terr = territories(countries)
    names = {eid: m.get("name", "") for eid, m in sites.items() if m.get("name")}
    rows = []
    for iso, m in terr.items():
        total = float(m.get("area_listed", 0))
        share = float(m.get("top_site_share", 0))
        if total >= 100_000 and share > 0:
            rows.append((iso, int(float(m["sites_listed"])), total, share,
                         names.get(m.get("top_site", ""), "")))
    rows.sort(key=lambda r: -r[3])
    rows = rows[:14]
    p = head(w, h, "Most of a country's protection can be one row",
             "Share of each territory's reported protected area held by its "
             "single largest site. Territories covering 100,000 km\u00b2 or more.",
             ["Site COUNT hides this completely: Denmark lists 1,173 protected "
              "areas and 91% of its area is one of them.",
              "The named site on each bar is the one whose disappearance would "
              "take that share of the country's protected estate with it."])
    x0, y0, row = 214, 196, 30
    for i, (iso, n, total, share, top) in enumerate(rows):
        y = y0 + i * row
        p.append(T(x0 - 14, y + 11, name_of(iso), 12, INK, anchor="end", weight="600"))
        p.append(T(x0 - 14, y + 24, f"{n:,} sites  ·  {km2(total)}", 10, MUTED, anchor="end"))
        p.append(R(x0, y, 420, 16, GRID, rx=4))
        p.append(R(x0, y, 420 * share, 16, ACCENT if share >= 0.8 else HUE, rx=4))
        p.append(T(x0 + 430, y + 12, f"{share:.0%}", 12, INK, weight="600"))
        # WDPA truncates NAME itself -- Greenland's park arrives as
        # "Nationalparken i Nord- og Østg", 30 characters. Do not make it worse.
        p.append(T(x0 + 468, y + 12, top[:44], 11, INK2))
    p.append(T(56, y0 + len(rows) * row + 30,
               "Orange is a territory where four fifths or more of everything it "
               "protects is a single site in a single monthly file.",
               13, INK, weight="600"))
    p.append(T(56, y0 + len(rows) * row + 52,
               "Nothing published today would tell any of these countries that "
               "the row had stopped appearing.", 12, INK2))
    save(p, "one-row-away.svg", w, h)


def chart_cannot_be_weighed(sites, countries):
    """Present, and still unusable: the rows with no area and no year."""
    w, h = 940, 630
    real = set(territories(countries))
    per = collections.defaultdict(lambda: [0, 0, 0])
    for eid, m in sites.items():
        iso = m.get("country", "unknown")
        if iso not in real:
            continue
        per[iso][0] += 1
        if float(m.get("area_listed", 0)) == 0:
            per[iso][1] += 1
    big = [(iso, v) for iso, v in per.items() if v[0] >= 500]
    rows = sorted(big, key=lambda kv: -kv[1][1] / kv[1][0])[:12]
    p = head(w, h, "Present in the file, and still impossible to weigh",
             "Share of each territory's sites reporting no area at all. "
             "Territories with at least 500 sites.",
             ["A site with REP_AREA of zero can be observed leaving and cannot "
              "be measured when it does. It is presence without a denominator.",
              "Across the whole database this is "
              f"{sum(v[1] for v in per.values()):,} of "
              f"{sum(v[0] for v in per.values()):,} sites."])
    x0, y0, row = 250, 180, 28
    for i, (iso, (n, na, _)) in enumerate(rows):
        y = y0 + i * row
        share = na / n
        p.append(T(x0 - 14, y + 12, f"{name_of(iso)}", 12, INK, anchor="end"))
        p.append(T(x0 - 14, y + 24, f"{n:,} sites", 10, MUTED, anchor="end"))
        p.append(R(x0, y, 480, 16, GRID, rx=4))
        p.append(R(x0, y, 480 * share, 16, ACCENT if share > 0.5 else HUE, rx=4))
        p.append(T(x0 + 490, y + 12, f"{share:.0%}  ({na:,})", 11, INK2))
    worst = rows[0]
    p.append(T(56, y0 + len(rows) * row + 30,
               f"{name_of(worst[0])} reports no area for "
               f"{worst[1][1]/worst[1][0]:.0%} of its {worst[1][0]:,} sites.",
               13, INK, weight="600"))
    p.append(T(56, y0 + len(rows) * row + 50,
               "These rows are still worth capturing — presence is the "
               "observation — but they cannot be ranked against the rest.",
               12, INK2))
    save(p, "cannot-be-weighed.svg", w, h)


def main():
    sites, countries, iucn, realms, feed = load()
    if not sites:
        raise SystemExit("no observations — run `wss derive --parsers parsers.wdpa_site_v1` first")
    print(f"loaded {len(sites):,} sites, {len(countries)} territories, "
          f"{len(iucn)} IUCN categories")
    chart_only_release(feed)
    chart_count_or_area(countries)
    chart_where_area_is(iucn)
    chart_realm_weight(realms, feed)
    chart_one_row_away(countries, sites)
    chart_cannot_be_weighed(sites, countries)


if __name__ == "__main__":
    main()
