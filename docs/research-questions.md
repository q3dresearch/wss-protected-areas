# What an archive of the World Database on Protected Areas is for

Written before the registry, because the rule is: probe the shape, write the
questions down, name who acts on them, try to answer them from what you already
have — and only then decide what to build. Most questions die at the fourth
step, and that is the point.

The screening that chose this source is in `webprobes/catalogue.csv` under
`wdpa.protected.areas`.

## The spine

**The WDPA has no way to say a protected area is gone.**

Here is the entire status vocabulary of the September 2026 release. It has
314,766 rows, which collapse to **312,943 sites** — `SITE_PID` splits a site
into parts, and the site is the thing that gets degazetted, so every number
below is counted per site:

| STATUS | rows |
| --- | --- |
| Designated | 304,978 |
| Established | 6,375 |
| Proposed | 1,270 |
| Inscribed | 276 |
| Adopted | 34 |
| Not Reported | 10 |

There is no `Degazetted`. There is no `Removed`, `Revoked`, `Downgraded` or
`Lapsed`. A protected area that is downgraded, downsized or degazetted does not
change status — **it stops appearing in next month's file**, and that is the
only trace.

**And next month's file is the only file.** Tested directly on 2026-09-11. The
download path is literally `/current/`:

| request | result |
| --- | --- |
| `/current/WDPA_Sep2026_Public_csv.zip` | **200**, last-modified 1 Sep 2026 |
| `/current/WDPA_Aug2026_Public_csv.zip` | 404 |
| `/current/WDPA_Jul2026_Public_csv.zip` | 404 |
| `/current/WDPA_Jun2026_Public_csv.zip` | 404 |
| `/current/WDPA_Jan2026_Public_csv.zip` | 404 |
| `/current/WDPA_Sep2025_Public_csv.zip` | 404 |
| the same six under their own month prefix | 404 |

UNEP-WCMC releases monthly and keeps exactly one release online. Earlier
releases are *available on request* — which is the ask-a-person screen, and the
reason this repository exists.

## Area is the denominator, and the count actively misleads

A departure counted as one site in 312,943 is meaningless. `REP_AREA` turns it
into a magnitude, and the two disagree so violently that using the count is a
mistake rather than an approximation:

| `REALM` | sites | share of sites | km² | share of area | mean site |
| --- | --- | --- | --- | --- | --- |
| **Marine** | 6,455 | **2.1%** | 43,437,677 | **57.4%** | **6,729 km²** |
| Coastal | 10,410 | 3.3% | 2,344,549 | 3.1% | 225 km² |
| Terrestrial | 296,078 | 94.6% | 29,844,377 | 39.5% | 101 km² |

**2.1% of the sites hold 57.4% of the planet's protected area**, and the
average marine site is **67×** the average terrestrial one.

`Coastal` is a real third category and not a rounding of the other two: at
225 km² a coastal site is nearer a terrestrial one than a marine one. An
earlier version of this parser derived a marine/terrestrial binary from
`REP_M_AREA > 0` instead of reading `REALM`, and it disagreed with WDPA's own
label on **9,539 sites** — 2,492 sites WDPA calls Marine report no marine area,
and 1,590 it calls Terrestrial report some. The binary was wrong twice over and
understated the finding. See *What the pilot capture changed*, below.

The same split by country. Sweden holds **32,959 sites totalling 264,641 km²**;
the Cook Islands holds **3 sites totalling 2,278,077 km²**. By count Sweden
is 10,986× the larger record; by area the Cook Islands is 9× the larger loss.

| by site count | | by area |
| --- | --- | --- |
| USA 51,248 | | FRA 10,036,224 km² (7,464 sites) |
| SWE 32,959 | | USA 9,684,794 km² |
| DEU 23,609 | | AUS 7,439,010 km² |
| EST 21,681 | | BRA 6,787,681 km² |
| FIN 19,659 | | GBR 4,338,770 km² |

And IUCN category VI is **10,072 sites carrying 19,364,825 km²** — the largest
area class in the database from the third-smallest count.

**23,656 sites (7.6%) have `REP_AREA` of zero**, so for those the denominator
does not exist at all and a departure genuinely cannot be weighed. That is a
limit of the source, and it is stated here rather than hidden in a footnote.

## Coverage

Global from the first capture, with nothing to extend: **222 distinct
`PRNT_ISO3` values** = 196 single-country codes, 25 transboundary codes, and
**ABNJ** — 10 sites, 3,244,114 km² beyond national jurisdiction.

**The transboundary codes are a trap, and it was walked into here before it was
caught.** `FRA;ITA;MCO` and `KAZ;TKM;UZB` are joint designations, not countries
— 25 of them holding 28 sites between them. Counting them as territories makes
22 look like countries holding exactly one protected area, which produced a
chart claiming that 22 national estates were one row from zero. France holds
7,464 sites. Excluding joint codes, **7 real territories hold five sites or
fewer and none holds exactly one.** Every per-territory measurement in this
repository excludes any code containing a semicolon, and the derived table
carries `is_territory` on each one so a reader cannot repeat the mistake.

**The fragility that survives the correction is concentration, not count.** How
much of a country's protected estate is a single site:

| territory | sites | reported area | share in its largest site | that site |
| --- | --- | --- | --- | --- |
| Cook Islands | 3 | 2,278,077 km² | **100%** | Marae Moana |
| Niue | 6 | 127,059 km² | **100%** | Niue Moana Mahu MPA |
| **Denmark** | **1,173** | 1,073,813 km² | **91%** | Nationalparken i Nord- og Østg |
| Central African Rep. | 32 | 656,441 km² | 84% | Chinko |
| Palau | 66 | 608,664 km² | 83% | Palau National Marine Sanctuary |
| France | 7,464 | 10,036,224 km² | 45% | Tainui Atea |

