# Pilot study: does one capture justify publishing this?

Run 2026-09-11 against the first capture, following step 10 of the wss research
sequence — *interrogate the finished charts before believing them*. The five
questions are asked of the whole set, not of one chart.

The capture: `WDPA_Sep2026_Public_csv.zip`, 23,820,193 bytes, to R2. Derived to
1,281,605 observations over 312,943 sites.

## 1. Is any chart lying?

**35 of 35 published headline claims were recomputed from the derived rows by
code that does not import `visualize.py`, and all 35 reproduce exactly.**

That covers the Sweden/Cook Islands pair and both ratios, the IUCN VI figures
and the claim that VI is the largest area class, all nine realm figures,
Denmark's 91% and the Cook Islands' 100%, Nigeria's 91% and that it is the
worst territory over 500 sites, and every feed-level count.

Separately: the archived bytes were read back out of R2, unzipped, and the
whole analysis re-run from them. The charts regenerate byte-identically.

## 2. Did you merge categories that are not one thing?

**Yes, and this question caught it.** The rule is to check a merge against a
*second* column rather than the one merged on, and doing that broke the
original classification outright.

The first parser derived a marine / terrestrial binary from `REP_M_AREA > 0`.
WDPA publishes a `REALM` column naming the answer, and it has **three** values:

| | sites | area | mean site |
| --- | --- | --- | --- |
| Marine | 6,455 | 43,437,677 km² | 6,729 km² |
| Coastal | 10,410 | 2,344,549 km² | 225 km² |
| Terrestrial | 296,078 | 29,844,377 km² | 101 km² |

The binary disagreed with WDPA's own label on **9,539 sites** — 2,492 that WDPA
calls Marine report no marine area, and 1,590 it calls Terrestrial report some
— and it collapsed `Coastal`, which at 225 km² belongs with neither side.

The published claim was *"marine is 3.5% of sites and 47.0% of area"*. The
source's own answer is **2.1% of sites and 57.4% of area**, a ratio of 67 rather
than 25. The error understated the finding, which is the direction that gets
published unchallenged.

A second merge was checked and stands: the transboundary correction. 25 of the
222 `PRNT_ISO3` values are joint designations, they are excluded from every
per-territory measure, and `is_territory` travels on each one so a reader cannot
repeat the mistake.

## 3. Does any chart raise more than it answers?

**`cannot-be-weighed.svg` did, and now carries its own answer.** Showing that
Nigeria reports no area for 91% of its sites invites *"then how much of the
75.6M km² total is missing?"* The feed carries `sites_without_area` (23,656) and
`sites_without_year` (34,459) so the reader can bound it without leaving the
repository.

**`the-only-release.svg` deliberately raises one it cannot answer**: what was in
the eight missing months. That is the repository's reason to exist, and the
caption says so rather than implying the archive already knows.

## 4. What must be read together?

- **`count-or-area.svg` and `the-weight-of-a-realm.svg` are one argument.** The
  first shows that territories rank differently by count and by area; the second
  shows why (2.1% of sites hold 57.4% of the planet). Either alone reads as a
  curiosity.
- **`one-row-away.svg` is invalid without the transboundary correction**, which
  is stated in its own section of the README and in the questions doc. Without
  it the chart says 22 countries hold one protected area each, which is false.
- **`cannot-be-weighed.svg` bounds every other chart.** 23,656 sites cannot be
  weighed when they leave, and no area-weighted finding here covers them.

## 5. What policy or prediction follows, and what does not?

**Follows.** Any 30×30 or GBF Target 3 figure must be weighted by area and split
by realm, because 2.1% of the entries carry 57.4% of the total and one marine
degazettement outweighs 67 terrestrial ones. A country whose `top_site_share` is
near 1.0 — Denmark 91%, Cook Islands and Niue 100% — has a single-row exposure
that its site count completely hides, and that is a monitorable risk today.

