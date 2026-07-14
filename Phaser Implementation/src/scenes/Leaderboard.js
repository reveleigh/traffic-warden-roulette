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

            // Native browser prompt for Name
            setTimeout(() => {
                let name = prompt("Enter your name for the high scores:", "Anon");
                if (!name || name.trim() === "") name = "Anon";
                
                DBManager.saveScore(name, this.finalMoney);
                this.showLeaderboard();
            }, 500);
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
