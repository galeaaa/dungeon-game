import tkinter as tk
from tkinter import ttk
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
    def __init__(self, x, y, detection_range=8.0, attack_range=1.5):
        self.x = x
        self.y = y
        self.detection_range = detection_range
        self.attack_range = attack_range
        self.state = "PATROL"
        self.current_path = []
        
        # Posisi Rute Patroli saat Player belum terdeteksi
        self.patrol_waypoints = [(14, 9), (14, 3), (9, 3), (9, 9)]
        self.patrol_index = 0

    def update(self, player_x, player_y, grid, cols, rows):
        # 1. Hitung Jarak Euclidean ke Player
        distance = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)

        # 2. Evaluasi State Machine (FSM)
        if distance > self.detection_range:
            # STATE: PATROL (Musuh terus berjalan patroli di area dungeon)
            self.state = "PATROL"
            target_waypoint = self.patrol_waypoints[self.patrol_index]
            
            if (self.x, self.y) == target_waypoint:
                # Lanjut ke titik patroli berikutnya
                self.patrol_index = (self.patrol_index + 1) % len(self.patrol_waypoints)
                target_waypoint = self.patrol_waypoints[self.patrol_index]

            self.current_path = astar_pathfinding(grid, (self.x, self.y), target_waypoint, cols, rows)
            if len(self.current_path) > 1:
                self.x, self.y = self.current_path[1]

        elif distance <= self.attack_range:
            # STATE: ATTACK (Musuh sudah menempel dan melakukan serangan)
            self.state = "ATTACK"
            self.current_path = []
        else:
            # STATE: CHASE (Musuh mengejar Player menggunakan A* Pathfinding)
            self.state = "CHASE"
            self.current_path = astar_pathfinding(grid, (self.x, self.y), (player_x, player_y), cols, rows)
            if len(self.current_path) > 1:
                next_x, next_y = self.current_path[1]
                self.x = next_x
                self.y = next_y

        return distance

