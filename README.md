# SciDash Research KPI Dashboard

เว็บ Dashboard สำหรับติดตามผลงานตีพิมพ์และ KPI ด้านการวิจัยของ School of Science, Mae Fah Luang University

ตอนนี้เป็น browser dashboard ที่มีข้อมูลตัวอย่าง และมี backend proxy สำหรับต่อ Scopus API โดยไม่เปิดเผย API key ในฝั่ง browser

## Run Locally

ตั้งค่า Scopus API key ในไฟล์ `.env`:

```bash
cp .env.example .env
```

จากนั้นแก้ค่า `SCOPUS_API_KEY` ใน `.env`

แนะนำให้ใช้สคริปต์ที่เตรียมไว้:

```bash
python3 scripts/start_server.py
```

ถ้าต้องการหยุด server:

```bash
python3 scripts/stop_server.py
```

หรือรันเองด้วย Python:

```bash
python3 -m http.server 4173 --bind 0.0.0.0
```

จากนั้นเปิด:

```text
http://localhost:4173
```

ถ้าต้องการให้คนอื่นในเครือข่ายเดียวกันเข้าใช้งาน ให้ใช้ IP ของเครื่องนี้แทน `localhost` เช่น:

```text
http://YOUR_LOCAL_IP:4173
```

## Features

- KPI cards: Publications, Citations, Q1/Q2 Ratio, School h-index
- Filter ตามปี ผู้แต่ง Quartile และคำค้นหา
- Sync ข้อมูลจาก Scopus API ผ่าน backend endpoint `/api/scopus/search`
- Auto sync เมื่อเปิดหน้าเว็บ ถ้า backend มี `SCOPUS_API_KEY`
- ถ้า API ใช้งานไม่ได้ ระบบจะแสดงไม่มีข้อมูล แทนการใช้ mock data
- กรองผล Scopus เฉพาะรายชื่ออาจารย์/ผู้บริหารวิชาการจากหน้า Executive Staff ของ School of Science
- Publication trend chart
- Journal quartile chart
- Ranking ผู้แต่งตามจำนวนผลงาน
- ตารางผลงานตีพิมพ์
- Review queue สำหรับรายการที่ต้องตรวจสอบ affiliation หรือ author mapping
- Export CSV ตามข้อมูลที่กรองอยู่

## Next Steps

- เพิ่มฐานข้อมูล PostgreSQL
- เพิ่มระบบ login และ role-based access
- เพิ่ม workflow สำหรับ verify, exclude และแก้ไข publication records
- เพิ่ม scheduler สำหรับอัปเดตข้อมูลอัตโนมัติ