**Does not follow.** Nothing here says protected areas are being lost. This is
one release. The repository cannot yet report a single departure, a rate, or a
trend, and any chart that implied one would be lying. The three founding
questions all read *needs the archive*, and the honest claim is that **the
September 2026 release is now preserved and the October one will produce the
first delta.**

## 6. May any of this be published? (step 11, added because of this repo)

**Asked last, and it nearly went unasked.** The sequence had ten steps and none
of them mentioned the publisher's terms. UNEP-WCMC's say:

> WDPA materials "may not be sub-licensed in whole or in part **including
> within Derivative Works**" and may be published online "providing (a) the
> Data **are not downloadable**".

Two things followed, and both were live:

- **`LICENSE-DATA` carried the scaffold's CC-BY-4.0 text for a day.** Applying
  CC-BY to `derived/` is sub-licensing. Removed.
- **A public `derived/observations/*.csv.gz` is downloadable Data** — 1,558,769
  per-site rows across 312,943 protected areas is the attribute database
  restructured, not a statistic about it.

**And the git history mattered more than the working tree.** Four commits
already on the remote held the full table. Stripping it from `HEAD` would have
published it in every earlier commit. `git filter-repo --invert-paths` removed
that one blob from all twelve commits while keeping every message, and the
result was verified from a **fresh clone** by walking every reachable object:
one partition blob, 4,788 rows, zero per-site rows.

The registry declares `publish: aggregates`, and the engine applies it on every derive: per-site rows to object
storage, **4,788 aggregate rows** to git. The test it has to pass is that
**every chart redraws from the public half alone** — verified byte-identical
against the pre-split renders. A public repository whose figures cannot be
regenerated is a slideshow.

## Against the rest of the fleet

| | this repo | published fleet |
| --- | --- | --- |
| sources | 1 | 1–48 (`wss-forest-harvest` 2, `wss-mining-pipeline` 2) |
| charts | **9** | 3–14 |
| questions with honest statuses | 12 | 0–15 |
| questions still `source not yet added` | 2 | 0–2 |
| cadence | quarterly | weekly to quarterly |

One source is the fleet's floor, not below it, and nine charts is above its
median.

## What changed after the pilot, and why

| | at the pilot | now |
| --- | --- | --- |
| cadence | monthly | **quarterly** |
| realm | a binary from `REP_M_AREA` | **`REALM`, three values** |
| `status_year` | emitted | dropped in the REALM rewrite, **restored** |
| charts | 5 | **9** |
| `derived/` in git | everything | **aggregates only** |
| licence on `derived/` | CC-BY-4.0 | **none — it cannot be licensed** |
| visibility | private | **public** |

The cadence change is the one that came from evidence rather than from
correcting a mistake. Georgia is the only country with two verified frames, and
across 26 months the 94 sites present in both moved **−0%** in measured area,
kept identical bounding boxes on 88%, and shared **99.6% of their vertices**.
One site left, 4.4 km². Of 77 arrivals, exactly one was designated inside the
window.

The finding that mattered — Georgia's published area rose 65% while the same
sites moved 0% and the register itself grew 176% — needed **two frames 26 months
apart**. Monthly capture would have produced 26 frames to reach it.

## Verdict

**Published, quarterly, aggregates only.**

The pilot found one substantive error in the data (the realm binary, which
understated the finding it got wrong) and the sequence found one more after it
(the licence). Both were caught by a written step rather than by luck, and the
second one only existed because this repository needed it — step 11 is now in
`webprobes/sequences.py` for every build that follows.

What would change this verdict:

1. **A quarter with no measurable change at all.** If the January 2027 capture
   is byte-identical to September 2026's, the source is slower than quarterly
   and this should drop to annual or stop.
2. **UNEP-WCMC granting written permission** to redistribute, which would make
   the per-site rows publishable and the split unnecessary.
3. **A second country with two verified frames** contradicting Georgia — if
   boundaries move elsewhere, the founding question P1 is alive after all and
   the cadence argument reopens.
