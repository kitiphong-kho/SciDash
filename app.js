let publications = [
  {
    id: "SCID-001",
    year: 2026,
    title: "Machine learning assisted screening of bioactive compounds from northern Thai plants",
    doi: "10.1016/j.scidash.2026.001",
    journal: "Journal of Natural Products Analytics",
    quartile: "Q1",
    citations: 34,
    authors: ["Assoc. Prof. Narin S.", "Dr. Pimchanok W.", "Dr. Kittipong T."],
    affiliation: "School of Science, Mae Fah Luang University",
    status: "verified",
    type: "Article",
  },
  {
    id: "SCID-002",
    year: 2026,
    title: "Remote sensing indicators for watershed health in upper northern Thailand",
    doi: "10.3390/rsdash.2026.014",
    journal: "Environmental Monitoring Letters",
    quartile: "Q2",
    citations: 18,
    authors: ["Dr. Mayuree C.", "Dr. Anucha P."],
    affiliation: "Mae Fah Luang University; School of Science",
    status: "verified",
    type: "Article",
  },
  {
    id: "SCID-003",
    year: 2025,
    title: "Functional polymer membranes for selective heavy metal adsorption",
    doi: "10.1021/poly.2025.219",
    journal: "Applied Polymer Research",
    quartile: "Q1",
    citations: 52,
    authors: ["Prof. Siriporn K.", "Dr. Kittipong T."],
    affiliation: "School of Science, MFU",
    status: "verified",
    type: "Review",
  },
  {
    id: "SCID-004",
    year: 2025,
    title: "A comparative genomic survey of pathogenic fungi in tropical soils",
    doi: "10.1186/genbio.2025.072",
    journal: "Tropical Genomics",
    quartile: "Q2",
    citations: 27,
    authors: ["Dr. Pimchanok W.", "Dr. Arthit L."],
    affiliation: "School of Science, Mae Fah Luang University",
    status: "review",
    reviewReason: "Author spelling differs from staff registry",
    type: "Article",
  },
  {
    id: "SCID-005",
    year: 2024,
    title: "Low-cost electrochemical sensors for nitrate detection in agricultural runoff",
    doi: "10.1016/sens.2024.044",
    journal: "Sensors and Actuators in Chemistry",
    quartile: "Q1",
    citations: 61,
    authors: ["Dr. Anucha P.", "Assoc. Prof. Narin S."],
    affiliation: "Mae Fah Luang University",
    status: "verified",
    type: "Article",
  },
  {
    id: "SCID-006",
    year: 2024,
    title: "Mathematical modelling of dengue transmission under seasonal climate variance",
    doi: "10.1371/model.2024.086",
    journal: "Computational Epidemiology",
    quartile: "Q2",
    citations: 39,
    authors: ["Dr. Mayuree C.", "Dr. Chaiwat R."],
    affiliation: "School of Science, Mae Fah Luang University",
    status: "verified",
    type: "Article",
  },
  {
    id: "SCID-007",
    year: 2023,
    title: "Biodegradable packaging films reinforced by cellulose nanofibers",
    doi: "10.1016/matbio.2023.331",
    journal: "Sustainable Materials Today",
    quartile: "Q1",
    citations: 74,
    authors: ["Prof. Siriporn K.", "Dr. Pimchanok W."],
    affiliation: "School of Science, Mae Fah Luang University",
    status: "verified",
    type: "Article",
  },
  {
    id: "SCID-008",
    year: 2023,
    title: "High performance computing workflow for protein docking studies",
    doi: "10.1109/hpcbio.2023.102",
    journal: "Computational Biology Systems",
    quartile: "Q3",
    citations: 13,
    authors: ["Dr. Kittipong T.", "Dr. Chaiwat R."],
    affiliation: "MFU School of Science",
    status: "review",
    reviewReason: "Affiliation abbreviation needs confirmation",
    type: "Conference Paper",
  },
  {
    id: "SCID-009",
    year: 2022,
    title: "Antioxidant profile of edible mushrooms collected in Chiang Rai",
    doi: "10.1016/foodchem.2022.118",
    journal: "Food Chemistry Insights",
    quartile: "Q2",
    citations: 46,
    authors: ["Assoc. Prof. Narin S.", "Dr. Arthit L."],
    affiliation: "School of Science, Mae Fah Luang University",
    status: "verified",
    type: "Article",
  },
  {
    id: "SCID-010",
    year: 2022,
    title: "Data-driven optimization of laboratory safety inspection schedules",
    doi: "10.1080/safety.2022.011",
    journal: "Science Operations Review",
    quartile: "Q4",
    citations: 7,
    authors: ["Dr. Chaiwat R.", "Dr. Mayuree C."],
    affiliation: "Mae Fah Luang University",
    status: "review",
    reviewReason: "School-level affiliation is missing",
    type: "Article",
  },
  {
    id: "SCID-011",
    year: 2021,
    title: "Nanoparticle assisted detection of trace pesticides in tea plantations",
    doi: "10.1021/nanoagri.2021.055",
    journal: "Analytical Nanoscience",
    quartile: "Q1",
    citations: 88,
    authors: ["Dr. Anucha P.", "Prof. Siriporn K."],
    affiliation: "School of Science, Mae Fah Luang University",
    status: "verified",
    type: "Article",
  },
  {
    id: "SCID-012",
    year: 2021,
    title: "Cloud-based dashboarding for university research management",
    doi: "10.1145/researchops.2021.208",
    journal: "Research Information Systems",
    quartile: "Q3",
    citations: 15,
    authors: ["Dr. Chaiwat R.", "Dr. Kittipong T."],
    affiliation: "School of Science, Mae Fah Luang University",
    status: "verified",
    type: "Article",
  },
];
const samplePublications = publications.map((item) => ({ ...item, authors: [...item.authors] }));
publications = [];
let staffDirectory = [];

