<h1 align="center">wss-protected-areas</h1>

<p align="center">
  <strong>Every protected area on earth, kept because only this month's exist</strong>
</p>

<div align="center">

  <a href="https://github.com/q3dresearch/wss-protected-areas/actions/workflows/capture-quarterly.yml"><img alt="capture status" src="https://img.shields.io/github/actions/workflow/status/q3dresearch/wss-protected-areas/capture-quarterly.yml?label=capture&style=flat-square"></a>
  <a href="https://github.com/q3dresearch/wss-protected-areas/commits"><img alt="last capture" src="https://img.shields.io/github/last-commit/q3dresearch/wss-protected-areas?label=last%20capture&style=flat-square"></a>
  <a href="https://github.com/q3dresearch/wss-protected-areas/blob/main/LICENSE"><img alt="licence" src="https://img.shields.io/github/license/q3dresearch/wss-protected-areas?style=flat-square"></a>
  <a href="https://github.com/q3dresearch/wss-protected-areas"><img alt="stars" src="https://img.shields.io/github/stars/q3dresearch/wss-protected-areas?style=social"></a>

</div>

<p align="center">
  <sub>fleet: <a href="https://github.com/q3dresearch/wss-engine">engine</a> · <a href="https://github.com/q3dresearch/wss-forest-harvest">forest harvest</a> · <a href="https://github.com/q3dresearch/wss-drug-scarcity">drug scarcity</a> · <a href="https://github.com/q3dresearch/wss-healthcare-exclusions">healthcare exclusions</a> · <strong>protected areas</strong></sub>
</p>

**The World Database on Protected Areas is released monthly and exactly one
release is online.** The download path is literally `/current/`.

<p align="center">
  <img src="examples/charts/the-only-release.svg" width="900" alt="Nine monthly WDPA releases requested on 2026-09-11: September 2026 answers 200 with 23,820,193 bytes; August, July, June, May, April, March, February and January 2026 all return 404.">
</p>

Every one of those was fetched twice — once under `/current/` and once under
its own month prefix. Only the current month answers, at either path. Earlier
releases are *available on request*, by email, from UNEP-WCMC.

## There is no way for the WDPA to say a protected area is gone

That is the whole reason this repository exists. Here is the entire `STATUS`
vocabulary of the September 2026 release:

| STATUS | sites |
| --- | --- |
| Designated | 304,978 |
| Established | 6,375 |
| Proposed | 1,270 |
| Inscribed | 276 |
| Adopted | 34 |
| Not Reported | 10 |

No `Degazetted`. No `Removed`, `Revoked` or `Lapsed`. A protected area that is
downgraded, downsized or degazetted does not change status — **it stops
appearing in next month's file**, and with the previous file gone there is
nothing to compare against. Presence is the observation.