Denmark is the case that makes the point: **1,173 protected areas on the
register, and 91% of everything it protects is one of them.** Site count hides
that completely.

## The questions

One status — `source not yet added` — is the only one that justifies another
registry entry.

| # | question | needs | status |
| --- | --- | --- | --- |
| P1 | **Which protected areas leave the WDPA, and how many km² go with them?** | ~3 months | **the founding question.** Unanswerable today and unanswerable from any other live source, because there is no exit status and no prior release. Every capture records that a site WAS here, so absence becomes evidence |
| P2 | Does a site shrink before it disappears? | ~12 months | needs the archive. `REP_AREA` travels on every row. If downsizing precedes degazettement the loss is predictable a year out; if sites vanish at full size it is not. Nobody can currently tell, because nobody holds two releases |
| P3 | Was a departure a real degazettement or a data correction? | a source | **`source not yet added`** — PADDDtracker is the other half, and it is a larder: its download button points at `zenodo.org/records/4974336`, DOI'd and versioned. Fetch once as a join control, do not listen to it. A site that vanishes AND appears in PADDD is a policy event; one that vanishes alone is probably a merge or a re-survey |
| P4 | Which countries lose sites against their share of the standing 314,766? | ~12 months | needs the archive, and the denominator is already in hand. The share must be computed on area as well as count, because the two orderings are different databases (see above) |
| P5 | Do the three realms leave at different rates? | ~12 months | needs the archive. Marine is 2.1% of sites and 57.4% of area, so **one marine departure weighs 67 terrestrial ones**. Coastal sits between them at 225 km² and is the category most likely to be reclassified rather than removed — watching all three separately is the only way to tell a reclassification from a loss |
| P6 | Does `STATUS` ever move backwards — Designated to Proposed? | ~6 months | needs the archive. This is the one degradation the vocabulary CAN express, and because only one release exists nobody has ever counted it |
| P7 | How much of the 30×30 trend is new sites versus the same sites being remeasured? | ~12 months | needs the archive, and this is the question with a policy deadline attached. `REP_AREA` vs `GIS_AREA` already agree to a median relative gap of **0.0%** across 287,832 comparable rows, so a moving `REP_AREA` is a real change rather than a measurement artefact |
| P8 | Are privately governed sites more fragile? | ~12 months | needs the archive. `GOV_TYPE` names **9,528 sites governed by individual landowners** and 22,806 by non-profits, against 185,986 federal. Private protection is the part that can lapse with an owner's death or a sale, and it is 3% of rows |
| P11 | Does a territory's keystone site ever move? | ~12 months | needs the archive, and it is the sharpest alarm available. `top_site_share` is emitted per territory from the first capture. If Denmark's 91% or the Cook Islands' 100% changes at all, one row moved and a national protected estate moved with it |
| P12 | Does a site change REALM? | ~12 months | needs the archive. A site moving Coastal→Terrestrial is a reclassification, not a loss, and from a single release the two are indistinguishable. This question exists because the first parser could not have asked it — it had collapsed the column |
| P9 | How stable is the schema itself? | **partly answered, and it already broke.** | The columns are `SITE_ID` / `SITE_PID` in this release. The documented WDPA identifiers for years were `WDPAID` / `WDPA_PID`. Any script written against the old names silently reads nothing. One capture cannot date the change; two consecutive captures date any future one to the month |
| P10 | How many sites carry no usable date or area? | **answered, and it bounds everything above.** | `STATUS_YR` is `0` on **34,459 sites (11.0%)** and `REP_AREA` is `0` on **23,656 (7.6%)**. Nigeria reports no area for **91% of its 1,005 sites**, Albania 89%, Italy 57% of 3,962. Those rows can be observed leaving but not weighed or aged |

## Who acts on these, and what changes

Each row names a decision, not a sector. A question with no name against it is
trivia, and trivia does not justify a job that runs for years.

| who | questions | the decision it changes |
| --- | --- | --- |
| **Anyone reporting on 30×30 / GBF Target 3** | P1, P4, P5, P7 | whether a rise in protected coverage is new protection or remeasurement. Today the year-on-year number cannot be reproduced at all, because last year's release is gone |
| **PADDD researchers** | P1, P2, P3 | which degazettements to investigate, while they are happening rather than in a retrospective. PADDD is a curated historical dataset; this is the live edge of it |
| **Conservation finance and debt-for-nature deals** | P2, P8 | whether the site securing an instrument is still in the register at the size it was priced at. A downsizing that precedes degazettement is a covenant event |
| **National agencies with a small estate** | P1, P4 | 22 territories have exactly one site. Their entire protected estate is one row, and nobody is watching it |
| **UNEP-WCMC itself** | P6, P9, P10 | whether status regressions and blank fields cluster by reporting country. They hold this internally and publish no series |

**Who this is NOT for.** Anyone wanting today's protected-area boundaries. That
is Protected Planet, it is free, authoritative and better than anything here.
This archive answers the opposite question — what used to be in it.

## What would make this worth stopping

1. UNEP-WCMC publishes prior releases at stable URLs. Then P1 through P8 become
   queries against them and this repository is redundant — which would be a
   good outcome, and the README should say so.
2. A `Degazetted` or `Removed` status is added to the vocabulary. Then
   departures are announced and only the timing is ours.
3. Twelve months pass with no site over 1,000 km² leaving. That would mean
   churn lives entirely in the small-site tail, which is worth knowing and
   worth re-scoping for.
