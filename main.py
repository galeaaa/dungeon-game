import tkinter as tk
import math
import heapq

# ==========================================
# 1. STRUCT & NODE UNTUK ALGORITMA A*
# ==========================================
class Node:
    def __init__(self, x, y, walkable=True):
        self.x = x
        self.y = y
        self.walkable = walkable
        self.g = float('inf')
        self.h = 0.0
        self.f = float('inf')
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f

# Algoritma A* Pathfinding (Manhattan Distance)
def find_path_astar(grid, start_pos, target_pos, cols, rows):
    # Reset node cost
    nodes = {}
    for r in range(rows):
        for c in range(cols):
            nodes[(c, r)] = Node(c, r, walkable=(grid[r][c] == 0))

    start_node = nodes.get(start_pos)
    target_node = nodes.get(target_pos)

    if not start_node or not target_node or not target_node.walkable:
        return []

    start_node.g = 0
    start_node.h = abs(start_node.x - target_node.x) + abs(start_node.y - target_node.y)
    start_node.f = start_node.g + start_node.h

    open_set = [(start_node.f, start_node)]
    closed_set = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == target_node:
            path = []
            curr = current
            while curr:
                path.append((curr.x, curr.y))
                curr = curr.parent
            return path[::-1]

        closed_set.add((current.x, current.y))

        # 4 Arah Pergerakan (Atas, Bawah, Kiri, Kanan)
        neighbors_pos = [
            (current.x + 1, current.y),
            (current.x - 1, current.y),
            (current.x, current.y + 1),
            (current.x, current.y - 1)
        ]

        for nx, ny in neighbors_pos:
            if 0 <= nx < cols and 0 <= ny < rows:
                neighbor = nodes[(nx, ny)]
                if not neighbor.walkable or (nx, ny) in closed_set:
                    continue

                tentative_g = current.g + 1
                if tentative_g < neighbor.g:
                    neighbor.parent = current
                    neighbor.g = tentative_g
                    neighbor.h = abs(neighbor.x - target_node.x) + abs(neighbor.y - target_node.y)
                    neighbor.f = neighbor.g + neighbor.h
                    heapq.heappush(open_set, (neighbor.f, neighbor))

    return []

# ==========================================
# 2. LOGIKA ENEMY AI & STATE MACHINE
# ==========================================
class EnemyAI:
    def __init__(self, x, y, detection_range=6.0, attack_range=1.5):
        self.x = x
        self.y = y
        self.detection_range = detection_range
        self.attack_range = attack_range
        self.state = "IDLE"
        self.current_path = []

    def update(self, player_x, player_y, grid, cols, rows):
        # 1. Hitung Jarak Euclidean
        distance = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)

        # 2. Evaluasi Finite State Machine (FSM)
        if distance > self.detection_range:
            self.state = "IDLE"
            self.current_path = []
        elif distance <= self.attack_range:
            self.state = "ATTACK"
            self.current_path = []
        else:
            self.state = "CHASE"
            # 3. Cari jalur A* terpendek ke Player
            self.current_path = find_path_astar(grid, (self.x, self.y), (player_x, player_y), cols, rows)
            if len(self.current_path) > 1:
                # Bergerak 1 langkah mengikuti jalur A*
                next_x, next_y = self.current_path[1]
                self.x = next_x
                self.y = next_y

        return distance

