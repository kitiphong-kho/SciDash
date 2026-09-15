"""Shared Scopus fetching/normalization logic used by both the sync job and the web server."""
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOPUS_ENDPOINT = "https://api.elsevier.com/content/search/scopus"
SERIAL_TITLE_ENDPOINT = "https://api.elsevier.com/content/serial/title"
ABSTRACT_RETRIEVAL_ENDPOINT = "https://api.elsevier.com/content/abstract/eid"
AFFILIATION_WIDE_QUERY = 'AFFIL("Mae Fah Luang University") AND AFFIL("School of Science")'
STAFF_SOURCE_URLS = {
    "Chemistry": "https://science.mfu.ac.th/en/sci-staff/sci-academic-staff/sci-staff-chemistry.html",
    "Bioscience": "https://science.mfu.ac.th/en/sci-staff/sci-academic-staff/sci-staff-biological-science.html",
    "Material Science and Engineering": "https://science.mfu.ac.th/en/sci-staff/sci-academic-staff/sci-staff-material-and-enginee.html",
    "Computational Science": "https://science.mfu.ac.th/en/sci-staff/sci-academic-staff/sci-staff-computational-science.html",
}
STAFF_GROUPS = ("Chemistry", "Biology", "Material Science Engineering", "CIX")
STAFF_GROUP_BY_DEPARTMENT = {
    "Chemistry": "Chemistry",
    "Bioscience": "Biology",
    "Material Science and Engineering": "Material Science Engineering",
}
SOURCE_METRIC_CACHE = {}
SOURCE_METRIC_TTL_SECONDS = 86400
TITLE_PREFIXES = (
    "Adjunct Prof. Dr. ",
    "Assoc. Prof. Dr. ",
    "Asst. Prof. Dr. ",
    "Asst.Prof. Dr. ",
    "Prof. Dr. ",
    "Ajarn Dr. ",
)
SDG_KEYWORDS = (
    ("SDG 2", "Zero Hunger", (
        "agriculture", "agricultural", "crop", "food", "rice", "tea", "coffee", "mushroom",
        "edible", "soil", "plant growth", "postharvest", "nutrition",
    )),
    ("SDG 3", "Good Health and Well-being", (
        "health", "biomedical", "disease", "pathogen", "antimicrobial", "antibacterial",
        "antifungal", "antiviral", "biofilm", "cancer", "tumor", "neuro", "memory",
        "inflammation", "pharmac", "drug", "dengue", "epidemiology", "microbiota",
        "hypertension", "diabetes", "hospital", "clinical", "veterinary", "toxicity",
    )),
    ("SDG 4", "Quality Education", (
        "education", "teaching", "learning", "classroom", "curriculum", "student",
    )),
    ("SDG 6", "Clean Water and Sanitation", (
        "water", "wastewater", "aquatic", "freshwater", "river", "runoff", "nitrate",
        "sanitation", "filtration",
    )),
    ("SDG 7", "Affordable and Clean Energy", (
        "energy", "battery", "fuel cell", "solar", "photovoltaic", "methanol", "hydrogen",
        "biofuel",
    )),
    ("SDG 9", "Industry, Innovation and Infrastructure", (
        "material", "polymer", "composite", "membrane", "sensor", "nanomaterial",
        "nanoparticle", "engineering", "electrode", "geopolymer", "glass", "fiber",
        "thin film", "ceramic",
    )),
    ("SDG 11", "Sustainable Cities and Communities", (
        "urban", "city", "municipal", "air quality", "pm2 5", "particulate matter",
        "transport",
    )),
    ("SDG 12", "Responsible Consumption and Production", (
        "waste", "recycling", "biodegradable", "packaging", "green extraction", "biomass",
        "biochar", "sustainable", "life cycle", "by product",
    )),
    ("SDG 13", "Climate Action", (
        "climate", "emission", "carbon", "greenhouse", "atmospheric", "pollution",
        "volatile organic compound",
    )),
    ("SDG 14", "Life Below Water", (
        "marine", "mangrove", "coral", "seawater", "coastal",
    )),
    ("SDG 15", "Life on Land", (
        "biodiversity", "fungi", "fungal", "taxonomy", "phylogeny", "forest",
        "terrestrial", "plant pathogen", "lichen", "basidiomycota", "ascomycota",
        "species", "ecology",
    )),
)


