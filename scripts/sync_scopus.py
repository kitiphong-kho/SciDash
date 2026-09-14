#!/usr/bin/env python3
"""SciDash v2.0 sync job.

Fetches publications from the Scopus API and writes a static snapshot to
site-data/publications.json. That JSON file is:
  - the single source of truth the dashboard (app.js) reads from -- it never
    calls Scopus directly, whether served locally or from GitHub Pages.
  - committed to git, so it IS the persistent store across runs (including
    ephemeral GitHub Actions runners that have no local disk state).

Optionally also mirrors the same data into a Google Sheet (for humans to
browse/edit) if GOOGLE_SHEET_ID + service account credentials are configured
-- see sheets_export.py. That is best-effort and never blocks the sync.

Sync strategy:
  - First run ever (no site-data/publications.json yet) or `--full`: fetch
    the full 5-year window.
  - Otherwise (incremental, the normal scheduled case): only re-fetch the
    last 2 calendar years. This is enough to pick up newly indexed
    publications and refreshed citation counts without re-querying Scopus
    for years of history that will not change, keeping API usage small and
    bounded regardless of how much history has already accumulated.

Either way, publications are merged by Scopus EID, so nothing already
stored is lost -- incremental runs only add/refresh the recent window.
"""
import argparse
import json
import os
import sys
import traceback
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

import scidash_core as core

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "site-data" / "publications.json"


def incremental_date_range():
    end_year = datetime.now().year
    start_year = end_year - 1
    return f"{start_year}-{end_year}"


def load_existing_snapshot():
    if not SNAPSHOT_PATH.exists():
        return {}, {}
    try:
        payload = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}, {}
    publications_by_id = {pub["id"]: pub for pub in payload.get("publications", []) if pub.get("id")}
    meta = {
        "lastFullSyncAt": payload.get("lastFullSyncAt"),
        "lastSyncedAt": payload.get("lastSyncedAt"),
    }
    return publications_by_id, meta


def write_snapshot(publications_by_id, meta, sync_mode, date_range):
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    publications = list(publications_by_id.values())
    payload = {
        "staff": core.ACADEMIC_STAFF,
        "staffGroups": core.STAFF_GROUPS,
        "staffSources": core.STAFF_SOURCE_URLS,
        "lastSyncedAt": meta["lastSyncedAt"],
        "lastFullSyncAt": meta["lastFullSyncAt"],
        "lastSyncMode": sync_mode,
        "lastSyncDateRange": date_range,
        "totalPublications": len(publications),
        "publications": publications,
    }
    SNAPSHOT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def run_sync(full: bool):
    core.load_env_file()
    api_key = os.environ.get("SCOPUS_API_KEY", "").strip()
    if not api_key:
        print("SCOPUS_API_KEY is not configured in .env -- aborting sync")
        return 1

    existing_publications, meta = load_existing_snapshot()
    is_full_sync = full or not meta.get("lastFullSyncAt")
    date_range = core.default_five_year_range() if is_full_sync else incremental_date_range()
    sync_mode = "full" if is_full_sync else "incremental"

    print(f"[{datetime.now().isoformat(timespec='seconds')}] Starting {sync_mode} sync, date range {date_range}")

    try:
        total_results, fetched_count, affiliation_publications = core.fetch_affiliation_publications(
            api_key, page_size=25, start=0, date=date_range
        )
        staff_publication_map, staff_results = core.fetch_current_staff_matches(
            api_key, page_size=25, start=0, date=date_range
        )
        core.overlay_current_staff_matches(affiliation_publications, staff_publication_map)

        fetched = {publication["id"]: publication for publication in affiliation_publications}
        for pub_id, publication in staff_publication_map.items():
            fetched.setdefault(pub_id, publication)

        core.enrich_publications_with_metrics(api_key, list(fetched.values()))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        print(f"Scopus API returned an error ({error.code}): {detail}")
        return 1
    except urllib.error.URLError as error:
        print(f"Could not reach Scopus API: {error.reason}")
        return 1
    except Exception:
        traceback.print_exc()
        return 1

    existing_publications.update(fetched)
    synced_at = datetime.now(timezone.utc).isoformat()
    meta["lastSyncedAt"] = synced_at
    if is_full_sync:
        meta["lastFullSyncAt"] = synced_at

    payload = write_snapshot(existing_publications, meta, sync_mode, date_range)

    print(
        f"[{datetime.now().isoformat(timespec='seconds')}] Sync done: "
        f"{len(fetched)} publications fetched, {payload['totalPublications']} total stored in {SNAPSHOT_PATH}."
    )

    try:
        import sheets_export
        sheets_export.export_publications(payload["publications"])
    except Exception as error:  # best-effort, never fail the sync because of Sheets
        print(f"Google Sheets export skipped/failed: {error}")

    return 0


def main():
    parser = argparse.ArgumentParser(description="Sync Scopus publications into site-data/publications.json")
    parser.add_argument("--full", action="store_true", help="Force a full 5-year re-sync instead of the incremental window")
    args = parser.parse_args()
    sys.exit(run_sync(args.full))


if __name__ == "__main__":
    main()
