# เกณฑ์การคำนวณ KPI บน SciDash

เอกสารนี้สรุปตรรกะจริงที่ใช้คำนวณแต่ละตัวชี้วัดบน dashboard อ้างอิงจากโค้ดปัจจุบัน หากมีการแก้ไขเกณฑ์ข้อใด **ต้องเพิ่ม entry ในส่วน [Changelog](#changelog) ท้ายไฟล์นี้ทุกครั้ง**

## 1. International Co-authors

ที่มาโค้ด: `scripts/scidash_core.py: normalize_scopus_entry` (สร้างฟิลด์ `affiliationCountries`); `app.js: hasForeignCoauthorAffiliation`

ใช้ฟิลด์ `affiliation-country` ที่ **Scopus ส่งมาให้ตรงๆ ต่อ affiliation แต่ละอัน** (ไม่ใช่การเดา) — เก็บเป็น `affiliationCountries` (list ประเทศไม่ซ้ำ) ต่อผลงาน 1 ชิ้นตอน sync:

1. ผลงานมีรายชื่อ country อย่างน้อย 1 ประเทศที่ไม่ใช่ `Thailand` (case-insensitive) → นับว่ามี international co-author
2. ถ้าไม่มีข้อมูล `affiliationCountries` เลย (ผลงานเก่าที่ sync ก่อนมีฟีเจอร์นี้) → fallback ไปใช้วิธีเดิม (keyword matching จากข้อความ affiliation ผ่าน `getAffiliationParts`, `isThaiAffiliation`, `isLikelyOrganization`)

**ไม่มีข้อจำกัดเรื่อง keyword matching อีกต่อไป** (แก้ไปแล้ว) เพราะใช้ country code จริงจาก Scopus โดยตรง ไม่ใช่การเดา

## 0. การจับคู่ผลงานกับรายชื่ออาจารย์ (matchedStaff) — พื้นฐานของทุกหัวข้อด้านบน

ที่มาโค้ด: `scripts/scidash_core.py` — `fetch_staff_publications`, `build_staff_query`, `author_matches_staff`, `fetch_affiliation_publications` → `detect_staff_matches`

ระบบดึงข้อมูลผลงานของอาจารย์แต่ละคนด้วย query `AUTHLASTNAME(นามสกุล) AND AFFIL(...)` ต่อ Scopus API — query นี้กรองแค่ **นามสกุล** ฝั่ง Scopus เอง ไม่กรองชื่อจริงด้วย ดังนั้นถ้ามีอาจารย์ 2 คนนามสกุลเดียวกัน (เช่น Anant Eungwanichayapant กับ Prapassorn Damrongkool Eungwanichayapant) ผลลัพธ์ที่ Scopus คืนมาจะเป็นชุดเดียวกันสำหรับทั้งคู่ — ต้องมีการตรวจสอบซ้ำในเครื่องด้วย `author_matches_staff` (เช็คนามสกุล + ชื่อ/initial จริงจาก author list ที่ Scopus คืนมา) ก่อนจะยืนยันว่าเป็นผลงานของคนนั้นจริง — ผลงานที่ไม่มี author คนไหนตรงกับ initial/ชื่อของอาจารย์คนนั้นจะถูกตัดทิ้งจากรายชื่อของอาจารย์คนนั้น (แต่ยังไปอยู่ถูกคนของอาจารย์อีกคนที่นามสกุลตรงกันจริง)

ใช้ `view=COMPLETE` (แทน `STANDARD`) ตอนเรียก Scopus Search API เพื่อให้ได้ author list เต็ม (พร้อมชื่อจริง ไม่ใช่แค่ initial ที่โดนตัดทอน) มาใช้ตรวจสอบได้แม่นยำขึ้น — ข้อแลกเปลี่ยนคือ `view=COMPLETE` จำกัด page size สูงสุดที่ 25 รายการ/request (STANDARD ได้ถึง 200) ทำให้ sync ใช้เวลานานขึ้นเล็กน้อย

## 2. Q1 / Quartile

ที่มาโค้ด: `scripts/scidash_core.py` — `extract_source_metric`, `quartile_from_percentile`

มาจาก Scopus CiteScore (Serial Title API) ไม่ได้คำนวณเอง:

1. ยิง Serial Title API **ครั้งเดียวต่อวารสาร** (ไม่ใช่ต่อผลงานหรือต่อปี) — response ที่ได้กลับมามีประวัติ CiteScore ย้อนหลังให้ครบทุกปีที่ Scopus เก็บไว้ (ปัจจุบันคือ ~5 ปีล่าสุด) อยู่แล้วในครั้งเดียว
2. **เลือกปี CiteScore ให้ตรงกับปีที่ผลงานนั้นตีพิมพ์จริง** (`extract_source_metric(payload, publication_year)`) — ถ้าปีนั้นมีอยู่ในประวัติที่ Scopus คืนมา ใช้ปีนั้นตรงๆ ถ้าไม่มี (เช่น ผลงานเก่ากว่าที่ Scopus เก็บ CiteScore ไว้) จะ fallback ไปใช้ปีล่าสุดที่สถานะ `Complete` แทน
3. หา percentile สูงสุดในบรรดา subject category ที่วารสารถูกจัดอยู่ในปีนั้น (เลือกค่าที่ดีที่สุด ถ้าอยู่หลายสาขา)
4. แปลง percentile → quartile:
   - ≥ 75 → **Q1**
   - ≥ 50 → **Q2**
   - ≥ 25 → **Q3**
   - ต่ำกว่านั้น → **Q4**
   - ไม่มีข้อมูล CiteScore → **NA**
5. KPI "Q1 / Total Publications" = (จำนวนที่ quartile = Q1) ÷ (จำนวนผลงานทั้งหมดที่กรองอยู่ตอนนั้น)

## 3. SDG (Sustainable Development Goals)

ที่มาโค้ด: `scripts/scidash_core.py` — `classify_sdgs`, `SDG_KEYWORDS`

เป็น rule-based keyword matching ไม่ใช่ AI classification:

1. รวมข้อความจาก title + journal name + publication type เป็นก้อนเดียว
2. เทียบกับ keyword list ของ SDG แต่ละข้อ — **ครอบคลุม 11 จาก 17 ข้อ**: SDG 2, 3, 4, 6, 7, 9, 11, 12, 13, 14, 15
3. พบ keyword ตรงกับ SDG ไหน → ติด SDG นั้น พร้อมเก็บคำที่ match ไว้ (สูงสุด 4 คำ)
4. แสดงผลสูงสุด **3 SDG ต่อผลงาน** แม้จะ match มากกว่านั้น

**ข้อจำกัด:** จับจาก title/journal name เท่านั้น ไม่ได้อ่าน abstract จึงพลาดงานที่เกี่ยวข้องจริงแต่ชื่อเรื่องไม่มีคำ keyword ตรง และไม่ครอบคลุม SDG 1, 5, 8, 10, 16, 17

## 4. การระบุ First และ Corresponding Author

ที่มาโค้ด: `scripts/scidash_core.py` — `classify_author_role`; `app.js` — `authorRoleLabels`, `getAuthorRoles`

- **First author**: เช็คว่าผู้แต่งคนแรกในลิสต์ (`authors[0]`) ตรงกับอาจารย์ที่ match หรือไม่ โดยต้องตรงทั้ง **นามสกุล + ชื่อ (หรืออย่างน้อย initial ของชื่อ)** ผ่านฟังก์ชัน `author_matches_staff` เดียวกับที่ใช้จับคู่ staff ทั่วทั้งระบบ → ตรง = `first_author`, ไม่ตรง = `co_author`
  - ⚠️ ข้อจำกัดที่เหลืออยู่: ถ้าอาจารย์ 2 ท่านนามสกุลเดียวกัน **และ** initial ชื่อขึ้นต้นตัวเดียวกัน (เช่น "Somchai Suwan" กับ "Somsri Suwan") ระบบยังแยกไม่ออก เพราะ heuristic ใช้แค่ first-initial ไม่ใช่ชื่อเต็ม (จุดร่วมกับการจับคู่ staff ทั่วทั้งระบบ ไม่ใช่แค่ role)
- **Corresponding author**: ดึงจาก **Scopus Abstract Retrieval API** (คนละ endpoint จาก Search API ที่ใช้ค้นหาผลงาน) — `scidash_core.py: request_abstract_retrieval`, `extract_corresponding_author_names`, `enrich_publications_with_corresponding_authors`
  1. ยิง Abstract Retrieval **1 ครั้งต่อผลงาน 1 ชิ้น** (เฉพาะผลงานที่มี matchedStaff เท่านั้น) เพื่อดึง block `correspondence` ซึ่ง Scopus ระบุชัดเจนว่าใครเป็น corresponding author (มีได้มากกว่า 1 คน)
  2. เทียบชื่อใน `correspondence` กับอาจารย์แต่ละคนที่ match ผ่าน `author_matches_staff` เดียวกับจุดอื่นๆ
  3. ถ้าตรง → เซ็ต role เป็น `corresponding_author` (ทับค่า first_author/co_author เดิม) ถ้าไม่ตรงหรือ Scopus ไม่มีข้อมูล correspondence เก็บไว้ → คงค่า first_author/co_author เดิมไว้
  - **ต้นทุน:** เพิ่ม API call อีก 1 ครั้ง/ผลงาน ทำให้ sync ใช้เวลานานขึ้นมาก จึงรันเฉพาะผลงานที่ถูก (re)fetch ในรอบ sync นั้นๆ เท่านั้น (full sync = ทุกผลงาน, incremental sync = เฉพาะช่วง 2 ปีล่าสุด) ไม่ทำย้อนหลังทั้งหมดทุกรอบ
  - **ข้อจำกัด:** ถ้า Scopus ไม่มีข้อมูล correspondence สำหรับผลงานนั้น (พบได้บ่อยในวารสารเก่าหรือวารสารท้องถิ่น) ระบบจะไม่ระบุ corresponding author ให้เลย ไม่ได้แปลว่าไม่มีคนเป็น corresponding author จริง
- **การกรองในหน้าเว็บ (ตัวกรอง "ผู้แต่ง" + "บทบาทผู้แต่ง")**: `app.js: getFilteredPublications` — เมื่อเลือกทั้งชื่ออาจารย์และ role พร้อมกัน ระบบจะเช็คว่า role นั้นเป็นของ**อาจารย์คนที่เลือกจริง** ไม่ใช่ของ staff คนอื่นที่ match อยู่ในผลงานเดียวกัน (ถ้าไม่ได้เลือกชื่ออาจารย์ จะเช็คว่ามี staff คนไหนก็ได้ในผลงานนั้นมี role ตรงที่เลือก)

---

## Changelog

การแก้ไขเกณฑ์ข้างต้นทุกครั้งต้องบันทึกที่นี่ (วันที่ / เกณฑ์ที่แก้ / เหตุผล)

### 2026-09-15
- **แก้เกณฑ์ International Co-authors ให้ใช้ country code จริงจาก Scopus** (`scripts/scidash_core.py: normalize_scopus_entry` เพิ่มฟิลด์ `affiliationCountries`; `app.js: hasForeignCoauthorAffiliation`) — เดิมเดาจาก keyword matching (เช็คคำว่า "university"/"thailand" ในข้อความ affiliation) ผู้ใช้ถามว่าดึง country จริงได้ไหม ตรวจสอบพบว่า Scopus ส่ง `affiliation-country` มาให้ตรงๆ อยู่แล้วในข้อมูลที่ดึงมาอยู่แล้ว (ไม่ต้องเพิ่ม API call) แค่โค้ดเดิมทิ้งฟิลด์นี้ไป
  - เปลี่ยนมาเก็บ `affiliationCountries` (list ประเทศจริงจาก Scopus) ต่อผลงาน แล้วเช็คว่ามีประเทศอื่นนอกจาก Thailand ไหม แทนการเดาด้วย keyword
  - ผลเทียบกับข้อมูลจริง: keyword-based เดิมนับ 749 ผลงานเป็น international, ของจริง (country-based) คือ 716 ผลงาน (keyword เดิมนับเกินไป ~33 ผลงาน)
  - คง fallback ไปใช้ keyword matching ไว้เผื่อผลงานเก่าที่ sync ก่อนมีฟีเจอร์นี้ (ไม่มี `affiliationCountries`)

### 2026-09-14 (4)
- **แก้บั๊ก: ตัวกรอง "ผู้แต่ง" + "บทบาทผู้แต่ง" จับคู่ผิดคน** (`app.js: getFilteredPublications`) — ผู้ใช้แจ้งว่าเลือกกรอง Asst. Prof. Dr. Kitiphong Khongphinitbunjong + Corresponding author แล้วขึ้นผลงานที่จริงๆ อาจารย์ท่านอื่น (ที่ match อยู่ในผลงานเดียวกัน) เป็น corresponding author ไม่ใช่ Kitiphong
  - สาเหตุ: `matchesAuthor` และ `matchesAuthorRole` เดิมเช็คแยกกันคนละส่วน — แค่เช็คว่า "มี staff คนไหนก็ได้ตรงกับชื่อที่ค้น" AND "มี staff คนไหนก็ได้ (อาจคนละคน) มี role ตรงที่เลือก" ไม่ได้บังคับว่าต้องเป็นคนเดียวกัน
  - แก้โดยให้ role filter เช็คเฉพาะ staff ที่ตรงกับชื่อในตัวกรอง "ผู้แต่ง" เท่านั้น
  - ทดสอบกับข้อมูลจริง: filter "Kitiphong" + "corresponding_author" จาก 11 ผลงาน (ผิด) เหลือ 2 ผลงาน (ถูกต้อง)

### 2026-09-14 (3)
- **เพิ่มเกณฑ์ Corresponding author** (`scripts/scidash_core.py: request_abstract_retrieval`, `extract_corresponding_author_names`, `enrich_publications_with_corresponding_authors`) — เดิมไม่มีข้อมูลรองรับเลย (ดูหัวข้อที่ 4 เดิม) แก้โดยดึงจาก Scopus Abstract Retrieval API เพิ่ม (คนละ endpoint จาก Search API) ยิง 1 ครั้ง/ผลงาน เฉพาะผลงานที่ (re)fetch ในรอบ sync นั้น เพื่อคุมต้นทุน API
  - เพิ่ม dropdown option "Co-author" ใน `index.html` ด้วย (ค่านี้มีอยู่แล้วใน data แต่ dropdown ไม่เคยมีตัวเลือกให้กรอง)
  - full re-sync แรกหลังแก้: 374 จาก 705 matched-staff role ถูกระบุเป็น corresponding_author

### 2026-09-14 (2)
- **แก้บั๊กสำคัญ: การจับคู่ผลงานข้ามคนสำหรับอาจารย์นามสกุลซ้ำ** (`scripts/scidash_core.py: fetch_staff_publications`, `request_scopus`) — ผู้ใช้แจ้งว่า Asst. Prof. Dr. Anant Eungwanichayapant มีผลงานที่ไม่ใช่ของตัวเองปรากฏอยู่ ตรวจสอบพบว่า query `AUTHLASTNAME(...)` ที่ยิงต่อ Scopus กรองแค่นามสกุล ไม่กรองชื่อจริง ทำให้ผลงานของ Asst. Prof. Dr. Prapassorn Damrongkool Eungwanichayapant (นามสกุลเดียวกัน) ถูกนับซ้ำเป็นของ Anant ด้วยทั้งหมด (ยืนยันด้วยการยิง query ตรงและดู view=COMPLETE เห็นชัดว่า author จริงคือ Prapassorn ไม่ใช่ Anant)
  - เปลี่ยน `view` จาก `STANDARD` เป็น `COMPLETE` เพื่อได้ author list เต็ม (มีชื่อจริง ไม่ใช่แค่ initial ที่ถูกตัดทอน)
  - เพิ่มการตรวจสอบซ้ำในเครื่องด้วย `author_matches_staff` ก่อนยืนยันว่าเป็นผลงานของอาจารย์คนนั้นจริง ถ้าไม่มี author คนไหนตรงชื่อ/initial เลย จะตัดออกจากรายชื่อของอาจารย์คนนั้น
  - ผลข้างเคียง: `view=COMPLETE` จำกัด page size 25/request (เดิม 200) sync ใช้เวลานานขึ้น จึงลด `page_size` ใน `sync_scopus.py` จาก 100 เหลือ 25
  - ต้องรัน full re-sync ใหม่ทั้งหมด (ไม่ใช่แค่ recompute ในเครื่อง) เพราะ query ที่ยิงไป Scopus เปลี่ยน ไม่ใช่แค่ post-processing

### 2026-09-14
- สร้างเอกสารนี้ สรุปเกณฑ์ที่ใช้อยู่จริงในโค้ด ณ ขณะนั้น (ยังไม่มีการแก้ไขเกณฑ์ใดๆ)
- บันทึกข้อจำกัดที่พบ: Corresponding author filter ยังไม่มีข้อมูลรองรับจริง, SDG ครอบคลุมแค่ 11/17 ข้อ, International co-author ใช้ keyword matching ไม่ใช่ country code จริง
- **แก้เกณฑ์ First author** (`scripts/scidash_core.py: classify_author_role`): เดิมเช็คแค่นามสกุลของผู้แต่งคนแรกตรงกับอาจารย์ไหม ทำให้อาจารย์ 2 ท่านนามสกุลเดียวกันถูกระบุ first author ผิดคนได้ — เปลี่ยนมาเช็คนามสกุล + ชื่อ/initial ผ่าน `author_matches_staff` (ฟังก์ชันเดียวกับที่ใช้จับคู่ staff ทั่วระบบ) เหตุผล: ผู้ใช้แจ้งว่าอาจารย์บางท่านนามสกุลซ้ำกัน ทำให้ผลลัพธ์ First author คลาดเคลื่อน
  - ยังเหลือ residual limitation: นามสกุลซ้ำ + initial ชื่อขึ้นต้นตัวเดียวกัน ยังแยกไม่ออก (ดูรายละเอียดในหัวข้อที่ 4 ด้านบน)
