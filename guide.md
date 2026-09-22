# SciDash Guide & Change Log

อัปเดตล่าสุด: 2026-07-09 11:15 ICT

ไฟล์นี้ใช้เป็นคู่มือและบันทึกการเปลี่ยนแปลงของโปรเจกต์ SciDash ทุกครั้งที่มีการแก้ระบบ ควรอัปเดตไฟล์นี้ด้วยเสมอ

## ภาพรวมระบบ

SciDash เป็น Web Dashboard สำหรับติดตามผลงานตีพิมพ์และ KPI ด้านวิจัยของ School of Science, Mae Fah Luang University

ระบบปัจจุบันทำงานเป็น browser dashboard ผ่าน `http://localhost:4173` และมี backend proxy ขนาดเล็กใน Python เพื่อเรียก Scopus/Elsevier API โดยไม่เปิดเผย API key ในฝั่ง browser

## วิธีรันระบบ

ตั้งค่า API key ในไฟล์ `.env`

```bash
cp .env.example .env
```

ใส่ค่า:

```text
SCOPUS_API_KEY=your_key_here
SCOPUS_INST_TOKEN=your_insttoken_here
```

`SCOPUS_INST_TOKEN` ใส่เฉพาะถ้า Elsevier ออก InstToken มาให้ (เช่นกรณี API key อย่างเดียวโดน จำกัดผลลัพธ์/access denied) ถ้าไม่มีก็เว้นว่างไว้ได้

เริ่ม server:

```bash
python3 scripts/start_server.py
```

หยุด server:

```bash
python3 scripts/stop_server.py
```

หากหน้าเว็บขึ้นว่า `ไม่มีข้อมูลให้แสดง เพราะเชื่อมต่อ Scopus API ไม่สำเร็จ หรือ query ไม่พบข้อมูล` ให้ตรวจ `/api/config` ก่อน:

```bash
python3 - <<'PY'
import json, urllib.request
print(json.loads(urllib.request.urlopen('http://localhost:4173/api/config').read()))
PY
```

ถ้าได้ `{"scopusConfigured": false}` แปลว่า server ที่รันอยู่ยังไม่โหลด `SCOPUS_API_KEY` ให้สร้างหรือแก้ไฟล์ `.env` แล้ว restart server:

```bash
python3 scripts/stop_server.py
python3 scripts/start_server.py
```

หมายเหตุ: `.env` ถูก ignore โดย git แล้ว เพื่อไม่ให้ API key หลุดเข้า repository

เปิดใช้งาน:

```text
http://localhost:4173
```

หากให้คนอื่นในเครือข่ายเดียวกันเข้าใช้งาน ให้ใช้ IP ของเครื่องที่รัน server เช่น:

```text
http://192.168.1.130:4173
```

## API ที่มีในระบบ

### `GET /api/config`

ตรวจว่า server มี `SCOPUS_API_KEY` แล้วหรือยัง

### `GET /api/staff`

คืนรายชื่ออาจารย์ whitelist ที่ใช้กรองข้อมูล

### `GET /api/scopus/search`

ดึงผลงานจาก Scopus ตามรายชื่ออาจารย์ whitelist

พารามิเตอร์หลัก:

- `count`: จำนวน record ต่อหน้า สูงสุด 25
- `date`: ช่วงปี เช่น `2022-2026`
- `staff`: นามสกุลอาจารย์ เช่น `Khongphinitbunjong`; ถ้าไม่ส่งจะค้นทุกคน

ค่าเริ่มต้นของระบบคือย้อนหลัง 5 ปี จากปีปัจจุบัน เช่นวันที่ 2026-06-01 จะใช้ช่วง `2022-2026`

## รายชื่อ Academic Staff ที่ใช้เป็น whitelist

ที่มา:

- Chemistry: https://science.mfu.ac.th/en/sci-staff/sci-academic-staff/sci-staff-chemistry.html
- Bioscience: https://science.mfu.ac.th/en/sci-staff/sci-academic-staff/sci-staff-biological-science.html
- Material Science and Engineering: https://science.mfu.ac.th/en/sci-staff/sci-academic-staff/sci-staff-material-and-enginee.html
- Computational Science: https://science.mfu.ac.th/en/sci-staff/sci-academic-staff/sci-staff-computational-science.html

