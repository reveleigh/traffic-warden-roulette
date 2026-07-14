# Traffic Warden Roulette - Phaser 3 Architecture

This document fully decomposes the Pygame version of "Traffic Warden Roulette" into a modern Phaser 3 architecture. The proposed structure uses ES6 JavaScript modules and plain HTML/JS for now, ensuring a smooth transition into a Next.js route in the future.

## 1. Directory Structure

A modular, scene-based structure is highly recommended for Phaser 3.

```text
Phaser Implementation/
├── index.html               # Entry point, hosts the Phaser canvas
├── style.css                # Basic styling to center the game canvas
├── assets/                  # Images, audio, and data (copied from Pygame)
│   ├── images/
│   └── sounds/
└── src/                     # All source code
    ├── main.js              # Phaser config and instantiation
    ├── scenes/
    │   ├── Boot.js          # Preloads loading bar assets, sets up scaling
    │   ├── Preloader.js     # Loads all main game assets (images, audio)
    │   ├── Splash.js        # Title screen and animations
    │   ├── Instructions.js  # Story text and controls
    │   ├── Game.js          # Main gameplay loop, map rendering, entity logic
    │   ├── UI.js            # Overlay HUD (Money, Date, Audacity Bars)
    │   ├── Cutscene.js      # Handles the "Busted" animation
    │   └── Leaderboard.js   # High score display and Name input
    ├── entities/
    │   ├── Player.js        # Player sprite, grid movement, history (undo)
    │   └── Warden.js        # AI sprite, pathfinding, rage mode
    ├── map/
    │   ├── GameMap.js       # Procedural generation logic & tile rendering
    │   └── Pathfinding.js   # A* or BFS logic adapted from Python Graph class
    └── managers/
        ├── MissionManager.js# Generates targets, costs, and risks
        ├── StateManager.js  # Global state (money, date, logic levels)
        └── DBManager.js     # LocalStorage wrapper for high scores
```

## 2. Scene Breakdown

Pygame's single massive `while` loop relying on integer states (`STATE_RUNNING`, `STATE_SPLASH`, etc.) is converted into discrete Phaser Scenes. 

### Boot & Preloader Scenes
- **Purpose**: Phaser separates asset loading from gameplay. 
- **Implementation**: `Preloader.js` will `this.load.image()` and `this.load.audio()` all assets. A progress bar will be drawn using Phaser Graphics.

### Splash & Instructions Scenes
- **Purpose**: Translates `STATE_SPLASH` and `STATE_INSTRUCTIONS`.
- **Implementation**: Uses `Phaser.GameObjects.Text` and tweens for the pulsating title text and the sliding warden animation. Space/Enter key listeners transition to the next scene via `this.scene.start('Game')`.

### Game & UI Scenes
- **Purpose**: Translates `STATE_RUNNING`, `STATE_ACTIVITY`, and `STATE_MISSION_POPUP`.
- **Implementation**: 
  - `Game.js` handles the core grid logic.
  - `UI.js` is launched in parallel (`this.scene.launch('UI')`). It listens to events from `Game.js` to update the HUD (Money, Audacity, Fine bars) and renders the Mission Popups.

### Cutscene Scene
- **Purpose**: Translates `STATE_BUSTED_CUTSCENE`.
- **Implementation**: Pauses `Game.js`, uses Phaser Tweens to slide in the Van and Warden sprites, calculates the fine, applies the guilt logic, and then resumes `Game.js`.

### Leaderboard Scene
- **Purpose**: Translates `STATE_LEADERBOARD` and `STATE_NAME_INPUT`.
- **Implementation**: Uses HTML DOM elements over the canvas for native text input, or Phaser 3's DOM Element support.

## 3. Map & Pathfinding (`GameMap.js` & `Pathfinding.js`)

### Map Generation
- The 20x15 grid generation from `game_map.py` can be directly ported. 
- **Phaser Native**: Instead of blitting rects, `GameMap.js` will generate a 2D array of tile indices and use `this.make.tilemap()` with a `DynamicTilemapLayer`. This gives built-in camera culling and scaling.

### Navigation Graph
- The custom `Graph` and BFS pathfinding will be moved into `Pathfinding.js`.
- It will create a graph using the `TILE_ROAD` indices from the generated tilemap. 

## 4. Game Objects (Entities)

### `Player.js` (Extends `Phaser.GameObjects.Sprite`)
- **Properties**: `gridX`, `gridY`, `history` (array for Undo), `isSafe`.
- **Movement**: Instead of instant teleports, we can use `this.scene.tweens.add()` to smoothly move the sprite from one 40x40 grid tile to the next over ~100ms.
- **Undo**: Popping the last coordinate from the `history` array and tweening back.

### `Warden.js` (Extends `Phaser.GameObjects.Sprite`)
- **Properties**: `path` (array of nodes), `moveInterval`.
- **Logic**: Uses a Phaser `TimerEvent` instead of `pygame.time.set_timer`. Every tick, it polls `Pathfinding.js` for the next node towards the Player and tweens there.
- **Rage Mode**: Speeds up the timer event and changes the pathfinding target to the edges of the grid.
- **Elite Wardens (Ambush)**: `Game.js` will manage a Phaser `Group` of Warden objects during an ambush.

## 5. Managers & Data

### `StateManager.js` (Global Data)
Phaser provides a global data registry (`this.registry`). `StateManager.js` will wrap this to hold:
- `money`, `current_date`
- `reward_level`, `fine_level`
- `guilt_chance`, `guilt_mode_active`

### `MissionManager.js`
Ports the `start_new_mission()` logic from Python. Given a list of available parking spots from `GameMap.js`, it picks a spot, calculates costs and auditing bonuses, and emits a generic event that `UI.js` catches to display the pop-up.

### `DBManager.js` (LocalStorage)
Replacing SQLite (`database.py`):
```javascript
export default class DBManager {
    static getScores() {
        const scores = localStorage.getItem('twr_scores');
        return scores ? JSON.parse(scores) : [];
    }

    static saveScore(name, score) {
        const scores = this.getScores();
        scores.push({ name, score, date_achieved: new Date().toISOString() });
        scores.sort((a, b) => b.score - a.score);
        localStorage.setItem('twr_scores', JSON.stringify(scores.slice(0, 50)));
    }
}
```

## 6. Future-Proofing for Next.js

Since this will eventually be ported to Next.js:
1. **ES6 Modules**: Keeping the code strictly ES6 module based (`import`/`export`) means it will drop neatly into a React/Next.js bundle.
2. **Component Wrapper**: In Next.js, the Phaser game will be mounted inside a `useEffect` hook referencing a `div` ref. Keeping the DOM completely clean inside `index.html` ensures it won't clash with React's DOM management.
3. **Asset Paths**: Use relative paths (`./assets/...`) so Next.js's public folder routing can resolve them easily later.
