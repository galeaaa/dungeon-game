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
    def __init__(self, x, y, patrol_a, patrol_b, detection_range=9.0, attack_range=1.5):
        self.x = x
        self.y = y
        self.detection_range = detection_range
        self.attack_range = attack_range
        self.state = "PATROL"
        self.current_path = []
        
        self.patrol_a = patrol_a
        self.patrol_b = patrol_b
        self.target_patrol = patrol_b

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
# 3. PYGAME GAME ENGINE
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
        pygame.display.set_caption("Dungeon Crawler - Escape Game with Enemy AI")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_title = pygame.font.SysFont("Segoe UI", 15, bold=True)
        self.font_hud = pygame.font.SysFont("Consolas", 12, bold=True)
        self.font_overlay = pygame.font.SysFont("Consolas", 20, bold=True)

        # Map Grid: 0 = Jalan, 1 = Tembok
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

        # Inisialisasi Posisi
        self.player_x = 1
        self.player_y = 1
        self.has_key = False
        self.key_pos = (7, 5)  # Kunci di tengah labirin
        self.finish_pos = (14, 9)  # Pintu Finish di pojok kanan bawah (di balik penjagaan musuh!)

        # 2 Musuh AI Menjaga Labirin & Pintu Keluar
        self.enemy1 = EnemyAI(x=9, y=5, patrol_a=(9, 5), patrol_b=(9, 9), detection_range=8.0)
        self.enemy2 = EnemyAI(x=14, y=5, patrol_a=(14, 5), patrol_b=(14, 1), detection_range=9.0)

        self.game_status = "PLAYING"
        self.move_timer = 0
        self.move_delay = 190  # Kecepatan gerak musuh (ms)

    def reset_game(self):
        self.player_x = 1
        self.player_y = 1
        self.has_key = False
        self.enemy1.x = 9
        self.enemy1.y = 5
        self.enemy1.state = "PATROL"
        self.enemy2.x = 14
        self.enemy2.y = 5
        self.enemy2.state = "PATROL"
        self.game_status = "PLAYING"

    def move_player(self, dx, dy):
        if self.game_status != "PLAYING":
            return

        nx = self.player_x + dx
        ny = self.player_y + dy

        if 0 <= nx < self.cols and 0 <= ny < self.rows and self.grid[ny][nx] == 0:
            self.player_x = nx
            self.player_y = ny

            # Ambil Kunci
            if not self.has_key and (self.player_x, self.player_y) == self.key_pos:
                self.has_key = True

            # Cek Pintu Keluar
            if (self.player_x, self.player_y) == self.finish_pos:
                if self.has_key:
                    self.game_status = "WIN"

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)

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

            # Update Enemy AI
            if self.game_status == "PLAYING":
                self.move_timer += dt
                if self.move_timer >= self.move_delay:
                    self.move_timer = 0
                    self.enemy1.update(self.player_x, self.player_y, self.grid, self.cols, self.rows)
                    self.enemy2.update(self.player_x, self.player_y, self.grid, self.cols, self.rows)

                    if self.enemy1.state == "ATTACK" or self.enemy2.state == "ATTACK":
                        self.game_status = "GAMEOVER"

            self.render()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def render(self):
        self.screen.fill((18, 19, 28))

        # --- A. HEADER BAR ---
        pygame.draw.rect(self.screen, (26, 28, 41), (0, 0, self.width, self.header_height))
        pygame.draw.line(self.screen, (41, 46, 66), (0, self.header_height), (self.width, self.header_height), 2)

        title_surf = self.font_title.render("DUNGEON ESCAPE - AI CHASE & GUARDIANS", True, (122, 162, 247))
        self.screen.blit(title_surf, (16, 6))

        key_str = "🔑 KEY: OBTAINED!" if self.has_key else "🔑 KEY: NEEDED (GRAB AT CENTER!)"
        hud_text = f"HERO: ({self.player_x},{self.player_y}) | {key_str}"
        hud_surf = self.font_hud.render(hud_text, True, (255, 224, 130) if self.has_key else (247, 118, 142))
        self.screen.blit(hud_surf, (16, 28))

        # --- B. MAP DUNGEON ---
        offset_y = self.header_height
        for r in range(self.rows):
            for c in range(self.cols):
                x = c * self.tile_size
                y = r * self.tile_size + offset_y

                if self.grid[r][c] == 1:
                    pygame.draw.rect(self.screen, (31, 35, 53), (x, y, self.tile_size, self.tile_size))
                    pygame.draw.rect(self.screen, (41, 46, 66), (x+2, y+2, self.tile_size-4, self.tile_size-4), 1)
                else:
                    floor_col = (22, 23, 34) if (r + c) % 2 == 0 else (19, 20, 31)
                    pygame.draw.rect(self.screen, floor_col, (x, y, self.tile_size, self.tile_size))
                    pygame.draw.rect(self.screen, (31, 35, 53), (x, y, self.tile_size, self.tile_size), 1)

        # --- C. ITEM KUNCI (KEY) ---
        if not self.has_key:
            kx = self.key_pos[0] * self.tile_size + self.tile_size // 2
            ky = self.key_pos[1] * self.tile_size + offset_y + self.tile_size // 2
            pygame.draw.circle(self.screen, (255, 215, 0), (kx, ky), 10)
            pygame.draw.circle(self.screen, (255, 160, 0), (kx, ky), 6)
            lbl_k = self.font_hud.render("KEY", True, (17, 17, 27))
            self.screen.blit(lbl_k, (kx-10, ky-6))

        # --- D. PINTU FINISH (EXIT DOOR AT BOTTOM-RIGHT) ---
        door_x = self.finish_pos[0] * self.tile_size + 4
        door_y = self.finish_pos[1] * self.tile_size + offset_y + 4
        door_w = self.tile_size - 8
        door_col = (158, 206, 106) if self.has_key else (100, 100, 120)
        pygame.draw.rect(self.screen, door_col, (door_x, door_y, door_w, door_w), border_radius=4)
        pygame.draw.rect(self.screen, (255, 255, 255), (door_x-2, door_y-2, door_w+4, door_w+4), 2, border_radius=4)
        
        door_lbl = self.font_hud.render("EXIT", True, (17, 17, 27))
        self.screen.blit(door_lbl, (door_x + 6, door_y + 12))

        # --- E. RENDER 2 ENEMIES & A* PATH ---
        for enemy in [self.enemy1, self.enemy2]:
            ex_center = enemy.x * self.tile_size + self.tile_size // 2
            ey_center = enemy.y * self.tile_size + offset_y + self.tile_size // 2
            rad_px = int(enemy.detection_range * self.tile_size)

            st_colors = {"PATROL": (125, 207, 255), "CHASE": (255, 158, 100), "ATTACK": (247, 118, 142)}
            b_col = st_colors.get(enemy.state, (247, 118, 142))

            pygame.draw.circle(self.screen, b_col, (ex_center, ey_center), rad_px, 1)

            if enemy.state == "CHASE" and len(enemy.current_path) > 1:
                pts = [(px * self.tile_size + self.tile_size // 2, py * self.tile_size + offset_y + self.tile_size // 2) for px, py in enemy.current_path]
                for cx, cy in pts:
                    pygame.draw.circle(self.screen, (255, 158, 100), (cx, cy), 4)
                if len(pts) >= 2:
                    pygame.draw.lines(self.screen, (255, 158, 100), False, pts, 3)

            # Monster Body & Horns
            er = self.tile_size // 2 - 6
            pygame.draw.polygon(self.screen, b_col, [(ex_center-er+4, ey_center-er+2), (ex_center-er+10, ey_center-er-6), (ex_center-2, ey_center-er+4)])
            pygame.draw.polygon(self.screen, b_col, [(ex_center+er-4, ey_center-er+2), (ex_center+er-10, ey_center-er-6), (ex_center+2, ey_center-er+4)])
            pygame.draw.circle(self.screen, b_col, (ex_center, ey_center), er)

        # --- F. PLAYER SPRITE (KNIGHT HERO) ---
        px_c = self.player_x * self.tile_size + self.tile_size // 2
        py_c = self.player_y * self.tile_size + offset_y + self.tile_size // 2
        pr = self.tile_size // 2 - 6

        pygame.draw.circle(self.screen, (158, 206, 106), (px_c, py_c), pr + 2, 2)
        pygame.draw.circle(self.screen, (115, 218, 202), (px_c, py_c), pr)
        pygame.draw.rect(self.screen, (192, 202, 245), (px_c - pr + 6, py_c - 4, pr*2 - 12, 8))

        # --- G. WIN / GAME OVER OVERLAY ---
        if self.game_status == "WIN":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((17, 17, 27, 200))
            self.screen.blit(overlay, (0, 0))

            card = pygame.Rect(self.width//2 - 230, self.height//2 - 50, 460, 100)
            pygame.draw.rect(self.screen, (158, 206, 106), card, border_radius=8)
            t1 = self.font_overlay.render("🎉 YOU ESCAPED THE DUNGEON!", True, (17, 17, 27))
            t2 = self.font_hud.render("Tekan 'R' untuk main lagi", True, (31, 35, 53))
            self.screen.blit(t1, t1.get_rect(center=(self.width//2, self.height//2 - 14)))
            self.screen.blit(t2, t2.get_rect(center=(self.width//2, self.height//2 + 18)))

        elif self.game_status == "GAMEOVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((17, 17, 27, 200))
            self.screen.blit(overlay, (0, 0))

            card = pygame.Rect(self.width//2 - 230, self.height//2 - 50, 460, 100)
            pygame.draw.rect(self.screen, (247, 118, 142), card, border_radius=8)
            t1 = self.font_overlay.render("💀 GAME OVER! TERTANGKAP AI!", True, (17, 17, 27))
            t2 = self.font_hud.render("Tekan 'R' untuk mencoba lagi", True, (31, 35, 53))
            self.screen.blit(t1, t1.get_rect(center=(self.width//2, self.height//2 - 14)))
            self.screen.blit(t2, t2.get_rect(center=(self.width//2, self.height//2 + 18)))

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    game = PygameDungeonGame()
    game.run()
