# แผนการทำงาน: Research Publications & KPI Dashboard

## 1. วัตถุประสงค์ของระบบ (Objective)

พัฒนา Web Application หรือ Dashboard สำหรับติดตาม คัดกรอง ประมวลผล และแสดงผลข้อมูลผลงานตีพิมพ์ระดับนานาชาติ รวมถึง KPI ด้านการวิจัยของสำนักวิชา โดยเน้นข้อมูลที่เกี่ยวข้องกับ School of Science, Mae Fah Luang University

ระบบนี้มีเป้าหมายเพื่อช่วยให้ผู้บริหารและบุคลากรสามารถตรวจสอบภาพรวมผลงานวิจัย วิเคราะห์แนวโน้ม และติดตามตัวชี้วัดสำคัญได้อย่างเป็นระบบ ลดภาระงาน manual ในการรวบรวม ตรวจสอบ และสรุปข้อมูลจากหลายแหล่ง

## 2. ขอบเขตการทำงานของระบบ (Scope of Work)

### 2.1 Data Ingestion: การดึงข้อมูล

ระบบต้องสามารถดึงข้อมูลผลงานตีพิมพ์จาก Scopus API โดยครอบคลุมข้อมูลหลัก เช่น

- ชื่อผลงานตีพิมพ์
- รายชื่อผู้แต่ง
- Affiliation ของผู้แต่ง
- ปีที่ตีพิมพ์
- ชื่อวารสารหรือแหล่งตีพิมพ์
- DOI, EID หรือ identifier อื่นที่ใช้ตรวจสอบความซ้ำ
- จำนวน citation
- ประเภทเอกสาร เช่น Article, Review, Conference Paper
- Subject area หรือสาขาที่เกี่ยวข้อง
- ข้อมูลวารสาร เช่น quartile, percentile, SJR หรือ CiteScore หากสามารถดึงได้จากแหล่งข้อมูลที่รองรับ

แนวทางการดึงข้อมูล:

- เชื่อมต่อ Scopus API ด้วย API key และ configuration ที่ปลอดภัย
- กำหนด query สำหรับค้นหาผลงานที่เกี่ยวข้องกับ Mae Fah Luang University และ School of Science
- รองรับการดึงข้อมูลตามช่วงปี เช่น รายปี หรือย้อนหลังหลายปี
- เก็บ log การดึงข้อมูลแต่ละครั้ง เช่น วันที่ดึง จำนวน records ที่ได้ และ error ที่พบ
- ออกแบบให้สามารถตั้งเวลาอัปเดตอัตโนมัติ เช่น รายวัน รายสัปดาห์ หรือรายเดือน

### 2.2 Data Filtering & Cleaning: การกลั่นกรองและทำความสะอาดข้อมูล

ระบบต้องคัดกรองข้อมูลให้เหลือเฉพาะผลงานที่เกี่ยวข้องกับ School of Science, Mae Fah Luang University โดยพิจารณาจาก Affiliation และ Authors

เงื่อนไขการคัดกรองหลัก:

- Affiliation มีข้อความที่เกี่ยวข้องกับ Mae Fah Luang University
- Affiliation มีข้อความที่เกี่ยวข้องกับ School of Science หรือหน่วยงานย่อยภายในสำนักวิชา
- ผู้แต่งตรงกับรายชื่อบุคลากรของ School of Science
- รองรับกรณีชื่อผู้แต่งมีหลายรูปแบบ เช่น ชื่อย่อ ชื่อเต็ม การสะกดต่างกัน หรือมี middle name

การทำความสะอาดข้อมูล:

- ตรวจสอบและลบข้อมูลซ้ำโดยใช้ DOI, EID, Scopus ID หรือ combination ของ title, year และ authors
- จัดรูปแบบชื่อผู้แต่งให้เป็นมาตรฐานเดียวกัน
- จัดรูปแบบ affiliation ให้สามารถค้นหาและจัดกลุ่มได้
- ตรวจสอบข้อมูลที่ไม่สมบูรณ์ เช่น ไม่มี DOI, ไม่มี citation count, ไม่มี affiliation
- แยกสถานะข้อมูล เช่น verified, needs review, excluded
- มีหน้าหรือ workflow สำหรับให้เจ้าหน้าที่ตรวจสอบข้อมูลที่ระบบไม่มั่นใจ

### 2.3 Data Storage: การจัดเก็บข้อมูล

ระบบควรมีฐานข้อมูลกลางสำหรับเก็บข้อมูลที่ผ่านการดึง คัดกรอง และตรวจสอบแล้ว

ตารางข้อมูลสำคัญที่ควรมี:

