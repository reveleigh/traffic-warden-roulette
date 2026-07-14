import { TILE_SIZE } from '../map/GameMap.js';

export default class Player extends Phaser.GameObjects.Sprite {
    constructor(scene, x, y) {
        // x and y are grid coordinates
        super(scene, x * TILE_SIZE + TILE_SIZE / 2, y * TILE_SIZE + 90 + TILE_SIZE / 2, 'player');
        scene.add.existing(this);
        
        this.setOrigin(0.5, 0.5);
        this.setDisplaySize(TILE_SIZE, TILE_SIZE);
        
        this.gridX = x;
        this.gridY = y;
        this.startX = x;
        this.startY = y;
        
        this.history = [];
        this.isSafe = false;
        
        this.offsetY = 90; // MAP_OFFSET_Y
        this.isMoving = false;
    }

    reset() {
        this.gridX = this.startX;
        this.gridY = this.startY;
        this.history = [];
        this.isSafe = false;
        this.updatePosition();
    }

    updatePosition() {
        this.x = this.gridX * TILE_SIZE + TILE_SIZE / 2;
        this.y = this.gridY * TILE_SIZE + this.offsetY + TILE_SIZE / 2;
    }

    move(dx, dy, gameMap) {
        if (this.isMoving) return false;

        this.isSafe = false; // Reset safety

        // Rotation logic matching python
        if (dx === 1) this.setAngle(90);
        else if (dx === -1) this.setAngle(-90);
        else if (dy === -1) this.setAngle(180);
        else if (dy === 1) this.setAngle(0);

        const newX = this.gridX + dx;
        const newY = this.gridY + dy;

        if (gameMap.isRoad(newX, newY)) {
            // Record history
            this.history.push({x: this.gridX, y: this.gridY});
            
            this.gridX = newX;
            this.gridY = newY;
            
            // Smooth movement
            this.isMoving = true;
            this.scene.tweens.add({
                targets: this,
                x: this.gridX * TILE_SIZE + TILE_SIZE / 2,
                y: this.gridY * TILE_SIZE + this.offsetY + TILE_SIZE / 2,
                duration: 100,
                onComplete: () => {
                    this.isMoving = false;
                    this.scene.events.emit('player_moved', this.gridX, this.gridY);
                }
            });
            return true;
        }
        return false;
    }

    undo() {
        if (this.isMoving || this.history.length === 0) return;
        
        const prev = this.history.pop();
        this.gridX = prev.x;
        this.gridY = prev.y;
        
        this.isMoving = true;
        this.scene.tweens.add({
            targets: this,
            x: this.gridX * TILE_SIZE + TILE_SIZE / 2,
            y: this.gridY * TILE_SIZE + this.offsetY + TILE_SIZE / 2,
            duration: 100,
            onComplete: () => {
                this.isMoving = false;
                console.log(`Undo: Moved back to ${this.gridX}, ${this.gridY}`);
            }
        });
    }
}
