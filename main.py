import tkinter as tk
import math
import heapq

# ==========================================
# 1. ALGORITMA A* PATHFINDING & NODE
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

def astar_pathfinding(grid, start_pos, target_pos, cols, rows):
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

        neighbors = [
            (current.x + 1, current.y),
            (current.x - 1, current.y),
            (current.x, current.y + 1),
            (current.x, current.y - 1)
        ]

        for nx, ny in neighbors:
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
# 2. LOGIKA ENEMY AI & FINITE STATE MACHINE
# ==========================================
class EnemyAI:
    def __init__(self, x, y, detection_range=6.5, attack_range=1.5):
        self.x = x
        self.y = y
        self.detection_range = detection_range
        self.attack_range = attack_range
        self.state = "IDLE"
        self.current_path = []

    def update(self, player_x, player_y, grid, cols, rows):
        # Hitung Jarak Euclidean
        distance = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)

        # FSM Decision Tree
        if distance > self.detection_range:
            self.state = "IDLE"
            self.current_path = []
        elif distance <= self.attack_range:
            self.state = "ATTACK"
            self.current_path = []
        else:
            self.state = "CHASE"
            # Pathfinding A* ke posisi player
            self.current_path = astar_pathfinding(grid, (self.x, self.y), (player_x, player_y), cols, rows)
            if len(self.current_path) > 1:
                # Bergerak 1 node di sepanjang jalur
                next_x, next_y = self.current_path[1]
                self.x = next_x
                self.y = next_y

        return distance