const state = {
  dataScope: "staff",
  selectedYears: new Set(),
  author: "",
  staffGroup: "all",
  authorRole: "all",
  quartile: "all",
  search: "",
  dataSource: "empty",
};

const elements = {
  dataScopeFilter: document.querySelector("#dataScopeFilter"),
  yearChecklist: document.querySelector("#yearChecklist"),
  authorFilter: document.querySelector("#authorFilter"),
  authorOptions: document.querySelector("#authorOptions"),
  staffGroupFilter: document.querySelector("#staffGroupFilter"),
  authorRoleFilter: document.querySelector("#authorRoleFilter"),
  quartileFilter: document.querySelector("#quartileFilter"),
  searchInput: document.querySelector("#searchInput"),
  totalPublications: document.querySelector("#totalPublications"),
  internationalCollaborations: document.querySelector("#internationalCollaborations"),
  internationalDelta: document.querySelector("#internationalDelta"),
  totalCitations: document.querySelector("#totalCitations"),
  topQuartileRatio: document.querySelector("#topQuartileRatio"),
  hIndex: document.querySelector("#hIndex"),
  publicationDelta: document.querySelector("#publicationDelta"),
  trendChart: document.querySelector("#trendChart"),
  quartileChart: document.querySelector("#quartileChart"),
  authorRankList: document.querySelector("#authorRankList"),
  yearlySummary: document.querySelector("#yearlySummary"),
  publicationTable: document.querySelector("#publicationTable"),
  recordCount: document.querySelector("#recordCount"),
  reviewGrid: document.querySelector("#reviewGrid"),
  reviewCount: document.querySelector("#reviewCount"),
  syncStatus: document.querySelector("#syncStatus"),
  lastUpdated: document.querySelector("#lastUpdated"),
  refreshButton: document.querySelector("#refreshButton"),
  exportButton: document.querySelector("#exportButton"),
  dataSourceTitle: document.querySelector("#dataSourceTitle"),
  dataSourceCopy: document.querySelector("#dataSourceCopy"),
};

function unique(values) {
  return [...new Set(values)].sort((a, b) => String(a).localeCompare(String(b), "th"));
}

const authorRoleLabels = {
  first_author: "First author",
  corresponding_author: "Corresponding author",
  co_author: "Co-author",
};
const staffGroupOptions = ["Chemistry", "Biology", "Material Science Engineering", "CIX"];
const thaiAffiliationTerms = [
  "thailand",
  "mae fah luang",
  "mfu",
  "chiang rai",
  "chiang mai",
  "bangkok",
  "mahidol",
  "chulalongkorn",
  "kasetsart",
  "thammasat",
  "walailak",
  "phayao",
  "khon kaen",
  "naresuan",
  "suranaree",
  "silpakorn",
  "burapha",
  "thaksin",
  "prince of songkla",
  "king mongkut",
  "ramathibodi",
  "siriraj",
  "rajabhat",
  "rajamangala",
  "national science and technology development agency",
  "nstda",
  "biotec",
];
const organizationTerms = [
  "university",
  "institute",
  "academy",
  "college",
  "hospital",
  "center",
  "centre",
  "school",
  "faculty",
  "department",
  "laboratory",
  "lab ",
  "ministry",
  "agency",
];

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  }[character]));
}

function getAuthorRoles(item) {
  const roles = item.matchedStaffRoles || {};
  const matchedNames = getMatchedStaffNames(item);
  return matchedNames.map((name) => roles[name] || item.authorRole || "co_author");
}

