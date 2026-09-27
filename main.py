import pygame
import math
import heapq
import sys

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

        if (current.x, current.y) == (target_node.x, target_node.y):
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
        
        # Patrol Waypoints
        self.patrol_a = (14, 9)
        self.patrol_b = (14, 1)
        self.target_patrol = self.patrol_b

    def update(self, player_x, player_y, grid, cols, rows):
        # 1. Hitung Jarak Euclidean ke Player
        distance = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)

        # 2. Evaluasi Finite State Machine (FSM)
        if distance > self.detection_range:
            # STATE: PATROL (Jalan terus di lorong tanpa henti)
            self.state = "PATROL"
            if (self.x, self.y) == self.target_patrol:
                self.target_patrol = self.patrol_a if self.target_patrol == self.patrol_b else self.patrol_b

            self.current_path = astar_pathfinding(grid, (self.x, self.y), self.target_patrol, cols, rows)
            if len(self.current_path) > 1:
                self.x, self.y = self.current_path[1]

        elif distance <= self.attack_range:
            # STATE: ATTACK
            self.state = "ATTACK"
            self.current_path = []
        else:
            # STATE: CHASE (Menggunakan A* Pathfinding)
            self.state = "CHASE"
            self.current_path = astar_pathfinding(grid, (self.x, self.y), (player_x, player_y), cols, rows)
            if len(self.current_path) > 1:
                self.x, self.y = self.current_path[1]

        return distance

