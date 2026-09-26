import math
import heapq
import time
import os

class Node:
    def __init__(self, x: int, y: int, walkable: bool = True):
        self.x = x
        self.y = y
        self.walkable = walkable
        self.g = float('inf')  # Cost from start to current node
        self.h = 0.0           # Estimated cost from current node to end
        self.f = float('inf')  # Total cost (g + h)
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


class DungeonGrid:
    def __init__(self, width: int, height: int, layout: list[str] = None):
        self.width = width
        self.height = height
        self.nodes = []

        if layout:
            self.height = len(layout)
            self.width = len(layout[0])
            for y in range(self.height):
                row = []
                for x in range(self.width):
                    is_walkable = layout[y][x] != '#'
                    row.append(Node(x, y, is_walkable))
                self.nodes.append(row)
        else:
            for y in range(height):
                row = []
                for x in range(width):
                    row.append(Node(x, y, True))
                self.nodes.append(row)

    def get_node(self, x: int, y: int) -> Node:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.nodes[y][x]
        return None

    def get_neighbors(self, node: Node) -> list[Node]:
        neighbors = []
        # 4-directional movement (Up, Down, Left, Right)
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in directions:
            nx, ny = node.x + dx, node.y + dy
            neighbor = self.get_node(nx, ny)
            if neighbor and neighbor.walkable:
                neighbors.append(neighbor)
        return neighbors


def heuristic_manhattan(node_a: Node, node_b: Node) -> float:
    return abs(node_a.x - node_b.x) + abs(node_a.y - node_b.y)


def heuristic_euclidean(node_a: Node, node_b: Node) -> float:
    return math.sqrt((node_a.x - node_b.x) ** 2 + (node_a.y - node_b.y) ** 2)


def astar_pathfinding(grid: DungeonGrid, start_pos: tuple[int, int], target_pos: tuple[int, int]) -> list[tuple[int, int]]:
    """
    Algoritma A* Pathfinding untuk menemukan jalur terpendek dari start_pos ke target_pos.
    """
    # Reset node costs
    for y in range(grid.height):
        for x in range(grid.width):
            n = grid.nodes[y][x]
            n.g = float('inf')
            n.f = float('inf')
            n.parent = None

    start_node = grid.get_node(*start_pos)
    target_node = grid.get_node(*target_pos)

    if not start_node or not target_node or not target_node.walkable:
        return []

    start_node.g = 0
    start_node.h = heuristic_manhattan(start_node, target_node)
    start_node.f = start_node.g + start_node.h

    open_set = []
    heapq.heappush(open_set, (start_node.f, start_node))
    open_set_hash = {start_node}
    closed_set = set()

    while open_set:
        _, current = heapq.heappop(open_set)
        open_set_hash.discard(current)

        if current == target_node:
            # Reconstruct path
            path = []
            curr = current
            while curr:
                path.append((curr.x, curr.y))
                curr = curr.parent
            path.reverse()
            return path

        closed_set.add(current)

        for neighbor in grid.get_neighbors(current):
            if neighbor in closed_set:
                continue

            tentative_g = current.g + 1  # Cost antar node bertetangga = 1

            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = tentative_g
                neighbor.h = heuristic_manhattan(neighbor, target_node)
                neighbor.f = neighbor.g + neighbor.h

                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (neighbor.f, neighbor))
                    open_set_hash.add(neighbor)

    return []  # Path tidak ditemukan


class EnemyAI:
    def __init__(self, x: int, y: int, detection_range: float = 7.0, attack_range: float = 1.5):
        self.x = x
        self.y = y
        self.detection_range = detection_range
        self.attack_range = attack_range
        self.state = "IDLE"  # IDLE, CHASE, ATTACK

    def calculate_distance_to_player(self, player_x: int, player_y: int) -> float:
        """
        Menghitung jarak Euclidean dari Enemy ke Player.
        """
        return math.sqrt((self.x - player_x) ** 2 + (self.y - player_y) ** 2)

    def update(self, player_x: int, player_y: int, grid: DungeonGrid) -> str:
        """
        FSM update loop:
        1. Hitung Jarak ke Player
        2. Cek apakah Player dalam Detection Range
        3. Jika ya, tentukan apakah dalam Attack Range atau Chase Range
        4. Jalankan A* Pathfinding jika Chase
        """
        distance = self.calculate_distance_to_player(player_x, player_y)

        # 1. State Decision (Deteksi & Jangkauan)
        if distance > self.detection_range:
            self.state = "IDLE"
            message = f"Enemy IDLE. Player out of detection range (Distance: {distance:.2f})"
        elif distance <= self.attack_range:
            self.state = "ATTACK"
            message = f"Enemy ATTACKING Player! (Distance: {distance:.2f})"
        else:
            self.state = "CHASE"
            # 2. Pathfinding ke Player
            path = astar_pathfinding(grid, (self.x, self.y), (player_x, player_y))
            if len(path) > 1:
                # Bergerak 1 langkah mengikuti jalur (path[0] adalah posisi saat ini, path[1] adalah langkah berikutnya)
                next_pos = path[1]
                self.x, self.y = next_pos
                message = f"Enemy CHASING Player. Moved to {next_pos}. Path remaining: {len(path)-1} steps."
            else:
                message = f"Enemy CHASING Player, but no path found!"

        return message


def render_dungeon(grid: DungeonGrid, player_pos: tuple[int, int], enemy_pos: tuple[int, int], path: list[tuple[int, int]] = None):
    grid_display = []
    path_set = set(path) if path else set()

    for y in range(grid.height):
        row_str = ""
        for x in range(grid.width):
            pos = (x, y)
            if pos == enemy_pos:
                row_str += " E "  # Enemy
            elif pos == player_pos:
                row_str += " P "  # Player
            elif pos in path_set:
                row_str += " * "  # Path node
            elif not grid.get_node(x, y).walkable:
                row_str += "###"  # Wall
            else:
                row_str += " . "  # Empty floor
        grid_display.append(row_str)

    return "\n".join(grid_display)


def main():
    # Peta Dungeon (15x9)
    # '#' = Dinding (Obstacle), '.' = Area Kosong
    dungeon_map = [
        "###############",
        "#.......#.....#",
        "#..###..#..#..#",
        "#....#.....#..#",
        "#..#.#######..#",
        "#..#..........#",
        "#..#######....#",
        "#.............#",
        "###############"
    ]

    grid = DungeonGrid(0, 0, dungeon_map)

    # Posisi Awal Player dan Enemy
    player_x, player_y = 12, 7
    enemy = EnemyAI(x=1, y=1, detection_range=20.0, attack_range=1.5)

    print("=== SIMULASI AI ENEMY DI DUNGEON ===")
    print("Legend: P = Player, E = Enemy, * = Path A*, ### = Wall, . = Floor\n")

    step = 0
    while True:
        step += 1
        path = astar_pathfinding(grid, (enemy.x, enemy.y), (player_x, player_y))
        
        print(f"--- STEP {step} ---")
        print(render_dungeon(grid, (player_x, player_y), (enemy.x, enemy.y), path))
        
        status = enemy.update(player_x, player_y, grid)
        print(f"Status: {status}\n")

        if enemy.state == "ATTACK" or step >= 25:
            break

        time.sleep(0.1)

if __name__ == "__main__":
    main()