def staff_record(name, department):
    clean_name = name
    for prefix in TITLE_PREFIXES:
        clean_name = clean_name.replace(prefix, "")
    parts = clean_name.split()
    return {
        "name": name,
        "first": parts[0],
        "last": parts[-1],
        "department": department,
        "academicGroup": STAFF_GROUP_BY_DEPARTMENT.get(department, "CIX"),
        "role": "Academic Staff",
    }


ACADEMIC_STAFF = [
    staff_record("Prof. Dr. Surat Laphookhieo", "Chemistry"),
    staff_record("Assoc. Prof. Dr. Orawan Suwantong", "Chemistry"),
    staff_record("Assoc. Prof. Dr. Patcharee Pripdeevech", "Chemistry"),
    staff_record("Asst. Prof. Dr. Acharavadee Pansanit", "Chemistry"),
    staff_record("Asst. Prof. Dr. Chuleeporn Thanomsilp", "Chemistry"),
    staff_record("Asst. Prof. Dr. Kanchana Watla-iad", "Chemistry"),
    staff_record("Asst. Prof. Dr. Patchara Punyamoonwongsa", "Chemistry"),
    staff_record("Asst. Prof. Dr. Patcharanan Choto", "Chemistry"),
    staff_record("Asst. Prof. Dr. Phunrawie Promnart", "Chemistry"),
    staff_record("Asst. Prof. Dr. Suwanna Deachathai", "Chemistry"),
    staff_record("Asst. Prof. Dr. Tharakorn Maneerat", "Chemistry"),
    staff_record("Asst. Prof. Dr. Thitipone Suwunwong", "Chemistry"),
    staff_record("Ajarn Dr. Prachak Inkaew", "Chemistry"),
    staff_record("Ajarn Dr. Thinnapong Wongpakdee", "Chemistry"),
    staff_record("Adjunct Prof. Dr. Kevin Hyde", "Bioscience"),
    staff_record("Assoc. Prof. Dr. Siam Popluechai", "Bioscience"),
    staff_record("Assoc. Prof. Dr. Siraprapa Mahanil", "Bioscience"),
    staff_record("Asst. Prof. Dr. Ekachai Chukeatirote", "Bioscience"),
    staff_record("Asst. Prof. Dr. Khanobporn Tangtrakulwanich", "Bioscience"),
    staff_record("Asst. Prof. Dr. Kitiphong Khongphinitbunjong", "Bioscience"),
    staff_record("Asst. Prof. Dr. Nanthanit Jaruseranee", "Bioscience"),
    staff_record("Asst. Prof. Dr. Natsaran Saichana", "Bioscience"),
    staff_record("Asst. Prof. Dr. Panom Winyayong", "Bioscience"),
    staff_record("Asst. Prof. Dr. Pattana Kakumyan", "Bioscience"),
    staff_record("Asst. Prof. Dr. Plaipol Dedvisitsakul", "Bioscience"),
    staff_record("Asst. Prof. Dr. Prapassorn Damrongkool Eungwanichayapant", "Bioscience"),
    staff_record("Asst. Prof. Dr. Ruvishika Jayawardena", "Bioscience"),
    staff_record("Asst. Prof. Dr. Somrudee Nilthong", "Bioscience"),
    staff_record("Asst. Prof. Dr. Sunita Chamyuang", "Bioscience"),
    staff_record("Asst. Prof. Dr. Amorn Owatworakit", "Bioscience"),
    staff_record("Ajarn Dr. Chitrabhanu Sharma Bhunjun", "Bioscience"),
    staff_record("Ajarn Dr. Jantrararuk Tovaranonte", "Bioscience"),
    staff_record("Ajarn Dr. Kittirat Saharat", "Bioscience"),
    staff_record("Asst. Prof. Dr. Kritsakorn Saninjuk", "Bioscience"),
    staff_record("Ajarn Dr. Naritsada Thongklang", "Bioscience"),
    staff_record("Asst. Prof. Dr. Natthawut Yodsuwan", "Bioscience"),
    staff_record("Assoc. Prof. Dr. Darunee Wattanasiriwech", "Material Science and Engineering"),
    staff_record("Assoc. Prof. Dr. Nattakan Soykeabkaew", "Material Science and Engineering"),
    staff_record("Assoc. Prof. Dr. Suthee Wattanasiriwech", "Material Science and Engineering"),
    staff_record("Asst. Prof. Dr. Nattaya Tawichai", "Material Science and Engineering"),
    staff_record("Asst. Prof. Dr. Nuttachat Wisittipanit", "Material Science and Engineering"),
    staff_record("Asst. Prof. Dr. Prathak Jienkulsawad", "Material Science and Engineering"),
    staff_record("Asst. Prof. Dr. Sitthi Duangphet", "Material Science and Engineering"),
    staff_record("Asst. Prof. Dr. Somwan Chumphongphan", "Material Science and Engineering"),
    staff_record("Asst. Prof. Dr. Tophan Thandorn", "Material Science and Engineering"),
    staff_record("Asst. Prof. Dr. Uraiwan Intatha", "Material Science and Engineering"),
    staff_record("Assoc. Prof. Dr. Piyanuch Siriwat", "Computational Science"),
    staff_record("Asst. Prof. Dr. Anant Eungwanichayapant", "Computational Science"),
    staff_record("Asst. Prof. Dr. Rungrote Nilthong", "Computational Science"),
    staff_record("Asst. Prof. Dr. Theeradech Mookum", "Computational Science"),
]
STAFF_BY_NAME = {staff["name"]: staff for staff in ACADEMIC_STAFF}


