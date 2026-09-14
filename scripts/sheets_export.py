"""Mirrors synced publications into a Google Sheet for human browsing/editing.

Optional: only runs if GOOGLE_SHEET_ID and a service account credential are
configured. Missing config is not an error -- it just means Sheets export is
skipped (e.g. on a local dev machine that only cares about the JSON file).

Credentials can come from either:
  - GOOGLE_SERVICE_ACCOUNT_JSON: the service account key file contents, as a
    JSON string (how it's normally supplied via a GitHub Actions secret).
  - GOOGLE_SERVICE_ACCOUNT_FILE: a path to the service account key file.

The target sheet/tab must already exist and be shared with the service
account's email (Editor access) -- this script does not create either.
"""
import json
import os

SHEET_TAB = os.environ.get("GOOGLE_SHEET_TAB", "Publications")
COLUMNS = (
    "id", "year", "title", "journal", "type", "doi", "citations",
    "quartile", "citeScore", "authors", "matchedStaff", "matchedStaffGroups",
    "sdgs", "status", "affiliation",
)


def _row_for(publication):
    return [
        publication.get("id", ""),
        publication.get("year", ""),
        publication.get("title", ""),
        publication.get("journal", ""),
        publication.get("type", ""),
        publication.get("doi", ""),
        publication.get("citations", 0),
        publication.get("quartile", ""),
        publication.get("citeScore", ""),
        "; ".join(publication.get("authors", []) or []),
        "; ".join(publication.get("matchedStaff", []) or []),
        "; ".join(sorted(set((publication.get("matchedStaffGroups") or {}).values()))),
        "; ".join(sdg.get("code", "") for sdg in publication.get("sdgs", []) or [] if isinstance(sdg, dict)),
        publication.get("status", ""),
        publication.get("affiliation", ""),
    ]


def _load_credentials():
    from google.oauth2.service_account import Credentials

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    raw_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw_json:
        return Credentials.from_service_account_info(json.loads(raw_json), scopes=scopes)

    key_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    if key_file:
        return Credentials.from_service_account_file(key_file, scopes=scopes)

    return None


def export_publications(publications):
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not sheet_id:
        print("GOOGLE_SHEET_ID not set -- skipping Google Sheets export")
        return

    credentials = _load_credentials()
    if not credentials:
        print("No Google service account credentials configured -- skipping Google Sheets export")
        return

    from googleapiclient.discovery import build

    service = build("sheets", "v4", credentials=credentials)
    sorted_publications = sorted(
        publications, key=lambda item: (item.get("year", 0), item.get("citations", 0)), reverse=True
    )
    rows = [list(COLUMNS)] + [_row_for(publication) for publication in sorted_publications]

    service.spreadsheets().values().clear(
        spreadsheetId=sheet_id, range=SHEET_TAB
    ).execute()
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"{SHEET_TAB}!A1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()
    print(f"Exported {len(sorted_publications)} publications to Google Sheet {sheet_id} ({SHEET_TAB})")
