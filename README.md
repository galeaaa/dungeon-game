Nama  : Galea Violet
NIM   : 20240801104
Kelas : KH001
Mata Kuliah : Game Development

# Tugas Game Development: Enemy AI Detection, Pathfinding, and Movement in Dungeon

Proyek ini berisi jawaban tugas serta aplikasi simulasi game interaktif 2D (*Dungeon Crawler*) dalam bahasa **Python** untuk mendemonstrasikan logika kecerdasan buatan (*Enemy AI*) secara langsung.

---

## 1. Identifikasi Algoritma yang Digunakan

Untuk skenario pergerakan dan deteksi musuh di dalam dungeon, digunakan 3 algoritma utama:

1. **Finite State Machine (FSM)**  
   Digunakan untuk mengatur status perilaku musuh secara dinamis berdasarkan kondisi player di sekitar:
   - **PATROL / IDLE**: Musuh berpatroli berkeliling dungeon saat player berada di luar jangkauan (`Jarak > Detection Range`).
   - **CHASE**: Musuh mengejar player dan mencari rute terpendek saat player masuk jangkauan deteksi (`Attack Range < Jarak <= Detection Range`).
   - **ATTACK**: Musuh berhenti dan menyerang saat player masuk jangkauan serang (`Jarak <= Attack Range`).

2. **Euclidean Distance**  
   Digunakan untuk menghitung jarak fisik langsung antara lokasi musuh (x1, y1) dan lokasi player (x2, y2):
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
<Apakah Jarak <= Jangkauan Deteksi?> ────── Tidak ─────► [Set State = PATROL] ──► [SELESAI]
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

## 3. Code Snippet & Game Engine (Python)

Seluruh logika AI, algoritma A*, FSM, dan visualisasi GUI game diimplementasikan di dalam file [`main.py`](file:///d:/Documents/Semester%205/Game%20Development/Dungeon%20Game/main.py):

```python
import math
import heapq

# 1. Algoritma A* Pathfinding
def astar_pathfinding(grid, start_pos, target_pos, cols, rows):
    # Evaluasi Node dengan f(n) = g(n) + h(n)
    # Mengembalikan daftar koordinat rute terpendek
    pass

# 2. Kelas Enemy AI (Finite State Machine + Euclidean Distance)
class EnemyAI:
    def __init__(self, x, y, detection_range=8.0, attack_range=1.5):
        self.x = x
        self.y = y
        self.detection_range = detection_range
        self.attack_range = attack_range
        self.state = "PATROL"
        self.current_path = []

    def update(self, player_x, player_y, grid, cols, rows):
        # 1. Hitung Jarak Euclidean ke Player
        distance = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)

        # 2. FSM Decision Making
        if distance > self.detection_range:
            self.state = "PATROL"
            # Jalankan rute patroli otomatis
        elif distance <= self.attack_range:
            self.state = "ATTACK"
        else:
            self.state = "CHASE"
            # Cari rute A* dan gerakkan musuh 1 langkah ke Player
            self.current_path = astar_pathfinding(grid, (self.x, self.y), (player_x, player_y), cols, rows)
            if len(self.current_path) > 1:
                self.x, self.y = self.current_path[1]

        return distance
```

### 🎮 Cara Menjalankan Game
```bash
python main.py
```