def load_env_file() -> None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        return

    for line in env_file.read_text().splitlines():
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("#") or "=" not in clean_line:
            continue
        key, value = clean_line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def text_value(value, default=""):
    if value is None:
        return default
    if isinstance(value, list):
        return text_value(value[0], default) if value else default
    return str(value)


def normalize_scopus_entry(entry, index, matched_staff=None):
    cover_date = text_value(entry.get("prism:coverDate"))
    year = int(cover_date[:4]) if cover_date[:4].isdigit() else 0
    doi = text_value(entry.get("prism:doi"))
    eid = text_value(entry.get("eid"), f"SCOPUS-{index + 1}")
    raw_authors = entry.get("author") if isinstance(entry.get("author"), list) else []
    authors = [
        text_value(author.get("authname") or author.get("ce:indexed-name"))
        for author in raw_authors
        if isinstance(author, dict)
    ]
    if not authors:
        authors = [text_value(entry.get("dc:creator"), "Unknown author")]

    affiliations = entry.get("affiliation") if isinstance(entry.get("affiliation"), list) else []
    affiliation_text = "; ".join(
        filter(
            None,
            [
                text_value(item.get("affilname") or item.get("affiliation-name"))
                for item in affiliations
                if isinstance(item, dict)
            ],
        )
    )
    if not affiliation_text:
        affiliation_text = "Affiliation not returned by Scopus Search"

    # Scopus already returns a country per affiliation -- use it directly
    # instead of guessing country from the affiliation text with keywords.
    affiliation_countries = sorted({
        text_value(item.get("affiliation-country"))
        for item in affiliations
        if isinstance(item, dict) and text_value(item.get("affiliation-country"))
    })

    matched_staff = matched_staff or []
    publication = {
        "id": eid,
        "year": year,
        "title": text_value(entry.get("dc:title"), "Untitled publication"),
        "doi": doi or eid,
        "journal": text_value(entry.get("prism:publicationName"), "Unknown source"),
        "sourceId": text_value(entry.get("source-id")),
        "issn": text_value(entry.get("prism:issn")),
        "eIssn": text_value(entry.get("prism:eIssn")),
        "quartile": "NA",
        "quartileYear": "",
        "citeScore": "",
        "citeScorePercentile": "",
        "citations": int(text_value(entry.get("citedby-count"), "0") or 0),
        "authors": authors,
        "matchedStaff": matched_staff,
        "affiliation": affiliation_text,
        "affiliationCountries": affiliation_countries,
        "status": "verified" if matched_staff else "review",
        "reviewReason": "Quartile and school-level affiliation should be verified",
        "schoolAffiliationVerified": bool(matched_staff),
        "schoolAffiliationScope": "School of Science, Mae Fah Luang University",
        "schoolFilterEvidence": "Matched by Scopus query: staff last name + AFFIL(Mae Fah Luang University) + AFFIL(School of Science)",
        "type": text_value(entry.get("subtypeDescription"), "Publication"),
    }
    publication["sdgs"] = classify_sdgs(publication)
    publication["sdgMethod"] = "Rule-based keyword inference from title, journal, and publication type"
    return publication


