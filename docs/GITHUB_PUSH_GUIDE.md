# วิธี Push โค้ด SciDash ขึ้น GitHub

สรุปขั้นตอนสำหรับ push โค้ดจากเครื่องขึ้น repository บน GitHub (ใช้ครั้งแรก และใช้ทบทวนได้ในอนาคต)

## 1. สร้าง Repository บน GitHub (ทำครั้งเดียว)

1. ไปที่ https://github.com/new
2. ตั้งชื่อ repo เช่น `SciDash`
3. เลือก **Public** (ถ้าต้องการใช้ GitHub Pages แบบฟรี ต้องเป็น Public)
4. **ห้ามติ๊ก** "Add a README file" เพราะมีโค้ดอยู่แล้วในเครื่อง
5. กด **Create repository** แล้วเก็บ URL ไว้ เช่น `https://github.com/<username>/SciDash.git`

## 2. สร้าง Personal Access Token (PAT)

GitHub ไม่รับรหัสผ่านบัญชีจริงสำหรับ push อีกต่อไป ต้องสร้าง token แทน:

1. ไปที่ https://github.com/settings/tokens
2. กด **Generate new token** → **Generate new token (classic)**
3. Note: ตั้งชื่ออะไรก็ได้ เช่น `SciDash push`
4. Expiration: เลือก 90 days หรือ No expiration
5. Scopes: ติ๊ก **repo**
6. กด **Generate token** แล้ว **copy เก็บไว้ทันที** (โชว์ครั้งเดียว ปิดหน้าไปแล้วดูซ้ำไม่ได้)

⚠️ **ห้ามวาง token ไว้ในไฟล์ที่ commit ขึ้น GitHub หรือแชร์ในที่สาธารณะ** — ถ้า token หลุดไปที่ไหนโดยไม่ตั้งใจ (เช่น พิมพ์ผิดที่ หรือแชร์หน้าจอ) ให้ไปลบ/สร้างใหม่ทันทีที่ https://github.com/settings/tokens

## 3. ตั้งค่า git ให้จำ token ให้ (ทำครั้งเดียว)

เปิด Terminal แล้วรัน:

```bash
git config --global credential.helper osxkeychain
```

คำสั่งนี้บอกให้ macOS เก็บ token ไว้ใน Keychain อย่างปลอดภัย ไม่ต้องพิมพ์ซ้ำทุกครั้งที่ push

จากนั้นบันทึก token ลง Keychain (แทน `<token>` ด้วยค่าที่ copy มาจากขั้นตอนที่ 2, แทน `<username>` ด้วย GitHub username ของคุณ):

```bash
printf 'protocol=https\nhost=github.com\nusername=<username>\npassword=<token>\n' | git credential-osxkeychain store
```

## 4. Push โค้ดขึ้น GitHub

ในโฟลเดอร์โปรเจกต์ (`/Users/kitiphongkhongphinitbunjong/Documents/SciDash`):

```bash
git add .
git commit -m "ข้อความอธิบายว่าแก้อะไรไป"
git remote add origin https://github.com/<username>/SciDash.git   # ทำครั้งแรกครั้งเดียว
git push -u origin main
```

ถ้าเคยรัน `git remote add origin ...` ไปแล้ว ครั้งต่อไป push แค่:

```bash
git add .
git commit -m "ข้อความอธิบายว่าแก้อะไรไป"
git push
```

เพราะตั้งค่า credential helper ไว้แล้ว จะไม่ถูกถามรหัสผ่าน/token อีก

## 5. ตรวจสอบว่า push สำเร็จ

```bash
git ls-remote origin
git rev-parse HEAD
```

ถ้า commit hash สองอันตรงกัน แปลว่า push สำเร็จ ข้อมูลบน GitHub ตรงกับในเครื่องแล้ว

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ/วิธีแก้ |
|---|---|
| `fatal: could not read Username for 'https://github.com': Device not configured` | รันจาก environment ที่ไม่มีหน้าต่างให้ล็อกอิน (ไม่มี TTY) — ให้รันจาก Terminal.app ปกติ หรือทำตามขั้นตอนที่ 3 เพื่อฝัง credential ไว้ล่วงหน้า |
| ใส่รหัสผ่าน GitHub จริงแล้วขึ้น error | GitHub ไม่รับรหัสผ่านบัญชีแล้ว ต้องใช้ Personal Access Token (ขั้นตอนที่ 2) แทนตอนถูกถาม password |
| `Support for password authentication was removed` | เหมือนข้อบน ต้องใช้ token ไม่ใช่รหัสผ่าน |
| token หมดอายุ | สร้าง token ใหม่ตามขั้นตอนที่ 2 แล้วรันขั้นตอนที่ 3 ใหม่ด้วย token ใหม่ |

## ขั้นตอนถัดไปหลัง push สำเร็จ

- เปิด GitHub Pages: repo → Settings → Pages → Source: Deploy from a branch → main / (root)
- ใส่ Secret `SCOPUS_API_KEY`: repo → Settings → Secrets and variables → Actions → New repository secret
