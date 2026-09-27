Nama  : Galea Violet
NIM   : 20240801104
Kelas : KH 001

# Tugas Game Development: Enemy AI Detection, Pathfinding, and Movement in Dungeon

Soal:
Player bergerak di dalam sebuah dungeon. Enemy harus mendeteksi player, menentukan apakah player berada dalam jangkauan, mencari jalur menuju player, kemudian bergerak menuju player.

1. Identifikasi Algoritma yang digunakan?
2. Buatlah flow chart untuk algoritma tersebut?
3. Buat code snippet untuk algoritma tersebut dengan bahasa pemrograman yang anda bisa?

---

## 1. Identifikasi Algoritma yang Digunakan

Untuk skenario pergerakan dan deteksi musuh di dalam dungeon, digunakan kombinasi 3 algoritma utama:

1. **Finite State Machine (FSM)**  
   Digunakan untuk mengelola status perilaku musuh secara dinamis berdasarkan posisi player:
   - **IDLE**: Musuh diam saat player berada di luar jangkauan deteksi.
   - **CHASE**: Musuh bergerak mengejar player saat player masuk dalam jangkauan deteksi (*Detection Range*).
   - **ATTACK**: Musuh berhenti dan melakukan serangan saat player berada dalam jangkauan serang (*Attack Range*).

2. **Euclidean Distance**  
   Digunakan untuk mengukur jarak fisik langsung antara musuh $(x_1, y_1)$ dan player $(x_2, y_2)$:
   $$\text{Jarak } (d) = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$$
   - Jika $d \le \text{Detection Range}$ ➔ Berubah ke state **CHASE**.
   - Jika $d \le \text{Attack Range}$ ➔ Berubah ke state **ATTACK**.

3. **A* (A-Star) Pathfinding**  
   Algoritma untuk mencari rute/jalur terpendek dari musuh menuju player mengitari rintangan/tembok dungeon. Algoritma ini mengevaluasi fungsi biaya $f(n) = g(n) + h(n)$ dengan menggunakan heuristik Manhattan Distance $h(n) = |x_{\text{target}} - x_n| + |y_{\text{target}} - y_n|$.

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

## 3. Code Snippet (Python)

Berikut adalah implementasi kode Python sederhana yang menangani deteksi jarak, FSM, dan pergerakan A* Pathfinding:

```python
import math
import heapq

# 1. Algoritma A* Pathfinding
def astar_pathfinding(grid, start, target, cols, rows):
    # Mengembalikan jalur terpendek berupa list posisi (x, y) dari start ke target
    pass

# 2. Kelas Enemy AI (FSM + Euclidean Distance + Movement)
class EnemyAI:
    def __init__(self, x, y, detection_range=8.0, attack_range=1.5):
        self.x = x
        self.y = y
        self.detection_range = detection_range
        self.attack_range = attack_range
        self.state = "IDLE"

    def update(self, player_x, player_y, grid, cols, rows):
        # 1. Hitung Jarak Euclidean ke Player
        distance = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)

        # 2. Evaluasi State Machine (FSM)
        if distance > self.detection_range:
            self.state = "IDLE"
        elif distance <= self.attack_range:
            self.state = "ATTACK"
        else:
            self.state = "CHASE"
            # 3. Cari rute terpendek pakai A* dan gerakkan musuh 1 langkah
            path = astar_pathfinding(grid, (self.x, self.y), (player_x, player_y), cols, rows)
            if len(path) > 1:
                self.x, self.y = path[1]

        return self.state
```

Untuk melihat simulasi pergerakan algoritma ini langkah demi langkah, jalankan file `main.py`:
```bash
python main.py
```