def is_publication_entry(entry):
    if not isinstance(entry, dict):
        return False
    if entry.get("error"):
        return False
    return bool(entry.get("eid") or entry.get("dc:title"))


def normalized_name_token(value):
    return re.sub(r"[^a-z0-9]", "", value.lower())


def normalized_word_tokens(value):
    return [token for token in re.split(r"[^a-z0-9]+", value.lower()) if token]


def author_matches_staff(author, staff):
    author_token = normalized_name_token(author)
    staff_last = normalized_name_token(staff["last"])
    if not staff_last or staff_last not in author_token:
        return False

    first_initial = staff["first"][:1].lower()
    if not first_initial:
        return True

    author_tokens = normalized_word_tokens(author)
    staff_first = staff["first"].lower()
    if staff_first in author_tokens:
        return True

    return any(token.startswith(first_initial) and token != staff["last"].lower() for token in author_tokens)


def detect_staff_matches(publication):
    matched_staff = []
    matched_roles = {}
    matched_groups = {}

    for staff in ACADEMIC_STAFF:
        if any(author_matches_staff(author, staff) for author in publication.get("authors", [])):
            matched_staff.append(staff["name"])
            matched_roles[staff["name"]] = classify_author_role(publication, staff)
            matched_groups[staff["name"]] = staff["academicGroup"]

    publication["matchedStaff"] = sorted(matched_staff)
    publication["matchedStaffRoles"] = matched_roles
    publication["matchedStaffGroups"] = matched_groups
    publication["academicStaffMatchMethod"] = "author indexed-name last name plus first-initial match"
    return publication


def normalized_keyword_text(value):
    clean_value = re.sub(r"[^a-z0-9]+", " ", text_value(value).lower()).strip()
    return f" {clean_value} "


def classify_sdgs(publication):
    search_text = normalized_keyword_text(
        " ".join([
            publication.get("title", ""),
            publication.get("journal", ""),
            publication.get("type", ""),
        ])
    )
    matched_sdgs = []

    for code, label, keywords in SDG_KEYWORDS:
        matched_terms = []
        for keyword in keywords:
            clean_keyword = normalized_keyword_text(keyword).strip()
            if clean_keyword and f" {clean_keyword} " in search_text:
                matched_terms.append(keyword)
        if matched_terms:
            matched_sdgs.append({
                "code": code,
                "label": label,
                "matchedTerms": matched_terms[:4],
            })

    return matched_sdgs[:3]


def classify_author_role(publication, staff):
    first_author = publication.get("authors", [""])[0]
    if author_matches_staff(first_author, staff):
        return "first_author"
    return "co_author"


def build_staff_query(staff):
    return (
        f'AUTHLASTNAME({staff["last"]}) '
        f'AND {AFFILIATION_WIDE_QUERY}'
    )


def request_scopus(api_key, query, count, start, date):
    scopus_params = {
        "query": query,
        "count": count,
        "start": start,
        # STANDARD view truncates the returned author list (sometimes to a
        # single name), which made it impossible to verify that a per-staff
        # AUTHLASTNAME(...) hit was actually written by that staff member
        # rather than a different person who happens to share a surname.
        # COMPLETE returns the full author list so fetch_staff_publications
        # can verify authorship locally (see author_matches_staff below).
        "view": "COMPLETE",
    }
    if date:
        scopus_params["date"] = date

    url = f"{SCOPUS_ENDPOINT}?{urllib.parse.urlencode(scopus_params)}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "X-ELS-APIKey": api_key,
        },
    )

    cert_file = os.environ.get("SSL_CERT_FILE") or "/etc/ssl/cert.pem"
    context = ssl.create_default_context(cafile=cert_file if Path(cert_file).exists() else None)

    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=25, context=context) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
            time.sleep(2.5 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2.5 * (attempt + 1))


