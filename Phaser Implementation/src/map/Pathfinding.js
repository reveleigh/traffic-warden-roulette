import { TILE_ROAD, MAP_WIDTH, MAP_HEIGHT } from './GameMap.js';

export default class Pathfinding {
    constructor(gameMap) {
        this.gameMap = gameMap;
    }

    // Standard BFS Pathfinding matching python Graph behavior
    findPath(startX, startY, targetX, targetY) {
        if (startX === targetX && startY === targetY) return [{x: startX, y: startY}];

        const queue = [[{x: startX, y: startY}]];
        const visited = new Set();
        visited.add(`${startX},${startY}`);

        const dirs = [[0, -1], [0, 1], [-1, 0], [1, 0]]; // Up, Down, Left, Right

        while (queue.length > 0) {
            const path = queue.shift();
            const node = path[path.length - 1];

            if (node.x === targetX && node.y === targetY) {
                return path;
            }

            for (const [dx, dy] of dirs) {
                const nx = node.x + dx;
                const ny = node.y + dy;

                if (nx >= 0 && nx < MAP_WIDTH && ny >= 0 && ny < MAP_HEIGHT) {
                    // Is road
                    if (this.gameMap.grid[ny][nx] === TILE_ROAD) {
                        const key = `${nx},${ny}`;
                        if (!visited.has(key)) {
                            visited.add(key);
                            const newPath = [...path, {x: nx, y: ny}];
                            queue.push(newPath);
                        }
                    }
                }
            }
        }
        return null; // No path
    }

    getNeighbors(x, y) {
        const neighbors = [];
        const dirs = [[0, -1], [0, 1], [-1, 0], [1, 0]];
        for (const [dx, dy] of dirs) {
            const nx = x + dx;
            const ny = y + dy;
            if (nx >= 0 && nx < MAP_WIDTH && ny >= 0 && ny < MAP_HEIGHT) {
                if (this.gameMap.grid[ny][nx] === TILE_ROAD) {
                    neighbors.push({x: nx, y: ny});
                }
            }
        }
        return neighbors;
    }
}