ระบบใช้รายชื่อ academic staff ทุกสาขา รวม 50 คน แยกเป็น:

- Chemistry: 14 คน
- Bioscience: 22 คน
- Material Science and Engineering: 10 คน
- Computational Science: 4 คน

รายชื่อถูกเก็บใน `ACADEMIC_STAFF` ใน `scripts/start_server.py` พร้อม `department` ของแต่ละคน

การจัดกลุ่มสำหรับ Dashboard:

- Chemistry -> Chemistry
- Bioscience -> Biology
- Material Science and Engineering -> Material Science Engineering
- กลุ่มอื่น ๆ เช่น Computational Science -> CIX

Frontend มี filter `สาขา` เพื่อดู publication ตามกลุ่ม academic staff และ CSV export มีคอลัมน์ `staffGroups`

## Scopus Author ID Export

ใช้สคริปต์นี้เพื่อดึง Scopus Author ID ของ academic staff จาก Scopus Author Search API:

```bash
python3 scripts/export_author_ids.py
```

ไฟล์ที่ได้:

- `staff_scopus_author_ids_recommended.csv`: 1 อาจารย์ต่อ 1 แถว เป็น candidate ที่ระบบแนะนำให้ใช้เป็น mapping หลัก
- `staff_scopus_author_ids.csv`: รายการ candidate ทั้งหมดจาก Scopus สำหรับตรวจสอบซ้ำ กรณีคนเดียวมีหลาย Author ID

คอลัมน์สำคัญ:

- `scopusAuthorId`: Author ID จาก Scopus
- `recommended`: `yes` คือ candidate ที่ระบบเลือกเป็นตัวหลัก
- `matchConfidence`: ระดับความมั่นใจ เช่น `high`, `medium`, `needs_review`, `not_found`
- `currentAffiliationName`: affiliation ปัจจุบันที่ Scopus Author Search ส่งกลับมา
- `documentCount`: จำนวนเอกสารรวมของ Author ID นั้นตาม Scopus Author Search API

ผล export ล่าสุดวันที่ 2026-06-04:

- recommended mapping: 50 แถว จาก academic staff 50 คน
- candidate ทั้งหมด: 73 แถว
- not found: 0 คน
- confidence ของ recommended mapping: high 46 คน, medium 4 คน

รายการ medium ที่ควรตรวจซ้ำก่อนใช้ผูกกับระบบถาวร:

- Ajarn Dr. Thinnapong Wongpakdee
- Asst. Prof. Dr. Nanthanit Jaruseranee
- Asst. Prof. Dr. Tophan Thandorn
- Asst. Prof. Dr. Anant Eungwanichayapant

## Scopus Query Strategy

ระบบเคยใช้ query แบบ:

```text
AUTHLASTNAME(lastname)
AND AUTHOR-NAME(firstname)
AND AFFIL("Mae Fah Luang University")
```

แต่พบว่าทำให้ผลงานตกหล่น เช่น Asst. Prof. Dr. Kitiphong Khongphinitbunjong ในปี 2026 ควรมี 3 เรื่อง แต่ query เดิมพบ 1 เรื่อง เพราะ Scopus index ชื่อผู้แต่งบาง record เป็นรูปแบบอื่น

จึงเปลี่ยนเป็น:

```text
AUTHLASTNAME(lastname)
AND AFFIL("Mae Fah Luang University")
AND AFFIL("School of Science")
```

ข้อดี:

- ลดการตกหล่นจากชื่อจริงหรือชื่อย่อที่ Scopus index ไม่เหมือนกัน
- พบผลงานของ Kitiphong ปี 2026 ครบ 3 เรื่อง

ข้อควรระวัง:

- อาจมี false positive หากมีคนใช้นามสกุลเดียวกัน หรือ Scopus ผูก affiliation กว้างเกินไป
- วิธีที่แม่นที่สุดในระยะถัดไปคือใช้ Scopus Author ID รายคน เช่น `AU-ID(...)`

