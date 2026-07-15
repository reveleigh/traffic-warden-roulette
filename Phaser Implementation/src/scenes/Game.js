import GameMap from '../map/GameMap.js';
import Pathfinding from '../map/Pathfinding.js';
import Player from '../entities/Player.js';
import Warden from '../entities/Warden.js';
import StateManager from '../managers/StateManager.js';
import MissionManager from '../managers/MissionManager.js';

export default class Game extends Phaser.Scene {
    constructor() {
        super('Game');
    }

    create() {
        // Init Managers
        this.stateManager = new StateManager(this);
        this.stateManager.init(); // Reset to start
        
        this.gameMap = new GameMap(this);
        this.pathfinder = new Pathfinding(this.gameMap);
        this.missionManager = new MissionManager(this, this.stateManager, this.gameMap);

        // Music
        this.sound.stopAll();
        this.sound.play('music_bg', { loop: true });

        // Render Map
        this.gameMap.render();

        // Target Highlight Graphics
        this.targetHighlight = this.add.rectangle(0, 0, 40, 40, 0x000000, 0)
            .setStrokeStyle(4, 0xffd700)
            .setOrigin(0, 0)
            .setDepth(10);

        // Entities
        this.player = new Player(this, 0, 0).setDepth(20);
        this.warden = new Warden(this, 19, 14, this.pathfinder).setDepth(20);
        this.eliteWardens = [];

        // Game State Variables Local to Scene
        this.isActivityRunning = false;
        this.isMissionPopupOpen = false;
        this.distractionTarget = null;
        
        // Timers
        this.wardenInterval = 400;
        this.startWardenTimer();
        
        this.dateTimer = this.time.addEvent({
            delay: 250,
            loop: true,
            callback: this.advanceDate,
            callbackScope: this
        });

        // Launch UI overlay
        this.scene.launch('UI', { gameScene: this, state: this.stateManager, mission: this.missionManager });

        // Input
        this.cursors = this.input.keyboard.createCursorKeys();
        this.input.keyboard.on('keydown-Z', () => this.player.undo());
        this.input.keyboard.on('keydown-ESC', () => {
            this.scene.stop('UI');
            this.scene.start('Splash');
        });

        // Event Listeners
        this.events.on('player_moved', this.checkArrival, this);
        this.events.on('warden_moved', this.checkCollision, this);
        this.events.on('mission_choice', this.handleMissionChoice, this);

        // Start first mission
        this.startNewMission();
    }

    startNewMission() {
        this.distractionTarget = null;
        const target = this.missionManager.generateMission();
        
        this.targetHighlight.setPosition(target.x * 40, target.y * 40 + 90);
        this.targetHighlight.setVisible(true);

        this.events.emit('update_ui_mission');
    }

    advanceDate() {
        if (this.isMissionPopupOpen || this.isActivityRunning) return;
        
        this.stateManager.advanceDay();
        this.events.emit('update_ui_hud');

        if (this.stateManager.isYearEnd) {
            this.scene.stop('UI');
            this.scene.start('GameOver'); // Wait, there is no GameOver scene, it's Leaderboard handles Name Input.
            // Let's redirect to Leaderboard but maybe pass state?
            this.scene.start('Leaderboard', { money: this.stateManager.money, isGameOver: true });
        }
    }

    startWardenTimer() {
        if (this.wardenTimer) this.wardenTimer.remove();
        this.wardenTimer = this.time.addEvent({
            delay: this.wardenInterval,
            loop: true,
            callback: this.moveWardens,
            callbackScope: this
        });
    }

    moveWardens() {
        if (this.isMissionPopupOpen) return;

        if (this.stateManager.rewardLevel >= 6) {
            this.warden.updateRageLogic(this.gameMap);
        } else {
            let tx = this.player.gridX;
            let ty = this.player.gridY;

            if (this.isActivityRunning && this.distractionTarget) {
                tx = this.distractionTarget.x;
                ty = this.distractionTarget.y;
            }
            this.warden.updateLogic(tx, ty);
        }

        // Elite Wardens (Ambush)
        if (this.stateManager.ambushActive && this.eliteWardens.length > 0) {
            for (const ew of this.eliteWardens) {
                ew.updateLogic(this.player.gridX, this.player.gridY);
            }
        }
    }

    update() {
        if (this.isMissionPopupOpen) return;

        // Player Movement Logic
        let dx = 0, dy = 0;
        if (Phaser.Input.Keyboard.JustDown(this.cursors.left)) dx = -1;
        else if (Phaser.Input.Keyboard.JustDown(this.cursors.right)) dx = 1;
        else if (Phaser.Input.Keyboard.JustDown(this.cursors.up)) dy = -1;
        else if (Phaser.Input.Keyboard.JustDown(this.cursors.down)) dy = 1;

        if (dx !== 0 || dy !== 0) {
            this.player.move(dx, dy, this.gameMap);
        }
    }

    checkArrival(px, py) {
        if (px === this.missionManager.currentSpot.x && py === this.missionManager.currentSpot.y) {
            this.sound.play('sfx_blip');
            this.isMissionPopupOpen = true;
            this.events.emit('show_mission_popup');
        }
    }