def request_serial_title_once(api_key, params):
    url = f"{SERIAL_TITLE_ENDPOINT}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "X-ELS-APIKey": api_key,
        },
    )
    cert_file = os.environ.get("SSL_CERT_FILE") or "/etc/ssl/cert.pem"
    context = ssl.create_default_context(cafile=cert_file if Path(cert_file).exists() else None)

    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=25, context=context) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 1:
                return None
            time.sleep(1.5)
        except (urllib.error.URLError, TimeoutError):
            if attempt == 1:
                return None
            time.sleep(1.5)
    return None


def serial_title_candidates(publication):
    candidates = []
    if publication.get("sourceId"):
        candidates.append(("source-id", publication["sourceId"]))
    if publication.get("issn"):
        candidates.append(("issn", publication["issn"]))
    if publication.get("eIssn"):
        candidates.append(("issn", publication["eIssn"]))
    if publication.get("journal"):
        candidates.append(("title", publication["journal"]))
    return candidates


def request_serial_title(api_key, publication):
    for key, value in serial_title_candidates(publication):
        cache_key = f"{key}:{value}"
        cached = SOURCE_METRIC_CACHE.get(cache_key)
        if cached:
            timestamp, payload = cached
            if datetime.now().timestamp() - timestamp <= SOURCE_METRIC_TTL_SECONDS:
                metric = extract_source_metric(payload)
                if metric:
                    return payload
                SOURCE_METRIC_CACHE.pop(cache_key, None)

        payload = request_serial_title_once(api_key, {"view": "CITESCORE", key: value})
        metric = extract_source_metric(payload)
        if metric:
            SOURCE_METRIC_CACHE[cache_key] = (datetime.now().timestamp(), payload)
            return payload

    return None


def list_value(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def quartile_from_percentile(percentile):
    if percentile >= 75:
        return "Q1"
    if percentile >= 50:
        return "Q2"
    if percentile >= 25:
        return "Q3"
    return "Q4"


def extract_source_metric(payload):
    if not payload:
        return None

    response = payload.get("serial-metadata-response", {})
    entries = list_value(response.get("entry"))
    if not entries:
        return None

    entry = entries[0]
    year_info_list = entry.get("citeScoreYearInfoList", {})
    year_infos = list_value(year_info_list.get("citeScoreYearInfo"))
    if not year_infos:
        return None

    complete_infos = [item for item in year_infos if item.get("@status") == "Complete"]
    selected_info = complete_infos[0] if complete_infos else year_infos[0]
    info_lists = list_value(selected_info.get("citeScoreInformationList"))
    cite_infos = []
    for item in info_lists:
        cite_infos.extend(list_value(item.get("citeScoreInfo")))

    best = None
    for cite_info in cite_infos:
        ranks = list_value(cite_info.get("citeScoreSubjectRank"))
        for rank in ranks:
            try:
                percentile = int(text_value(rank.get("percentile"), "0") or 0)
            except ValueError:
                continue
            if best is None or percentile > best["percentile"]:
                best = {
                    "percentile": percentile,
                    "subjectCode": text_value(rank.get("subjectCode")),
                    "rank": text_value(rank.get("rank")),
                    "citeScore": text_value(cite_info.get("citeScore")),
                }

    if not best:
        return None

    return {
        "quartile": quartile_from_percentile(best["percentile"]),
        "quartileYear": text_value(selected_info.get("@year")),
        "citeScore": best["citeScore"],
        "citeScorePercentile": str(best["percentile"]),
        "quartileSource": "Scopus CiteScore",
    }


def enrich_publications_with_metrics(api_key, publications):
    source_publications = {}
    for publication in publications:
        source_key = publication.get("sourceId") or publication.get("issn") or publication.get("eIssn")
        if source_key and source_key not in source_publications:
            source_publications[source_key] = publication

    source_metrics = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_map = {
            executor.submit(request_serial_title, api_key, publication): source_key
            for source_key, publication in source_publications.items()
        }
        for future in as_completed(future_map):
            source_key = future_map[future]
            try:
                source_metrics[source_key] = extract_source_metric(future.result())
            except Exception:
                source_metrics[source_key] = None

    for publication in publications:
        source_key = publication.get("sourceId") or publication.get("issn") or publication.get("eIssn")
        metric = source_metrics.get(source_key)
        if metric:
            publication.update(metric)


def request_abstract_retrieval(api_key, eid):
    url = f"{ABSTRACT_RETRIEVAL_ENDPOINT}/{urllib.parse.quote(eid)}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "X-ELS-APIKey": api_key,
        },
    )
    cert_file = os.environ.get("SSL_CERT_FILE") or "/etc/ssl/cert.pem"
    context = ssl.create_default_context(cafile=cert_file if Path(cert_file).exists() else None)

    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=25, context=context) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 1:
                return None
            time.sleep(1.5)
        except (urllib.error.URLError, TimeoutError):
            if attempt == 1:
                return None
            time.sleep(1.5)
    return None


