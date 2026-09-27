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
    def __init__(self, x, y, detection_range=8.0, attack_range=1.5):
        self.x = x
        self.y = y
        self.detection_range = detection_range
        self.attack_range = attack_range
        self.state = "PATROL"
        self.current_path = []
        
        # Rute Patroli Otomatis
        self.patrol_waypoints = [(14, 9), (14, 2), (9, 2), (9, 9)]
        self.patrol_index = 0

    def update(self, player_x, player_y, grid, cols, rows):
        distance = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)

        if distance > self.detection_range:
            self.state = "PATROL"
            target = self.patrol_waypoints[self.patrol_index]
            if (self.x, self.y) == target:
                self.patrol_index = (self.patrol_index + 1) % len(self.patrol_waypoints)
                target = self.patrol_waypoints[self.patrol_index]

            self.current_path = astar_pathfinding(grid, (self.x, self.y), target, cols, rows)
            if len(self.current_path) > 1:
                self.x, self.y = self.current_path[1]

        elif distance <= self.attack_range:
            self.state = "ATTACK"
            self.current_path = []
        else:
            self.state = "CHASE"
            self.current_path = astar_pathfinding(grid, (self.x, self.y), (player_x, player_y), cols, rows)
            if len(self.current_path) > 1:
                self.x, self.y = self.current_path[1]

        return distance

