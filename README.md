# Portal Kampus P06 - Latihan Keamanan AI/LLM

Portal ini dibangun untuk simulasi risiko keamanan pada modul AI (Asisten Kampus).

## Struktur Proyek
- `rentan/`: Versi dengan kontrol keamanan minimal.
- `aman/`: Versi dengan kontrol keamanan berlapis (LLM Guardrails).
- `src/`: Template sumber.
- `build.py`: Skrip untuk menghasilkan kedua versi.

## Mitigasi Risiko (Versi AMAN)
1. **Prompt Injection**: Menggunakan pemisahan peran instruksi sistem dan konten pengguna.
2. **Sensitive Data Disclosure**: Filter output untuk mencegah pembocoran alamat, nomor telepon, dan data sensitif lainnya.
3. **Insecure Output Handling**: Output model di-escape (tidak memakai `innerHTML`) untuk mencegah XSS.
4. **Excessive Agency**: Setiap aksi kritis (mengubah nilai, menghapus akun) memerlukan persetujuan manusia (`menunggu_persetujuan`).
5. **Human Oversight**: Antrean persetujuan untuk aksi model dan pencatatan log audit.

## Data Sintetis
Semua data (nama, NPM, telepon, alamat) adalah rekaan dan tidak berhubungan dengan data nyata.
