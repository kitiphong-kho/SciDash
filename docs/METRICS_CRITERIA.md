# เกณฑ์การคำนวณ KPI บน SciDash

เอกสารนี้สรุปตรรกะจริงที่ใช้คำนวณแต่ละตัวชี้วัดบน dashboard อ้างอิงจากโค้ดปัจจุบัน หากมีการแก้ไขเกณฑ์ข้อใด **ต้องเพิ่ม entry ในส่วน [Changelog](#changelog) ท้ายไฟล์นี้ทุกครั้ง**

## 1. International Co-authors

ที่มาโค้ด: `app.js` — `getAffiliationParts`, `isThaiAffiliation`, `isLikelyOrganization`, `hasForeignCoauthorAffiliation`

คำนวณจากฟิลด์ `affiliation` (ข้อความ affiliation ที่ Scopus คืนมา ต่อผลงาน 1 ชิ้น):

1. แยกข้อความด้วย `;` เป็นรายชื่อหน่วยงานทีละรายการ
2. ตัดออกถ้าเข้าข่าย "หน่วยงานไทย" — มีคำใดคำหนึ่งใน `thaiAffiliationTerms` (เช่น `thailand`, `mae fah luang`, `chiang rai`, ชื่อมหาวิทยาลัยไทยหลัก, `nstda`, `biotec` ฯลฯ)
3. ต้องดูเหมือนหน่วยงานจริง — มีคำใดคำหนึ่งใน `organizationTerms` (เช่น `university`, `institute`, `hospital`, `faculty`, `department`)
4. ถ้าเหลือ affiliation อย่างน้อย 1 รายการที่ผ่านทั้ง 2 เงื่อนไข (ไม่ใช่ไทย + ดูเหมือนหน่วยงาน) → นับผลงานนั้นว่ามี international co-author

**ข้อจำกัด:** เป็น keyword matching ไม่ได้เช็ค country code จริงจาก Scopus หน่วยงานไทยที่ไม่อยู่ใน list อาจถูกนับผิดเป็นต่างประเทศ

## 0. การจับคู่ผลงานกับรายชื่ออาจารย์ (matchedStaff) — พื้นฐานของทุกหัวข้อด้านบน

ที่มาโค้ด: `scripts/scidash_core.py` — `fetch_staff_publications`, `build_staff_query`, `author_matches_staff`, `fetch_affiliation_publications` → `detect_staff_matches`

ระบบดึงข้อมูลผลงานของอาจารย์แต่ละคนด้วย query `AUTHLASTNAME(นามสกุล) AND AFFIL(...)` ต่อ Scopus API — query นี้กรองแค่ **นามสกุล** ฝั่ง Scopus เอง ไม่กรองชื่อจริงด้วย ดังนั้นถ้ามีอาจารย์ 2 คนนามสกุลเดียวกัน (เช่น Anant Eungwanichayapant กับ Prapassorn Damrongkool Eungwanichayapant) ผลลัพธ์ที่ Scopus คืนมาจะเป็นชุดเดียวกันสำหรับทั้งคู่ — ต้องมีการตรวจสอบซ้ำในเครื่องด้วย `author_matches_staff` (เช็คนามสกุล + ชื่อ/initial จริงจาก author list ที่ Scopus คืนมา) ก่อนจะยืนยันว่าเป็นผลงานของคนนั้นจริง — ผลงานที่ไม่มี author คนไหนตรงกับ initial/ชื่อของอาจารย์คนนั้นจะถูกตัดทิ้งจากรายชื่อของอาจารย์คนนั้น (แต่ยังไปอยู่ถูกคนของอาจารย์อีกคนที่นามสกุลตรงกันจริง)

ใช้ `view=COMPLETE` (แทน `STANDARD`) ตอนเรียก Scopus Search API เพื่อให้ได้ author list เต็ม (พร้อมชื่อจริง ไม่ใช่แค่ initial ที่โดนตัดทอน) มาใช้ตรวจสอบได้แม่นยำขึ้น — ข้อแลกเปลี่ยนคือ `view=COMPLETE` จำกัด page size สูงสุดที่ 25 รายการ/request (STANDARD ได้ถึง 200) ทำให้ sync ใช้เวลานานขึ้นเล็กน้อย

## 2. Q1 / Quartile

ที่มาโค้ด: `scripts/scidash_core.py` — `extract_source_metric`, `quartile_from_percentile`

มาจาก Scopus CiteScore (Serial Title API) ไม่ได้คำนวณเอง:

1. ดึง CiteScore ปีล่าสุดที่สถานะ `Complete` ของวารสารนั้น
2. หา percentile สูงสุดในบรรดา subject category ที่วารสารถูกจัดอยู่ (เลือกค่าที่ดีที่สุด ถ้าอยู่หลายสาขา)
3. แปลง percentile → quartile:
   - ≥ 75 → **Q1**
   - ≥ 50 → **Q2**
   - ≥ 25 → **Q3**
   - ต่ำกว่านั้น → **Q4**
   - ไม่มีข้อมูล CiteScore → **NA**
4. KPI "Q1 / Total Publications" = (จำนวนที่ quartile = Q1) ÷ (จำนวนผลงานทั้งหมดที่กรองอยู่ตอนนั้น)

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
