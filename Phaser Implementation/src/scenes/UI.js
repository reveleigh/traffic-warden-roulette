export default class UI extends Phaser.Scene {
    constructor() {
        super({ key: 'UI', active: false });
    }

    init(data) {
        this.gameScene = data.gameScene;
        this.state = data.state;
        this.mission = data.mission;
    }

    create() {
        // HUD Top Bar
        this.add.rectangle(0, 0, 800, 40, 0x000000).setOrigin(0, 0);

        this.moneyDateText = this.add.text(20, 10, '', { fontSize: '24px', fill: '#ffffff' });
        this.missionGoalText = this.add.text(400, 60, '', { fontSize: '20px', fill: '#ffffff', backgroundColor: '#000000' })
            .setOrigin(0.5)
            .setPadding(10)
            .setStroke('#ffd700', 2);

        // Message Popups
        this.messageText = this.add.text(400, 360, '', { fontSize: '40px', fill: '#ff0000', stroke: '#000000', strokeThickness: 6 })
            .setOrigin(0.5).setAlpha(0);

        // Progress Bar
        this.progressBarContainer = this.add.container(200, 660).setVisible(false);
        this.progressBg = this.add.rectangle(0, 0, 400, 30, 0x323232).setOrigin(0, 0).setStrokeStyle(2, 0xffffff);
        this.progressFill = this.add.rectangle(0, 0, 0, 30, 0x00ff00).setOrigin(0, 0);
        this.progressText = this.add.text(200, -20, 'Risking IT', { fontSize: '20px', fill: '#ffffff' }).setOrigin(0.5);
        this.progressBarContainer.add([this.progressBg, this.progressFill, this.progressText]);

        // Rage Mode Overlay
        this.rageOverlay = this.add.rectangle(0, 90, 800, 600, 0x00ff00, 0.2).setOrigin(0, 0).setVisible(false);
        this.rageText = this.add.text(400, 55, 'WARDEN DESPAIR RAGE', { fontSize: '40px', fill: '#ff0000', fontStyle: 'bold' }).setOrigin(0.5).setVisible(false);
        
        // Guilt Mode Overlay
        this.guiltOverlay = this.add.rectangle(0, 90, 800, 600, 0xff0000, 0.4).setOrigin(0, 0).setVisible(false);
        this.guiltText = this.add.text(400, 100, 'Moral Panic: Guilt Mode Enabled', { fontSize: '60px', fill: '#ffffff' }).setOrigin(0.5).setVisible(false);
        this.guiltTextShadow = this.add.text(402, 102, 'Moral Panic: Guilt Mode Enabled', { fontSize: '60px', fill: '#000000' }).setOrigin(0.5).setVisible(false);
        
        // Flashing text timer
        this.time.addEvent({
            delay: 500,
            loop: true,
            callback: () => {
                if (this.state.guiltModeActive) {
                    const isVis = this.guiltText.visible;
                    this.guiltText.setVisible(!isVis);
                    this.guiltTextShadow.setVisible(!isVis);
                }
            }
        });

        // Meters (Audacity / Fine)
        this.add.text(420 - 75, 12, 'Audacity:', { fontSize: '20px', fill: '#c8c8c8' });
        this.add.text(650 - 45, 12, 'Fine:', { fontSize: '20px', fill: '#c8c8c8' });

        this.audacityBlocks = [];
        for (let i = 0; i < 6; i++) {
            const block = this.add.rectangle(420 + i * 17, 10, 15, 20, 0x323232).setOrigin(0, 0);
            this.audacityBlocks.push(block);
        }

        this.fineBlocks = [];
        for (let i = 0; i < 6; i++) {
            const block = this.add.rectangle(650 + i * 17, 10, 15, 20, 0x320000).setOrigin(0, 0);
            this.fineBlocks.push(block);
        }

        // Mission Pop-up Container
        this.popupContainer = this.add.container(0, 0).setVisible(false);
        const pbg = this.add.rectangle(400, 360, 600, 400, 0x14141e).setOrigin(0.5).setStrokeStyle(2, 0xffffff);
        this.popupText = this.add.text(150, 200, '', { fontSize: '24px', fill: '#ffffff', wordWrap: { width: 500 }});
        
        this.payOption = this.add.text(150, 400, '[P] PAY', { fontSize: '24px', fill: '#64ff64' });
        this.riskOption = this.add.text(150, 450, '[SPACE] RISK IT', { fontSize: '24px', fill: '#ff6464' });
        
        this.popupContainer.add([pbg, this.popupText, this.payOption, this.riskOption]);

        // Event Listeners from Game Scene
        this.gameScene.events.on('update_ui_hud', this.updateHUD, this);
        this.gameScene.events.on('update_ui_mission', this.updateMission, this);
        this.gameScene.events.on('show_mission_popup', this.showPopup, this);
        this.gameScene.events.on('ui_message', this.showMessage, this);
        this.gameScene.events.on('start_activity_bar', this.startProgressBar, this);

        // Input
        this.input.keyboard.on('keydown-P', () => {
            if (this.popupContainer.visible) {
                this.popupContainer.setVisible(false);
                this.gameScene.events.emit('mission_choice', 'pay');
            }
        });
        
        this.input.keyboard.on('keydown-SPACE', () => {
            if (this.popupContainer.visible) {
                if (this.state.guiltModeActive) {
                    this.showMessage("Too guilty to risk it!");
                } else {
                    this.popupContainer.setVisible(false);
                    this.gameScene.events.emit('mission_choice', 'risk');
                }
            }
        });

        // Initialize display
        this.updateHUD();
        this.updateMission();
    }

    updateHUD() {
        const d = new Date(this.state.currentDate);
        const day = d.getDate().toString().padStart(2, '0');
        const month = d.toLocaleString('en-GB', { month: 'short' });
        this.moneyDateText.setText(`£${this.state.money.toFixed(2)}   Date: ${day} ${month}`);
        
        // Update Meters
        for (let i = 0; i < 6; i++) {
            if (i < this.state.rewardLevel) {
                if (this.state.rewardLevel >= 6 && i === 5) {
                    this.audacityBlocks[i].setFillStyle(0xffd700); // Gold for full rage
                } else {
                    this.audacityBlocks[i].setFillStyle(0x00ff64); // Green
                }
            } else {
                this.audacityBlocks[i].setFillStyle(0x323232); // Empty
            }
            
            if (i < this.state.fineLevel) {
                this.fineBlocks[i].setFillStyle(0xff0000); // Red
            } else {
                this.fineBlocks[i].setFillStyle(0x320000); // Empty
            }
        }

        // Update Overlays
        const isRage = this.state.rewardLevel >= 6;
        this.rageOverlay.setVisible(isRage);
        this.rageText.setVisible(isRage);

        if (!this.state.guiltModeActive) {
            this.guiltOverlay.setVisible(false);
            this.guiltText.setVisible(false);
            this.guiltTextShadow.setVisible(false);
        } else {
            this.guiltOverlay.setVisible(true);
            // The flashing timer will handle the text visibility
        }
    }

    updateMission() {
        this.missionGoalText.setText(`GOAL: ${this.mission.taskName} @ ${this.mission.locName}`);
    }

    showPopup() {
        this.popupText.setText(this.mission.missionBriefing);
        this.popupContainer.setVisible(true);

        const safeProfit = 0.00;
        const riskProfit = this.mission.potentialReward * Math.pow(1.1, this.state.rewardLevel);

        this.payOption.setText(`[P] PAY £${this.mission.missionCost.toFixed(2)} (Profit: £${safeProfit.toFixed(2)})`);
        this.riskOption.setText(`[SPACE] RISK IT (Profit: £${riskProfit.toFixed(2)})`);
    }

    showMessage(msg) {
        this.messageText.setText(msg);
        this.messageText.setAlpha(1);
        this.tweens.add({
            targets: this.messageText,
            alpha: 0,
            delay: 1000,
            duration: 1000
        });
    }

    startProgressBar(durationTicks, isSafe) {
        this.progressBarContainer.setVisible(true);
        this.progressFill.width = 0;
        this.progressFill.setFillStyle(isSafe ? 0x00ff00 : 0xffa500);
        this.progressText.setText(isSafe ? "PAID" : "RISKING IT");

        this.tweens.add({
            targets: this.progressFill,
            width: 400,
            duration: durationTicks * 16.66,
            onComplete: () => {
                this.progressBarContainer.setVisible(false);
            }
        });
    }
}