- Publications: ข้อมูลผลงานตีพิมพ์
- Authors: ข้อมูลผู้แต่ง
- AcademicStaffGroups: การจัดกลุ่ม academic staff เป็น Chemistry, Biology, Material Science Engineering และ CIX
- Affiliations: ข้อมูลหน่วยงานต้นสังกัด
- PublicationAuthors: ความสัมพันธ์ระหว่างผลงานและผู้แต่ง
- Journals: ข้อมูลวารสาร
- PublicationSDGs: SDG ที่เกี่ยวข้องกับผลงาน พร้อมวิธีระบุ เช่น keyword inference หรือ verified source
- KPIResults: ผลการคำนวณ KPI ตามรอบเวลา
- ImportLogs: ประวัติการดึงข้อมูล
- ReviewQueue: รายการที่ต้องตรวจสอบด้วยมือ

ฐานข้อมูลที่เหมาะสม:

- PostgreSQL สำหรับระบบที่ต้องการความน่าเชื่อถือและ query เชิงวิเคราะห์
- SQLite สำหรับ prototype หรือ proof of concept
- รองรับการ export เป็น CSV หรือ Excel เพื่อใช้ประกอบรายงาน

### 2.4 Data Visualization: การแสดงผล Dashboard

Dashboard ต้องสรุปข้อมูลให้ตอบโจทย์การกำกับติดตามผลงานวิจัยและ KPI ของสำนักวิชา

หน้าหลักที่ควรมี:

- Overview Dashboard: ภาพรวมผลงานตีพิมพ์ทั้งหมด
- Publication Trend: จำนวนผลงานตีพิมพ์รายปี
- Author Performance: ผลงานรายบุคคล
- Citation Dashboard: จำนวน citation รวม รายปี และรายผลงาน
- Journal Quartile Dashboard: สัดส่วนผลงานใน Q1, Q2, Q3, Q4
- SDG Dashboard/Column: แสดง SDG ที่เกี่ยวข้องกับผลงานตีพิมพ์เพื่อใช้ติดตามผลกระทบเชิงยุทธศาสตร์
- h-index / Research Impact: ตัวชี้วัดผลกระทบทางวิชาการ
- Data Review: หน้าตรวจสอบข้อมูลที่ระบบคัดกรองไม่ได้ชัดเจน
- Export Report: ส่งออกข้อมูลและรายงาน

ตัวกรองที่ควรมี:

- ปีที่ตีพิมพ์ 5 ปีย้อนหลัง เริ่มตั้งแน่ 2021
- ชื่อผู้แต่ง
- หน่วยงานหรือหลักสูตร
- กลุ่ม academic staff: Chemistry, Biology, Material Science Engineering, CIX
- ประเภทเอกสาร
- Quartile
- Subject area
- สถานะการตรวจสอบข้อมูล

รูปแบบ visualization ที่ควรใช้:

- KPI cards สำหรับตัวเลขสรุปสำคัญ
- Line chart สำหรับแนวโน้มรายปี
- Bar chart สำหรับเปรียบเทียบผลงานรายบุคคลหรือรายหน่วยงาน
- Pie หรือ donut chart สำหรับสัดส่วน quartile
- Table สำหรับรายการผลงานแบบละเอียด
- Search และ filter สำหรับค้นหาข้อมูลเฉพาะ

## 3. KPI ที่ระบบควรรองรับ

ระบบควรรองรับการคำนวณและแสดงผล KPI ด้านการวิจัย เช่น

- จำนวนผลงานตีพิมพ์ทั้งหมด
- จำนวนผลงานตีพิมพ์รายปี
- จำนวนผลงานตีพิมพ์รายบุคคล
- จำนวนผลงานตีพิมพ์ในฐาน Scopus
- จำนวน citation รวม
- จำนวน citation เฉลี่ยต่อผลงาน
- h-index ระดับบุคคลหรือระดับสำนักวิชา
- สัดส่วนผลงานในวารสาร Q1 และ Q2
- จำนวนผลงาน international collaboration
- จำนวนผลงานที่มี corresponding author อยู่ใน School of Science
- จำนวนผลงานตาม subject area

หมายเหตุ: นิยาม KPI ควรยืนยันกับผู้ใช้งานหลักก่อนเริ่มพัฒนา เพราะบางตัวชี้วัดอาจมีสูตรคำนวณเฉพาะตามเกณฑ์ของมหาวิทยาลัยหรือหน่วยงานประเมิน

## 4. ผู้ใช้งานระบบ (User Roles)

### 4.1 ผู้บริหาร

- ดูภาพรวม KPI และแนวโน้มผลงานวิจัย
- Export รายงานเพื่อใช้ประกอบการประชุมหรือประเมินผล
- ติดตามผลรายปี รายหลักสูตร หรือรายบุคคล

### 4.2 เจ้าหน้าที่วิจัยหรือผู้ดูแลข้อมูล