def extract_corresponding_author_names(payload):
    """Returns the indexed-name strings (e.g. "Bera I.") of every corresponding
    author listed for a publication, per Scopus Abstract Retrieval's
    `correspondence` block. Empty list if the publication has none on record
    or the lookup failed."""
    if not payload:
        return []

    head = (
        payload.get("abstracts-retrieval-response", {})
        .get("item", {})
        .get("bibrecord", {})
        .get("head", {})
    )
    correspondence = list_value(head.get("correspondence"))
    names = []
    for entry in correspondence:
        person = entry.get("person", {}) if isinstance(entry, dict) else {}
        indexed_name = text_value(person.get("ce:indexed-name"))
        if indexed_name:
            names.append(indexed_name)
    return names


def enrich_publications_with_corresponding_authors(api_key, publications):
    """Fetches Scopus Abstract Retrieval per publication (one API call each --
    only called for publications actually being (re)fetched this sync run, not
    the whole accumulated history) and marks matchedStaffRoles entries as
    "corresponding_author" where a listed staff member is on the
    correspondence list. Best-effort: a lookup failure just leaves the
    existing first_author/co_author role in place."""
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_map = {
            executor.submit(request_abstract_retrieval, api_key, publication["id"]): publication
            for publication in publications
            if publication.get("matchedStaff")
        }
        for future in as_completed(future_map):
            publication = future_map[future]
            try:
                corresponding_names = extract_corresponding_author_names(future.result())
            except Exception:
                continue
            if not corresponding_names:
                continue

            roles = publication.setdefault("matchedStaffRoles", {})
            for staff_name in publication.get("matchedStaff", []):
                staff = STAFF_BY_NAME.get(staff_name)
                if not staff:
                    continue
                if any(author_matches_staff(name, staff) for name in corresponding_names):
                    roles[staff_name] = "corresponding_author"


def parse_positive_int(value, default, maximum):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return min(max(parsed, 1), maximum)


def parse_non_negative_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(parsed, 0)


def default_five_year_range():
    end_year = datetime.now().year
    start_year = end_year - 4
    return f"{start_year}-{end_year}"


def merge_publication(merged, publication, staff_name):
    existing = merged.get(publication["id"])
    if existing:
        existing_staff = set(existing.get("matchedStaff", []))
        existing_staff.add(staff_name)
        existing["matchedStaff"] = sorted(existing_staff)
        existing_roles = existing.setdefault("matchedStaffRoles", {})
        existing_roles.update(publication.get("matchedStaffRoles", {}))
        existing_groups = existing.setdefault("matchedStaffGroups", {})
        existing_groups.update(publication.get("matchedStaffGroups", {}))
        existing_sdg_codes = {item.get("code") for item in existing.get("sdgs", []) if isinstance(item, dict)}
        for sdg in publication.get("sdgs", []):
            if isinstance(sdg, dict) and sdg.get("code") not in existing_sdg_codes:
                existing.setdefault("sdgs", []).append(sdg)
        existing["status"] = "verified"
        existing["reviewReason"] = "Multiple listed academic staff matched this publication"
        return
    merged[publication["id"]] = publication


