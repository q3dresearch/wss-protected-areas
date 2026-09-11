"""wdpa-site.v1 — every protected area on earth, and the ones that stop existing.

PRESENCE IS THE OBSERVATION. The WDPA status vocabulary has no exit. The whole
of it, September 2026: Designated 304,978 / Established 6,375 / Proposed 1,270 /
Inscribed 276 / Adopted 34 / Not Reported 10. No Degazetted, no Removed, no
Revoked. A protected area that is downgraded, downsized or degazetted does not
change status -- it stops appearing in next month's file. So every capture
records that each site WAS here, and a row that stops appearing is the only
evidence anything happened.

AND AREA IS THE POINT, NOT THE COUNT. The 314,766 rows collapse to 312,943
sites. Marine sites are 6,455 of those (2.1%) and 43,437,677 of 75,626,603 km2
(57.4%): an average marine site is 6,729 km2 against a terrestrial 101 km2, a
factor of 67. Sweden holds 32,959 sites totalling 264,641 km2; the Cook Islands
holds 3 totalling 2,278,077 km2. Counting departures would rank those
backwards, so `area_listed` carries the weight on the same row that carries the
presence.

REALM IS THE SOURCE'S OWN THREE-VALUE COLUMN, AND IT IS USED VERBATIM. The
first version of this parser derived a marine/terrestrial binary from
REP_M_AREA > 0 instead, and it was wrong twice over. It disagreed with WDPA's
own REALM label on 9,539 sites -- 2,492 sites WDPA calls Marine report no
marine area and 1,590 it calls Terrestrial report some -- and it collapsed
COASTAL, which is a real third category of 10,410 sites, into whichever side
happened to win. Coastal averages 225 km2 against Marine's 6,729 and
Terrestrial's 101, so it belongs with neither. REP_M_AREA still travels, as
`marine_area` -- how much of a site is sea is a different question from which
realm the site is in.

OBSERVED_AT IS THE RELEASE MONTH, NOT THE FETCH TIME. The file names its own
month -- WDPA_Sep2026_Public_csv.zip -- and that is the date the state was true.
Taking the fetch time instead would file a re-fetch of the September release
under October and invent a month of history that was never published.

THE IDENTIFIER RENAMED ITSELF. This release uses SITE_ID / SITE_PID. The
documented WDPA identifiers for years were WDPAID / WDPA_PID, and anything
written against the old names silently reads nothing. Both spellings are
accepted, and which one was found is recorded as an observation so a future
rename is dated to the month rather than discovered as an empty capture.

WHY NAMES ARE NOT ON EVERY ROW, and this was measured rather than assumed.
`name` is 4.5 MB of an 11.0 MB monthly partition -- 41% of the file for one
static field restated 312,943 times a month. Emitting it only for sites of
100 km2 or more, plus the single largest site of every territory, covers 5.7%
of the sites and 98.5% of the area at risk. Nothing is lost that cannot be
recovered: the complete zip is in object storage, so the derived table is the
thing you scan and the raw is the thing you investigate.

TRANSBOUNDARY CODES ARE NOT TERRITORIES. PRNT_ISO3 holds 222 distinct values
and 25 of them are joint designations like "FRA;ITA;MCO" or "KAZ;TKM;UZB" --
28 sites between them. Counting those as countries makes 22 of them look like
territories holding exactly one protected area, which is nonsense: France holds
7,464. Every per-territory measurement here excludes any code containing a
semicolon, and ABNJ (the high seas) is kept separate for the same reason.

THE FRAGILITY WORTH MEASURING IS CONCENTRATION, NOT COUNT. Denmark lists 1,173
sites and 91% of its 1,073,813 km2 is one of them (the Northeast Greenland
National Park). The Cook Islands and Niue are at 100%. `top_site_share` is
emitted per territory so that "how much of this country's protected estate is
one row" is answerable from the first capture, not the twelfth.
"""

import csv
import io
import re
import zipfile

from wss import derive

PARSER_VERSION = "1"

# WDPA_Sep2026_Public_csv.zip -> ("Sep", "2026")
MONTH_IN_NAME = re.compile(r"WDPA_([A-Z][a-z]{2})(\d{4})_", re.IGNORECASE)
MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}

ID_COLUMNS = ("SITE_ID", "WDPAID")

# A site big enough that its departure is an event on its own. 100 km2 is
# 17,582 of 312,943 sites and 98.5% of the world's reported protected area.
NAMED_AREA_KM2 = 100.0
# A territory small enough that any departure is most of its estate. Excludes
# transboundary codes: of the 196 real single-country codes, 7 hold five sites
# or fewer and NONE holds exactly one.
FRAGILE_TERRITORY_SITES = 10

MIN_ROWS = 100_000


def _release_month(text: str) -> str | None:
    """'2026-09-01' from a filename, or None if it does not name a month."""
    m = MONTH_IN_NAME.search(text or "")
    if not m:
        return None
    mon = MONTHS.get(m.group(1).lower())
    return f"{m.group(2)}-{mon:02d}-01" if mon else None


