export default class Instructions extends Phaser.Scene {
    constructor() {
        super('Instructions');
    }

    create() {
        const width = this.cameras.main.width;
        const height = this.cameras.main.height;

        this.add.rectangle(0, 0, width, height, 0x1e1e28).setOrigin(0, 0);
        this.add.image(0, 0, 'ciren').setOrigin(0, 0).setDisplaySize(width, height).setAlpha(0.6);

        const content = `CIRENCESTER'S BUSIEST DAD

You are Rupert, the ultimate busy dad of Cirencester. Your schedule is packed tighter than the Fleece on a Friday night. Your wife Clementine has an endless list of 'essential' errands, from picking up her specific vintage of wine to dropping off dry cleaning. Your daughter Fenella needs taxiing to ballet, and your teenage son Ivor has rugby practice, drum lessons, and a social life better than yours.

But there's a problem. Parking in Cirencester costs a small fortune, and the Council have deployed their elite squad of Traffic Wardens to squeeze every penny out of motorists. You have a choice: play it safe and pay the extortionate parking fees, seeing your family's holiday fund dwindle away, or be audacious.

Risking a fine by not paying builds your 'Audacity'. The more audacious you are, the more money you save for the big family adventure next year. But be warned: if you get caught, the fines are hefty, and your hard-earned audacity is reset.

HOW TO PLAY:
1. Drive to the YELLOW ZONES to complete errands.
2. 'Pay' to be safe, or 'Risk it' to build Audacity.
3. High Audacity multiplies your savings.
4. If a Warden catches you while risking it, you get FINED.
5. Survive the year with the biggest Holiday Fund possible.

[PRESS ENTER TO START]`;

        this.instructionsText = this.add.text(width / 2, 100, content, {
            fontSize: '24px',
            fill: '#ffffff',
            stroke: '#000000',
            strokeThickness: 4,
            align: 'center',
            wordWrap: { width: width - 100 },
            fontFamily: 'monospace'
        }).setOrigin(0.5, 0);

        this.input.keyboard.on('keydown-ENTER', () => {
            this.scene.start('Game');
        });
        
        this.input.keyboard.on('keydown-ESC', () => {
            this.scene.start('Splash');
        });

        // Mouse Wheel Scrolling
        this.input.on('wheel', (pointer, gameObjects, deltaX, deltaY, deltaZ) => {
            this.instructionsText.y -= deltaY * 0.5;
            this.clampScroll();
        });

        this.cursors = this.input.keyboard.createCursorKeys();
    }

    update() {
        if (this.cursors.up.isDown) {
            this.instructionsText.y += 5;
            this.clampScroll();
        } else if (this.cursors.down.isDown) {
            this.instructionsText.y -= 5;
            this.clampScroll();
        }
    }

    clampScroll() {
        const height = this.cameras.main.height;
        const maxY = 100;
        const minY = Math.min(maxY, height - this.instructionsText.height - 50);

        if (this.instructionsText.y > maxY) {
            this.instructionsText.y = maxY;
        } else if (this.instructionsText.y < minY) {
            this.instructionsText.y = minY;
        }
    }
}