# ==========================================
# 3. GAME GUI ENGINE (TKINTER)
# ==========================================
class DungeonGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dungeon Game - Enemy AI Simulation (A* & FSM)")

        self.cols = 16
        self.rows = 12
        self.cell_size = 40

        # Map Dungeon: 0 = Jalan, 1 = Tembok/Rintangan
        self.grid = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

        # Posisi Awal Player & Enemy
        self.player_x = 1
        self.player_y = 1
        self.enemy = EnemyAI(x=14, y=9, detection_range=7.0, attack_range=1.5)

        # Panel UI Info Atas
        self.info_frame = tk.Frame(root, bg="#1e1e2e", padx=10, pady=10)
        self.info_frame.pack(fill=tk.X)

        self.lbl_status = tk.Label(
            self.info_frame, 
            text="Gunakan WASD / Arrow Keys untuk Menggerakkan Player", 
            fg="#cdd6f4", bg="#1e1e2e", font=("Consolas", 11, "bold")
        )
        self.lbl_status.pack()

        # Canvas Game
        canvas_width = self.cols * self.cell_size
        canvas_height = self.rows * self.cell_size
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="#181825", highlightthickness=0)
        self.canvas.pack()

        # Bind Kontrol Keyboard
        self.root.bind("<Key>", self.handle_keypress)

        # Draw Awal
        self.draw_game()

    def handle_keypress(self, event):
        key = event.keysym.lower()
        new_x, new_y = self.player_x, self.player_y

        if key in ['w', 'up']:
            new_y -= 1
        elif key in ['s', 'down']:
            new_y += 1
        elif key in ['a', 'left']:
            new_x -= 1
        elif key in ['d', 'right']:
            new_x += 1

        # Cek tabrakan dengan tembok
        if 0 <= new_x < self.cols and 0 <= new_y < self.rows:
            if self.grid[new_y][new_x] == 0:
                self.player_x = new_x
                self.player_y = new_y
                
                # Update Enemy AI setelah Player bergerak
                distance = self.enemy.update(self.player_x, self.player_y, self.grid, self.cols, self.rows)
                self.draw_game()

    def draw_game(self):
        self.canvas.delete("all")

        # 1. Gambar Grid & Tembok Dungeon
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if self.grid[r][c] == 1:
                    # Tembok / Obstacle
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#313244", outline="#45475a", width=1)
                else:
                    # Jalan
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#1e1e2e", outline="#181825", width=1)

        # 2. Gambar Jalur A* (jika sedang CHASE)
        if self.enemy.state == "CHASE" and len(self.enemy.current_path) > 1:
            for px, py in self.enemy.current_path[1:-1]:
                cx = px * self.cell_size + self.cell_size // 2
                cy = py * self.cell_size + self.cell_size // 2
                self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill="#f9e2af", outline="")

        # 3. Gambar Player (Hijau)
        px1 = self.player_x * self.cell_size + 6
        py1 = self.player_y * self.cell_size + 6
        px2 = (self.player_x + 1) * self.cell_size - 6
        py2 = (self.player_y + 1) * self.cell_size - 6
        self.canvas.create_oval(px1, py1, px2, py2, fill="#a6e3a1", outline="#94e2d5", width=2)
        self.canvas.create_text(
            self.player_x * self.cell_size + self.cell_size//2, 
            self.player_y * self.cell_size + self.cell_size//2, 
            text="P", fill="#11111b", font=("Consolas", 12, "bold")
        )

        # 4. Gambar Enemy (Warna sesuai FSM State)
        state_colors = {
            "IDLE": "#89b4fa",    # Biru
            "CHASE": "#fab387",   # Oranye
            "ATTACK": "#f38ba8"   # Merah
        }
        enemy_color = state_colors.get(self.enemy.state, "#f38ba8")

        ex1 = self.enemy.x * self.cell_size + 6
        ey1 = self.enemy.y * self.cell_size + 6
        ex2 = (self.enemy.x + 1) * self.cell_size - 6
        ey2 = (self.enemy.y + 1) * self.cell_size - 6
        self.canvas.create_oval(ex1, ey1, ex2, ey2, fill=enemy_color, outline="#f5e0dc", width=2)
        self.canvas.create_text(
            self.enemy.x * self.cell_size + self.cell_size//2, 
            self.enemy.y * self.cell_size + self.cell_size//2, 
            text="E", fill="#11111b", font=("Consolas", 12, "bold")
        )

        # 5. Hitung Jarak Euclidean & Update UI Header
        dist = math.sqrt((self.enemy.x - self.player_x)**2 + (self.enemy.y - self.player_y)**2)
        info_text = f"PLAYER: ({self.player_x}, {self.player_y})   |   ENEMY: ({self.enemy.x}, {self.enemy.y})   |   JARAK: {dist:.2f}   |   AI STATE: {self.enemy.state}"
        self.lbl_status.config(text=info_text, fg=enemy_color)

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = DungeonGameGUI(root)
    root.mainloop()