## ผลงาน Kitiphong Khongphinitbunjong ปี 2026

หลังแก้ query พบครบ 3 records:

- Identification of Aquapteridospora guangxiensis sp. nov., a Novel Lignicolous Freshwater Fungus from Guangxi Province, China
- Morpho-cultural and molecular phylogenetic analyses reveal Neoarthrinium kaempferiae sp. nov. (Neoarthriniaceae), an endophytic fungus from Kaempferia galanga in Guangdong, China
- Poly(styrene-alt-maleic acid)-assisted Membrane Solubilization for Improved Immobilization and Catalytic Performance of Soybean Lipolytic Enzymes in Electrospun Poly(vinyl alcohol) Fibers

## Q1/Q2 และ Journal Metrics

Scopus Search API `STANDARD` view ไม่คืนค่า quartile โดยตรง ระบบจึงใช้ข้อมูลจาก Elsevier Serial Title API:

```text
https://api.elsevier.com/content/serial/title
```

ระบบใช้ `source-id` หรือ ISSN จาก publication record ไปค้นข้อมูลวารสารด้วย `view=CITESCORE`

จากนั้นคำนวณ quartile จาก CiteScore percentile:

- Q1: percentile 75 ขึ้นไป
- Q2: percentile 50-74
- Q3: percentile 25-49
- Q4: percentile ต่ำกว่า 25

ในตาราง Publication Records จะแสดงรูปแบบ:

```text
Q1
2024 · P92
```

หมายถึง CiteScore metric ปี 2024 และ percentile 92

## สถานะข้อมูลล่าสุดที่ทดสอบ

ทดสอบล่าสุดหลังเพิ่ม academic staff ทุกสาขา:

- ดึงข้อมูลย้อนหลัง 5 ปี ช่วง `2022-2026`
- ใช้ academic staff whitelist 50 คนจาก 4 สาขา
- ระบบดึงครบแบบ pagination
- หน้า Dashboard แสดง Q1/Q2 ใน Publication Records
- เลือกปี 2026 + Asst. Prof. Dr. Kitiphong Khongphinitbunjong แล้วพบ 3 records
- ทดสอบ API ได้ 638 publications หลัง dedupe จาก total staff-query results 1042 records
- รอบแรกหลัง restart ใช้เวลาประมาณ 36.8 วินาที หลังจากนั้นเร็วขึ้นด้วย cache ฝั่ง server
- หน้าเว็บจะ auto sync เมื่อโหลดหน้า หาก backend มี `SCOPUS_API_KEY`
- หากเชื่อมต่อ Scopus API ไม่สำเร็จ ระบบจะแสดงไม่มีข้อมูล ไม่ fallback ไปใช้ mock data
- ตรวจ quality ของวารสารใหม่ทั้งชุด 638 records หลังปรับ fallback การหา metric แล้วได้ Q1/Q2/Q3/Q4 เกือบครบ เหลือ `NA` 4 records ที่ Serial Title API ไม่คืน CiteScore metric
- ตรวจจำนวนผลงานรายปีจาก dataset ล่าสุด 638 records แล้ว พบว่าปี 2025 มี 170 เรื่องแบบ dedupe paper แต่มี 307 counts หากนับแบบ staff-authorship
- เพิ่ม filter บทบาทผู้แต่งในหน้า Dashboard ได้แก่ Authors, First author และ Corresponding author

หลังเปลี่ยน query เป็นนามสกุล + MFU + School of Science ยอดรวม 5 ปีเพิ่มขึ้นจากเดิม เพราะ query เดิมมีการตกหล่น

หมายเหตุเรื่องการ sync: รอบแรกหลัง restart server อาจใช้เวลาประมาณ 30-60 วินาที เพราะระบบต้องดึงทั้ง Scopus publications ของ staff 50 คน และเติม Q1/Q2 จาก Elsevier Serial Title API ของหลายวารสาร หลังจากนั้นจะเร็วขึ้นเพราะมี cache ฝั่ง server 10 นาที