# ==========================================
# 3. GAME ENGINE & INTERFACE (TKINTER)
# ==========================================
class DungeonGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dungeon Game - Real-time Enemy AI Simulation")
        self.root.configure(bg="#0f0f17")

        self.cols = 16
        self.rows = 12
        self.cell_size = 45

        # Peta Dungeon: 0 = Lantai, 1 = Tembok Batu
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

        # Inisialisasi Posisi Awal
        self.player_x = 1
        self.player_y = 1
        self.enemy = EnemyAI(x=14, y=9, detection_range=6.5, attack_range=1.5)

        self.is_paused = False
        self.move_counter = 0

        # UI Header Panel
        self.header_frame = tk.Frame(root, bg="#161622", padx=15, pady=10)
        self.header_frame.pack(fill=tk.X)

        self.lbl_title = tk.Label(
            self.header_frame, 
            text="⚔️ DUNGEON CRAWLER - ENEMY AI REALTIME", 
            fg="#7aa2f7", bg="#161622", font=("Helvetica", 12, "bold")
        )
        self.lbl_title.pack(anchor="w")

        self.lbl_status = tk.Label(
            self.header_frame, 
            text="Gunakan WASD / Arrow Keys untuk bergerak | SPACE: Pause/Play | R: Reset", 
            fg="#a9b1d6", bg="#161622", font=("Consolas", 10)
        )
        self.lbl_status.pack(anchor="w", pady=(2, 0))

        # Canvas Game Rendering
        canvas_w = self.cols * self.cell_size
        canvas_h = self.rows * self.cell_size
        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="#0f0f17", highlightthickness=0)
        self.canvas.pack(padx=15, pady=15)

        # Key Bindings
        self.pressed_keys = set()
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)

        # Game Loop Timer otomatis (Real-time update)
        self.update_game_loop()

    def on_key_press(self, event):
        key = event.keysym.lower()
        if key == "space":
            self.is_paused = not self.is_paused
        elif key == "r":
            self.reset_game()
        else:
            self.pressed_keys.add(key)

    def on_key_release(self, event):
        key = event.keysym.lower()
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def reset_game(self):
        self.player_x = 1
        self.player_y = 1
        self.enemy.x = 14
        self.enemy.y = 9
        self.enemy.state = "IDLE"

    def process_player_input(self):
        new_x, new_y = self.player_x, self.player_y

        if "w" in self.pressed_keys or "up" in self.pressed_keys:
            new_y -= 1
        elif "s" in self.pressed_keys or "down" in self.pressed_keys:
            new_y += 1
        elif "a" in self.pressed_keys or "left" in self.pressed_keys:
            new_x -= 1
        elif "d" in self.pressed_keys or "right" in self.pressed_keys:
            new_x += 1

        # Cek collision tembok
        if 0 <= new_x < self.cols and 0 <= new_y < self.rows:
            if self.grid[new_y][new_x] == 0:
                self.player_x = new_x
                self.player_y = new_y

    def update_game_loop(self):
        if not self.is_paused:
            # 1. Gerakkan Player dari Keyboard Input
            self.process_player_input()

            # 2. Gerakkan Enemy AI Setiap Beberapa Tick (Realtime Movement)
            self.move_counter += 1
            if self.move_counter % 2 == 0:  # Kecepatan gerak musuh
                self.enemy.update(self.player_x, self.player_y, self.grid, self.cols, self.rows)

            # 3. Render Visual Tampilan Game
            self.render()

        # Ulangi loop secara otomatis setiap 120ms (Realtime Loop)
        self.root.after(120, self.update_game_loop)

    def render(self):
        self.canvas.delete("all")

        # --- A. GAMBAR GRID & TEMBOK DUNGEON (Retro Tile Style) ---
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if self.grid[r][c] == 1:
                    # Tembok Batu 3D Bevel Effect
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#24283b", outline="#1f2335", width=2)
                    self.canvas.create_rectangle(x1+3, y1+3, x2-3, y2-3, fill="#3b4261", outline="")
                else:
                    # Lantai Dungeon dengan Grid Pattern
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#1a1b26", outline="#24283b", width=1)

        # --- B. GAMBAR JANGKAUAN DETEKSI RADAR (Subtle Radius Circle) ---
        ex_px = self.enemy.x * self.cell_size + self.cell_size // 2
        ey_px = self.enemy.y * self.cell_size + self.cell_size // 2
        rad_px = self.enemy.detection_range * self.cell_size

        self.canvas.create_oval(
            ex_px - rad_px, ey_px - rad_px, ex_px + rad_px, ey_px + rad_px, 
            outline="#7aa2f7" if self.enemy.state == "IDLE" else "#ff9e64", 
            dash=(3, 5), width=1
        )

        # --- C. GAMBAR JALUR TERPENDEK A* (Pathing Dots & Line) ---
        if self.enemy.state == "CHASE" and len(self.enemy.current_path) > 1:
            coords = []
            for px, py in self.enemy.current_path:
                cx = px * self.cell_size + self.cell_size // 2
                cy = py * self.cell_size + self.cell_size // 2
                coords.extend([cx, cy])
                # Dot jalur A*
                self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill="#e0af68", outline="")

            if len(coords) >= 4:
                self.canvas.create_line(coords, fill="#e0af68", width=2, dash=(4, 2))

        # --- D. GAMBAR PLAYER (Knight Badge - Emerald Green) ---
        px1 = self.player_x * self.cell_size + 6
        py1 = self.player_y * self.cell_size + 6
        px2 = (self.player_x + 1) * self.cell_size - 6
        py2 = (self.player_y + 1) * self.cell_size - 6

        # Outer Glow
        self.canvas.create_oval(px1-2, py1-2, px2+2, py2+2, outline="#9ece6a", width=2)
        # Body
        self.canvas.create_oval(px1, py1, px2, py2, fill="#73daca", outline="#9ece6a", width=2)
        # Icon Text
        self.canvas.create_text(
            self.player_x * self.cell_size + self.cell_size//2, 
            self.player_y * self.cell_size + self.cell_size//2, 
            text="🛡️ P", fill="#15161e", font=("Segoe UI Emoji", 11, "bold")
        )

        # --- E. GAMBAR ENEMY (Monster Badge - Dynamic FSM Color) ---
        colors = {
            "IDLE": ("#2ac3de", "#7dcfff"),    # Blue/Cyan
            "CHASE": ("#ff9e64", "#e0af68"),   # Orange/Gold
            "ATTACK": ("#f7768e", "#db4b4b")   # Red Crimson
        }
        fill_color, border_color = colors.get(self.enemy.state, ("#f7768e", "#db4b4b"))

        ex1 = self.enemy.x * self.cell_size + 6
        ey1 = self.enemy.y * self.cell_size + 6
        ex2 = (self.enemy.x + 1) * self.cell_size - 6
        ey2 = (self.enemy.y + 1) * self.cell_size - 6

        # Glowing Aura Ring
        self.canvas.create_oval(ex1-3, ey1-3, ex2+3, ey2+3, outline=border_color, width=2)
        # Main Body
        self.canvas.create_oval(ex1, ey1, ex2, ey2, fill=fill_color, outline=border_color, width=2)

        # Icon Monster
        icon = "😴 E" if self.enemy.state == "IDLE" else ("👾 E" if self.enemy.state == "CHASE" else "⚔️ E")
        self.canvas.create_text(
            self.enemy.x * self.cell_size + self.cell_size//2, 
            self.enemy.y * self.cell_size + self.cell_size//2, 
            text=icon, fill="#15161e", font=("Segoe UI Emoji", 11, "bold")
        )

        # Efek Serangan Flash jika ATTACK
        if self.enemy.state == "ATTACK":
            self.canvas.create_rectangle(0, 0, self.cols*self.cell_size, self.rows*self.cell_size, fill="#f7768e", stipple="gray25")

        # --- F. UPDATE HUD STATUS HEADER ---
        dist = math.sqrt((self.enemy.x - self.player_x)**2 + (self.enemy.y - self.player_y)**2)
        pause_str = " [PAUSED]" if self.is_paused else ""
        info_text = f"PLAYER: ({self.player_x}, {self.player_y}) | ENEMY: ({self.enemy.x}, {self.enemy.y}) | JARAK: {dist:.2f} | AI STATE: {self.enemy.state}{pause_str}"
        self.lbl_status.config(text=info_text, fg=fill_color)

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = DungeonGameGUI(root)
    root.mainloop()
