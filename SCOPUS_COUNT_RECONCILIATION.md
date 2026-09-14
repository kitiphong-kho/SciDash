# Scopus Count Reconciliation

Generated: 2026-06-02 11:37 ICT

## Queries Compared

- Dashboard current logic: 50 current academic staff whitelist, each searched with `AUTHLASTNAME(last) AND AFFIL("Mae Fah Luang University") AND AFFIL("School of Science")`, then deduped by Scopus EID.
- Affiliation-wide API query: `AFFIL("Mae Fah Luang University") AND AFFIL("School of Science")`
- General text API query: `"Mae Fah Luang University" AND "School of Science"`
- User reported Scopus website counts: 2026=76, 2025=211, 2024=222, 2023=207, 2022=178
- `date=<year>` and `PUBYEAR IS <year>` returned the same API counts in this check.

## Count Comparison

| Year | User website | API affiliation | API general text | Dashboard academic staff | Affiliation not in dashboard | Dashboard not in affiliation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026 | 76 | 74 | 76 | 63 | 11 | 0 |
| 2025 | 211 | 210 | 211 | 170 | 40 | 0 |
| 2024 | 222 | 223 | 224 | 160 | 63 | 0 |
| 2023 | 207 | 207 | 208 | 120 | 87 | 0 |
| 2022 | 178 | 179 | 179 | 125 | 54 | 0 |

## Finding

- The user website counts align with an affiliation/general Scopus search, not with the dashboard staff-whitelist definition.
- The dashboard is lower because it only includes publications matched to the current 50 academic staff names from the School of Science staff pages.
- The affiliation-wide query includes records with School of Science/MFU affiliation that may belong to students, former staff, visiting/adjunct authors not in the whitelist, staff name variants, or records where Scopus exposes the school affiliation but the current whitelist name is not matched.
- CSV of affiliation-wide records not currently included in the dashboard: `scopus_affiliation_not_in_staff_dashboard.csv`