def _number(value) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return 0.0


def parse(body: bytes, ctx: derive.ParseContext):
    zf = zipfile.ZipFile(io.BytesIO(body))
    names = [n for n in zf.namelist()
             if n.lower().endswith(".csv") and "sources" not in n.lower()]
    if not names:
        raise ValueError(
            "wdpa-site.v1: no site CSV in the zip. Members were: "
            + ", ".join(zf.namelist()[:8]))
    member = max(names, key=lambda n: zf.getinfo(n).file_size)

    observed = _release_month(member) or _release_month(ctx.url)
    if not observed:
        raise ValueError(
            f"wdpa-site.v1: neither the zip member {member!r} nor the url names a "
            f"release month. Refusing to date these rows by fetch time, which "
            f"would file one release under two months")

    # utf-8-sig: the CSV ships a BOM, so without it the first column reads as
    # '﻿TYPE' and every lookup of TYPE fails on row one.
    handle = io.TextIOWrapper(zf.open(member), encoding="utf-8-sig", errors="replace")
    reader = csv.DictReader(handle)
    cols = reader.fieldnames or []
    id_col = next((c for c in ID_COLUMNS if c in cols), None)
    if not id_col:
        raise ValueError(
            f"wdpa-site.v1: no identity column. Looked for {ID_COLUMNS}, found "
            f"{cols[:10]}. The WDPA renamed WDPAID to SITE_ID once already")

    # One pass to gather. SITE_PID splits a site into parts; the SITE is the
    # thing that gets degazetted, so parts are collapsed and areas summed.
    rows = 0
    sites: dict[str, dict] = {}
    by_country_n: dict[str, int] = {}
    by_iucn: dict[str, list] = {}
    by_gov: dict[str, int] = {}
    by_year: dict[str, int] = {}
    no_year = 0

    for row in reader:
        rows += 1
        site = (row.get(id_col) or "").strip()
        if not site:
            continue
        area = _number(row.get("REP_AREA"))
        marine_area = _number(row.get("REP_M_AREA"))
        realm = (row.get("REALM") or "").strip().lower() or "unknown"
        country = (row.get("PRNT_ISO3") or "").strip() or "unknown"
        iucn = (row.get("IUCN_CAT") or "").strip() or "unknown"
        gov = (row.get("GOV_TYPE") or "").strip() or "unknown"
        year = (row.get("STATUS_YR") or "").strip()

        by_iucn.setdefault(iucn, [0, 0.0])
        by_iucn[iucn][0] += 1
        by_iucn[iucn][1] += area
        by_gov[gov] = by_gov.get(gov, 0) + 1
        if year and year != "0":
            by_year[year] = by_year.get(year, 0) + 1
        else:
            no_year += 1

        prior = sites.get(site)
        if prior is None:
            sites[site] = {
                "area": area, "marine_area": marine_area, "realm": realm,
                "country": country,
                "name": (row.get("NAME") or "").strip(),
                "status": (row.get("STATUS") or "").strip() or "unknown",
            }
            by_country_n[country] = by_country_n.get(country, 0) + 1
        else:
            prior["area"] += area
            prior["marine_area"] += marine_area

    if rows < MIN_ROWS:
        raise ValueError(
            f"wdpa-site.v1: only {rows} rows. The September 2026 release had "
            f"314,766 -- a file this small is a truncated download, not a month "
            f"in which the world lost its protected areas")

    # ";" is a joint designation, not a country. ABNJ is the high seas.
    def is_territory(code: str) -> bool:
        return ";" not in code and code not in ("ABNJ", "unknown")

    fragile = {c for c, n in by_country_n.items()
               if n <= FRAGILE_TERRITORY_SITES and is_territory(c)}
    # The single largest site in each territory, so every country's keystone is
    # named however small the country's total is.
    largest: dict[str, tuple[float, str]] = {}
    for site, s in sites.items():
        c = s["country"]
        if largest.get(c, (-1.0, ""))[0] < s["area"]:
            largest[c] = (s["area"], site)
    keystones = {site for _, site in largest.values()}

    named = 0
    area_total = 0.0
    marine_area_total = 0.0
    no_area = 0
    country_area: dict[str, float] = {}
    status_n: dict[str, int] = {}
    realm_n: dict[str, int] = {}
    realm_area: dict[str, float] = {}

    for site, s in sites.items():
        eid = f"pa:{site}"
        # Round FIRST, then test. `area_listed` is what a reader sees, and a
        # site of 0.00001 km2 publishes as 0.0 -- counting the unrounded value
        # here made the feed's sites_without_area disagree with the site rows
        # by 96, which is exactly the kind of drift nobody notices for a year.
        area = round(s["area"], 4)
        area_total += s["area"]
        if area == 0:
            no_area += 1
        marine_area_total += s["marine_area"]
        realm_n[s["realm"]] = realm_n.get(s["realm"], 0) + 1
        realm_area[s["realm"]] = realm_area.get(s["realm"], 0.0) + s["area"]
        country_area[s["country"]] = country_area.get(s["country"], 0.0) + s["area"]
        status_n[s["status"]] = status_n.get(s["status"], 0) + 1

        # `area_listed` is both the presence and the weight: the row existing
        # says the site was here, the value says how much of the planet leaves
        # with it.
        yield derive.Observation(eid, "area_listed", area, "km2", observed_at=observed)
        yield derive.Observation(eid, "country", s["country"], "text", observed_at=observed)
        yield derive.Observation(eid, "status", s["status"], "state", observed_at=observed)
        # WDPA's own label, not a binary inferred from a different column.
        yield derive.Observation(eid, "realm", s["realm"], "state", observed_at=observed)
        if s["marine_area"] > 0:
            yield derive.Observation(eid, "marine_area", round(s["marine_area"], 4),
                                     "km2", observed_at=observed)
        if s["name"] and (s["area"] >= NAMED_AREA_KM2 or s["country"] in fragile
                          or site in keystones):
            named += 1
            yield derive.Observation(eid, "name", s["name"], "text", observed_at=observed)

    feed = "feed:wdpa"
    yield derive.Observation(feed, "sites_listed", len(sites), "count", observed_at=observed)
    yield derive.Observation(feed, "rows_listed", rows, "count", observed_at=observed)
    yield derive.Observation(feed, "area_listed_total", round(area_total, 2), "km2",
                             observed_at=observed)
    yield derive.Observation(feed, "marine_area_total", round(marine_area_total, 2), "km2",
                             observed_at=observed)
    yield derive.Observation(feed, "territories_listed", len(by_country_n), "count",
                             observed_at=observed)
    yield derive.Observation(feed, "sites_named", named, "count", observed_at=observed)
    yield derive.Observation(feed, "fragile_territories", len(fragile), "count",
                             observed_at=observed)
    yield derive.Observation(feed, "territories_excl_joint",
                             sum(1 for c in by_country_n if is_territory(c)), "count",
                             observed_at=observed)
    yield derive.Observation(feed, "joint_designations",
                             sum(1 for c in by_country_n if ";" in c), "count",
                             observed_at=observed)
    # The two blind spots, counted rather than hidden: a site with no area
    # cannot be weighed when it leaves, and one with no year cannot be aged.
    yield derive.Observation(feed, "sites_without_area", no_area, "count", observed_at=observed)
    yield derive.Observation(feed, "sites_without_year", no_year, "count", observed_at=observed)
    # Which spelling of the identity column this release used. A rename gets
    # dated to the month instead of discovered as an empty capture.
    yield derive.Observation(feed, "id_column", id_col, "text", observed_at=observed)
    yield derive.Observation(feed, "columns", str(len(cols)), "count", observed_at=observed)

    for country in sorted(by_country_n):
        cid = f"country:{country}"
        total = country_area.get(country, 0.0)
        yield derive.Observation(cid, "sites_listed", by_country_n[country], "count",
                                 observed_at=observed)
        yield derive.Observation(cid, "area_listed", round(total, 2), "km2",
                                 observed_at=observed)
        yield derive.Observation(cid, "is_territory", "yes" if is_territory(country) else "no",
                                 "state", observed_at=observed)
        # How much of this territory's protected estate is a single row.
        # Denmark is 91%, the Cook Islands and Niue 100%. That is the
        # fragility worth watching, and counting sites hides it completely.
        top_area, top_site = largest.get(country, (0.0, ""))
        if total > 0:
            yield derive.Observation(cid, "top_site_share", round(top_area / total, 4),
                                     "ratio", observed_at=observed)
            yield derive.Observation(cid, "top_site", f"pa:{top_site}", "text",
                                     observed_at=observed)
    for cat in sorted(by_iucn):
        n, a = by_iucn[cat]
        yield derive.Observation(f"iucn:{cat}", "sites_listed", n, "count", observed_at=observed)
        yield derive.Observation(f"iucn:{cat}", "area_listed", round(a, 2), "km2",
                                 observed_at=observed)
    for realm in sorted(realm_n):
        rid = f"realm:{realm}"
        yield derive.Observation(rid, "sites_listed", realm_n[realm], "count",
                                 observed_at=observed)
        yield derive.Observation(rid, "area_listed", round(realm_area[realm], 2), "km2",
                                 observed_at=observed)
    for status in sorted(status_n):
        yield derive.Observation(f"status:{status}", "sites_listed", status_n[status],
                                 "count", observed_at=observed)
    for gov in sorted(by_gov):
        yield derive.Observation(f"governance:{gov}", "sites_listed", by_gov[gov], "count",
                                 observed_at=observed)
    for year in sorted(by_year):
        yield derive.Observation(f"designated:{year}", "sites_listed", by_year[year],
                                 "count", observed_at=observed)


derive.register("wdpa-site.v1", parse, PARSER_VERSION)