- ตรวจสอบรายการผลงานที่ระบบดึงเข้ามา
- ยืนยัน แก้ไข หรือยกเว้นข้อมูล
- จัดการรายชื่อบุคลากรและ mapping ชื่อผู้แต่ง
- ตรวจสอบ log การอัปเดตข้อมูล

### 4.3 อาจารย์หรือนักวิจัย

- ดูผลงานของตนเอง
- ตรวจสอบความถูกต้องของข้อมูล
- แจ้งแก้ไขข้อมูลที่ไม่สมบูรณ์

## 5. แนวทางสถาปัตยกรรมระบบ (System Architecture)

โครงสร้างระบบที่แนะนำ:

- Frontend: Web Dashboard สำหรับแสดงผลและจัดการข้อมูล
- Backend API: จัดการ business logic, authentication, filtering, KPI calculation
- Database: เก็บข้อมูล publications, authors, affiliations, KPI และ logs
- Data Ingestion Worker: ดึงข้อมูลจาก Scopus API ตามรอบเวลา
- Data Cleaning Pipeline: ประมวลผล ลบข้อมูลซ้ำ และจัดสถานะข้อมูล
- Scheduler: ตั้งเวลาอัปเดตข้อมูลอัตโนมัติ
- Export Module: สร้างรายงาน CSV, Excel หรือ PDF

Technology stack ที่สามารถพิจารณา:

- Frontend: Next.js, React, Vue หรือ Streamlit สำหรับ prototype
- Backend: Node.js, Python FastAPI หรือ Django
- Database: PostgreSQL
- Charts: Recharts, ECharts, Plotly หรือ Chart.js
- Background jobs: Celery, BullMQ, cron job หรือ scheduler ของ cloud provider
- Deployment: Docker, VPS, university server หรือ cloud platform

## 6. แผนการดำเนินงาน (Implementation Plan)

### Phase 1: Requirement & KPI Definition

ระยะเวลาโดยประมาณ: 1-2 สัปดาห์

งานหลัก:

- ระบุผู้ใช้งานหลักและ workflow ที่ต้องการ
- สรุป KPI ที่ต้องแสดงผล
- กำหนดนิยามของผลงานที่นับเป็นของ School of Science
- รวบรวมรายชื่อบุคลากรและ affiliation ที่เกี่ยวข้อง
- ตรวจสอบเงื่อนไขการเข้าถึง Scopus API

ผลลัพธ์:

- เอกสาร requirement
- รายการ KPI พร้อมสูตรคำนวณ
- รายชื่อ authors และ affiliation สำหรับใช้คัดกรอง

### Phase 2: Data Model & Prototype

ระยะเวลาโดยประมาณ: 2-3 สัปดาห์

งานหลัก:

- ออกแบบ database schema
- สร้าง prototype สำหรับดึงข้อมูลจาก Scopus API
- ทดลอง query ข้อมูลตามปีและ affiliation
- สร้าง rule เบื้องต้นสำหรับ filter และ deduplication
- สร้าง dashboard เบื้องต้นจากข้อมูลตัวอย่าง

ผลลัพธ์:

- Prototype ที่ดึงข้อมูลได้จริง
- Database schema รุ่นแรก
- Dashboard mockup หรือ working prototype

### Phase 3: Data Cleaning & Verification Workflow

ระยะเวลาโดยประมาณ: 2-4 สัปดาห์

งานหลัก:

- พัฒนา pipeline สำหรับ clean, normalize และ deduplicate ข้อมูล
- สร้างระบบ author matching
- สร้างสถานะข้อมูล เช่น verified, needs review, excluded
- ทำหน้าจอสำหรับตรวจสอบข้อมูลที่ต้อง review
- เก็บประวัติการแก้ไขหรือการยืนยันข้อมูล

ผลลัพธ์:

- ระบบคัดกรองข้อมูลที่ใช้งานได้
- หน้าตรวจสอบข้อมูล
- ข้อมูลผลงานที่ผ่านการตรวจสอบชุดแรก

### Phase 4: Dashboard & KPI Calculation

ระยะเวลาโดยประมาณ: 3-5 สัปดาห์

งานหลัก:

- พัฒนาหน้า dashboard หลัก
- คำนวณ KPI ตามนิยามที่ตกลง
- เพิ่ม filter และ search
- เพิ่ม chart และ table สำหรับ drill-down
- เพิ่ม export รายงาน
- ตรวจสอบความถูกต้องของตัวเลขกับข้อมูล manual เดิมถ้ามี

ผลลัพธ์:

- Dashboard ที่ใช้งานได้จริง
- KPI cards และ charts สำคัญ
- Export รายงานได้

### Phase 5: Automation, Security & Deployment

ระยะเวลาโดยประมาณ: 2-4 สัปดาห์

งานหลัก:

