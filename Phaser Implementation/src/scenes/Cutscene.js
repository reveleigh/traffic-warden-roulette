export default class Cutscene extends Phaser.Scene {
    constructor() {
        super('Cutscene');
    }

    init(data) {
        this.gameScene = data.gameScene;
        this.locImageKey = data.locImageKey;
        this.state = data.stateManager;
    }

    create() {
        const width = this.cameras.main.width;
        const height = this.cameras.main.height;

        if (this.locImageKey) {
            this.add.image(0, 0, this.locImageKey).setOrigin(0, 0).setDisplaySize(width, height).setDepth(0);
        }
        
        this.add.rectangle(0, 0, width, height, 0x000000, 0.5).setOrigin(0, 0).setDepth(1);

        // Assets
        this.van = this.add.image(-750, height - 500, 'cutscene_van').setDisplaySize(750, 500).setOrigin(0, 0).setDepth(2);
        this.warden = this.add.image(width, height - 600, 'cutscene_warden').setDisplaySize(300, 600).setOrigin(0, 0).setDepth(2);

        this.sound.play('sfx_busted');

        this.add.text(width/2, 100, 'BUSTED!', { fontSize: '100px', fill: '#ff0000', fontStyle: 'bold' }).setOrigin(0.5).setDepth(3);

        // Animation
        this.tweens.add({
            targets: this.van,
            x: 0,
            duration: 500,
            ease: 'Power2'
        });

        this.tweens.add({
            targets: this.warden,
            x: width - 300,
            duration: 500,
            ease: 'Power2',
            onComplete: () => {
                this.time.delayedCall(1500, this.finalizeBust, [], this);
            }
        });
    }

    finalizeBust() {
        // Calculate fine
        const fineMult = Math.pow(1.5, this.state.fineLevel);
        const fineAmt = 50 * fineMult;
        
        this.state.money -= fineAmt;
        this.state.fineLevel += 1;
        this.state.rewardLevel = 0;

        // Reset entities
        this.gameScene.player.reset();
        this.gameScene.warden.reset();
        
        // Speed up warden slightly
        this.gameScene.wardenInterval = Math.max(50, this.gameScene.wardenInterval * 0.9);
        this.gameScene.startWardenTimer();

        // Defer guilt check to Game.js
        this.gameScene.pendingGuiltCheck = true;

        this.gameScene.scene.resume();
        this.scene.resume('UI');
        this.gameScene.events.emit('ui_message', `FINED £${fineAmt.toFixed(2)}`);
        this.gameScene.events.emit('update_ui_hud');

        this.scene.stop();
    }
}
