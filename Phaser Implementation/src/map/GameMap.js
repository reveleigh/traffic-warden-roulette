// Tile Types
export const TILE_EMPTY = 0;
export const TILE_ROAD = 1;
export const TILE_BUILDING = 2;
export const TILE_SHOP = 3;
export const TILE_PARK = 4;

// Specific Shop Types
export const TILE_SHOP_BAKERY = 10;
export const TILE_SHOP_CLOTHING = 11;
export const TILE_SHOP_TECH = 12;
export const TILE_SHOP_CAFE = 13;

// Landmarks
export const TILE_POOL = 24;
export const TILE_MUSEUM = 25;
export const TILE_SUPERMARKET = 26;
export const TILE_CHURCH = 27;
export const TILE_SCHOOL = 28;

// Large Structures
export const TILE_OFFICE_LARGE = 20;
export const TILE_HOSPITAL = 21;
export const TILE_PARK_LARGE = 22;
export const TILE_AMPITHEATRE = 23;
export const TILE_OCCUPIED = 99; // Invisible tile for 2x2s

export const ALL_SHOPS = [TILE_SHOP, TILE_SHOP_BAKERY, TILE_SHOP_CLOTHING, TILE_SHOP_TECH, TILE_SHOP_CAFE];
export const ALL_BUILDINGS = [TILE_BUILDING, TILE_OFFICE_LARGE, TILE_HOSPITAL, TILE_PARK_LARGE, TILE_AMPITHEATRE, TILE_OCCUPIED, 
                              TILE_POOL, TILE_MUSEUM, TILE_SUPERMARKET, TILE_CHURCH, TILE_SCHOOL];

// Map Settings
export const MAP_WIDTH = 20;
export const MAP_HEIGHT = 15;
export const TILE_SIZE = 40;

export const LANDMARKS = [
    { name: "Roman Amphitheatre", x: 15, y: 7, w: 3, h: 3, tile: TILE_AMPITHEATRE, imageKey: 'ampitheatre', tasks: ["Meet Tour Group", "Photo Opportunity", "Historical Walk", "School Trip Help"] },
    { name: "Open Air Pool", x: 3, y: 11, w: 2, h: 2, tile: TILE_POOL, imageKey: 'swimming_pool', tasks: ["Swimming Lesson (Fenella)", "Morning Laps (Rupert)", "Lifeguard Chat", "Collect Swimming Kit"] },
    { name: "Corinium Museum", x: 7, y: 3, w: 2, h: 2, tile: TILE_MUSEUM, imageKey: 'museum', tasks: ["View Roman Mosaic", "Donate Old Coin", "Meet Curator", "Kids Workshop"] },
    { name: "Tesco Extra", x: 3, y: 3, w: 2, h: 2, tile: TILE_SUPERMARKET, imageKey: 'supermarket', tasks: ["Weekly Big Shop", "Buy Clementine's Wine", "Emergency Nappy Run", "Return Trolley"] },
    { name: "Cirencester Church", x: 11, y: 3, w: 2, h: 2, tile: TILE_CHURCH, imageKey: 'church', tasks: ["Bell Ringing Practice", "Flower Arranging", "Meet Vicar", "Choir Practice"] },
    { name: "Deer Park School", x: 15, y: 3, w: 2, h: 2, tile: TILE_SCHOOL, imageKey: 'school', tasks: ["Pick up Ivor", "Drop off Fenella", "Parents Evening", "Sports Day Event", "School Play"] },
    { name: "St Micheals Hoard Mgt", x: 7, y: 11, w: 2, h: 2, tile: TILE_OFFICE_LARGE, imageKey: 'building_large_office', tasks: ["Count Gold Bars", "Lease Sign-off", "Hide Assets", "Investment Meeting", "Hoard Check"] },
    { name: "Minor Injuries Unit", x: 11, y: 7, w: 2, h: 2, tile: TILE_HOSPITAL, imageKey: 'hospital', tasks: ["Rugby Injury (Ivor)", "X-Ray Appointment", "Stitched Finger", "Tetanus Shot", "Visit Granny"] }
];

export default class GameMap {
    constructor(scene) {
        this.scene = scene;
        this.width = MAP_WIDTH;
        this.height = MAP_HEIGHT;
        this.grid = [];
        this.generateMap();
    }

    generateMap() {
        // 1. Initialise empty grid
        this.grid = Array(this.height).fill(null).map(() => Array(this.width).fill(TILE_EMPTY));

        // 2. Generate Roads (Border)
        for (let x = 0; x < this.width; x++) {
            this.grid[0][x] = TILE_ROAD;
            this.grid[this.height - 1][x] = TILE_ROAD;
        }
        for (let y = 0; y < this.height; y++) {
            this.grid[y][0] = TILE_ROAD;
            this.grid[y][this.width - 1] = TILE_ROAD;
        }

        // Internal Roads
        for (let x = 2; x < this.width - 2; x += 4) {
            for (let y = 0; y < this.height; y++) this.grid[y][x] = TILE_ROAD;
        }
        for (let y = 2; y < this.height - 2; y += 4) {
            for (let x = 0; x < this.width; x++) this.grid[y][x] = TILE_ROAD;
        }

        // 3. Place Fixed Landmarks
        for (const lm of LANDMARKS) {
            const {x, y, w, h, tile} = lm;
            if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
                this.grid[y][x] = tile;
                // Occupied tiles
                for (let r = y; r < y + h; r++) {
                    for (let c = x; c < x + w; c++) {
                        if (r >= 0 && r < this.height && c >= 0 && c < this.width) {
                            if (r === y && c === x) continue;
                            this.grid[r][c] = TILE_OCCUPIED;
                        }
                    }
                }
            }
        }