## จำนวนผลงานรายปี

นับจากข้อมูลล่าสุดช่วง `2022-2026` รวม 638 records หลัง dedupe

| ปี | ผลงานแบบ dedupe | นับตาม staff-authorship | Q1 | Q2 | Q3 | Q4 | NA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026 | 63 | 110 | 28 | 16 | 18 | 1 | 0 |
| 2025 | 170 | 307 | 100 | 31 | 37 | 1 | 1 |
| 2024 | 160 | 263 | 84 | 32 | 39 | 5 | 0 |
| 2023 | 120 | 180 | 72 | 24 | 19 | 4 | 1 |
| 2022 | 125 | 182 | 75 | 14 | 32 | 2 | 2 |

หมายเหตุ:

- `ผลงานแบบ dedupe` หมายถึง paper หนึ่งเรื่องนับหนึ่งครั้ง แม้มีอาจารย์หลายคนใน whitelist อยู่ใน paper เดียวกัน
- หน้า Dashboard แสดงค่า dedupe รายปีใน panel `Yearly Dedupe Publications` โดยใช้ข้อมูลจาก Scopus API response ปัจจุบัน
- `staff-authorship` หมายถึง paper เดียวกันอาจถูกนับมากกว่าหนึ่งครั้ง หากมีอาจารย์ใน whitelist หลายคนร่วมอยู่ในผลงานนั้น
- ตัวเลขปี 2025 ที่จำได้ว่าเกิน 186 สอดคล้องกับการนับแบบ staff-authorship ซึ่งได้ 307

## Author Role Filter

หน้า Dashboard มี filter `บทบาทผู้แต่ง` โดย option default แสดงเป็น `Authors`

- First author
- Corresponding author

ข้อจำกัดปัจจุบัน:

- `First author` ตรวจจาก `dc:creator` หรือ first creator ที่ Scopus Search API `STANDARD` view ส่งกลับมา
- `Co-author` คืออาจารย์ที่ match กับ publication แต่ไม่ใช่ first creator
- `Corresponding author` ยังไม่สามารถตรวจแบบอัตโนมัติได้จาก API key ปัจจุบัน เพราะ Abstract Retrieval `FULL`/`META_ABS` ได้ `401 Unauthorized`; option นี้จึงเตรียมไว้สำหรับต่อข้อมูล corresponding author ในอนาคต

ผลตรวจล่าสุดจาก dataset 638 records:

- First author staff-authorship count: 53
- Co-author staff-authorship count: 989
- Corresponding author count: 0 เพราะยังไม่มี source ที่ระบุ corresponding author

## SDG Mapping

หน้า Publication Records มีคอลัมน์ `SDG` เพื่อแสดง Sustainable Development Goals ที่เกี่ยวข้องกับผลงานตีพิมพ์

วิธี mapping ปัจจุบัน:

- Backend ตรวจ keyword จาก `title`, `journal` และ `publication type`
- ระบบแสดงได้หลาย SDG ต่อหนึ่ง publication หากมี keyword ตรงหลายกลุ่ม
- หากไม่พบ keyword จะแสดง `Unmapped`
- ค่า SDG ปัจจุบันเป็น `rule-based inference` ไม่ใช่ metadata ที่ Scopus ยืนยันโดยตรง จึงควรใช้เป็นข้อมูลตั้งต้นสำหรับตรวจสอบหรือปรับ mapping ต่อ

การคัดกรอง School of Science/MFU:

- Scopus query ใช้ pattern `AUTHLASTNAME(<staff last name>) AND AFFIL("Mae Fah Luang University") AND AFFIL("School of Science")`
- แต่ละ publication มี field `schoolFilterEvidence` เพื่อบอกหลักฐานการคัดกรองเบื้องต้น
- API response มี `filterCriteria` เพื่อให้ตรวจสอบเงื่อนไขที่ใช้ดึงข้อมูลในรอบนั้นได้

## ไฟล์หลัก

