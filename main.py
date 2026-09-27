import math
import heapq

# ==========================================
# 1. NODE UNTUK GRID DUNGEON
# ==========================================
class Node:
    def __init__(self, x, y, walkable=True):
        self.x = x
        self.y = y
        self.walkable = walkable
        self.g = 0
        self.h = 0
        self.f = 0
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f

# ==========================================
# 2. ALGORITMA A* PATHFINDING (PENCARI JALUR TERPENDEK)
# ==========================================
def astar_pathfinding(grid, start, target, cols, rows):
    nodes = {}
    for r in range(rows):
        for c in range(cols):
            nodes[(c, r)] = Node(c, r, walkable=(grid[r][c] == 0))

    start_node = nodes[start]
    target_node = nodes[target]

    open_set = []
    heapq.heappush(open_set, start_node)
    closed_set = set()

    while open_set:
        current = heapq.heappop(open_set)

        if (current.x, current.y) == (target_node.x, target_node.y):
            path = []
            curr = current
            while curr:
                path.append((curr.x, curr.y))
                curr = curr.parent
            return path[::-1]

        closed_set.add((current.x, current.y))

        # Check 4 Tetangga (Atas, Bawah, Kiri, Kanan)
        neighbors = [(current.x+1, current.y), (current.x-1, current.y), (current.x, current.y+1), (current.x, current.y-1)]
        for nx, ny in neighbors:
            if 0 <= nx < cols and 0 <= ny < rows:
                neighbor = nodes[(nx, ny)]
                if not neighbor.walkable or (nx, ny) in closed_set:
                    continue

                tentative_g = current.g + 1
                if neighbor not in open_set or tentative_g < neighbor.g:
                    neighbor.parent = current
                    neighbor.g = tentative_g
                    neighbor.h = abs(neighbor.x - target_node.x) + abs(neighbor.y - target_node.y)
                    neighbor.f = neighbor.g + neighbor.h
                    if neighbor not in open_set:
                        heapq.heappush(open_set, neighbor)

    return []

# ==========================================
# 3. ENEMY AI (FSM + EUCLIDEAN DETEKTOR + MOVEMENT)
# ==========================================
class EnemyAI:
    def __init__(self, x, y, detection_range=10.0, attack_range=1.5):
        self.x = x
        self.y = y
        self.detection_range = detection_range
        self.attack_range = attack_range
        self.state = "IDLE"

    def update(self, player_x, player_y, grid, cols, rows):
        # 1. Hitung Jarak Euclidean ke Player
        distance = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)

        # 2. Penentuan State (FSM) berdasarkan Jangkauan
        if distance > self.detection_range:
            self.state = "IDLE"
        elif distance <= self.attack_range:
            self.state = "ATTACK"
        else:
            self.state = "CHASE"
            # 3. Cari Jalur Terpendek Menggunakan A* Pathfinding
            path = astar_pathfinding(grid, (self.x, self.y), (player_x, player_y), cols, rows)
            if len(path) > 1:
                self.x, self.y = path[1]

        return distance, self.state

# ==========================================
# DEMO SIMULASI JALAN AI (MAIN EXECUTION)
# ==========================================
if __name__ == "__main__":
    cols, rows = 10, 10
    # Map Dungeon Grid (0 = Jalan, 1 = Tembok)
    dungeon_grid = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    player_pos = (1, 1)
    enemy = EnemyAI(x=8, y=8, detection_range=12.0, attack_range=1.5)

    print("=== SIMULASI PERGERAKAN ENEMY AI ===")
    print(f"Posisi Player     : {player_pos}")
    print(f"Posisi Awal Musuh : ({enemy.x}, {enemy.y})\n")

    step = 1
    while step <= 20:
        dist, state = enemy.update(player_pos[0], player_pos[1], dungeon_grid, cols, rows)
        print(f"Langkah {step:02d} | Posisi Musuh: ({enemy.x}, {enemy.y}) | Jarak: {dist:.2f} | State: {state}")

        if state == "ATTACK":
            print("\n[SELESAI] Musuh berhasil menjangkau dan menyerang Player!")
            break

        step += 1