        // 4. Fill Empty Spots
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                if (this.grid[y][x] === TILE_EMPTY) {
                    const dice = Math.random();
                    if (dice < 0.6) this.grid[y][x] = TILE_BUILDING;
                    else if (dice < 0.8) {
                        const shops = [TILE_SHOP_BAKERY, TILE_SHOP_CLOTHING, TILE_SHOP_TECH, TILE_SHOP_CAFE];
                        this.grid[y][x] = shops[Math.floor(Math.random() * shops.length)];
                    }
                    else this.grid[y][x] = TILE_PARK;
                }
            }
        }
    }

    render(offsetY = 90) {
        // Draw green background
        this.scene.add.rectangle(0, offsetY, this.width * TILE_SIZE, this.height * TILE_SIZE, 0x228B22)
            .setOrigin(0, 0);

        // Map Tile constants to image keys
        const imgMap = {
            [TILE_ROAD]: 'road',
            [TILE_BUILDING]: 'building',
            [TILE_SHOP]: 'shop',
            [TILE_PARK]: 'park',
            [TILE_SHOP_BAKERY]: 'shop_bakery',
            [TILE_SHOP_CLOTHING]: 'shop_clothing',
            [TILE_SHOP_TECH]: 'shop_tech',
            [TILE_SHOP_CAFE]: 'shop_cafe',
            [TILE_OFFICE_LARGE]: 'building_large_office',
            [TILE_HOSPITAL]: 'hospital',
            [TILE_PARK_LARGE]: 'park_large',
            [TILE_AMPITHEATRE]: 'ampitheatre',
            [TILE_POOL]: 'swimming_pool',
            [TILE_MUSEUM]: 'museum',
            [TILE_SUPERMARKET]: 'supermarket',
            [TILE_CHURCH]: 'church',
            [TILE_SCHOOL]: 'school'
        };

        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                const tile = this.grid[y][x];
                if (tile === TILE_EMPTY || tile === TILE_OCCUPIED) continue;
                
                const key = imgMap[tile];
                if (key) {
                    // Calculate size based on landmark or standard tile
                    let displayW = TILE_SIZE;
                    let displayH = TILE_SIZE;
                    
                    const lm = LANDMARKS.find(l => l.tile === tile);
                    if (lm) {
                        displayW = lm.w * TILE_SIZE;
                        displayH = lm.h * TILE_SIZE;
                    } else if (tile === TILE_OFFICE_LARGE || tile === TILE_HOSPITAL || tile === TILE_PARK_LARGE) {
                        displayW = 80;
                        displayH = 80;
                    }

                    const sprite = this.scene.add.sprite(x * TILE_SIZE, y * TILE_SIZE + offsetY, key);
                    sprite.setOrigin(0, 0);
                    sprite.setDisplaySize(displayW, displayH);
                }
            }
        }
    }

    isRoad(x, y) {
        if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
            return this.grid[y][x] === TILE_ROAD;
        }
        return false;
    }

    getParkingSpots() {
        let spots = [];
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                if (this.grid[y][x] === TILE_ROAD) {
                    let hasBuilding = false;
                    const dirs = [[-1,0], [1,0], [0,-1], [0,1]];
                    for (const [dy, dx] of dirs) {
                        const ny = y + dy, nx = x + dx;
                        if (ny >= 0 && ny < this.height && nx >= 0 && nx < this.width) {
                            const t = this.grid[ny][nx];
                            if (ALL_BUILDINGS.includes(t) || ALL_SHOPS.includes(t)) {
                                hasBuilding = true;
                                break;
                            }
                        }
                    }
                    if (hasBuilding) spots.push({x, y});
                }
            }
        }
        return spots;
    }

    getLandmarkMissionSpot(landmarkName) {
        const target = LANDMARKS.find(lm => lm.name === landmarkName);
        if (!target) return null;

        const {x: lx, y: ly, w: lw, h: lh} = target;
        let perimeter = [];

        for (let r = ly - 1; r <= ly + lh; r++) {
            for (let c = lx - 1; c <= lx + lw; c++) {
                // Check if on border
                if (r < ly || r >= ly + lh || c < lx || c >= lx + lw) {
                    if (r >= 0 && r < this.height && c >= 0 && c < this.width) {
                        if (this.grid[r][c] === TILE_ROAD) {
                            perimeter.push({x: c, y: r});
                        }
                    }
                }
            }
        }

        return perimeter.length > 0 ? Phaser.Utils.Array.GetRandom(perimeter) : null;
    }

    findPath(startX, startY, targetX, targetY) {
        if (startX === targetX && startY === targetY) return [];

        const queue = [{x: startX, y: startY, path: []}];
        const visited = new Set([`${startX},${startY}`]);
        const dirs = [[-1, 0], [1, 0], [0, -1], [0, 1]];

        while (queue.length > 0) {
            const current = queue.shift();

            for (const [dx, dy] of dirs) {
                const nx = current.x + dx;
                const ny = current.y + dy;

                if (nx === targetX && ny === targetY) {
                    return [...current.path, {dx, dy}];
                }

                if (this.isRoad(nx, ny) && !visited.has(`${nx},${ny}`)) {
                    visited.add(`${nx},${ny}`);
                    queue.push({
                        x: nx,
                        y: ny,
                        path: [...current.path, {dx, dy}]
                    });
                }
            }
        }
        return [];
    }
}
