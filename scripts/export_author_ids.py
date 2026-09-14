#!/usr/bin/env python3
import csv
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHOR_SEARCH_ENDPOINT = "https://api.elsevier.com/content/search/author"

sys.path.insert(0, str(ROOT))
from scripts.start_server import ACADEMIC_STAFF, load_env_file, text_value  # noqa: E402


def make_ssl_context():
    cert_file = os.environ.get("SSL_CERT_FILE") or "/etc/ssl/cert.pem"
    if Path(cert_file).exists():
        return ssl.create_default_context(cafile=cert_file)
    return ssl._create_unverified_context()


def request_author_search(api_key, query, count=10):
    params = urllib.parse.urlencode({"query": query, "count": count})
    request = urllib.request.Request(
        f"{AUTHOR_SEARCH_ENDPOINT}?{params}",
        headers={
            "Accept": "application/json",
            "X-ELS-APIKey": api_key,
        },
    )
    context = make_ssl_context()

    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=30, context=context) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise
            time.sleep(2.0 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise
            time.sleep(2.0 * (attempt + 1))


def entries_from_response(payload):
    search_results = payload.get("search-results", {}) if isinstance(payload, dict) else {}
    entries = search_results.get("entry", [])
    return entries if isinstance(entries, list) else []


def author_id_from_entry(entry):
    identifier = text_value(entry.get("dc:identifier"))
    return identifier.replace("AUTHOR_ID:", "").strip()


def preferred_name(entry):
    name = entry.get("preferred-name") if isinstance(entry.get("preferred-name"), dict) else {}
    surname = text_value(name.get("surname"))
    given = text_value(name.get("given-name"))
    initials = text_value(name.get("initials"))
    return surname, given, initials


def current_affiliation(entry):
    affiliation = entry.get("affiliation-current")
    if isinstance(affiliation, list):
        affiliation = affiliation[0] if affiliation else {}
    return affiliation if isinstance(affiliation, dict) else {}


def subject_areas(entry):
    areas = entry.get("subject-area")
    if isinstance(areas, dict):
        areas = [areas]
    if not isinstance(areas, list):
        return ""
    labels = []
    for area in areas[:5]:
        if isinstance(area, dict):
            labels.append(text_value(area.get("$")))
    return "; ".join(label for label in labels if label)


def name_matches(staff, entry):
    surname, given, initials = preferred_name(entry)
    staff_first = staff["first"].lower()
    staff_last = staff["last"].lower()
    surname_match = surname.lower() == staff_last
    given_text = given.lower()
    first_match = given_text == staff_first or staff_first in given_text.split()
    initial_match = bool(initials) and initials[:1].lower() == staff_first[:1]
    return surname_match, first_match, initial_match


def score_candidate(staff, entry):
    surname_match, first_match, initial_match = name_matches(staff, entry)
    affiliation = current_affiliation(entry)
    affiliation_name = text_value(affiliation.get("affiliation-name"))
    affiliation_country = text_value(affiliation.get("affiliation-country"))
    affiliation_lower = affiliation_name.lower()

    score = 0
    reasons = []
    if surname_match:
        score += 5
        reasons.append("surname exact")
    if first_match:
        score += 5
        reasons.append("given name exact")
    elif initial_match:
        score += 2
        reasons.append("first initial match")
    if "mae fah luang" in affiliation_lower:
        score += 5
        reasons.append("current affiliation Mae Fah Luang University")
    if affiliation_country.lower() == "thailand":
        score += 1
        reasons.append("current affiliation country Thailand")

    if score >= 15:
        confidence = "high"
    elif score >= 10:
        confidence = "medium"
    else:
        confidence = "needs_review"
    return score, confidence, "; ".join(reasons)


def candidate_row(staff, entry, query_labels, recommended=False):
    author_id = author_id_from_entry(entry)
    surname, given, initials = preferred_name(entry)
    affiliation = current_affiliation(entry)
    score, confidence, reason = score_candidate(staff, entry)
    return {
        "staffName": staff["name"],
        "department": staff["department"],
        "academicGroup": staff["academicGroup"],
        "staffFirstName": staff["first"],
        "staffLastName": staff["last"],
        "scopusAuthorId": author_id,
        "recommended": "yes" if recommended else "no",
        "matchConfidence": confidence,
        "matchScore": score,
        "matchReason": reason,
        "scopusPreferredSurname": surname,
        "scopusPreferredGivenName": given,
        "scopusInitials": initials,
        "documentCount": text_value(entry.get("document-count")),
        "currentAffiliationId": text_value(affiliation.get("affiliation-id")),
        "currentAffiliationName": text_value(affiliation.get("affiliation-name")),
        "currentAffiliationCity": text_value(affiliation.get("affiliation-city")),
        "currentAffiliationCountry": text_value(affiliation.get("affiliation-country")),
        "orcid": text_value(entry.get("orcid")),
        "subjectAreas": subject_areas(entry),
        "scopusAuthorUrl": text_value(entry.get("prism:url")),
        "apiQueriesUsed": " | ".join(query_labels),
        "note": "",
    }


def fetch_staff_candidates(api_key, staff):
    queries = [
        (
            "name_exact",
            f'AUTHLASTNAME({staff["last"]}) AND AUTHFIRST({staff["first"]})',
        ),
        (
            "mfu_affiliation",
            f'AUTHLASTNAME({staff["last"]}) AND AFFIL("Mae Fah Luang University")',
        ),
    ]
    candidates = {}
    labels_by_id = {}
    errors = []

    for label, query in queries:
        try:
            payload = request_author_search(api_key, query)
        except Exception as error:
            errors.append(f"{label}: {error}")
            continue
        for entry in entries_from_response(payload):
            author_id = author_id_from_entry(entry)
            if not author_id:
                continue
            candidates[author_id] = entry
            labels_by_id.setdefault(author_id, []).append(f"{label}: {query}")
        time.sleep(0.15)

    if not candidates:
        return [{
            "staffName": staff["name"],
            "department": staff["department"],
            "academicGroup": staff["academicGroup"],
            "staffFirstName": staff["first"],
            "staffLastName": staff["last"],
            "scopusAuthorId": "",
            "recommended": "no",
            "matchConfidence": "not_found",
            "matchScore": 0,
            "matchReason": "",
            "scopusPreferredSurname": "",
            "scopusPreferredGivenName": "",
            "scopusInitials": "",
            "documentCount": "",
            "currentAffiliationId": "",
            "currentAffiliationName": "",
            "currentAffiliationCity": "",
            "currentAffiliationCountry": "",
            "orcid": "",
            "subjectAreas": "",
            "scopusAuthorUrl": "",
            "apiQueriesUsed": " | ".join(f"{label}: {query}" for label, query in queries),
            "note": "; ".join(errors) if errors else "No author candidate returned by Scopus Author Search API",
        }]

    ranked = sorted(
        candidates.items(),
        key=lambda item: (
            score_candidate(staff, item[1])[0],
            int(text_value(item[1].get("document-count"), "0") or 0),
        ),
        reverse=True,
    )
    best_id = ranked[0][0]
    rows = [
        candidate_row(staff, entry, labels_by_id.get(author_id, []), recommended=(author_id == best_id))
        for author_id, entry in ranked
    ]
    return rows


def main():
    load_env_file()
    api_key = os.environ.get("SCOPUS_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("SCOPUS_API_KEY is not configured in .env")

    output_path = ROOT / "staff_scopus_author_ids.csv"
    recommended_output_path = ROOT / "staff_scopus_author_ids_recommended.csv"
    rows = []
    for index, staff in enumerate(ACADEMIC_STAFF, start=1):
        print(f"{index:02d}/{len(ACADEMIC_STAFF)} {staff['name']}")
        rows.extend(fetch_staff_candidates(api_key, staff))

    fieldnames = list(rows[0].keys()) if rows else []
    with output_path.open("w", newline="", encoding="utf-8-sig") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    recommended_rows = [row for row in rows if row.get("recommended") == "yes"]
    with recommended_output_path.open("w", newline="", encoding="utf-8-sig") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(recommended_rows)

    recommended = sum(1 for row in rows if row.get("recommended") == "yes")
    not_found = sum(1 for row in rows if row.get("matchConfidence") == "not_found")
    print(f"written={output_path}")
    print(f"written={recommended_output_path}")
    print(f"rows={len(rows)} recommended={recommended} not_found={not_found}")


if __name__ == "__main__":
    main()
