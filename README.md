Nama  : Galea Violet
NIM   : 20240801104
Kelas : KH001
Mata Kuliah : Game Development

# Tugas Game Development: Enemy AI Detection, Pathfinding, and Movement in Dungeon

Deskripsi Singkat:
Player bergerak di dalam sebuah dungeon. Enemy harus mendeteksi player, menentukan apakah player berada dalam jangkauan, mencari jalur menuju player, kemudian bergerak menuju player.

---

## 1. Identifikasi Algoritma yang Digunakan

Untuk skenario pergerakan dan deteksi musuh di dalam dungeon, digunakan kombinasi algoritma berikut:

1. **Finite State Machine (FSM)**  
   Digunakan untuk mengatur status perilaku musuh secara dinamis berdasarkan kondisi player di sekitar:
   - **IDLE / PATROL**: Musuh diam/patroli saat player belum terdeteksi.
   - **CHASE**: Musuh bergerak mengejar player saat player masuk ke dalam jangkauan deteksi (*Detection Range*).
   - **ATTACK**: Musuh berhenti dan menyerang saat player berada dalam jangkauan serang (*Attack Range*).

2. **Euclidean Distance**  
   Digunakan untuk mengukur jarak fisik langsung antara musuh dan player:
   `Jarak (d) = sqrt((x2 - x1)^2 + (y2 - y1)^2)`  
   - Jika `d <= Jangkauan Deteksi` ➔ Masuk status **CHASE**.
   - Jika `d <= Jangkauan Serang` ➔ Masuk status **ATTACK**.

3. **A* (A-Star) Pathfinding**  
   Algoritma untuk mencari rute/jalur terpendek dari musuh menuju player di dalam dungeon yang memiliki rintangan (dinding). Algoritma ini mengevaluasi fungsi biaya `f(n) = g(n) + h(n)` menggunakan jarak heuristik Manhattan `h(n) = |x_target - x_n| + |y_target - y_n|`.

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

## 3. Code Snippet (C#)

Berikut adalah potongan kode C# yang menangani pergerakan, deteksi jangkauan, dan FSM pada musuh:

```csharp
using System;
using System.Collections.Generic;

namespace DungeonGame
{
    public enum EnemyState { Idle, Chase, Attack }

    public class EnemyAI
    {
        public int x, y;
        public float detectionRange = 7.0f;
        public float attackRange = 1.5f;
        public EnemyState currentState = EnemyState.Idle;

        // 1. Hitung Jarak Euclidean ke Player
        public float CalculateDistance(int targetX, int targetY)
        {
            int dx = targetX - this.x;
            int dy = targetY - this.y;
            return (float)Math.Sqrt(dx * dx + dy * dy);
        }

        // 2. Update Logika & FSM Musuh
        public void UpdateAI(int playerX, int playerY, Node[,] gridMap, int mapWidth, int mapHeight)
        {
            float distance = CalculateDistance(playerX, playerY);

            // Deteksi Jangkauan & Penentuan State
            if (distance > detectionRange)
            {
                currentState = EnemyState.Idle;
            }
            else if (distance <= attackRange)
            {
                currentState = EnemyState.Attack;
            }
            else
            {
                currentState = EnemyState.Chase;

                // 3. Cari Jalur Terpendek Menggunakan A* Pathfinding
                List<Node> path = FindPathAStar(x, y, playerX, playerY, gridMap, mapWidth, mapHeight);

                // Bergerak 1 langkah menuju player jika jalur ditemukan
                if (path != null && path.Count > 1)
                {
                    this.x = path[1].x;
                    this.y = path[1].y;
                }
            }
        }
    }
}
```
