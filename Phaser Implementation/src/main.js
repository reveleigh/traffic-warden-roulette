// Phaser is loaded globally via CDN in index.html

import Boot from './scenes/Boot.js';
import Preloader from './scenes/Preloader.js';
import Splash from './scenes/Splash.js';
import Instructions from './scenes/Instructions.js';
import Game from './scenes/Game.js';
import UI from './scenes/UI.js';
import Cutscene from './scenes/Cutscene.js';
import Leaderboard from './scenes/Leaderboard.js';

const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 720,
    parent: 'game-container',
    backgroundColor: '#1e1e28',
    scene: [Boot, Preloader, Splash, Instructions, Game, UI, Cutscene, Leaderboard],
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH
    }
};

const game = new Phaser.Game(config);
