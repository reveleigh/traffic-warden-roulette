import DBManager from '../managers/DBManager.js';

export default class Leaderboard extends Phaser.Scene {
    constructor() {
        super('Leaderboard');
    }

    init(data) {
        this.finalMoney = data.money;
        this.isGameOver = data.isGameOver || false;
    }

    create() {
        const width = this.cameras.main.width;
        const height = this.cameras.main.height;

        this.add.rectangle(0, 0, width, height, 0x14141e).setOrigin(0, 0);

        if (this.isGameOver) {
            this.sound.stopAll();
            this.sound.play('music_gameover', { loop: true });
            
            this.add.text(width/2, 100, 'YEAR COMPLETE', { fontSize: '60px', fill: '#ffffff' }).setOrigin(0.5);
            this.add.text(width/2, 180, `Final Money: £${this.finalMoney.toFixed(2)}`, { fontSize: '40px', fill: '#ffd700' }).setOrigin(0.5);

            this.add.text(width/2, 280, 'ENTER YOUR NAME:', { fontSize: '40px', fill: '#ffffff' }).setOrigin(0.5);

            this.nameInput = document.createElement('input');
            this.nameInput.type = 'text';
            this.nameInput.id = 'name-input-dom';
            this.nameInput.maxLength = 15;
            this.nameInput.placeholder = 'Anon';
            
            this.domElement = this.add.dom(width / 2, 350, this.nameInput);
            this.nameInput.focus();

            const submitText = this.add.text(width / 2, 450, 'Press ENTER or Tap Here to Submit', { fontSize: '24px', fill: '#aaaaaa' }).setOrigin(0.5)
                .setInteractive({ useHandCursor: true });
                
            const submitName = () => {
                let finalName = this.nameInput.value.trim();
                if (!finalName || finalName === "") finalName = "Anon";
                
                this.domElement.destroy();
                submitText.destroy();
                
                DBManager.saveScore(finalName, this.finalMoney);
                this.showLeaderboard();
            };

            submitText.on('pointerdown', submitName);

            this.input.keyboard.on('keydown-ENTER', () => {
                if (this.domElement && this.domElement.active) {
                    submitName();
                }
            });

        } else {
            this.showLeaderboard();
        }
    }

    showLeaderboard() {
        this.children.removeAll(); // Clear existing text

        const width = this.cameras.main.width;
        const height = this.cameras.main.height;

        this.add.text(width/2, 50, 'LEADERBOARD', { fontSize: '50px', fill: '#ffd700' }).setOrigin(0.5);

        const scores = DBManager.getScores(10);
        
        let y = 150;
        scores.forEach((s, i) => {
            this.add.text(width/2, y, `${i+1}. ${s.name} : £${s.score}`, { fontSize: '30px', fill: '#ffffff' }).setOrigin(0.5);
            y += 40;
        });

        this.add.text(width/2, height - 100, "Press 'R' or Tap Here to Restart Year", { fontSize: '24px', fill: '#aaaaaa' }).setOrigin(0.5)
            .setInteractive({ useHandCursor: true })
            .on('pointerdown', () => this.scene.start('Game'));
            
        this.add.text(width/2, height - 60, "Press 'ESC' or Tap Here for Home", { fontSize: '24px', fill: '#aaaaaa' }).setOrigin(0.5)
            .setInteractive({ useHandCursor: true })
            .on('pointerdown', () => this.scene.start('Splash'));

        this.input.keyboard.on('keydown-R', () => {
            this.scene.start('Game');
        });
        
        this.input.keyboard.on('keydown-ESC', () => {
            this.scene.start('Splash');
        });
    }
}