- ตั้ง schedule สำหรับอัปเดตข้อมูลอัตโนมัติ
- จัดการ API key และ environment variables อย่างปลอดภัย
- เพิ่ม authentication และ role-based access control
- เตรียม deployment environment
- ทำ backup database
- จัดทำคู่มือผู้ใช้และคู่มือผู้ดูแลระบบ

ผลลัพธ์:

- ระบบพร้อมใช้งานบน server
- อัปเดตข้อมูลอัตโนมัติตามรอบที่กำหนด
- มีคู่มือใช้งานและแผนดูแลระบบ

## 7. Expected Outcomes: ผลลัพธ์ที่คาดหวัง

- ผู้บริหารและบุคลากรสามารถดูภาพรวมและรายละเอียดผลงานวิจัยได้แบบ real-time หรืออัปเดตอัตโนมัติตามรอบเวลา
- ลดภาระงานเอกสารในการรวบรวมและตรวจสอบข้อมูลผลงานตีพิมพ์ด้วยมือ
- เพิ่มความถูกต้องและความโปร่งใสของข้อมูล KPI ด้านการวิจัย
- สามารถติดตามแนวโน้มผลงานวิจัยของสำนักวิชาได้ต่อเนื่อง
- สนับสนุนการวางแผนยุทธศาสตร์ด้านการวิจัยและการประเมินผล
- มีฐานข้อมูลกลางสำหรับต่อยอดเป็นระบบรายงานหรือ analytics ขั้นสูงในอนาคต

## 8. ความเสี่ยงและข้อควรพิจารณา (Risks & Considerations)

- การเข้าถึง Scopus API อาจมีข้อจำกัดด้านสิทธิ์ API key quota หรือเงื่อนไข license
- ข้อมูล affiliation ใน Scopus อาจไม่สม่ำเสมอ ทำให้ต้องมี rule และ manual review
- ชื่อผู้แต่งอาจซ้ำกัน หรือมีหลายรูปแบบ ทำให้ต้องมีระบบ author mapping
- Quartile และ journal metrics อาจต้องดึงจากแหล่งข้อมูลเพิ่มเติม และต้องตรวจสอบเงื่อนไขการใช้งาน
- ค่า KPI บางรายการอาจต้องมีนิยามเฉพาะของมหาวิทยาลัย
- ควรมีแผน backup และ audit trail เพราะข้อมูลอาจถูกใช้ประกอบการประเมินอย่างเป็นทางการ

## 9. ข้อมูลที่ต้องเตรียมก่อนเริ่มพัฒนา

- Scopus API key และรายละเอียดสิทธิ์การใช้งาน
- รายชื่อบุคลากรของ School of Science
- รายชื่อหน่วยงาน หลักสูตร หรือสาขาภายในสำนักวิชา
- ตัวอย่างรายงาน KPI เดิม หากมี
- นิยาม KPI ที่ใช้จริงในการประเมิน
- ช่วงปีข้อมูลที่ต้องการดึงย้อนหลัง
- รูปแบบรายงานที่ต้อง export เช่น Excel, PDF หรือ CSV
- ผู้รับผิดชอบตรวจสอบข้อมูลในระบบ

## 10. Milestone เบื้องต้น

| Milestone | รายละเอียด | ระยะเวลาโดยประมาณ |
| --- | --- | --- |
| M1 | สรุป requirement, KPI และข้อมูลอ้างอิง | สัปดาห์ที่ 1-2 |
| M2 | สร้าง prototype ดึงข้อมูลจาก Scopus API | สัปดาห์ที่ 3-5 |
| M3 | พัฒนา data cleaning และ review workflow | สัปดาห์ที่ 6-9 |
| M4 | พัฒนา dashboard และ KPI calculation | สัปดาห์ที่ 10-14 |
| M5 | ทดสอบระบบ deploy และจัดทำคู่มือ | สัปดาห์ที่ 15-18 |

## 11. Definition of Done

ระบบถือว่าพร้อมใช้งานเมื่อ:

- ดึงข้อมูลจาก Scopus API ได้ตามเงื่อนไขที่กำหนด
- คัดกรองผลงานที่เกี่ยวข้องกับ School of Science ได้อย่างตรวจสอบได้
- แสดง SDG ที่เกี่ยวข้องกับผลงานตีพิมพ์ใน Publication Records พร้อมระบุที่มาหรือวิธี mapping
- ลดข้อมูลซ้ำและจัดการข้อมูลไม่สมบูรณ์ได้
- แสดง Dashboard และ KPI สำคัญได้ถูกต้อง
- ผู้ดูแลสามารถตรวจสอบและแก้ไขข้อมูลที่ไม่มั่นใจได้
- Export รายงานได้
- มีระบบอัปเดตข้อมูลตามรอบเวลา
- มีคู่มือผู้ใช้และคู่มือผู้ดูแลระบบ
- ผ่านการทดสอบกับข้อมูลจริงอย่างน้อย 1 รอบ