- `index.html`: โครงหน้า dashboard
- `preview.html`: redirect สำหรับเครื่องมือ preview ที่เปิด `/preview.html` ให้กลับไปหน้า dashboard หลัก
- `styles.css`: layout และ visual design
- `app.js`: frontend logic, filter, chart, export CSV, sync Scopus
- `scripts/start_server.py`: static server และ backend proxy สำหรับ Scopus/Elsevier APIs
- `scripts/stop_server.py`: หยุด server
- `.env.example`: ตัวอย่างการตั้งค่า API key
- `.gitignore`: กัน secret, log, pid และไฟล์ generated
- `README.md`: วิธี run แบบย่อ
- `RESEARCH_DASHBOARD_WORK_PLAN.md`: แผนการทำงานระบบ
- `STAFF_PUBLICATION_AUDIT.md`: รายงาน audit จำนวนผลงานรายอาจารย์แยกปี
- `staff_publication_audit.csv`: รายการผลงานละเอียด 1 แถวต่ออาจารย์ต่อ publication สำหรับตรวจใน spreadsheet
- `SCOPUS_COUNT_RECONCILIATION.md`: รายงานเทียบจำนวนผลงานระหว่าง Scopus website count, Scopus API affiliation query และ dashboard staff whitelist
- `scopus_affiliation_not_in_staff_dashboard.csv`: รายการ affiliation-wide records ที่ยังไม่เข้า dashboard เพราะไม่ match กับ current academic staff whitelist

## Change Log

### 2026-06-01

