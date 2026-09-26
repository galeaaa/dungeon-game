using System;
using System.Collections.Generic;

namespace DungeonGame
{
    // Node untuk Grid Dungeon
    public class Node
    {
        public int x;
        public int y;
        public bool isWalkable;
        public float gCost;
        public float hCost;
        public float fCost => gCost + hCost;
        public Node parent;

        public Node(int x, int y, bool isWalkable = true)
        {
            this.x = x;
            this.y = y;
            this.isWalkable = isWalkable;
        }
    }

    // State untuk Finite State Machine (FSM) Enemy
    public enum EnemyState
    {
        Idle,
        Chase,
        Attack
    }

    public class EnemyAI
    {
        public int x;
        public int y;
        public float detectionRange;
        public float attackRange;
        public EnemyState currentState;

        public EnemyAI(int startX, int startY, float detectionRange = 7.0f, float attackRange = 1.5f)
        {
            this.x = startX;
            this.y = startY;
            this.detectionRange = detectionRange;
            this.attackRange = attackRange;
            this.currentState = EnemyState.Idle;
        }

        // 1. Algoritma Deteksi Jangkauan (Euclidean Distance)
        public float CalculateDistance(int targetX, int targetY)
        {
            int dx = targetX - this.x;
            int dy = targetY - this.y;
            return (float)Math.Sqrt(dx * dx + dy * dy);
        }

        // 2. State Machine Update Loop
        public void UpdateAI(int playerX, int playerY, Node[,] gridMap, int mapWidth, int mapHeight)
        {
            float distanceToPlayer = CalculateDistance(playerX, playerY);

            // Deteksi Player & Penentuan Jangkauan
            if (distanceToPlayer > detectionRange)
            {
                currentState = EnemyState.Idle;
                Console.WriteLine($"[State: IDLE] Player di luar jangkauan deteksi ({distanceToPlayer:F2} unit).");
            }
            else if (distanceToPlayer <= attackRange)
            {
                currentState = EnemyState.Attack;
                Console.WriteLine($"[State: ATTACK] Enemy menyerang Player! (Jarak: {distanceToPlayer:F2} unit).");
            }
            else
            {
                currentState = EnemyState.Chase;
                Console.WriteLine($"[State: CHASE] Player terdeteksi! Mencari jalur & mengejar...");

                // 3. Algoritma Pathfinding (A*)
                List<Node> path = FindPathAStar(this.x, this.y, playerX, playerY, gridMap, mapWidth, mapHeight);

                if (path != null && path.Count > 1)
                {
                    // Moving to next node on path
                    Node nextStep = path[1];
                    this.x = nextStep.x;
                    this.y = nextStep.y;
                    Console.WriteLine($"Enemy bergerak ke node ({this.x}, {this.y}).");
                }
            }
        }

        // 3. Algoritma A* (A-Star) Pathfinding
        private List<Node> FindPathAStar(int startX, int startY, int targetX, int targetY, Node[,] gridMap, int mapWidth, int mapHeight)
        {
            Node startNode = gridMap[startY, startX];
            Node targetNode = gridMap[targetY, targetX];

            List<Node> openSet = new List<Node>();
            HashSet<Node> closedSet = new HashSet<Node>();

            // Reset cost
            for (int r = 0; r < mapHeight; r++)
            {
                for (int c = 0; c < mapWidth; c++)
                {
                    gridMap[r, c].gCost = float.MaxValue;
                    gridMap[r, c].parent = null;
                }
            }

            startNode.gCost = 0;
            startNode.hCost = GetHeuristicManhattan(startNode, targetNode);
            openSet.Add(startNode);

            while (openSet.Count > 0)
            {
                // Ambil node dengan fCost terendah
                Node currentNode = openSet[0];
                for (int i = 1; i < openSet.Count; i++)
                {
                    if (openSet[i].fCost < currentNode.fCost || 
                       (openSet[i].fCost == currentNode.fCost && openSet[i].hCost < currentNode.hCost))
                    {
                        currentNode = openSet[i];
                    }
                }

                openSet.Remove(currentNode);
                closedSet.Add(currentNode);

                if (currentNode == targetNode)
                {
                    return ReconstructPath(startNode, targetNode);
                }

                foreach (Node neighbor in GetNeighbors(currentNode, gridMap, mapWidth, mapHeight))
                {
                    if (!neighbor.isWalkable || closedSet.Contains(neighbor))
                        continue;

                    float newMovementCost = currentNode.gCost + 1.0f;
                    if (newMovementCost < neighbor.gCost)
                    {
                        neighbor.gCost = newMovementCost;
                        neighbor.hCost = GetHeuristicManhattan(neighbor, targetNode);
                        neighbor.parent = currentNode;

                        if (!openSet.Contains(neighbor))
                            openSet.Add(neighbor);
                    }
                }
            }

            return null; // Jalur tidak ditemukan
        }

        private float GetHeuristicManhattan(Node nodeA, Node nodeB)
        {
            return Math.Abs(nodeA.x - nodeB.x) + Math.Abs(nodeA.y - nodeB.y);
        }

        private List<Node> GetNeighbors(Node node, Node[,] gridMap, int mapWidth, int mapHeight)
        {
            List<Node> neighbors = new List<Node>();
            int[] dx = { 0, 0, -1, 1 };
            int[] dy = { -1, 1, 0, 0 };

            for (int i = 0; i < 4; i++)
            {
                int checkX = node.x + dx[i];
                int checkY = node.y + dy[i];

                if (checkX >= 0 && checkX < mapWidth && checkY >= 0 && checkY < mapHeight)
                {
                    neighbors.Add(gridMap[checkY, checkX]);
                }
            }

            return neighbors;
        }

        private List<Node> ReconstructPath(Node startNode, Node targetNode)
        {
            List<Node> path = new List<Node>();
            Node current = targetNode;

            while (current != null)
            {
                path.Add(current);
                current = current.parent;
            }

            path.Reverse();
            return path;
        }
    }
}
