import tkinter as tk
import math
import heapq

# ==========================================
# 1. ALGORITMA A* PATHFINDING
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

        for nx, ny in [(current.x+1, current.y), (current.x-1, current.y), (current.x, current.y+1), (current.x, current.y-1)]:
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
    def __init__(self, x, y, detection_range=8.0, attack_range=1.5):
        self.x = x
        self.y = y
        self.detection_range = detection_range
        self.attack_range = attack_range
        self.state = "PATROL"
        self.current_path = []
        
        self.patrol_a = (14, 9)
        self.patrol_b = (14, 1)
        self.target_patrol = self.patrol_b

    def update(self, player_x, player_y, grid, cols, rows):
        distance = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)

        if distance > self.detection_range:
            self.state = "PATROL"
            if (self.x, self.y) == self.target_patrol:
                self.target_patrol = self.patrol_a if self.target_patrol == self.patrol_b else self.patrol_b

            self.current_path = astar_pathfinding(grid, (self.x, self.y), self.target_patrol, cols, rows)
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
# 3. GAME SIMULATOR INTERFACE (TKINTER GUI)
# ==========================================
class DungeonGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dungeon Game - Escape the Dungeon!")
        self.root.configure(bg="#12131c")

        self.cols = 16
        self.rows = 11
        self.cell_size = 46

        # Peta Grid Dungeon: 0 = Jalan, 1 = Tembok
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

        # Posisi Awal, Target Finish, & Status Game
        self.player_x = 1
        self.player_y = 1
        self.finish_x = 1
        self.finish_y = 9
        self.enemy = EnemyAI(x=14, y=9, detection_range=8.0, attack_range=1.5)

        self.game_status = "PLAYING"  # PLAYING, WIN, GAMEOVER

        # Header Metrics UI
        self.header = tk.Frame(root, bg="#1a1c29", padx=16, pady=12)
        self.header.pack(fill=tk.X)

        self.lbl_title = tk.Label(self.header, text="🎯 TUJUAN: REACH THE FINISH DOOR (🚪 EXIT) WITHOUT GETTING CAUGHT!", fg="#9ece6a", bg="#1a1c29", font=("Helvetica", 11, "bold"))
        self.lbl_title.pack(anchor="w")

        self.sub_frame = tk.Frame(self.header, bg="#1a1c29")
        self.sub_frame.pack(fill=tk.X, pady=(4, 0))

        self.lbl_metrics = tk.Label(self.sub_frame, text="", fg="#a9b1d6", bg="#1a1c29", font=("Consolas", 10))
        self.lbl_metrics.pack(side=tk.LEFT)

        self.lbl_badge = tk.Label(self.sub_frame, text=" PATROL ", fg="#11111b", bg="#7dcfff", font=("Consolas", 10, "bold"), padx=8, pady=2)
        self.lbl_badge.pack(side=tk.RIGHT)

        # Canvas Game Viewport
        self.canvas = tk.Canvas(root, width=self.cols*self.cell_size, height=self.rows*self.cell_size, bg="#12131c", highlightthickness=0)
        self.canvas.pack(padx=16, pady=12)

        # Bottom Control Panel
        self.ctrl = tk.Frame(root, bg="#1a1c29", padx=16, pady=10)
        self.ctrl.pack(fill=tk.X)

        btn_cfg = {"bg": "#24283b", "fg": "#c0caf5", "font": ("Consolas", 10, "bold"), "relief": "flat", "padx": 10, "pady": 4}

        tk.Button(self.ctrl, text="⬅️ Kiri", command=lambda: self.move_player(-1, 0), **btn_cfg).pack(side=tk.LEFT, padx=3)
        tk.Button(self.ctrl, text="⬆️ Atas", command=lambda: self.move_player(0, -1), **btn_cfg).pack(side=tk.LEFT, padx=3)
        tk.Button(self.ctrl, text="⬇️ Bawah", command=lambda: self.move_player(0, 1), **btn_cfg).pack(side=tk.LEFT, padx=3)
        tk.Button(self.ctrl, text="➡️ Kanan", command=lambda: self.move_player(1, 0), **btn_cfg).pack(side=tk.LEFT, padx=3)

        tk.Button(self.ctrl, text="⚡ Uji Chase (Dekatkan Player)", command=self.teleport_near_enemy, bg="#ff9e64", fg="#11111b", font=("Consolas", 10, "bold"), relief="flat", padx=10, pady=4).pack(side=tk.RIGHT, padx=5)
        tk.Button(self.ctrl, text="🔄 Main Lagi / Reset", command=self.reset_game, bg="#7dcfff", fg="#11111b", font=("Consolas", 10, "bold"), relief="flat", padx=10, pady=4).pack(side=tk.RIGHT, padx=5)

        self.root.bind("<Key>", self.handle_key)

        # Loop animasi otomatis
        self.update_loop()

    def teleport_near_enemy(self):
        if self.game_status == "PLAYING":
            self.player_x = 10
            self.player_y = 8
            self.render()

    def reset_game(self):
        self.player_x = 1
        self.player_y = 1
        self.enemy.x = 14
        self.enemy.y = 9
        self.enemy.state = "PATROL"
        self.enemy.target_patrol = self.enemy.patrol_b
        self.game_status = "PLAYING"
        self.render()

    def move_player(self, dx, dy):
        if self.game_status != "PLAYING":
            return

        nx, ny = self.player_x + dx, self.player_y + dy
        if 0 <= nx < self.cols and 0 <= ny < self.rows and self.grid[ny][nx] == 0:
            self.player_x, self.player_y = nx, ny
            
            # Cek Kondisi WIN (Mencapai Pintu Finish)
            if (self.player_x, self.player_y) == (self.finish_x, self.finish_y):
                self.game_status = "WIN"

            self.render()

    def handle_key(self, event):
        k = event.keysym.lower()
        if k in ['w', 'up']: self.move_player(0, -1)
        elif k in ['s', 'down']: self.move_player(0, 1)
        elif k in ['a', 'left']: self.move_player(-1, 0)
        elif k in ['d', 'right']: self.move_player(1, 0)

    def update_loop(self):
        if self.game_status == "PLAYING":
            # Update AI Enemy
            self.enemy.update(self.player_x, self.player_y, self.grid, self.cols, self.rows)
            
            # Cek Kondisi GAME OVER (Tertangkap Musuh saat ATTACK)
            if self.enemy.state == "ATTACK":
                self.game_status = "GAMEOVER"

            self.render()

        self.root.after(200, self.update_loop)

    def render(self):
        self.canvas.delete("all")

        # --- A. MAP GRID DUNGEON ---
        for r in range(self.rows):
            for c in range(self.cols):
                x1, y1 = c*self.cell_size, r*self.cell_size
                x2, y2 = x1+self.cell_size, y1+self.cell_size

                if self.grid[r][c] == 1:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#1f2335", outline="#15161e", width=1)
                    self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, fill="#292e42", outline="#3b4261", width=1)
                else:
                    floor_col = "#161722" if (r+c)%2 == 0 else "#13141f"
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=floor_col, outline="#1f2335", width=1)

        # --- B. GAMBAR FINISH DOOR (EXIT TILE) ---
        fx1 = self.finish_x * self.cell_size + 4
        fy1 = self.finish_y * self.cell_size + 4
        fx2 = (self.finish_x + 1) * self.cell_size - 4
        fy2 = (self.finish_y + 1) * self.cell_size - 4

        # Glowing Green Door Aura
        self.canvas.create_rectangle(fx1-2, fy1-2, fx2+2, fy2+2, fill="#9ece6a", outline="#73daca")
        self.canvas.create_rectangle(fx1, fy1, fx2, fy2, fill="#41a6b5", outline="#9ece6a", width=2)
        self.canvas.create_text(
            self.finish_x * self.cell_size + self.cell_size // 2, 
            self.finish_y * self.cell_size + self.cell_size // 2, 
            text="🚪 FINISH", fill="#11111b", font=("Consolas", 8, "bold")
        )

        # --- C. RADAR JANGKAUAN DETEKSI ---
        ex_px = self.enemy.x * self.cell_size + self.cell_size // 2
        ey_px = self.enemy.y * self.cell_size + self.cell_size // 2
        rad_px = self.enemy.detection_range * self.cell_size

        st_cols = {"PATROL": "#7dcfff", "CHASE": "#ff9e64", "ATTACK": "#f7768e"}
        cur_col = st_cols.get(self.enemy.state, "#f7768e")
        self.canvas.create_oval(ex_px-rad_px, ey_px-rad_px, ex_px+rad_px, ey_px+rad_px, outline=cur_col, dash=(4, 6), width=2)

        # --- D. JALUR A* PATHFINDING ---
        if self.enemy.state == "CHASE" and len(self.enemy.current_path) > 1:
            coords = []
            for px, py in self.enemy.current_path:
                cx = px * self.cell_size + self.cell_size // 2
                cy = py * self.cell_size + self.cell_size // 2
                coords.extend([cx, cy])
                self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill="#ff9e64", outline="#e0af68", width=1)

            if len(coords) >= 4:
                self.canvas.create_line(coords, fill="#ff9e64", width=3, dash=(5, 3))

        # --- E. SPRITE PLAYER (KNIGHT HERO) ---
        cx = self.player_x * self.cell_size + self.cell_size // 2
        cy = self.player_y * self.cell_size + self.cell_size // 2
        r = self.cell_size // 2 - 6

        self.canvas.create_oval(cx-r-2, cy-r-2, cx+r+2, cy+r+2, outline="#9ece6a", width=2)
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#73daca", outline="#9ece6a", width=2)
        self.canvas.create_rectangle(cx-r+6, cy-4, cx+r-6, cy+4, fill="#c0caf5", outline="")
        self.canvas.create_text(cx, cy + r - 8, text="HERO", fill="#15161e", font=("Consolas", 7, "bold"))

        # --- F. SPRITE ENEMY (DEMON MONSTER WITH HORNS & GLOWING EYES) ---
        ecx = self.enemy.x * self.cell_size + self.cell_size // 2
        ecy = self.enemy.y * self.cell_size + self.cell_size // 2
        er = self.cell_size // 2 - 6

        # Tanduk Demon
        self.canvas.create_polygon(ecx-er+4, ecy-er+2, ecx-er+10, ecy-er-6, ecx-2, ecy-er+4, fill=cur_col, outline="")
        self.canvas.create_polygon(ecx+er-4, ecy-er+2, ecx+er-10, ecy-er-6, ecx+2, ecy-er+4, fill=cur_col, outline="")

        # Body Monster
        self.canvas.create_oval(ecx-er-2, ecy-er-2, ecx+er+2, ecy+er+2, outline=cur_col, width=2)
        self.canvas.create_oval(ecx-er, ecy-er, ecx+er, ecy+er, fill=cur_col, outline=cur_col, width=2)

        # Mata Monster
        eye_col = "#15161e" if self.enemy.state != "ATTACK" else "#ffffff"
        self.canvas.create_oval(ecx-10, ecy-6, ecx-2, ecy+2, fill="#15161e", outline="")
        self.canvas.create_oval(ecx+2, ecy-6, ecx+10, ecy+2, fill="#15161e", outline="")
        self.canvas.create_oval(ecx-8, ecy-4, ecx-4, ecy, fill=eye_col, outline="")
        self.canvas.create_oval(ecx+4, ecy-4, ecx+8, ecy, fill=eye_col, outline="")

        self.canvas.create_text(ecx, ecy + er - 8, text=self.enemy.state, fill="#15161e", font=("Consolas", 7, "bold"))

        # --- G. METRICS HUD ---
        dist = math.sqrt((self.enemy.x - self.player_x)**2 + (self.enemy.y - self.player_y)**2)
        self.lbl_metrics.config(text=f"PLAYER: ({self.player_x}, {self.player_y})  |  ENEMY: ({self.enemy.x}, {self.enemy.y})  |  JARAK: {dist:.2f}")
        self.lbl_badge.config(text=f" {self.enemy.state} ", bg=cur_col, fg="#11111b")

        # --- H. OVERLAY LAYAR WIN & GAME OVER ---
        cw = self.cols * self.cell_size
        ch = self.rows * self.cell_size

        if self.game_status == "WIN":
            self.canvas.create_rectangle(0, 0, cw, ch, fill="#11111b", stipple="gray75")
            self.canvas.create_rectangle(cw//2-220, ch//2-50, cw//2+220, ch//2+50, fill="#9ece6a", outline="#73daca", width=3)
            self.canvas.create_text(cw//2, ch//2-10, text="🎉 YOU WIN! BERHASIL KABUR!", fill="#11111b", font=("Consolas", 14, "bold"))
            self.canvas.create_text(cw//2, ch//2+18, text="Klik 'Main Lagi / Reset' untuk bermain ulang", fill="#1f2335", font=("Consolas", 9, "bold"))

        elif self.game_status == "GAMEOVER":
            self.canvas.create_rectangle(0, 0, cw, ch, fill="#11111b", stipple="gray75")
            self.canvas.create_rectangle(cw//2-220, ch//2-50, cw//2+220, ch//2+50, fill="#f7768e", outline="#db4b4b", width=3)
            self.canvas.create_text(cw//2, ch//2-10, text="💀 GAME OVER! TERTANGKAP MUSUH!", fill="#11111b", font=("Consolas", 14, "bold"))
            self.canvas.create_text(cw//2, ch//2+18, text="Klik 'Main Lagi / Reset' untuk mencoba lagi", fill="#1f2335", font=("Consolas", 9, "bold"))

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = DungeonGameGUI(root)
    root.mainloop()