[PADDDtracker](https://www.padddtracker.org/) is the existing record of these
events and it is a *larder*, not a listener: its own download button points at
[zenodo.org/records/4974336](https://zenodo.org/records/4974336) — a DOI'd,
versioned, permanently archived research dataset. Fetch it once as a join
control. It cannot tell you what left last month.

## Counting protected areas and measuring them are different questions

<p align="center">
  <img src="examples/charts/count-or-area.svg" width="900" alt="Log-log scatter of 196 territories, sites listed against reported area. Sweden and Estonia sit far right with many sites and small area; the Cook Islands sits far left with three sites and 2.3 million square kilometres.">
</p>

**Sweden lists 32,959 protected areas covering 264,641 km². The Cook Islands
lists 3, covering 2,278,077 km².** By count Sweden is 10,986× the larger
record; by area the Cook Islands is 9× the larger loss. Only one of those is a
fact about protection, which is why `area_listed` carries the weight on the
same row that carries the presence.

The same inversion runs through the management categories:

<p align="center">
  <img src="examples/charts/where-the-area-is.svg" width="900" alt="IUCN categories ranked by area: category VI holds 19.4M square kilometres from 10,072 sites, while category IV holds 8.4M from 95,696 sites.">
</p>

Category VI — sustainable use, the weakest protection class — is **10,072
sites holding 19,364,825 km²**, the largest area class in the database from the
third-smallest count.

And the realm split is sharper still. WDPA labels every site `Marine`,
`Coastal` or `Terrestrial`:

<p align="center">
  <img src="examples/charts/the-weight-of-a-realm.svg" width="900" alt="Marine sites are 2.1% of the 312,943 protected areas and 57.4% of the 75.6 million square kilometres, averaging 6,729 km² each; Coastal is 3.3% of sites and 3.1% of area at 225 km²; Terrestrial is 94.6% of sites and 39.5% of area at 101 km².">
</p>

**2.1% of the sites hold 57.4% of the planet's protected area**, and one marine
departure weighs **67** terrestrial ones. `Coastal` is a real third category
rather than a rounding of the other two: at 225 km² a coastal site is nearer a
terrestrial one than a marine one.

## Most of a country's protection can be one row

<p align="center">
  <img src="examples/charts/one-row-away.svg" width="900" alt="Share of each territory's protected area held by its single largest site: Cook Islands and Niue 100%, Denmark 91%, Central African Republic 84%, Palau 83%, France 45%.">
</p>

**Denmark lists 1,173 protected areas and 91% of everything it protects is one
of them** — the Northeast Greenland National Park, which the WDPA itself
truncates to `Nationalparken i Nord- og Østg`. The Cook Islands and Niue are at
100%. Site count hides this completely, and `top_site_share` is emitted per
territory from the very first capture so it does not take a year of archive to
see.

**A correction worth recording, because it was nearly published.** `PRNT_ISO3`
holds 222 values and 25 of them are joint designations — `FRA;ITA;MCO`,
`KAZ;TKM;UZB`, 28 sites between them. Counting those as countries made 22 look
like national estates holding exactly one protected area, and produced a chart
saying so. France holds 7,464. Excluding joint codes, **7 real territories hold
five sites or fewer and none holds exactly one.** Every per-territory
measurement here excludes any code containing a semicolon, and `is_territory`
travels on each one so a reader cannot repeat it.

## How much a second frame changes the picture

<p align="center">
  <img src="examples/charts/one-frame-japan.svg" width="900" alt="Japanese protected areas by designation decade from the September 2026 release alone: 972 sites from the 1970s holding 338k square kilometres, 3,014 from the 2010s, 1,270 from the 2020s. Every bar is survivors only.">
</p>

`STATUS_YR` reaches back to **1902**, so a single release looks like a century
of history. It is not. **Every bar is survivors only** — sites designated in
that decade *and still present in September 2026*. A park designated in 1975
and degazetted in 1998 is in no bar here, and in no other column of the
release. Nothing in one frame separates a designation record from a
survivorship curve.

Georgia is the only country with two independently verified frames — July 2024
and September 2026, both complete, checked record by record — and it shows what
the second frame is worth:

<p align="center">
  <img src="examples/charts/two-frames-georgia.svg" width="900" alt="Georgia July 2024 against September 2026: 95 sites becomes 171 and 14,189 square kilometres becomes 23,379. Of 94 sites in both frames, 72 changed reported area but only 45 changed measured area. Kazbegi's reported area fell 46% while its measured area moved 0.1%.">
</p>

**Of the 94 sites in both frames, 72 changed their reported area and only 45
changed their measured one.** Kazbegi National Park's `REP_AREA` fell **46%**
while its `GIS_AREA` moved **0.1%** — 783.1 km² to 782.6. Five more of the
largest drops are the same story: a reported figure roughly double the polygon,
corrected to match it.

Read from one frame, Georgia looks like a country that lost half its biggest
national parks. It didn't. The boundaries never moved; the numbers did. That is
**P7** — how much of a trend is new sites versus the same sites being
remeasured — and it is answerable only across frames.

And the geometry settles it outright:

<p align="center">
  <img src="examples/charts/the-same-boundary.svg" width="900" alt="Kazbegi National Park drawn from both releases overlaid: the September 2026 outline traces the July 2024 fill exactly. Vertices fell from 7,752 to 3,302 and reported area from 1,446.2 to 782.0 km², while measured area moved 783.1 to 782.6 and the bounding box is identical to five decimals.">
</p>

Both frames of Kazbegi, on top of each other. If the boundary had moved, the
July 2024 fill would show at the edges. It does not — the bounding box is
**identical to five decimal places**, and **3,289 of the 3,302 September 2026
vertices (99.6%) exist *exactly* in the July 2024 outline** to six decimals.
That is vertex-thinning, not a re-survey: 7,752 points became 3,302.

**`REP_AREA` and `GIS_AREA` are independent fields** — one is reported by the
country, the other computed from the polygon — so one can move while the other
does not. That is why a 46% fall in the reported area leaves the drawing
untouched.

**And the 2024 figure was an error, systematically.** In July 2024 the reported
area was **1.80× the measured one at the median**, with **76 of 82 Georgian
sites (93%) in a tight 1.6–2.0 band**. By September 2026 the median ratio is
**1.000** and 148 of 153 (97%) agree within 2%. A near-constant factor across
almost every site in one country is one bad national submission, corrected — not
82 separate mistakes, and not a change in what is protected.

Across all 94 Georgian sites in both frames the polygons went from **265,145
vertices to 70,295, a drop of 73%**, while **83 of 94 (88%) kept an identical
bounding box** and 92 lost points. The register was re-drawn at lower resolution
and its reported areas corrected to match. No protection was gained or lost.

**Japan cannot have this chart**, and that is the point: no second frame of
Japanese geometry exists anywhere, so there is no way to tell whether the same
thing happened there. The only fix is to start capturing now.

The per-country geometry used for that comparison is a **control**, read once.
This repository captures the global attribute release and nothing else; the
screening record is in `webprobes/catalogue.csv`.

## What the archive cannot fix

<p align="center">
  <img src="examples/charts/cannot-be-weighed.svg" width="900" alt="Share of each territory's sites reporting no area: Nigeria 91% of 1,005, Albania 89% of 830, Croatia 61%, Italy 57% of 3,962, Lithuania 51%.">
</p>

**23,656 sites (7.6%) report `REP_AREA` of zero and 34,459 (11.0%) report no
designation year.** Those rows can be observed leaving and cannot be weighed or
aged when they do. Nigeria reports no area for 91% of its 1,005 sites. This is
a limit of the source and it is counted in the derived table
(`sites_without_area`, `sites_without_year`) rather than hidden.

**The identifier has already renamed itself.** This release keys on `SITE_ID` /
`SITE_PID`; the documented WDPA identifiers for years were `WDPAID` /
`WDPA_PID`, and anything written against the old names silently reads nothing.
The parser accepts both and records which spelling a release used, so the next
rename is dated to the month instead of discovered as an empty capture.

The questions this archive exists to answer, with honest statuses and the
people who act on them, are in
[docs/research-questions.md](docs/research-questions.md).
The publication decision, and what interrogating the charts found before
it, is in [docs/pilot-study.md](docs/pilot-study.md).

## Coverage

| source | what it is | cadence | first capture |
| --- | --- | --- | --- |
| `wdpa.protected.areas` | the WDPA public CSV release, captured quarterly — 314,766 rows collapsing to 312,943 sites, 75,626,603 km², across 196 territories plus 25 joint designations and the high seas | quarterly | 2026-09 |

## The data you get

**This repository publishes aggregates, not the database.** UNEP-WCMC forbid
publishing WDPA data in downloadable form, so the engine's `publish: aggregates` mode sends
the 1,558,769 per-site rows to private object storage on every derive and keeps
the **4,788 aggregate rows** — counts and totals by territory, cohort, IUCN
category, realm and status — in git. Every chart above redraws from those 4,788
rows alone, byte-identically. Read [LICENSE-DATA](LICENSE-DATA) first.

`derived/observations/<YYYY-MM>.csv.gz` — one row per entity, per metric, per
release month:

```
series_id, entity_id, observed_at, captured_at, metric, value, unit, source_id, raw_ref, parser_version
```

`observed_at` is the **release month, not the fetch time** — the file names its
own month and that is the date the state was true. A re-fetch of the September
release cannot invent an October.

| entity | metrics |
| --- | --- |
| `pa:<SITE_ID>` | `area_listed` (km², and the presence), `country`, `status`, `realm`, `status_year`, `marine_area`, `name` — **object storage only, not in git** |
| `cohort:<ISO3>:<decade>` | `sites_listed`, `area_listed` — the designation cohorts that make a survivorship curve drawable per country |
| `country:<ISO3>` | `sites_listed`, `area_listed`, `is_territory`, `top_site_share`, `top_site`, `top_site_name`, `sites_without_area`, `sites_without_year` |
| `iucn:<cat>` | `sites_listed`, `area_listed` |
| `feed:wdpa` | `sites_listed`, `rows_listed`, `area_listed_total`, `marine_sites`, `marine_area`, `territories_listed`, `territories_excl_joint`, `joint_designations`, `sites_without_area`, `sites_without_year`, `id_column`, `columns` |

**`name` is not on every row, and that was measured.** Restating a static name
312,943 times a month cost 4.5 MB of an 11.0 MB partition — 41% of the file for
one field that never moves. It is emitted for sites of 100 km² or more, every
site in a territory holding ten or fewer, and every territory's single largest
site: **17,685 sites, 5.7% of the rows and 98.5% of the area at risk.** Nothing
is lost that cannot be recovered — the complete zip is in object storage, so
the derived table is what you scan and the raw is what you investigate.

## Storage

`storage: object`. One capture is 23.8 MB and the zip is already compressed, so
git would carry 286 MB a year and the repository would be unclonable inside
three. There is no smaller endpoint: the Protected Planet API needs a key and
would cost 312,943 requests to cover the same ground.

There is **no personal data**. `MANG_AUTH` names management authorities and
`GOV_TYPE` reaches "Individual landowners" (9,528 sites), but no individual is
named anywhere in the file. Object storage here is a size decision, not a
privacy one.

## Adding a source

1. Add `registry/<source_id>.yml` (copy the existing entry), `status: paused`.
2. Add a parser in `parsers/` if the payload shape is new.
3. `wss doctor <source_id>` — **read the raw response**.
4. Flip to `status: active`, add a Coverage row, commit.

Nothing else. No workflow edits, ever.

## Run it locally

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export WSS_CONTACT="https://github.com/q3dresearch/wss-protected-areas"

wss validate
wss doctor wdpa.protected.areas
wss capture --cadence quarterly
wss derive --parsers parsers.wdpa_site_v1
python examples/visualize.py
```

Capturing locally needs the R2 variables from `.env.example`, because the
source declares `storage: object`.

## Going live

1. Push this repo **and the engine repo** under the same GitHub owner
   (`q3dresearch`) — the workflows install the engine from
   `github.com/q3dresearch/wss-engine` at the pinned tag.
2. Set the repo secret **`WSS_CONTACT`** — capture refuses to run without it.
3. Set **`R2_ACCOUNT_ID`**, **`R2_ACCESS_KEY_ID`**, **`R2_SECRET_ACCESS_KEY`**,
   **`R2_BUCKET_NAME`** and optionally **`WSS_OBJECT_PREFIX`**. Without them the
   capture job runs and writes nothing, which looks like success until the
   derive finds no raw.
4. Run `capture-quarterly` once by hand (Actions → capture-quarterly → Run
   workflow), confirm the bot's data commit lands, then let the cron take over.

## Licences

Code is MIT ([LICENSE](LICENSE)). **The derived observations are NOT CC-BY and
cannot be** — UNEP-WCMC's terms forbid sub-licensing WDPA data, including
within derivative works, and forbid publishing it in downloadable form. Read
[LICENSE-DATA](LICENSE-DATA) before reusing anything in `derived/`. Citation in
[CITATION.cff](CITATION.cff).

**The WDPA itself is not redistributed here.** Protected Planet's terms allow
free non-commercial use with attribution and do not permit republishing the
database. `raw/` goes to private object storage; what this repository publishes
is aggregate measurement over time, not a copy. See
[protectedplanet.net/en/legal](https://www.protectedplanet.net/en/legal).

> UNEP-WCMC and IUCN (2026), *Protected Planet: The World Database on Protected
> Areas (WDPA)*, September 2026, Cambridge, UK: UNEP-WCMC and IUCN.
> www.protectedplanet.net

Topics: `git-scraping` · `open-data` · `point-in-time-data` · `conservation` · `protected-areas` · `30x30`
