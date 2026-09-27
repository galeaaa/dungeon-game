Nama  : Galea Violet
NIM   : 20240801104
Kelas : KH001
Mata Kuliah : Game Development

# Tugas Game Development: Enemy AI Detection, Pathfinding, and Movement in Dungeon

Proyek ini berisi jawaban tugas serta simulasi game interaktif 2D (*Dungeon Crawler*) untuk mendemonstrasikan logika kecerdasan buatan (*Enemy AI*) secara langsung.

---

## 1. Identifikasi Algoritma yang Digunakan

Untuk skenario pergerakan dan deteksi musuh di dalam dungeon, digunakan 3 algoritma utama:

1. **Finite State Machine (FSM)**  
   Digunakan untuk mengatur status perilaku musuh secara dinamis berdasarkan kondisi player di sekitar:
   - **IDLE / PATROL**: Musuh diam/patroli saat player belum terdeteksi (`Jarak > Detection Range`).
   - **CHASE**: Musuh mengejar player dan mencari rute terpendek saat player masuk jangkauan deteksi (`Attack Range < Jarak <= Detection Range`).
   - **ATTACK**: Musuh berhenti dan menyerang saat player masuk jangkauan serang (`Jarak <= Attack Range`).

2. **Euclidean Distance**  
   Digunakan untuk menghitung jarak fisik langsung antara lokasi musuh $(x_1, y_1)$ dan lokasi player $(x_2, y_2)$:
   `Jarak (d) = sqrt((x2 - x1)^2 + (y2 - y1)^2)`

3. **A* (A-Star) Pathfinding**  
   Algoritma untuk mencari rute/jalur terpendek dari musuh menuju player mengitari tembok/rintangan dungeon. Evaluasi fungsi biaya menggunakan `f(n) = g(n) + h(n)` dengan heuristik Manhattan `h(n) = |x_target - x_n| + |y_target - y_n|`.

---

## 2. Flowchart Algoritma Enemy AI

```text
[MULAI LOOP UPDATE AI ENEMY]
         │
         ▼
[Hitung Jarak Euclidean ke Player]
         │
         ▼
<Apakah Jarak <= Jangkauan Deteksi?> ────── Tidak ─────► [Set State = IDLE] ──► [SELESAI]
         │
        Ya
         │
         ▼
<Apakah Jarak <= Jangkauan Serang?> ─────── Ya ───────► [Set State = ATTACK] ─► [SELESAI]
         │
       Tidak
         │
         ▼
[Set State = CHASE]
         │
         ▼
[Hitung Rute Terpendek Menggunakan A* Pathfinding]
         │
         ▼
<Apakah Jalur Ditemukan?> ────── Tidak ─────► [Musuh Diam / Standby] ──► [SELESAI]
         │
        Ya
         │
         ▼
[Update Posisi Musuh 1 Langkah ke Node Berikutnya]
         │
         ▼
     [SELESAI]
```

---

## 3. Cara Menjalankan Game Simulasi Interaktif

Game simulasi ini dapat dijalankan langsung di komputer Anda dengan perintah:

```bash
python main.py
```

### 🎮 Kontrol & Fitur Game:
- **Tekan Tombol `W`, `A`, `S`, `D` atau `Arrow Keys`**: Menggerakkan Player (`P`, Lingkaran Hijau) mengelilingi labirin dungeon.
- **Musuh (`E`, Lingkaran Berwarna)**:
  - Berwarna **Biru (IDLE)** saat Player jauh.
  - Berwarna **Oranye (CHASE)** saat mendeteksi Player dan mengejar mengitari tembok menggunakan algoritma A* (jejak rute titik-titik kuning akan muncul di layar).
  - Berwarna **Merah (ATTACK)** saat sudah mencapai jangkauan serang ke Player.
- **HUD Atas**: Menampilkan koordinat Player, koordinat Musuh, Jarak Euclidean realtime, dan State AI yang aktif saat ini.