# ==========================================
# 3. GAME ENGINE & DASHBOARD INTERFACE
# ==========================================
class DungeonGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dungeon Crawler - Interactive Enemy AI & Pathfinding Demo")
        self.root.configure(bg="#0b0c10")

        self.cols = 16
        self.rows = 11
        self.cell_size = 46

        # Peta Dungeon Grid: 0 = Jalan (Lantai), 1 = Tembok Batu
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
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

        # Posisi Awal
        self.player_x = 1
        self.player_y = 1
        self.enemy = EnemyAI(x=14, y=9, detection_range=8.0, attack_range=1.5)

        self.is_paused = False
        self.move_speed_ms = 220  # Kecepatan gerak realtime (ms)

        # ---------------- HARDWARE / HEADER PANEL ----------------
        self.header_frame = tk.Frame(root, bg="#1f2430", padx=16, pady=12)
        self.header_frame.pack(fill=tk.X)

        self.lbl_title = tk.Label(
            self.header_frame, 
            text="⚔️ DUNGEON CRAWLER AI - REALTIME SIMULATOR", 
            fg="#73daca", bg="#1f2430", font=("Consolas", 14, "bold")
        )
        self.lbl_title.pack(anchor="w")

        self.status_container = tk.Frame(self.header_frame, bg="#1f2430")
        self.status_container.pack(fill=tk.X, pady=(6, 0))

        self.lbl_metrics = tk.Label(
            self.status_container, 
            text="PLAYER: (1,1)  |  ENEMY: (14,9)  |  JARAK: 15.26  |  STATE: PATROL", 
            fg="#cbccc6", bg="#1f2430", font=("Consolas", 10, "bold")
        )
        self.lbl_metrics.pack(side=tk.LEFT)

        self.lbl_badge = tk.Label(
            self.status_container, 
            text=" PATROL ", 
            fg="#15161e", bg="#7dcfff", font=("Consolas", 10, "bold"), padx=8, pady=2
        )
        self.lbl_badge.pack(side=tk.RIGHT)

        # ---------------- CANVAS VIEWPORT ----------------
        canvas_w = self.cols * self.cell_size
        canvas_h = self.rows * self.cell_size
        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="#0b0c10", highlightthickness=0)
        self.canvas.pack(padx=16, pady=12)

        # ---------------- CONTROL PANEL (TOMBOL INTERAKTIF) ----------------
        self.ctrl_frame = tk.Frame(root, bg="#1f2430", padx=16, pady=10)
        self.ctrl_frame.pack(fill=tk.X)

        btn_style = {"bg": "#343b58", "fg": "#c0caf5", "font": ("Consolas", 10, "bold"), "relief": "flat", "padx": 10, "pady": 4, "activebackground": "#414868", "activeforeground": "#ffffff"}

        tk.Button(self.ctrl_frame, text="⬅️ Kiri", command=lambda: self.move_player(-1, 0), **btn_style).pack(side=tk.LEFT, padx=3)
        tk.Button(self.ctrl_frame, text="⬆️ Atas", command=lambda: self.move_player(0, -1), **btn_style).pack(side=tk.LEFT, padx=3)
        tk.Button(self.ctrl_frame, text="⬇️ Bawah", command=lambda: self.move_player(0, 1), **btn_style).pack(side=tk.LEFT, padx=3)
        tk.Button(self.ctrl_frame, text="➡️ Kanan", command=lambda: self.move_player(1, 0), **btn_style).pack(side=tk.LEFT, padx=3)

        # Tombol Khusus Demo
        btn_chase = tk.Button(
            self.ctrl_frame, text="⚡ Uji Chase (Dekatkan Player)", 
            command=self.teleport_near_enemy, 
            bg="#ff9e64", fg="#15161e", font=("Consolas", 10, "bold"), relief="flat", padx=12, pady=4
        )
        btn_chase.pack(side=tk.RIGHT, padx=5)

        btn_reset = tk.Button(
            self.ctrl_frame, text="🔄 Reset Posisi", 
            command=self.reset_positions, 
            bg="#f7768e", fg="#15161e", font=("Consolas", 10, "bold"), relief="flat", padx=10, pady=4
        )
        btn_reset.pack(side=tk.RIGHT, padx=5)

        # Keyboard Bindings
        self.root.bind("<Key>", self.handle_keyboard_input)

        # Start Realtime Animation Loop
        self.update_game_loop()

    def teleport_near_enemy(self):
        # Tempatkan Player dekat musuh untuk memicu mode CHASE langsung
        self.player_x = 10
        self.player_y = 8
        self.render()

    def reset_positions(self):
        self.player_x = 1
        self.player_y = 1
        self.enemy.x = 14
        self.enemy.y = 9
        self.enemy.state = "PATROL"
        self.enemy.patrol_index = 0
        self.render()

    def move_player(self, dx, dy):
        new_x = self.player_x + dx
        new_y = self.player_y + dy

        if 0 <= new_x < self.cols and 0 <= new_y < self.rows:
            if self.grid[new_y][new_x] == 0:
                self.player_x = new_x
                self.player_y = new_y
                self.render()

    def handle_keyboard_input(self, event):
        key = event.keysym.lower()
        if key in ['w', 'up']:
            self.move_player(0, -1)
        elif key in ['s', 'down']:
            self.move_player(0, 1)
        elif key in ['a', 'left']:
            self.move_player(-1, 0)
        elif key in ['d', 'right']:
            self.move_player(1, 0)

    def update_game_loop(self):
        if not self.is_paused:
            # 1. Update AI Enemy (Selalu bergerak otomatis secara continuous!)
            self.enemy.update(self.player_x, self.player_y, self.grid, self.cols, self.rows)
            # 2. Render Ulang Canvas
            self.render()

        # Re-trigger Loop setiap speed_ms secara otomatis
        self.root.after(self.move_speed_ms, self.update_game_loop)

    def render(self):
        self.canvas.delete("all")

        # --- A. RENDERING TEMBOK & LANTAI DUNGEON ---
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if self.grid[r][c] == 1:
                    # Tembok Batu Fortress (Dual-tone 3D Shadow Style)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#1f2335", outline="#15161e", width=1)
                    self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, fill="#292e42", outline="#3b4261", width=1)
                    # Texture Bricks
                    self.canvas.create_line(x1+4, y1+self.cell_size//2, x2-4, y1+self.cell_size//2, fill="#1f2335", width=1)
                else:
                    # Checkerboard Floor Tile Pattern
                    is_even = (r + c) % 2 == 0
                    floor_color = "#181a24" if is_even else "#14151f"
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=floor_color, outline="#1f2335", width=1)

        # --- B. GAMBAR JANGKAUAN RADAR AI (Detection Circle) ---
        ex_px = self.enemy.x * self.cell_size + self.cell_size // 2
        ey_px = self.enemy.y * self.cell_size + self.cell_size // 2
        rad_px = self.enemy.detection_range * self.cell_size

        radar_color = "#7dcfff" if self.enemy.state == "PATROL" else ("#ff9e64" if self.enemy.state == "CHASE" else "#f7768e")
        self.canvas.create_oval(
            ex_px - rad_px, ey_px - rad_px, ex_px + rad_px, ey_px + rad_px, 
            outline=radar_color, dash=(4, 6), width=2
        )

        # --- C. GAMBAR JALUR A* PATHFINDING (Glowing Lines) ---
        if self.enemy.state == "CHASE" and len(self.enemy.current_path) > 1:
            coords = []
            for px, py in self.enemy.current_path:
                cx = px * self.cell_size + self.cell_size // 2
                cy = py * self.cell_size + self.cell_size // 2
                coords.extend([cx, cy])
                # Dot Node Jalur
                self.canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="#ff9e64", outline="#e0af68", width=1)

            if len(coords) >= 4:
                self.canvas.create_line(coords, fill="#ff9e64", width=3, dash=(6, 3))

        # --- D. GAMBAR PLAYER (Neon Emerald Knight) ---
        px1 = self.player_x * self.cell_size + 5
        py1 = self.player_y * self.cell_size + 5
        px2 = (self.player_x + 1) * self.cell_size - 5
        py2 = (self.player_y + 1) * self.cell_size - 5

        # Glow Aura Ring
        self.canvas.create_oval(px1-3, py1-3, px2+3, py2+3, outline="#73daca", width=2)
        # Circle Badge
        self.canvas.create_oval(px1, py1, px2, py2, fill="#00f5d4", outline="#73daca", width=2)
        # Label Hero
        self.canvas.create_text(
            self.player_x * self.cell_size + self.cell_size//2, 
            self.player_y * self.cell_size + self.cell_size//2, 
            text="🛡️ P", fill="#0f0f17", font=("Segoe UI Emoji", 12, "bold")
        )

        # --- E. GAMBAR ENEMY (Dynamic FSM State Color) ---
        badge_styles = {
            "PATROL": ("#7dcfff", "#2ac3de", "🚶 E"),
            "CHASE":  ("#ff9e64", "#e0af68", "👾 E"),
            "ATTACK": ("#f7768e", "#db4b4b", "⚔️ E")
        }
        main_color, glow_color, icon_text = badge_styles.get(self.enemy.state, ("#f7768e", "#db4b4b", "⚔️ E"))

        ex1 = self.enemy.x * self.cell_size + 5
        ey1 = self.enemy.y * self.cell_size + 5
        ex2 = (self.enemy.x + 1) * self.cell_size - 5
        ey2 = (self.enemy.y + 1) * self.cell_size - 5

        # Glow Aura
        self.canvas.create_oval(ex1-4, ey1-4, ex2+4, ey2+4, outline=glow_color, width=2)
        # Badge Main Body
        self.canvas.create_oval(ex1, ey1, ex2, ey2, fill=main_color, outline=glow_color, width=2)
        # Icon
        self.canvas.create_text(
            self.enemy.x * self.cell_size + self.cell_size//2, 
            self.enemy.y * self.cell_size + self.cell_size//2, 
            text=icon_text, fill="#0f0f17", font=("Segoe UI Emoji", 12, "bold")
        )

        # Flash Effect jika ATTACK
        if self.enemy.state == "ATTACK":
            self.canvas.create_rectangle(0, 0, self.cols*self.cell_size, self.rows*self.cell_size, fill="#f7768e", stipple="gray25")

        # --- F. UPDATE HEADER STATS & METRICS ---
        dist = math.sqrt((self.enemy.x - self.player_x)**2 + (self.enemy.y - self.player_y)**2)
        info_str = f"PLAYER: ({self.player_x}, {self.player_y})  |  ENEMY: ({self.enemy.x}, {self.enemy.y})  |  JARAK: {dist:.2f}"
        self.lbl_metrics.config(text=info_str)
        
        self.lbl_badge.config(text=f" STATE: {self.enemy.state} ", bg=main_color, fg="#0f0f17")

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = DungeonGameGUI(root)
    root.mainloop()
