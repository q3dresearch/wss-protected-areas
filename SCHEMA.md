# Data shape

*Generated 2026-09-15T13:15:05Z by `wss schema` from the derived rows. Do not hand-edit — regenerate after any derive.*

**You should not need to download anything to read this.**

- **4,788 observations** across 1 partition(s), in **1 series**
  - `wdpa.protected.areas` — 4,788 rows, **1821 entities**
- Raw: 0 file(s), 0 bytes on disk, 1 capture date(s), 2026-09-11 → 2026-09-11

## Sources

| source | cadence | endpoints | storage | personal data | licence |
| --- | --- | ---: | --- | --- | --- |
| `wdpa.protected.areas` | quarterly | 1 | object | none | Protected Planet terms of use -- free for non-commercial use |

## Columns

```
series_id, entity_id, observed_at, captured_at, metric, value, unit, source_id, raw_ref, parser_version
```

`entity_id` looks like: **wdpa.protected.areas** `cohort:ABNJ:2010`, `cohort:AFG:2000`, `cohort:AFG:2010`

## Metrics

| metric | series | rows | entities | type | unit | distinct | range / samples |
| --- | --- | ---: | ---: | --- | --- | ---: | --- |
| `area_listed` | wdpa.protected.areas | 1,635 | 1635 | number | km2 | 1570 | `0.0` … `43437677.13` |
| `area_listed_total` | wdpa.protected.areas | 1 | 1 | number | km2 | 1 | `75626602.57` … `75626602.57` |
| `columns` | wdpa.protected.areas | 1 | 1 | number | count | 1 | `34` … `34` |
| `fragile_territories` | wdpa.protected.areas | 1 | 1 | number | count | 1 | `19` … `19` |
| `id_column` | wdpa.protected.areas | 1 | 1 | text | text | 1 | `SITE_ID` |
| `is_territory` | wdpa.protected.areas | 222 | 222 | text | state | 2 | `no`, `yes` |
| `joint_designations` | wdpa.protected.areas | 1 | 1 | number | count | 1 | `25` … `25` |
| `marine_area_total` | wdpa.protected.areas | 1 | 1 | number | km2 | 1 | `33050853.66` … `33050853.66` |
| `rows_listed` | wdpa.protected.areas | 1 | 1 | number | count | 1 | `314766` … `314766` |
| `sites_listed` | wdpa.protected.areas | 1,821 | 1821 | number | count | 495 | `1` … `312943` |
| `sites_named` | wdpa.protected.areas | 1 | 1 | number | count | 1 | `17685` … `17685` |
| `sites_without_area` | wdpa.protected.areas | 223 | 223 | number | count | 62 | `0` … `23656` |
| `sites_without_year` | wdpa.protected.areas | 223 | 223 | number | count | 54 | `0` … `34459` |
| `territories_excl_joint` | wdpa.protected.areas | 1 | 1 | number | count | 1 | `196` … `196` |
| `territories_listed` | wdpa.protected.areas | 1 | 1 | number | count | 1 | `222` … `222` |
| `top_site` | wdpa.protected.areas | 218 | 218 | text | text | 218 | `pa:10091`, `pa:101835`, `pa:10708` |
| `top_site_name` | wdpa.protected.areas | 218 | 218 | text | text | 218 | `"W" Region (Benin)`, `Aire protégée des îles P`, `Akagera` |
| `top_site_share` | wdpa.protected.areas | 218 | 218 | number | ratio | 195 | `0.0147` … `1.0` |

## Partitions

- `derived/observations/2026-09.csv.gz`
