#!/usr/bin/env python3
"""Send the full observation table to object storage, keep aggregates in git.

    python tools/split_derived.py [--check]

WHY THIS EXISTS. UNEP-WCMC's terms permit publishing WDPA material online
"providing the Data are not downloadable", and forbid sub-licensing it "in
whole or in part including within Derivative Works". A public
derived/observations/*.csv.gz holding 1,558,769 per-site rows across 312,943
protected areas is downloadable Data -- the attribute database restructured,
not a statistic about it. See LICENSE-DATA.

So the split is not a size optimisation. It is the condition on which this
repository can be public at all.

WHAT STAYS IN GIT. Every entity that is a COUNT or a TOTAL rather than a
record: feed:, country:, cohort:, iucn:, realm:, status:, governance:,
designated:. About 4,800 rows. Enough to redraw every chart in examples/ --
which is the test this split has to pass, because a public repository whose
figures cannot be regenerated is a slideshow.

WHAT GOES TO R2. Every pa: row, which is the archive proper.

IDEMPOTENT, AND THE GUARD MATTERS. Run twice and the second run finds no pa:
rows and does nothing. Without that guard a re-run would upload the already
stripped file over the complete one in object storage and silently destroy the
archive -- the loud half succeeding while the quiet half failed.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PARTITIONS = REPO / "derived" / "observations"

# Entity prefixes that are aggregates about the data, not the data.
PUBLIC_PREFIXES = ("feed:", "country:", "cohort:", "iucn:", "realm:",
                   "status:", "governance:", "designated:")
# The per-site records. These are the ones the terms cover.
PRIVATE_PREFIX = "pa:"


def is_public(entity_id: str) -> bool:
    return entity_id.startswith(PUBLIC_PREFIXES)


def read_rows(path: Path) -> tuple[list[str], list[dict]]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        r = csv.DictReader(fh)
        return list(r.fieldnames or []), list(r)


def write_rows(path: Path, cols: list[str], rows: list[dict]) -> None:
    """Use the ENGINE's writer, not a local reimplementation.

    The first version of this function wrapped a GzipFile in a TextIOWrapper
    and closed only the GzipFile. The wrapper's buffer was never flushed, so
    the LAST 20 ROWS were silently dropped -- every realm: and status: row and
    part of iucn:, because those sort last. The file was a valid gzip, a valid
    CSV, and short. wss.csvio.write_csv closes the wrapper (which flushes
    through to the gzip) and already handles mtime=0.
    """
    from wss.csvio import write_csv
    write_csv(path, cols, rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report what would happen, upload and write nothing")
    args = ap.parse_args()

    parts = sorted(PARTITIONS.glob("*.csv.gz"))
    if not parts:
        print("no partitions; run `wss derive` first")
        return 0

    store = None
    if not args.check:
        from wss import storage
        cfg = storage.object_config()
        if not cfg["bucket"]:
            print("ERROR: no object storage configured. The per-site rows cannot be\n"
                  "       published, so refusing to strip them with nowhere to put them.",
                  file=sys.stderr)
            return 1
        store = storage.ObjectStore(bucket=cfg["bucket"], endpoint_url=cfg["endpoint_url"],
                                    prefix=cfg["prefix"], access_key=cfg["access_key"],
                                    secret_key=cfg["secret_key"])

    for path in parts:
        cols, rows = read_rows(path)
        private = [r for r in rows if not is_public(r["entity_id"])]
        public = [r for r in rows if is_public(r["entity_id"])]
        unknown = {r["entity_id"].split(":")[0] for r in private
                   if not r["entity_id"].startswith(PRIVATE_PREFIX)}
        if unknown:
            # An entity prefix nobody classified is a decision, not a default.
            print(f"ERROR: {path.name} holds unclassified entity prefixes {sorted(unknown)}.\n"
                  f"       Add them to PUBLIC_PREFIXES or confirm they are records.",
                  file=sys.stderr)
            return 1
        if not private:
            print(f"  {path.name}: already split ({len(public):,} aggregate rows) — skipped")
            continue
        key = f"derived/observations/{path.name}"
        print(f"  {path.name}: {len(rows):,} rows -> {len(private):,} to object "
              f"storage, {len(public):,} kept in git")
        if args.check:
            continue
        store.write(key, path.read_bytes())
        if not store.exists(key):
            print(f"ERROR: {key} did not land in object storage; not stripping",
                  file=sys.stderr)
            return 1
        # Read the archived copy back and count it before touching the local
        # file. Writing is not the same as having written.
        import gzip as _gz, io as _io
        kept = list(csv.DictReader(_gz.open(_io.BytesIO(store.read(key)), "rt",
                                            encoding="utf-8", newline="")))
        if len(kept) != len(rows):
            print(f"ERROR: object storage holds {len(kept):,} rows, expected "
                  f"{len(rows):,}; not stripping", file=sys.stderr)
            return 1
        write_rows(path, cols, public)
        back = read_rows(path)[1]
        if len(back) != len(public):
            print(f"ERROR: wrote {len(public):,} aggregate rows but read back "
                  f"{len(back):,}", file=sys.stderr)
            return 1
        print(f"      verified: {len(kept):,} in object storage, "
              f"{len(back):,} in git")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