- สร้าง `RESEARCH_DASHBOARD_WORK_PLAN.md` เป็นแผนงานพัฒนา Research Publications & KPI Dashboard
- สร้าง static web dashboard ด้วย `index.html`, `styles.css`, `app.js`
- เพิ่ม mock data, KPI cards, chart, filters, publication table, review queue และ export CSV
- เพิ่ม Python static server พร้อม start/stop scripts
- เพิ่ม backend proxy สำหรับ Scopus API โดยอ่าน `SCOPUS_API_KEY` จาก environment หรือ `.env`
- แก้ SSL certificate สำหรับ Python บน macOS ให้เรียก Elsevier API ได้
- เปลี่ยน Scopus Search API จาก `view=COMPLETE` เป็น `view=STANDARD` เพราะ API key ไม่มีสิทธิ์ COMPLETE
- เพิ่ม staff whitelist จากหน้า Executive Staff ของ School of Science, MFU
- ปรับการดึงข้อมูลเป็นย้อนหลัง 5 ปี และทำ pagination ให้ครบ
- เพิ่มการ enrich Q1/Q2 จาก Elsevier Serial Title API และคำนวณ quartile จาก CiteScore percentile
- แก้ query strategy จาก `AUTHOR-NAME(firstname)` เป็น `AUTHLASTNAME(lastname) + AFFIL(MFU) + AFFIL(School of Science)` เพื่อลดการตกหล่น
- ตรวจพบและแก้กรณี Kitiphong Khongphinitbunjong ปี 2026 จาก 1 record เป็น 3 records
- เพิ่มไฟล์ `guide.md` เพื่อเป็นคู่มือและบันทึกการเปลี่ยนแปลงของโปรเจกต์
- เพิ่ม progress timer และ timeout 120 วินาทีระหว่าง sync เพื่อให้ผู้ใช้เห็นว่าระบบยังรอ Scopus/Elsevier API อยู่ ไม่ได้ค้างเงียบ
- เปลี่ยน whitelist จาก executive staff 9 คน เป็น academic staff ทุกสาขา 50 คน จาก Chemistry, Bioscience, Material Science and Engineering และ Computational Science
- ปรับ backend ให้ค้น Scopus ของ staff หลายคนแบบ parallel เพื่อรองรับรายชื่อที่เพิ่มขึ้น
- ปิดการ fallback ไปใช้ mock data เมื่อ API ใช้งานไม่ได้ โดยให้แสดง empty state แทน
- เพิ่ม auto sync ตอนโหลดหน้าเว็บ ถ้า `/api/config` ตรวจพบว่า backend มี `SCOPUS_API_KEY`
- แก้การหา Q1/Q2 ให้ fallback จาก `source-id` ไป `ISSN`, `eISSN` และ `journal title` พร้อม retry กรณี Serial Title API ตอบช้าหรือ error ชั่วคราว
- ตรวจพบว่า `Biomedical Reports` ควรเป็น `Q1` และแก้แล้ว โดยได้ CiteScore metric ปี 2024 percentile 77
- หลัง audit quality ทั้งชุดล่าสุด: Q1 = 359, Q2 = 117, Q3 = 145, Q4 = 13, NA = 4 จากทั้งหมด 638 records
- ตรวจจำนวนผลงานรายปีและเพิ่มตาราง count semantics ลงใน `guide.md`; ปี 2025 ได้ 170 แบบ dedupe และ 307 แบบ staff-authorship
- เพิ่ม filter `บทบาทผู้แต่ง` ในหน้า Dashboard และเพิ่ม `matchedStaffRoles` ใน backend เพื่อรองรับ First author / Co-author / Corresponding author
- เปลี่ยน option default ของ filter บทบาทผู้แต่งจาก `ทุกบทบาท` เป็น `Authors` และลบ `Co-author` ออกจากตัวเลือก filter
- แก้ปัญหา server process รันโดยไม่มี `SCOPUS_API_KEY` ทำให้ `/api/scopus/search` ตอบ 503; เพิ่ม `.env` ในเครื่องและ restart server แล้ว API กลับมาได้ 638 publications
- เพิ่ม troubleshooting ใน `guide.md` สำหรับกรณี `/api/config` เป็น `scopusConfigured: false`
- เพิ่ม panel `Yearly Dedupe Publications` บน Dashboard เพื่อแสดงจำนวน publication แบบ dedupe ในแต่ละปีตามข้อมูล Scopus API
- 2026-06-01 20:11 ICT: เพิ่มคอลัมน์ `SDG` ใน Publication Records และ CSV export, เพิ่ม rule-based SDG mapping ใน backend, เพิ่ม `filterCriteria`/`schoolFilterEvidence` เพื่อให้ตรวจสอบการคัดกรอง School of Science, Mae Fah Luang University ได้ชัดขึ้น และอัปเดตแผนงานให้รองรับ PublicationSDGs
- ตรวจสอบ API หลัง restart server: ได้ 638 publications, มี `filterCriteria`, ทุก sample มี `schoolFilterEvidence`, และ map SDG ได้ 452 records
- 2026-06-01 21:18 ICT: เพิ่มการจัดกลุ่ม academic staff เป็น Chemistry, Biology, Material Science Engineering และ CIX ตามเมนู Academic Staff ของ School of Science; เพิ่ม field `academicGroup`, `matchedStaffGroups`, filter `สาขา`, badge กลุ่มใน Top Authors/Publication Records และคอลัมน์ `staffGroups` ใน CSV export
- ตรวจสอบ API หลัง restart server: staff group counts คือ Chemistry 14, Biology 22, Material Science Engineering 10, CIX 4; publication group counts คือ Chemistry 129, Biology 480, Material Science Engineering 52, CIX 42 จาก 638 publications
- 2026-06-02 10:42 ICT: เพิ่ม option `2023-2026` ใน filter ปี และเพิ่ม logic ให้ year filter รองรับช่วงปีรูปแบบ `YYYY-YYYY`
- 2026-06-02 10:45 ICT: เปลี่ยน filter ปีจาก select เป็น checklist เพื่อเลือกหลายปีเองได้ เช่น 2023, 2024, 2026 พร้อม option `ทุกปี` ที่ล้าง selection แล้วกลับไปแสดงข้อมูลทั้งหมด
- 2026-06-02 11:13 ICT: ตรวจสอบ publication ของ `Ajarn Dr. Prachak Inkaew` ปี 2026 จาก Scopus API ทั้ง endpoint เฉพาะ `staff=Inkaew` และ dataset รวมของ dashboard พบ 4 เรื่องตรงกัน
- 2026-06-02 11:17 ICT: สร้าง audit รายอาจารย์ทั้งหมดใน `STAFF_PUBLICATION_AUDIT.md` และ `staff_publication_audit.csv`; ตรวจ 50 academic staff ในช่วง 2022-2026 ได้ 638 deduped publications, 1042 staff-authorship rows, mismatch ระหว่าง staff query total กับ mapped count = 0, และพบ staff ที่ไม่มี publication ในช่วงนี้ 2 คน
- 2026-06-02 11:37 ICT: สร้าง `SCOPUS_COUNT_RECONCILIATION.md` และ `scopus_affiliation_not_in_staff_dashboard.csv` เพื่อเทียบจำนวนที่ผู้ใช้ตรวจจาก Scopus website กับ Scopus API; พบว่า website count ใกล้กับ affiliation/general query ส่วน dashboard ปัจจุบันต่ำกว่าเพราะนับเฉพาะ current academic staff whitelist 50 คน
- 2026-06-02 11:45 ICT: เพิ่ม filter `ขอบเขตข้อมูล` ให้เลือกได้ระหว่าง `Current academic staff` และ `Total (affiliation-wide Scopus)`; backend รองรับ `mode=staff` และ `mode=affiliation` ใน `/api/scopus/search`
- ตรวจสอบ API หลังเพิ่ม scope filter: `mode=staff` ได้ 638 deduped publications; `mode=affiliation` ได้ 892 deduped publications จาก raw total 893 และ count รายปีคือ 2026=74, 2025=210, 2024=222, 2023=207, 2022=179; เพิ่ม frontend timeout เป็น 240 วินาทีเพื่อรองรับ Total mode รอบแรก
- 2026-06-02 17:38 ICT: ปรับ filter `ผู้แต่ง` ให้ขึ้นกับ filter `สาขา` ในโหมด `Current academic staff`; เมื่อเลือกสาขา dropdown ผู้แต่งจะแสดงเฉพาะอาจารย์ในสาขานั้นจาก staff directory ทั้งหมด และ reset เป็น `ทุกคน` หากอาจารย์เดิมไม่อยู่ในสาขาใหม่
- 2026-06-02 17:48 ICT: สลับลำดับ filter ให้ `สาขา` มาก่อน `ผู้แต่ง` เพื่อให้เลือกสาขาก่อนแล้วค่อยเลือกอาจารย์ได้เป็นธรรมชาติกว่าเดิม
- 2026-06-02 17:58 ICT: ปรับ `Total (affiliation-wide Scopus)` ให้ตรวจจับ current academic staff จาก author indexed-name ด้วยนามสกุลและ first initial; ตารางจะแสดงชื่ออาจารย์ที่ match ได้จริง และแสดง `No current staff match` เมื่อไม่พบ match แทนการ fallback เป็นรายชื่อ authors ทั่วไป
- ตรวจสอบ Total mode หลังปรับ matching: affiliation-wide 5 ปีได้ 891 records และ detect current academic staff ได้ 49 records แยกเป็น 2026=6, 2025=12, 2024=11, 2023=9, 2022=11
- 2026-06-03 17:06 ICT: ปรับ `Total (affiliation-wide Scopus)` ให้ overlay `matchedStaff` จาก current academic staff Scopus queries ด้วย Scopus EID เพื่อจับ co-author ที่ Search API ไม่ส่งใน `authors`; ยืนยัน paper `Anti-cancer effects of cordyceps sinensis, C. militaris and C. cicadae and their mechanisms of action` แสดง `Ajarn Dr. Amorn Owatworakit` และ `Asst. Prof. Dr. Sunita Chamyuang` เป็น `co_author` ใน Total mode แล้ว พร้อมเพิ่ม retry/backoff และลด parallel staff overlay เพื่อลด 429 จาก Scopus
- 2026-06-03 17:22 ICT: เพิ่ม field `schoolAffiliationVerified`, `schoolAffiliationScope` และ `schoolFilterEvidence` สำหรับรายการ affiliation-wide โดยเฉพาะ record ที่เป็น `No current staff match`; frontend จะแสดง badge `School affiliation verified` เพื่อบอกว่าผ่าน Scopus query ของ `School of Science, Mae Fah Luang University` แล้ว แม้ไม่พบ current academic staff match
- 2026-06-03 17:31 ICT: เพิ่ม scorecard `International Co-authors` เพื่อนับผลงานที่มี affiliation ของ co-author จากสถาบันนอกประเทศไทย โดยตรวจจาก field `affiliation` ของ Scopus; CSV export เพิ่ม `internationalCoauthorAffiliation` และ `foreignAffiliations`
- 2026-06-03 17:42 ICT: เปลี่ยน filter `ผู้แต่ง` จาก dropdown อย่างเดียวเป็นช่องพิมพ์พร้อม dropdown (`input` + `datalist`) เพื่อให้พิมพ์ค้นชื่อบางส่วนได้ และยังเลือกจากรายการชื่อได้เหมือนเดิม
- 2026-06-04 15:29 ICT: หลัง restart เครื่อง local server หยุดทำงาน จึง start ใหม่ด้วย `python3 scripts/start_server.py`; ตรวจแล้ว `http://localhost:4173` ตอบ `200 OK` และ `/api/config` เป็น `scopusConfigured: true`
- 2026-06-04 15:40 ICT: เพิ่ม `scripts/export_author_ids.py` เพื่อดึง Scopus Author ID จาก Scopus Author Search API และสร้างไฟล์ `staff_scopus_author_ids_recommended.csv` กับ `staff_scopus_author_ids.csv`; export ล่าสุดได้ recommended mapping ครบ 50 academic staff, candidate ทั้งหมด 73 แถว, not found 0 คน
- 2026-06-11 09:49 ICT: เพิ่ม `preview.html` เป็น redirect ไปหน้า dashboard หลัก เพื่อแก้กรณีเครื่องมือ preview เปิด `/preview.html` แล้วเจอ 404
- 2026-06-11 09:53 ICT: เปลี่ยน local server เป็น threaded server เพื่อให้หน้า dashboard และ `/api/config` ยังเปิดได้ระหว่างที่ `/api/scopus/search` กำลังรอ Scopus/Elsevier API
- 2026-06-17 13:57 ICT: ปรับ scorecard จาก `Q1 / Q2 Ratio` เป็น `Q1 / Total Publications` โดยคำนวณจากจำนวนผลงาน Q1 หารด้วยจำนวนผลงานตีพิมพ์ทั้งหมดในชุดข้อมูลที่เลือก
- 2026-06-25 13:36 ICT: ตรวจกรณีเข้า dashboard ไม่ได้ พบว่า local server หยุดทำงานและ port `4173` ไม่ได้ถูกใช้งาน จึง start ใหม่ด้วย `python3 scripts/start_server.py`; ตรวจแล้ว `http://localhost:4173/` ตอบ `200 OK`, `/api/config` เป็น `scopusConfigured: true`, และ process ใหม่ `PID 7468` กำลัง listen ที่ port `4173`
- 2026-07-09 11:15 ICT: ตรวจกรณีเข้า SciDash ไม่ได้ พบว่า server เดิมยังทำงานที่ port `4173`; ตรวจหน้า dashboard, `styles.css`, `app.js` และ `/api/config` แล้วตอบ `200 OK` ทั้งหมด พร้อมยืนยัน `scopusConfigured: true` จึงให้เปิด URL ใหม่พร้อม cache-busting parameter

## Next Steps

- นำ mapping `staff -> Scopus Author ID` ไปใช้กับ query ของ dashboard เพื่อลด false positive/false negative จากการค้นด้วยนามสกุล
- เพิ่มหน้าตรวจสอบ manual review สำหรับ false positive/false negative
- เพิ่มฐานข้อมูลถาวร เช่น PostgreSQL หรือ SQLite
- เพิ่มระบบ login และ role-based access
- เพิ่มการ schedule sync อัตโนมัติ
- เพิ่มตัวเลือก download รายงานตามปี/อาจารย์/Quartile