def fetch_staff_publications(api_key, staff, page_size, start, date):
    query = build_staff_query(staff)
    staff_total = None
    fetched_count = 0
    next_start = start
    publications = []

    while staff_total is None or next_start < staff_total:
        payload = request_scopus(api_key, query, str(page_size), str(next_start), date)
        search_results = payload.get("search-results", {})
        entries = search_results.get("entry", [])
        if isinstance(entries, dict):
            entries = [entries]
        entries = [entry for entry in entries if is_publication_entry(entry)]

        staff_total = int(text_value(search_results.get("opensearch:totalResults"), "0") or 0)
        fetched_count += len(entries)

        for index, entry in enumerate(entries):
            publication = normalize_scopus_entry(entry, next_start + index, [staff["name"]])
            # AUTHLASTNAME(...) only filters by surname on Scopus's side, so a
            # hit here does not by itself prove this staff member wrote the
            # paper -- another person sharing the same surname would match
            # too. Verify against the actual (full, COMPLETE-view) author
            # list before attributing the paper to them.
            if not any(author_matches_staff(author, staff) for author in publication["authors"]):
                continue
            publication["matchedStaffRoles"] = {
                staff["name"]: classify_author_role(publication, staff)
            }
            publication["matchedStaffGroups"] = {
                staff["name"]: staff["academicGroup"]
            }
            publications.append(publication)

        if not entries:
            break
        next_start += page_size

    return (
        {
            "name": staff["name"],
            "last": staff["last"],
            "department": staff["department"],
            "academicGroup": staff["academicGroup"],
            "totalResults": staff_total or 0,
            "fetchedResults": fetched_count,
        },
        publications,
    )


def fetch_affiliation_publications(api_key, page_size, start, date):
    staff_total = None
    fetched_count = 0
    next_start = start
    publications = []

    while staff_total is None or next_start < staff_total:
        payload = request_scopus(api_key, AFFILIATION_WIDE_QUERY, str(page_size), str(next_start), date)
        search_results = payload.get("search-results", {})
        entries = search_results.get("entry", [])
        if isinstance(entries, dict):
            entries = [entries]
        entries = [entry for entry in entries if is_publication_entry(entry)]

        staff_total = int(text_value(search_results.get("opensearch:totalResults"), "0") or 0)
        fetched_count += len(entries)

        for index, entry in enumerate(entries):
            publication = normalize_scopus_entry(entry, next_start + index, [])
            detect_staff_matches(publication)
            publication["status"] = "verified"
            publication["reviewReason"] = "Matched by affiliation-wide School of Science query"
            publication["schoolAffiliationVerified"] = True
            publication["schoolAffiliationScope"] = "School of Science, Mae Fah Luang University"
            publication["schoolFilterEvidence"] = f"Matched by Scopus query: {AFFILIATION_WIDE_QUERY}"
            publications.append(publication)

        if not entries:
            break
        next_start += page_size

    return staff_total or 0, fetched_count, publications


def fetch_current_staff_matches(api_key, page_size, start, date):
    merged = {}
    staff_results = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_map = {
            executor.submit(fetch_staff_publications, api_key, staff, page_size, start, date): staff
            for staff in ACADEMIC_STAFF
        }
        for future in as_completed(future_map):
            staff_result, staff_publications = future.result()
            staff_results.append(staff_result)
            for publication in staff_publications:
                merge_publication(merged, publication, staff_result["name"])

    staff_order = {staff["name"]: index for index, staff in enumerate(ACADEMIC_STAFF)}
    staff_results.sort(key=lambda item: staff_order.get(item["name"], 9999))
    return merged, staff_results


def overlay_current_staff_matches(publications, staff_publication_map):
    for publication in publications:
        staff_publication = staff_publication_map.get(publication["id"])
        if not staff_publication:
            continue
        publication["matchedStaff"] = staff_publication.get("matchedStaff", [])
        publication["matchedStaffRoles"] = staff_publication.get("matchedStaffRoles", {})
        publication["matchedStaffGroups"] = staff_publication.get("matchedStaffGroups", {})
        publication["academicStaffMatchMethod"] = "overlaid from current academic staff Scopus queries by EID"