# ==========================================
# 3. PYGAME ENGINE & GRAPHICS RENDERER
# ==========================================
class PygameDungeonGame:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.cols = 16
        self.rows = 11
        self.tile_size = 48
        self.header_height = 54

        self.width = self.cols * self.tile_size
        self.height = self.rows * self.tile_size + self.header_height

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Dungeon Crawler - Enemy AI Pygame Engine")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_title = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.font_hud = pygame.font.SysFont("Consolas", 13, bold=True)
        self.font_overlay = pygame.font.SysFont("Consolas", 22, bold=True)

        # Peta Grid Dungeon: 0 = Jalan, 1 = Tembok Batu
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

        # Entity Position & Status
        self.player_x = 1
        self.player_y = 1
        self.finish_x = 1
        self.finish_y = 9
        self.enemy = EnemyAI(x=14, y=9, detection_range=8.0, attack_range=1.5)

        self.game_status = "PLAYING"
        self.move_timer = 0
        self.move_delay = 200  # ms interval for enemy step

    def reset_game(self):
        self.player_x = 1
        self.player_y = 1
        self.enemy.x = 14
        self.enemy.y = 9
        self.enemy.state = "PATROL"
        self.enemy.target_patrol = self.enemy.patrol_b
        self.game_status = "PLAYING"

    def move_player(self, dx, dy):
        if self.game_status != "PLAYING":
            return

        nx = self.player_x + dx
        ny = self.player_y + dy

        if 0 <= nx < self.cols and 0 <= ny < self.rows and self.grid[ny][nx] == 0:
            self.player_x = nx
            self.player_y = ny

            if (self.player_x, self.player_y) == (self.finish_x, self.finish_y):
                self.game_status = "WIN"

    def run(self):
        running = True
        last_ticks = pygame.time.get_ticks()

        while running:
            dt = self.clock.tick(60)
            current_ticks = pygame.time.get_ticks()

            # Handle Event Input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key in (pygame.K_w, pygame.K_UP):
                        self.move_player(0, -1)
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        self.move_player(0, 1)
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        self.move_player(-1, 0)
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        self.move_player(1, 0)

            # Update Enemy AI pada interval waktu (Continuous Loop)
            if self.game_status == "PLAYING":
                self.move_timer += dt
                if self.move_timer >= self.move_delay:
                    self.move_timer = 0
                    self.enemy.update(self.player_x, self.player_y, self.grid, self.cols, self.rows)

                    if self.enemy.state == "ATTACK":
                        self.game_status = "GAMEOVER"

            # Render Screen
            self.render()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def render(self):
        self.screen.fill((18, 19, 28))  # Dark Velvet BG

        # --- A. HEADER BAR ---
        pygame.draw.rect(self.screen, (26, 28, 41), (0, 0, self.width, self.header_height))
        pygame.draw.line(self.screen, (41, 46, 66), (0, self.header_height), (self.width, self.header_height), 2)

        title_surf = self.font_title.render("DUNGEON CRAWLER - ENEMY AI ENGINE", True, (122, 162, 247))
        self.screen.blit(title_surf, (16, 8))

        dist = math.sqrt((self.enemy.x - self.player_x)**2 + (self.enemy.y - self.player_y)**2)
        hud_text = f"HERO: ({self.player_x},{self.player_y}) | MONSTER: ({self.enemy.x},{self.enemy.y}) | DIST: {dist:.2f}"
        hud_surf = self.font_hud.render(hud_text, True, (169, 177, 214))
        self.screen.blit(hud_surf, (16, 30))

        # AI State Badge
        st_colors = {"PATROL": (125, 207, 255), "CHASE": (255, 158, 100), "ATTACK": (247, 118, 142)}
        badge_color = st_colors.get(self.enemy.state, (247, 118, 142))
        badge_surf = self.font_hud.render(f" STATE: {self.enemy.state} ", True, (17, 17, 27))
        badge_rect = badge_surf.get_rect(topright=(self.width - 16, 12))
        
        pygame.draw.rect(self.screen, badge_color, badge_rect.inflate(8, 4), border_radius=4)
        self.screen.blit(badge_surf, badge_rect)

        # --- B. RENDER MAP DUNGEON ---
        offset_y = self.header_height
        for r in range(self.rows):
            for c in range(self.cols):
                x = c * self.tile_size
                y = r * self.tile_size + offset_y

                if self.grid[r][c] == 1:
                    # Wall Tile 3D Style
                    pygame.draw.rect(self.screen, (31, 35, 53), (x, y, self.tile_size, self.tile_size))
                    pygame.draw.rect(self.screen, (41, 46, 66), (x+2, y+2, self.tile_size-4, self.tile_size-4), 1)
                    pygame.draw.line(self.screen, (21, 22, 30), (x+4, y+self.tile_size//2), (x+self.tile_size-4, y+self.tile_size//2), 1)
                else:
                    # Floor Tile Pattern
                    floor_col = (22, 23, 34) if (r + c) % 2 == 0 else (19, 20, 31)
                    pygame.draw.rect(self.screen, floor_col, (x, y, self.tile_size, self.tile_size))
                    pygame.draw.rect(self.screen, (31, 35, 53), (x, y, self.tile_size, self.tile_size), 1)

        # --- C. FINISH EXIT DOOR ---
        door_x = self.finish_x * self.tile_size + 4
        door_y = self.finish_y * self.tile_size + offset_y + 4
        door_w = self.tile_size - 8
        pygame.draw.rect(self.screen, (65, 166, 181), (door_x, door_y, door_w, door_w), border_radius=4)
        pygame.draw.rect(self.screen, (158, 206, 106), (door_x-2, door_y-2, door_w+4, door_w+4), 2, border_radius=4)
        
        door_lbl = self.font_hud.render("EXIT", True, (17, 17, 27))
        self.screen.blit(door_lbl, (door_x + 6, door_y + 12))

        # --- D. RADAR DETEKSI ENEMY ---
        ex_center = self.enemy.x * self.tile_size + self.tile_size // 2
        ey_center = self.enemy.y * self.tile_size + offset_y + self.tile_size // 2
        rad_px = int(self.enemy.detection_range * self.tile_size)

        pygame.draw.circle(self.screen, badge_color, (ex_center, ey_center), rad_px, 1)

        # --- E. JALUR A* PATHFINDING ---
        if self.enemy.state == "CHASE" and len(self.enemy.current_path) > 1:
            pts = []
            for px, py in self.enemy.current_path:
                cx = px * self.tile_size + self.tile_size // 2
                cy = py * self.tile_size + offset_y + self.tile_size // 2
                pts.append((cx, cy))
                pygame.draw.circle(self.screen, (255, 158, 100), (cx, cy), 4)

            if len(pts) >= 2:
                pygame.draw.lines(self.screen, (255, 158, 100), False, pts, 3)

        # --- F. PLAYER SPRITE (KNIGHT HERO) ---
        px_c = self.player_x * self.tile_size + self.tile_size // 2
        py_c = self.player_y * self.tile_size + offset_y + self.tile_size // 2
        pr = self.tile_size // 2 - 6

        pygame.draw.circle(self.screen, (158, 206, 106), (px_c, py_c), pr + 2, 2)
        pygame.draw.circle(self.screen, (115, 218, 202), (px_c, py_c), pr)
        # Visor
        pygame.draw.rect(self.screen, (192, 202, 245), (px_c - pr + 6, py_c - 4, pr*2 - 12, 8))

        # --- G. ENEMY SPRITE (MONSTER DEMON WITH HORNS & GLOWING EYES) ---
        ex_c = self.enemy.x * self.tile_size + self.tile_size // 2
        ey_c = self.enemy.y * self.tile_size + offset_y + self.tile_size // 2
        er = self.tile_size // 2 - 6

        # Horns
        pygame.draw.polygon(self.screen, badge_color, [(ex_c-er+4, ey_c-er+2), (ex_c-er+10, ey_c-er-6), (ex_c-2, ey_c-er+4)])
        pygame.draw.polygon(self.screen, badge_color, [(ex_c+er-4, ey_c-er+2), (ex_c+er-10, ey_c-er-6), (ex_c+2, ey_c-er+4)])

        # Body
        pygame.draw.circle(self.screen, badge_color, (ex_c, ey_c), er + 2, 2)
        pygame.draw.circle(self.screen, badge_color, (ex_c, ey_c), er)

        # Eyes
        eye_col = (255, 255, 255) if self.enemy.state == "ATTACK" else (21, 22, 30)
        pygame.draw.circle(self.screen, (21, 22, 30), (ex_c - 7, ey_c - 3), 4)
        pygame.draw.circle(self.screen, (21, 22, 30), (ex_c + 7, ey_c - 3), 4)
        pygame.draw.circle(self.screen, eye_col, (ex_c - 7, ey_c - 3), 2)
        pygame.draw.circle(self.screen, eye_col, (ex_c + 7, ey_c - 3), 2)

        # --- H. OVERLAY MENANG / KALAH ---
        if self.game_status == "WIN":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((17, 17, 27, 200))
            self.screen.blit(overlay, (0, 0))

            card_rect = pygame.Rect(self.width//2 - 220, self.height//2 - 50, 440, 100)
            pygame.draw.rect(self.screen, (158, 206, 106), card_rect, border_radius=8)
            pygame.draw.rect(self.screen, (115, 218, 202), card_rect, 3, border_radius=8)

            txt1 = self.font_overlay.render("YOU WIN! BERHASIL KABUR!", True, (17, 17, 27))
            txt2 = self.font_hud.render("Tekan 'R' untuk bermain lagi", True, (31, 35, 53))
            self.screen.blit(txt1, txt1.get_rect(center=(self.width//2, self.height//2 - 14)))
            self.screen.blit(txt2, txt2.get_rect(center=(self.width//2, self.height//2 + 18)))

        elif self.game_status == "GAMEOVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((17, 17, 27, 200))
            self.screen.blit(overlay, (0, 0))

            card_rect = pygame.Rect(self.width//2 - 220, self.height//2 - 50, 440, 100)
            pygame.draw.rect(self.screen, (247, 118, 142), card_rect, border_radius=8)
            pygame.draw.rect(self.screen, (219, 75, 75), card_rect, 3, border_radius=8)

            txt1 = self.font_overlay.render("GAME OVER! TERTANGKAP MUSUH!", True, (17, 17, 27))
            txt2 = self.font_hud.render("Tekan 'R' untuk mencoba lagi", True, (31, 35, 53))
            self.screen.blit(txt1, txt1.get_rect(center=(self.width//2, self.height//2 - 14)))
            self.screen.blit(txt2, txt2.get_rect(center=(self.width//2, self.height//2 + 18)))

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    game = PygameDungeonGame()
    game.run()