function getStaffGroupMap(item) {
  return item.matchedStaffGroups || {};
}

function getMatchedStaffNames(item) {
  return item.matchedStaff?.length ? item.matchedStaff : [];
}

function getAuthorFilterNames(item) {
  return state.dataScope === "affiliation" ? item.authors : getMatchedStaffNames(item);
}

function getStaffGroups(item) {
  const groupMap = getStaffGroupMap(item);
  const groups = getMatchedStaffNames(item).map((name) => groupMap[name]).filter(Boolean);
  return unique(groups);
}

function renderMatchedStaff(item) {
  const groupMap = getStaffGroupMap(item);
  const matchedNames = getMatchedStaffNames(item);
  if (!matchedNames.length) {
    const schoolEvidence = item.schoolAffiliationVerified
      ? `<span class="school-evidence" title="${escapeHtml(item.schoolFilterEvidence || "Matched by School of Science affiliation query")}">School affiliation verified</span>`
      : '<span class="school-evidence review">Needs school review</span>';
    return `
      <div class="staff-no-match">
        <span class="staff-empty">No current staff match</span>
        ${schoolEvidence}
      </div>
    `;
  }
  return matchedNames.map((name) => {
    const group = groupMap[name];
    const groupHtml = group ? `<span class="staff-group-pill">${escapeHtml(group)}</span>` : "";
    return `<div class="staff-name">${escapeHtml(name)}${groupHtml}</div>`;
  }).join("");
}

function getRoleLabel(role) {
  return authorRoleLabels[role] || role || "Co-author";
}

function getSdgs(item) {
  return Array.isArray(item.sdgs) ? item.sdgs : [];
}

function getSdgLabel(sdg) {
  if (typeof sdg === "string") {
    return sdg;
  }
  const code = sdg?.code || "SDG";
  const label = sdg?.label ? ` ${sdg.label}` : "";
  return `${code}${label}`;
}

function getScopeLabel(scope) {
  return scope === "affiliation" ? "Total (affiliation-wide Scopus)" : "Current academic staff";
}

function getAffiliationParts(item) {
  return String(item.affiliation || "")
    .split(";")
    .map((part) => part.trim())
    .filter(Boolean);
}

function isThaiAffiliation(affiliation) {
  const text = affiliation.toLowerCase();
  return thaiAffiliationTerms.some((term) => text.includes(term));
}

function isLikelyOrganization(affiliation) {
  const text = affiliation.toLowerCase();
  return organizationTerms.some((term) => text.includes(term));
}

function getForeignAffiliations(item) {
  return getAffiliationParts(item).filter((affiliation) =>
    !isThaiAffiliation(affiliation) && isLikelyOrganization(affiliation)
  );
}

function hasForeignCoauthorAffiliation(item) {
  return getForeignAffiliations(item).length > 0;
}

function renderSdgs(item) {
  const sdgs = getSdgs(item);
  if (!sdgs.length) {
    return '<span class="sdg-empty">Unmapped</span>';
  }
  return `
    <div class="sdg-list">
      ${sdgs.map((sdg) => {
        const code = typeof sdg === "string" ? sdg : sdg.code || "SDG";
        return `<span class="sdg-badge" title="${escapeHtml(getSdgLabel(sdg))}">${escapeHtml(code)}</span>`;
      }).join("")}
    </div>
  `;
}

function populateFilters() {
  const years = unique(publications.map((item) => item.year)).sort((a, b) => b - a);
  populateYearChecklist(years);
  elements.staffGroupFilter.innerHTML = '<option value="all">ทุกสาขา</option>';

  staffGroupOptions.forEach((group) => {
    const option = document.createElement("option");
    option.value = group;
    option.textContent = group;
    elements.staffGroupFilter.append(option);
  });
  populateAuthorFilter();
}

function getAuthorOptionsForCurrentGroup() {
  if (state.dataScope === "staff" && staffDirectory.length) {
    return unique(
      staffDirectory
        .filter((staff) => state.staffGroup === "all" || staff.academicGroup === state.staffGroup)
        .map((staff) => staff.name)
    );
  }

  const authors = [];
  publications.forEach((item) => {
    if (state.dataScope === "affiliation") {
      authors.push(...item.authors);
      return;
    }

    const groupMap = getStaffGroupMap(item);
    const matchedStaff = item.matchedStaff?.length ? item.matchedStaff : [];
    matchedStaff.forEach((name) => {
      if (state.staffGroup === "all" || groupMap[name] === state.staffGroup) {
        authors.push(name);
      }
    });
  });
  return unique(authors);
}

