import { TILE_SIZE, MAP_WIDTH, MAP_HEIGHT } from '../map/GameMap.js';

export default class Warden extends Phaser.GameObjects.Sprite {
    constructor(scene, x, y, pathfinder) {
        super(scene, x * TILE_SIZE + TILE_SIZE / 2, y * TILE_SIZE + 90 + TILE_SIZE / 2, 'warden');
        scene.add.existing(this);
        
        this.setOrigin(0.5, 0.5);
        this.setDisplaySize(TILE_SIZE, TILE_SIZE);
        
        this.gridX = x;
        this.gridY = y;
        this.startX = x;
        this.startY = y;
        
        this.pathfinder = pathfinder;
        this.offsetY = 90;
        this.isMoving = false;
    }

    reset() {
        this.gridX = this.startX;
        this.gridY = this.startY;
        this.updatePosition();
    }

    updatePosition() {
        this.x = this.gridX * TILE_SIZE + TILE_SIZE / 2;
        this.y = this.gridY * TILE_SIZE + this.offsetY + TILE_SIZE / 2;
    }

    updateLogic(targetX, targetY) {
        if (this.isMoving) return;

        const path = this.pathfinder.findPath(this.gridX, this.gridY, targetX, targetY);
        
        if (path && path.length > 1) {
            const nextNode = path[1];
            this.moveTo(nextNode.x, nextNode.y);
        } else if (this.gridX !== targetX || this.gridY !== targetY) {
            // Stuck fallback
            const neighbors = this.pathfinder.getNeighbors(this.gridX, this.gridY);
            if (neighbors.length > 0) {
                const nextNode = Phaser.Utils.Array.GetRandom(neighbors);
                this.moveTo(nextNode.x, nextNode.y);
            }
        }
    }

    updateRageLogic(gameMap) {
        if (this.isMoving) return;

        const w = MAP_WIDTH;
        const h = MAP_HEIGHT;

        const onEdge = (this.gridX === 0 || this.gridX === w - 1 || this.gridY === 0 || this.gridY === h - 1);

        if (onEdge) {
            // Move clockwise
            let nx = this.gridX, ny = this.gridY;
            if (this.gridY === 0 && this.gridX < w - 1) nx += 1;
            else if (this.gridX === w - 1 && this.gridY < h - 1) ny += 1;
            else if (this.gridY === h - 1 && this.gridX > 0) nx -= 1;
            else if (this.gridX === 0 && this.gridY > 0) ny -= 1;
            
            this.moveTo(nx, ny);
        } else {
            // Pathfind to nearest edge
            const candidates = [
                {x: 0, y: this.gridY}, {x: w-1, y: this.gridY},
                {x: this.gridX, y: 0}, {x: this.gridX, y: h-1}
            ];

            let target = null;
            let minDist = Infinity;

            for (const c of candidates) {
                if (gameMap.isRoad(c.x, c.y)) {
                    const dist = Math.abs(this.gridX - c.x) + Math.abs(this.gridY - c.y);
                    if (dist < minDist) {
                        minDist = dist;
                        target = c;
                    }
                }
            }

            if (target) {
                this.updateLogic(target.x, target.y);
            }
        }
    }

    moveTo(nx, ny) {
        this.gridX = nx;
        this.gridY = ny;
        this.isMoving = true;
        
        // Match duration to the interval set in GameScene
        this.scene.tweens.add({
            targets: this,
            x: this.gridX * TILE_SIZE + TILE_SIZE / 2,
            y: this.gridY * TILE_SIZE + this.offsetY + TILE_SIZE / 2,
            duration: this.scene.wardenInterval ? this.scene.wardenInterval * 0.8 : 100, // Slightly faster than interval
            onComplete: () => {
                if (!this.scene || !this.active) return;
                this.isMoving = false;
                this.scene.events.emit('warden_moved');
            }
        });
    }
}
