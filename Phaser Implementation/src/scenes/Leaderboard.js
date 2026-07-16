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
            this.nameInputText = this.add.text(width/2, 350, '_', { fontSize: '50px', fill: '#00ff00' }).setOrigin(0.5);
            this.isTypingName = true;
            this.playerName = "";

            this.nameInputListener = (event) => {
                if (!this.isTypingName) return;
                
                if (event.key === 'Backspace') {
                    if (this.playerName.length > 0) {
                        this.playerName = this.playerName.slice(0, -1);
                    }
                } else if (event.key === 'Enter') {
                    this.isTypingName = false;
                    let finalName = this.playerName.trim();
                    if (finalName === "") finalName = "Anon";
                    
                    this.input.keyboard.off('keydown', this.nameInputListener);
                    DBManager.saveScore(finalName, this.finalMoney);
                    this.showLeaderboard();
                } else if (event.key.length === 1 && this.playerName.length < 15) {
                    this.playerName += event.key;
                }
                
                if (this.isTypingName) {
                    this.nameInputText.setText(this.playerName + '_');
                }
            };

            this.input.keyboard.on('keydown', this.nameInputListener);

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

        this.add.text(width/2, height - 100, "Press 'R' to Restart Year", { fontSize: '24px', fill: '#aaaaaa' }).setOrigin(0.5);
        this.add.text(width/2, height - 60, "Press 'ESC' for Home", { fontSize: '24px', fill: '#aaaaaa' }).setOrigin(0.5);

        this.input.keyboard.on('keydown-R', () => {
            this.scene.start('Game');
        });
        
        this.input.keyboard.on('keydown-ESC', () => {
            this.scene.start('Splash');
        });
    }
}