function populateAuthorFilter() {
  const authors = getAuthorOptionsForCurrentGroup();
  elements.authorOptions.innerHTML = "";

  authors.forEach((author) => {
    const option = document.createElement("option");
    option.value = author;
    elements.authorOptions.append(option);
  });

  const authorQuery = state.author.trim().toLowerCase();
  const hasPossibleMatch = !authorQuery || authors.some((author) => author.toLowerCase().includes(authorQuery));
  if (!hasPossibleMatch) {
    state.author = "";
  }
  elements.authorFilter.value = state.author;
}

function createYearCheckbox(value, label, checked) {
  const wrapper = document.createElement("label");
  wrapper.className = "checklist-option";
  wrapper.innerHTML = `
    <input type="checkbox" value="${escapeHtml(value)}" ${checked ? "checked" : ""} />
    <span>${escapeHtml(label)}</span>
  `;
  return wrapper;
}

function populateYearChecklist(years) {
  elements.yearChecklist.innerHTML = "";
  elements.yearChecklist.append(createYearCheckbox("all", "ทุกปี", state.selectedYears.size === 0));
  years.forEach((year) => {
    const value = String(year);
    elements.yearChecklist.append(createYearCheckbox(value, value, state.selectedYears.has(value)));
  });
}

function syncYearChecklist() {
  const inputs = elements.yearChecklist.querySelectorAll('input[type="checkbox"]');
  inputs.forEach((input) => {
    input.checked = input.value === "all" ? state.selectedYears.size === 0 : state.selectedYears.has(input.value);
  });
}

function matchesYearFilter(year) {
  if (state.selectedYears.size === 0) {
    return true;
  }

  return state.selectedYears.has(String(year));
}

function getFilteredPublications() {
  const query = state.search.trim().toLowerCase();

  return publications.filter((item) => {
    const matchesYear = matchesYearFilter(item.year);
    const authorNames = getAuthorFilterNames(item);
    const matchedStaffNames = getMatchedStaffNames(item);
    const authorQuery = state.author.trim().toLowerCase();
    const matchesAuthor = !authorQuery || authorNames.some((author) => author.toLowerCase().includes(authorQuery));
    const matchesStaffGroup = state.staffGroup === "all" || getStaffGroups(item).includes(state.staffGroup);
    const matchesAuthorRole = state.authorRole === "all" || getAuthorRoles(item).includes(state.authorRole);
    const matchesQuartile = state.quartile === "all" || item.quartile === state.quartile;
    const sdgText = getSdgs(item).map(getSdgLabel).join(" ");
    const groupText = getStaffGroups(item).join(" ");
    const text = `${item.title} ${item.doi} ${item.journal} ${sdgText} ${groupText} ${item.authors.join(" ")} ${authorNames.join(" ")} ${matchedStaffNames.join(" ")}`.toLowerCase();
    const matchesSearch = !query || text.includes(query);

    return matchesYear && matchesAuthor && matchesStaffGroup && matchesAuthorRole && matchesQuartile && matchesSearch;
  });
}

function calculateHIndex(items) {
  const citations = items.map((item) => item.citations).sort((a, b) => b - a);
  let h = 0;
  citations.forEach((count, index) => {
    if (count >= index + 1) h = index + 1;
  });
  return h;
}

function getTrend(items) {
  const trend = new Map();
  publications.forEach((item) => trend.set(item.year, 0));
  items.forEach((item) => trend.set(item.year, (trend.get(item.year) || 0) + 1));
  return [...trend.entries()].sort((a, b) => a[0] - b[0]).map(([year, count]) => ({ year, count }));
}

function getQuartiles(items) {
  const labels = ["Q1", "Q2", "Q3", "Q4", "NA"];
  return labels.map((label) => ({
    label,
    count: items.filter((item) => item.quartile === label).length,
  }));
}

function getAuthorRanking(items) {
  const counts = new Map();
  const groups = new Map();
  items.forEach((item) => {
    const groupMap = getStaffGroupMap(item);
    const authorNames = getMatchedStaffNames(item);
    authorNames.forEach((author) => {
      counts.set(author, (counts.get(author) || 0) + 1);
      if (groupMap[author] && !groups.has(author)) {
        groups.set(author, groupMap[author]);
      }
    });
  });
  return [...counts.entries()]
    .map(([author, count]) => ({ author, count, group: groups.get(author) || "" }))
    .sort((a, b) => b.count - a.count || a.author.localeCompare(b.author))
    .slice(0, 7);
}