# ==========================================
# 3. GAME ENGINE & VECTOR GRAPHICS CANVAS
# ==========================================
class DungeonGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dungeon Game - Enemy AI Pathfinder (Rose Pine Palette)")
        self.root.configure(bg="#191724")

        self.cols = 16
        self.rows = 11
        self.cell_size = 48

        # 0 = Floor, 1 = Wall
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

        self.player_x = 1
        self.player_y = 1
        self.enemy = EnemyAI(x=14, y=9, detection_range=8.0, attack_range=1.5)

        self.is_paused = False
        self.move_speed_ms = 220

        # HEADER DASHBOARD
        self.header_frame = tk.Frame(root, bg="#1f1d2e", padx=18, pady=12)
        self.header_frame.pack(fill=tk.X)

        self.lbl_title = tk.Label(
            self.header_frame, 
            text="DUNGEON CRAWLER - ENEMY AI SIMULATOR", 
            fg="#ebbcba", bg="#1f1d2e", font=("Century Gothic", 13, "bold")
        )
        self.lbl_title.pack(anchor="w")

        self.status_container = tk.Frame(self.header_frame, bg="#1f1d2e")
        self.status_container.pack(fill=tk.X, pady=(6, 0))

        self.lbl_metrics = tk.Label(
            self.status_container, 
            text="PLAYER: (1,1)  |  ENEMY: (14,9)  |  DISTANCE: 15.26", 
            fg="#e0def4", bg="#1f1d2e", font=("Consolas", 10)
        )
        self.lbl_metrics.pack(side=tk.LEFT)

        self.lbl_badge = tk.Label(
            self.status_container, 
            text=" PATROL ", 
            fg="#191724", bg="#9ccfd8", font=("Consolas", 10, "bold"), padx=10, pady=2
        )
        self.lbl_badge.pack(side=tk.RIGHT)

        # CANVAS VIEWPORT
        canvas_w = self.cols * self.cell_size
        canvas_h = self.rows * self.cell_size
        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="#191724", highlightthickness=0)
        self.canvas.pack(padx=18, pady=12)

        # CONTROL PANEL
        self.ctrl_frame = tk.Frame(root, bg="#1f1d2e", padx=18, pady=10)
        self.ctrl_frame.pack(fill=tk.X)

        btn_style = {"bg": "#26233a", "fg": "#e0def4", "font": ("Consolas", 10, "bold"), "relief": "flat", "padx": 10, "pady": 5, "activebackground": "#31748f", "activeforeground": "#ffffff"}

        tk.Button(self.ctrl_frame, text="⬅️ Kiri", command=lambda: self.move_player(-1, 0), **btn_style).pack(side=tk.LEFT, padx=3)
        tk.Button(self.ctrl_frame, text="⬆️ Atas", command=lambda: self.move_player(0, -1), **btn_style).pack(side=tk.LEFT, padx=3)
        tk.Button(self.ctrl_frame, text="⬇️ Bawah", command=lambda: self.move_player(0, 1), **btn_style).pack(side=tk.LEFT, padx=3)
        tk.Button(self.ctrl_frame, text="➡️ Kanan", command=lambda: self.move_player(1, 0), **btn_style).pack(side=tk.LEFT, padx=3)

        btn_chase = tk.Button(
            self.ctrl_frame, text="⚡ Uji Chase (Dekatkan Player)", 
            command=self.teleport_near_enemy, 
            bg="#f6c177", fg="#191724", font=("Consolas", 10, "bold"), relief="flat", padx=12, pady=5
        )
        btn_chase.pack(side=tk.RIGHT, padx=5)

        btn_reset = tk.Button(
            self.ctrl_frame, text="🔄 Reset", 
            command=self.reset_positions, 
            bg="#eb6f92", fg="#191724", font=("Consolas", 10, "bold"), relief="flat", padx=10, pady=5
        )
        btn_reset.pack(side=tk.RIGHT, padx=5)

        self.root.bind("<Key>", self.handle_keyboard_input)

        # Loop animasi
        self.update_game_loop()

    def teleport_near_enemy(self):
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
            self.enemy.update(self.player_x, self.player_y, self.grid, self.cols, self.rows)
            self.render()
        self.root.after(self.move_speed_ms, self.update_game_loop)

    def render(self):
        self.canvas.delete("all")

        # --- A. MAP DUNGEON (Warm Stone Brick Palette) ---
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if self.grid[r][c] == 1:
                    # Wall Brick 3D Style
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#26233a", outline="#1f1d2e", width=1)
                    self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, fill="#31748f", outline="#ebbcba", width=1)
                    # Brick lines
                    self.canvas.create_line(x1+4, y1+self.cell_size//2, x2-4, y1+self.cell_size//2, fill="#191724", width=1)
                else:
                    # Floor Tiles
                    floor_bg = "#1f1d2e" if (r + c) % 2 == 0 else "#191724"
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=floor_bg, outline="#26233a", width=1)

        # --- B. RADAR JANGKAUAN DETEKSI ---
        ex_px = self.enemy.x * self.cell_size + self.cell_size // 2
        ey_px = self.enemy.y * self.cell_size + self.cell_size // 2
        rad_px = self.enemy.detection_range * self.cell_size

        radar_color = "#9ccfd8" if self.enemy.state == "PATROL" else ("#f6c177" if self.enemy.state == "CHASE" else "#eb6f92")
        self.canvas.create_oval(
            ex_px - rad_px, ey_px - rad_px, ex_px + rad_px, ey_px + rad_px, 
            outline=radar_color, dash=(4, 6), width=2
        )

        # --- C. JALUR A* PATHFINDING ---
        if self.enemy.state == "CHASE" and len(self.enemy.current_path) > 1:
            coords = []
            for px, py in self.enemy.current_path:
                cx = px * self.cell_size + self.cell_size // 2
                cy = py * self.cell_size + self.cell_size // 2
                coords.extend([cx, cy])
                self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill="#f6c177", outline="#ebbcba", width=1)

            if len(coords) >= 4:
                self.canvas.create_line(coords, fill="#f6c177", width=3, dash=(6, 3))

        # --- D. SPRITE VECTOR PLAYER (KNIGHT HERO WITH SHIELD) ---
        cx = self.player_x * self.cell_size + self.cell_size // 2
        cy = self.player_y * self.cell_size + self.cell_size // 2
        r = self.cell_size // 2 - 6

        # Outer Glow Circle
        self.canvas.create_oval(cx-r-2, cy-r-2, cx+r+2, cy+r+2, outline="#31748f", width=2)
        # Knight Body Badge
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#31748f", outline="#9ccfd8", width=2)
        # Knight Visor/Helmet Detail
        self.canvas.create_rectangle(cx-r+6, cy-4, cx+r-6, cy+4, fill="#e0def4", outline="")
        self.canvas.create_line(cx-r+10, cy, cx+r-10, cy, fill="#191724", width=2)
        # Crest Star
        self.canvas.create_text(cx, cy - r + 8, text="★", fill="#f6c177", font=("Arial", 9, "bold"))
        self.canvas.create_text(cx, cy + r - 8, text="HERO", fill="#e0def4", font=("Consolas", 7, "bold"))

        # --- E. SPRITE VECTOR ENEMY (GOBLIN / DRAGON MONSTER WITH HORNS & EYES) ---
        ecx = self.enemy.x * self.cell_size + self.cell_size // 2
        ecy = self.enemy.y * self.cell_size + self.cell_size // 2
        er = self.cell_size // 2 - 6

        styles = {
            "PATROL": ("#9ccfd8", "#31748f", "PATROL"),
            "CHASE":  ("#f6c177", "#ea9a97", "CHASE"),
            "ATTACK": ("#eb6f92", "#b4637a", "ATTACK")
        }
        main_col, border_col, st_label = styles.get(self.enemy.state, ("#eb6f92", "#b4637a", "ATTACK"))

        # Monster Horns (Tanduk Demon Vector)
        self.canvas.create_polygon(ecx-er+4, ecy-er+2, ecx-er+10, ecy-er-6, ecx-2, ecy-er+4, fill=border_col, outline="")
        self.canvas.create_polygon(ecx+er-4, ecy-er+2, ecx+er-10, ecy-er-6, ecx+2, ecy-er+4, fill=border_col, outline="")

        # Outer Glow
        self.canvas.create_oval(ecx-er-2, ecy-er-2, ecx+er+2, ecy+er+2, outline=border_col, width=2)
        # Main Monster Body
        self.canvas.create_oval(ecx-er, ecy-er, ecx+er, ecy+er, fill=main_col, outline=border_col, width=2)

        # Glowing Eyes (Mata Monster Vector)
        eye_color = "#eb6f92" if self.enemy.state != "ATTACK" else "#fff"
        self.canvas.create_oval(ecx-10, ecy-6, ecx-2, ecy+2, fill="#191724", outline="")
        self.canvas.create_oval(ecx+2, ecy-6, ecx+10, ecy+2, fill="#191724", outline="")
        self.canvas.create_oval(ecx-8, ecy-4, ecx-4, ecy, fill=eye_color, outline="")
        self.canvas.create_oval(ecx+4, ecy-4, ecx+8, ecy, fill=eye_color, outline="")

        # Label State
        self.canvas.create_text(ecx, ecy + er - 8, text=st_label, fill="#191724", font=("Consolas", 7, "bold"))

        # Flash Effect saat ATTACK
        if self.enemy.state == "ATTACK":
            self.canvas.create_rectangle(0, 0, self.cols*self.cell_size, self.rows*self.cell_size, fill="#eb6f92", stipple="gray25")

        # --- F. UPDATE HEADER METRICS ---
        dist = math.sqrt((self.enemy.x - self.player_x)**2 + (self.enemy.y - self.player_y)**2)
        info_str = f"PLAYER: ({self.player_x}, {self.player_y})  |  ENEMY: ({self.enemy.x}, {self.enemy.y})  |  DISTANCE: {dist:.2f}"
        self.lbl_metrics.config(text=info_str)
        self.lbl_badge.config(text=f" {self.enemy.state} ", bg=main_col, fg="#191724")

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = DungeonGameGUI(root)
    root.mainloop()