    handleMissionChoice(choice) {
        this.isMissionPopupOpen = false;

        if (choice === 'pay') {
            this.stateManager.money -= this.missionManager.missionCost;
            this.player.isSafe = true;
            this.sound.play('sfx_pay');

            // Reset Rage?
            if (this.stateManager.rewardLevel >= 6) {
                this.wardenInterval = Math.max(50, this.wardenInterval * 0.8);
                this.startWardenTimer();
            }
            this.stateManager.rewardLevel = 0;
            this.events.emit('update_ui_hud');
            
            // Distract warden
            this.distractWarden();
            this.startActivity();

        } else if (choice === 'risk') {
            this.player.isSafe = false;
            this.sound.play('sfx_risk');

            // Ambush Check
            const day = this.stateManager.currentDate.getDay();
            if (this.missionManager.locName.toLowerCase().includes('st micheals') && day > 0 && day < 6) {
                this.stateManager.ambushActive = true;
                this.spawnEliteWardens();
                this.events.emit('ui_message', "AMBUSH! RUN!");
            }
            this.startActivity();
        }
    }

    startActivity() {
        this.isActivityRunning = true;
        this.events.emit('start_activity_bar', this.missionManager.durationTicks, this.player.isSafe);

        // Timer for activity completion
        this.activityTimer = this.time.addEvent({
            delay: this.missionManager.durationTicks * 16.66, // Roughly 60fps equivalent
            callback: () => this.completeActivity(),
            callbackScope: this
        });

        // Check if Warden is already on the player
        this.checkCollision();
    }

    cancelActivity() {
        if (this.activityTimer) {
            this.activityTimer.remove();
            this.activityTimer = null;
        }
        
        this.isActivityRunning = false;
        
        if (this.stateManager.ambushActive) {
            this.stateManager.ambushActive = false;
            this.eliteWardens.forEach(w => w.destroy());
            this.eliteWardens = [];
        }

        this.player.isSafe = false;

        // Hide UI progress bar
        const uiScene = this.scene.get('UI');
        if (uiScene) {
            uiScene.progressBarContainer.setVisible(false);
            uiScene.tweens.killTweensOf(uiScene.progressFill);
        }

        // Start a new mission since this one failed
        this.startNewMission();
    }

    completeActivity() {
        this.isActivityRunning = false;
        this.sound.play('sfx_coin');

        // Cleanup Ambush
        if (this.stateManager.ambushActive) {
            this.stateManager.ambushActive = false;
            this.eliteWardens.forEach(w => w.destroy());
            this.eliteWardens = [];
            this.events.emit('ui_message', "Escaped the Squad!");
        }

        let reward = this.missionManager.potentialReward;
        if (this.player.isSafe) {
            this.stateManager.money += reward;
            this.events.emit('ui_message', `Done! +£${reward.toFixed(2)}`);
        } else {
            const mult = Math.pow(1.1, this.stateManager.rewardLevel);
            reward = reward * mult;
            this.stateManager.money += reward;
            this.events.emit('ui_message', `Risk Paid Off! +£${reward.toFixed(2)}`);
            if (this.stateManager.rewardLevel < 6) {
                this.stateManager.rewardLevel += 1;
            }
        }

        this.events.emit('update_ui_hud');
        this.player.isSafe = false;

        // Check Rage
        if (this.stateManager.rewardLevel >= 6) {
            if (this.stateManager.rewardLevel === 6) {
                this.sound.play('music_rage', { loop: true });
            }
            this.wardenInterval = 125;
            this.startWardenTimer();
        }

        this.startNewMission();
    }

    distractWarden() {
        const dxL = this.warden.gridX;
        const dxR = 19 - this.warden.gridX;
        const dyT = this.warden.gridY;
        const dyB = 14 - this.warden.gridY;
        
        const min = Math.min(dxL, dxR, dyT, dyB);
        if (min === dxL) this.distractionTarget = {x: 0, y: this.warden.gridY};
        else if (min === dxR) this.distractionTarget = {x: 19, y: this.warden.gridY};
        else if (min === dyT) this.distractionTarget = {x: this.warden.gridX, y: 0};
        else this.distractionTarget = {x: this.warden.gridX, y: 14};
    }

    spawnEliteWardens() {
        this.eliteWardens.forEach(w => w.destroy());
        this.eliteWardens = [
            new Warden(this, 0, 0, this.pathfinder).setDepth(20),
            new Warden(this, 19, 0, this.pathfinder).setDepth(20),
            new Warden(this, 0, 14, this.pathfinder).setDepth(20),
            new Warden(this, 19, 14, this.pathfinder).setDepth(20)
        ];
    }

    checkCollision() {
        if (!this.isActivityRunning) return;

        let hit = false;
        if (this.warden.gridX === this.player.gridX && this.warden.gridY === this.player.gridY) {
            hit = true;
        }

        for (const ew of this.eliteWardens) {
            if (ew.gridX === this.player.gridX && ew.gridY === this.player.gridY) {
                hit = true;
                break;
            }
        }

        if (hit) {
            if (!this.player.isSafe) {
                // BUSTED
                this.cancelActivity();
                
                this.scene.pause('UI');
                this.sound.pauseAll();
                this.scene.launch('Cutscene', { 
                    gameScene: this, 
                    locImageKey: this.missionManager.locImageKey,
                    stateManager: this.stateManager
                });
                this.scene.pause();
            } else {
                this.events.emit('ui_message', "Phew! Interaction Safe.");
            }
        }
    }
}
