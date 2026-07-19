global.Phaser = {
    Utils: {
        Array: {
            GetRandom: (arr) => arr[0]
        }
    }
};

import GameMap, { LANDMARKS } from './src/map/GameMap.js';

const mockScene = {
    add: {
        rectangle: () => ({ setOrigin: () => {} }),
        sprite: () => ({ setOrigin: () => {}, setDisplaySize: () => {} })
    }
};

const map = new GameMap(mockScene);

for (const lm of LANDMARKS) {
    const spot = map.getLandmarkMissionSpot(lm.name);
    console.log(`Landmark: ${lm.name}, Spot:`, spot);
}