function getYearlyDedupeSummary(items) {
  const summary = new Map();
  items.forEach((item) => {
    if (!item.year) return;
    if (!summary.has(item.year)) {
      summary.set(item.year, new Set());
    }
    summary.get(item.year).add(item.id || item.doi || item.title);
  });
  return [...summary.entries()]
    .map(([year, ids]) => ({ year, count: ids.size }))
    .sort((a, b) => b.year - a.year);
}

function resizeCanvas(canvas) {
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  const cssHeight = 240;
  canvas.width = rect.width * ratio;
  canvas.height = cssHeight * ratio;
  const context = canvas.getContext("2d");
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  return { context, width: rect.width, height: cssHeight };
}

function drawTrendChart(data) {
  const { context, width, height } = resizeCanvas(elements.trendChart);
  context.clearRect(0, 0, width, height);
  if (!data.length) {
    context.fillStyle = "#64727f";
    context.textAlign = "center";
    context.font = "14px system-ui";
    context.fillText("ไม่มีข้อมูล", width / 2, height / 2);
    return;
  }
  const padding = { top: 24, right: 18, bottom: 36, left: 38 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const maxValue = Math.max(1, ...data.map((item) => item.count));
  const barGap = 12;
  const barWidth = Math.max(18, (chartWidth - barGap * (data.length - 1)) / data.length);

  context.strokeStyle = "#d9e1e7";
  context.lineWidth = 1;
  context.fillStyle = "#64727f";
  context.font = "12px system-ui";

  for (let i = 0; i <= 4; i += 1) {
    const y = padding.top + chartHeight * (i / 4);
    context.beginPath();
    context.moveTo(padding.left, y);
    context.lineTo(width - padding.right, y);
    context.stroke();
  }

  data.forEach((item, index) => {
    const x = padding.left + index * (barWidth + barGap);
    const barHeight = (item.count / maxValue) * chartHeight;
    const y = padding.top + chartHeight - barHeight;

    context.fillStyle = "#0046be";
    roundRect(context, x, y, barWidth, barHeight, 6);
    context.fill();

    context.fillStyle = "#172026";
    context.textAlign = "center";
    context.fillText(String(item.count), x + barWidth / 2, y - 8);
    context.fillStyle = "#64727f";
    context.fillText(String(item.year), x + barWidth / 2, height - 12);
  });
}

function drawQuartileChart(data) {
  const { context, width, height } = resizeCanvas(elements.quartileChart);
  const total = data.reduce((sum, item) => sum + item.count, 0);
  const colors = ["#0046be", "#65c8e8", "#fff500", "#af192b", "#98a4ad"];
  const centerX = width / 2;
  const centerY = height / 2 - 4;
  const radius = Math.min(width, height) * 0.28;
  let startAngle = -Math.PI / 2;

  context.clearRect(0, 0, width, height);

  if (!total) {
    context.fillStyle = "#64727f";
    context.textAlign = "center";
    context.font = "14px system-ui";
    context.fillText("ไม่มีข้อมูล", centerX, centerY);
    return;
  }

  data.forEach((item, index) => {
    const slice = (item.count / total) * Math.PI * 2;
    context.beginPath();
    context.moveTo(centerX, centerY);
    context.fillStyle = colors[index];
    context.arc(centerX, centerY, radius, startAngle, startAngle + slice);
    context.closePath();
    context.fill();
    startAngle += slice;
  });

  context.beginPath();
  context.fillStyle = "#ffffff";
  context.arc(centerX, centerY, radius * 0.58, 0, Math.PI * 2);
  context.fill();

  context.fillStyle = "#172026";
  context.textAlign = "center";
  context.font = "700 24px system-ui";
  context.fillText(String(total), centerX, centerY + 4);
  context.font = "12px system-ui";
  context.fillStyle = "#64727f";
  context.fillText("records", centerX, centerY + 24);

  data.filter((item) => item.count > 0).forEach((item, index) => {
    const x = 18 + (index % 2) * (width / 2 - 8);
    const y = height - 44 + Math.floor(index / 2) * 22;
    context.fillStyle = colors[index];
    context.fillRect(x, y - 9, 10, 10);
    context.fillStyle = "#172026";
    context.textAlign = "left";
    context.font = "12px system-ui";
    context.fillText(`${item.label}: ${item.count}`, x + 16, y);
  });
}

function roundRect(context, x, y, width, height, radius) {
  const safeRadius = Math.min(radius, width / 2, height / 2);
  context.beginPath();
  context.moveTo(x + safeRadius, y);
  context.arcTo(x + width, y, x + width, y + height, safeRadius);
  context.arcTo(x + width, y + height, x, y + height, safeRadius);
  context.arcTo(x, y + height, x, y, safeRadius);
  context.arcTo(x, y, x + width, y, safeRadius);
  context.closePath();
}

function renderKpis(items) {
  const totalCitations = items.reduce((sum, item) => sum + item.citations, 0);
  const q1Publications = items.filter((item) => item.quartile === "Q1").length;
  const internationalItems = items.filter(hasForeignCoauthorAffiliation);
  const ratio = items.length ? Math.round((q1Publications / items.length) * 100) : 0;
  const internationalRatio = items.length ? Math.round((internationalItems.length / items.length) * 100) : 0;
  const years = publications.map((item) => item.year).filter(Boolean);
  const latestYear = years.length ? Math.max(...years) : "-";
  const latestCount = items.filter((item) => item.year === latestYear).length;

  elements.totalPublications.textContent = items.length.toLocaleString("th-TH");
  elements.internationalCollaborations.textContent = internationalItems.length.toLocaleString("th-TH");
  elements.internationalDelta.textContent = `${internationalRatio}% ของรายการที่เลือก`;
  elements.totalCitations.textContent = totalCitations.toLocaleString("th-TH");
  elements.topQuartileRatio.textContent = `${ratio}%`;
  elements.hIndex.textContent = calculateHIndex(items);
  elements.publicationDelta.textContent = latestYear === "-" ? "No publication year available" : `${latestCount} records in ${latestYear}`;
}

function renderAuthorRanking(items) {
  const ranking = getAuthorRanking(items);
  const max = Math.max(1, ...ranking.map((item) => item.count));
  elements.authorRankList.innerHTML = "";

  if (!ranking.length) {
    elements.authorRankList.innerHTML = '<div class="empty-state">ไม่มีข้อมูลผู้แต่งตามตัวกรองนี้</div>';
    return;
  }

  ranking.forEach((item) => {
    const row = document.createElement("div");
    row.className = "rank-item";
    row.innerHTML = `
      <div class="rank-row">
        <strong>${escapeHtml(item.author)}${item.group ? `<span class="staff-group-pill">${escapeHtml(item.group)}</span>` : ""}</strong>
        <span>${item.count}</span>
      </div>
      <div class="rank-bar" aria-hidden="true"><span style="width: ${(item.count / max) * 100}%"></span></div>
    `;
    elements.authorRankList.append(row);
  });
}

function renderYearlySummary(items) {
  const summary = getYearlyDedupeSummary(items);
  elements.yearlySummary.innerHTML = "";

  if (!summary.length) {
    elements.yearlySummary.innerHTML = '<div class="empty-state">ไม่มีข้อมูล publication แบบ dedupe</div>';
    return;
  }

  const total = summary.reduce((sum, item) => sum + item.count, 0);
  summary.forEach((item) => {
    const percent = total ? Math.round((item.count / total) * 100) : 0;
    const row = document.createElement("div");
    row.className = "yearly-item";
    row.innerHTML = `
      <div class="yearly-row">
        <strong>${item.year}</strong>
        <span>${item.count.toLocaleString("th-TH")} publications</span>
      </div>
      <div class="rank-bar" aria-hidden="true"><span style="width: ${percent}%"></span></div>
    `;
    elements.yearlySummary.append(row);
  });
}

function renderTable(items) {
  elements.publicationTable.innerHTML = "";
  elements.recordCount.textContent = `${items.length} records`;

  if (!items.length) {
    const row = document.createElement("tr");
    row.innerHTML = '<td colspan="9" class="empty-state">ไม่พบข้อมูลตามตัวกรองนี้</td>';
    elements.publicationTable.append(row);
    return;
  }

  items.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.year}</td>
      <td>
        <div class="pub-title">
          <strong>${item.title}</strong>
          <span>${item.doi} · ${item.type}</span>
        </div>
      </td>
      <td>${renderMatchedStaff(item)}</td>
      <td>${getAuthorRoles(item).map(getRoleLabel).join("<br>")}</td>
      <td>${item.journal}</td>
      <td>
        <div class="quartile-cell">
          <span class="badge ${item.quartile.toLowerCase()}">${item.quartile}</span>
          <span>${item.quartileYear ? `${item.quartileYear} · P${item.citeScorePercentile}` : "No metric"}</span>
        </div>
      </td>
      <td>${renderSdgs(item)}</td>
      <td>${item.citations}</td>
      <td><span class="status ${item.status}">${item.status === "verified" ? "Verified" : "Needs review"}</span></td>
    `;
    elements.publicationTable.append(row);
  });
}

function renderReview(items) {
  const reviewItems = items.filter((item) => item.status === "review");
  elements.reviewGrid.innerHTML = "";
  elements.reviewCount.textContent = `${reviewItems.length} pending`;

  if (!reviewItems.length) {
    elements.reviewGrid.innerHTML = '<div class="empty-state">ไม่มีรายการที่ต้องตรวจสอบในตัวกรองนี้</div>';
    return;
  }

  reviewItems.forEach((item) => {
    const card = document.createElement("article");
    card.className = "review-card";
    card.innerHTML = `
      <strong>${item.title}</strong>
      <p>${item.reviewReason}</p>
      <p><b>Matched staff:</b> ${(item.matchedStaff?.length ? item.matchedStaff : ["-"]).join(", ")}</p>
      <p><b>Affiliation:</b> ${item.affiliation}</p>
      <span class="badge ${item.quartile.toLowerCase()}">${item.quartile}</span>
    `;
    elements.reviewGrid.append(card);
  });
}

function render() {
  const items = getFilteredPublications();
  renderKpis(items);
  drawTrendChart(getTrend(items));
  drawQuartileChart(getQuartiles(items));
  renderAuthorRanking(items);
  renderYearlySummary(items);
  renderTable(items);
  renderReview(items);
}

function syncScopeControls() {
  const isAffiliationScope = state.dataScope === "affiliation";
  elements.staffGroupFilter.disabled = isAffiliationScope;
  elements.authorRoleFilter.disabled = isAffiliationScope;
  if (isAffiliationScope) {
    state.staffGroup = "all";
    state.authorRole = "all";
    elements.staffGroupFilter.value = "all";
    elements.authorRoleFilter.value = "all";
  }
  populateAuthorFilter();
}

function setSyncMessage(message) {
  elements.syncStatus.textContent = message;
  elements.lastUpdated.textContent = `Last updated: ${new Date().toLocaleString("th-TH")}`;
}

function resetFilterValues() {
  state.selectedYears.clear();
  state.author = "";
  state.staffGroup = "all";
  state.authorRole = "all";
  state.quartile = "all";
  state.search = "";
  elements.dataScopeFilter.value = state.dataScope;
  elements.authorFilter.value = "";
  elements.staffGroupFilter.value = "all";
  elements.authorRoleFilter.value = "all";
  elements.quartileFilter.value = "all";
  elements.searchInput.value = "";
  syncYearChecklist();
  syncScopeControls();
}

function setPublications(nextPublications, sourceLabel, nextStaff = []) {
  staffDirectory = Array.isArray(nextStaff) ? nextStaff : [];
  publications = nextPublications.map((item) => ({
    ...item,
    year: Number(item.year) || 0,
    quartile: item.quartile || "NA",
    citations: Number(item.citations) || 0,
    authors: Array.isArray(item.authors) && item.authors.length ? item.authors : ["Unknown author"],
    matchedStaff: Array.isArray(item.matchedStaff) ? item.matchedStaff : [],
    matchedStaffRoles: item.matchedStaffRoles || {},
    matchedStaffGroups: item.matchedStaffGroups || {},
    schoolAffiliationVerified: Boolean(item.schoolAffiliationVerified),
    schoolAffiliationScope: item.schoolAffiliationScope || "",
    schoolFilterEvidence: item.schoolFilterEvidence || "",
    sdgs: Array.isArray(item.sdgs) ? item.sdgs : [],
    status: item.status === "verified" ? "verified" : "review",
  }));
  state.dataSource = sourceLabel;
  resetFilterValues();
  populateFilters();
  render();
}

let cachedSnapshot = null;

async function fetchSnapshot(forceReload) {
  if (cachedSnapshot && !forceReload) {
    return cachedSnapshot;
  }
  const response = await fetch(`site-data/publications.json?ts=${Date.now()}`);
  if (!response.ok) {
    throw new Error(`ไม่พบไฟล์ข้อมูลที่ sync ไว้ (HTTP ${response.status})`);
  }
  const payload = await response.json();
  cachedSnapshot = payload;
  return payload;
}

function filterSnapshotForScope(payload, scope) {
  const all = Array.isArray(payload.publications) ? payload.publications : [];
  if (scope === "affiliation") {
    return all;
  }
  return all.filter((item) => Array.isArray(item.matchedStaff) && item.matchedStaff.length > 0);
}

async function loadScopusData(forceReload) {
  elements.refreshButton.disabled = true;
  elements.dataScopeFilter.disabled = true;
  const scope = state.dataScope;
  const scopeLabel = getScopeLabel(scope);
  setSyncMessage(`กำลังโหลดข้อมูลที่ sync ไว้ (${scopeLabel})...`);

  try {
    const payload = await fetchSnapshot(Boolean(forceReload));
    const scoped = filterSnapshotForScope(payload, scope);
    if (!scoped.length) {
      throw new Error("ไม่พบข้อมูลผลงานตีพิมพ์ในไฟล์ที่ sync ไว้");
    }

    setPublications(scoped, "scopus", payload.staff || []);
    elements.dataSourceTitle.textContent = "Synced data";
    const groupSummary = scope === "staff" && payload.staffGroups?.length ? ` กลุ่มสาขา: ${payload.staffGroups.join(", ")}` : "";
    const syncedAtText = payload.lastSyncedAt ? new Date(payload.lastSyncedAt).toLocaleString("th-TH") : "ไม่ทราบเวลา";
    elements.dataSourceCopy.textContent = `โหมด ${scopeLabel}: ${scoped.length} รายการ (sync ล่าสุด ${syncedAtText}).${groupSummary}`;
    setSyncMessage(`โหลดข้อมูลสำเร็จ (sync ล่าสุด ${syncedAtText})`);
  } catch (error) {
    setPublications([], "empty", []);
    elements.dataSourceTitle.textContent = "No data";
    elements.dataSourceCopy.textContent = "ยังไม่มีข้อมูลให้แสดง เพราะยังไม่มีไฟล์ข้อมูลที่ sync ไว้ หรือโหลดไม่สำเร็จ";
    setSyncMessage(`ไม่มีข้อมูล: ${error.message}`);
  } finally {
    elements.refreshButton.disabled = false;
    elements.dataScopeFilter.disabled = false;
    syncScopeControls();
  }
}

async function autoSyncIfConfigured() {
  setPublications([], "empty", []);
  elements.dataSourceTitle.textContent = "Loading";
  elements.dataSourceCopy.textContent = "กำลังโหลดข้อมูลที่ sync ไว้ล่าสุด";
  setSyncMessage("กำลังโหลดข้อมูล...");
  await loadScopusData(true);
}

function exportCsv() {
  const items = getFilteredPublications();
  const headers = [
    "year",
    "title",
    "doi",
    "matchedStaff",
    "staffGroups",
    "internationalCoauthorAffiliation",
    "foreignAffiliations",
    "schoolAffiliationVerified",
    "schoolFilterEvidence",
    "authorRoles",
    "authors",
    "journal",
    "quartile",
    "quartileYear",
    "citeScorePercentile",
    "citeScore",
    "sdgs",
    "citations",
    "status",
  ];
  const rows = items.map((item) =>
    headers.map((key) => {
      const value = key === "authorRoles"
        ? getAuthorRoles(item).map(getRoleLabel).join("; ")
        : key === "sdgs" ? getSdgs(item).map(getSdgLabel).join("; ")
        : key === "staffGroups" ? getStaffGroups(item).join("; ")
        : key === "internationalCoauthorAffiliation" ? (hasForeignCoauthorAffiliation(item) ? "yes" : "no")
        : key === "foreignAffiliations" ? getForeignAffiliations(item).join("; ")
        : key === "authors" || key === "matchedStaff" ? (item[key] || []).join("; ") : item[key];
      return `"${String(value).replaceAll('"', '""')}"`;
    }).join(",")
  );
  const csv = [headers.join(","), ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `scidash-publications-${Date.now()}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

function wireEvents() {
  elements.dataScopeFilter.addEventListener("change", (event) => {
    state.dataScope = event.target.value;
    syncScopeControls();
    loadScopusData();
  });
  elements.yearChecklist.addEventListener("change", (event) => {
    if (event.target.type !== "checkbox") {
      return;
    }

    if (event.target.value === "all") {
      state.selectedYears.clear();
    } else if (event.target.checked) {
      state.selectedYears.add(event.target.value);
    } else {
      state.selectedYears.delete(event.target.value);
    }

    syncYearChecklist();
    render();
  });
  elements.authorFilter.addEventListener("input", (event) => {
    state.author = event.target.value;
    render();
  });
  elements.staffGroupFilter.addEventListener("change", (event) => {
    state.staffGroup = event.target.value;
    populateAuthorFilter();
    render();
  });
  elements.authorRoleFilter.addEventListener("change", (event) => {
    state.authorRole = event.target.value;
    render();
  });
  elements.quartileFilter.addEventListener("change", (event) => {
    state.quartile = event.target.value;
    render();
  });
  elements.searchInput.addEventListener("input", (event) => {
    state.search = event.target.value;
    render();
  });
  elements.refreshButton.addEventListener("click", loadScopusData);
  elements.exportButton.addEventListener("click", exportCsv);
  window.addEventListener("resize", render);
}

wireEvents();
populateFilters();
render();
autoSyncIfConfigured();
