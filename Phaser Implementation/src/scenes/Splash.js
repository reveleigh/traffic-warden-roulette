export default class Splash extends Phaser.Scene {
    constructor() {
        super('Splash');
    }

    create() {
        const width = this.cameras.main.width;
        const height = this.cameras.main.height;

        this.add.image(0, 0, 'cotswold_splash_clear').setOrigin(0, 0).setDisplaySize(width, height);

        // Music
        this.sound.stopAll();
        this.sound.play('music_splash', { loop: true, volume: 0.5 });

        // Warden Pop-up Animation
        this.warden = this.add.image(Phaser.Math.Between(50, width - 200), height, 'cutscene_warden')
            .setOrigin(0, 0)
            .setDisplaySize(150, 300);

        this.time.addEvent({
            delay: 3000,
            loop: true,
            callback: () => {
                this.warden.x = Phaser.Math.Between(50, width - 200);
                this.tweens.add({
                    targets: this.warden,
                    y: height - 250,
                    yoyo: true,
                    hold: 2000,
                    duration: 500,
                    ease: 'Sine.easeInOut'
                });
            }
        });

        // Instructions Text
        const textConfig = { fontSize: '40px', fill: '#ffffff', stroke: '#000000', strokeThickness: 6, fontFamily: 'monospace' };
        this.add.text(width / 2, 400, 'Press ENTER to Begin', textConfig).setOrigin(0.5);
        this.add.text(width / 2, 450, "Press 'L' for Leaderboard", textConfig).setOrigin(0.5);

        // Title text
        this.title = this.add.text(width / 2, height - 150, 'Traffic Warden Roulette', {
            fontSize: '60px',
            fill: '#323232',
            stroke: '#ffff00',
            strokeThickness: 10,
            fontFamily: 'monospace',
            fontStyle: 'bold'
        }).setOrigin(0.5);

        // Title Pulse Tween
        this.tweens.add({
            targets: this.title,
            scaleX: 1.05,
            scaleY: 1.05,
            yoyo: true,
            loop: -1,
            duration: 800,
            ease: 'Sine.easeInOut'
        });

        // Input
        this.input.keyboard.on('keydown-ENTER', () => {
            this.scene.start('Instructions');
        });
        this.input.keyboard.on('keydown-L', () => {
            this.scene.start('Leaderboard', { isGameOver: false });
        });
    }
}
