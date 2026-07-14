export default class Boot extends Phaser.Scene {
    constructor() {
        super('Boot');
    }

    preload() {
        // Load very minimal assets for the Preloader screen (e.g., logo, loading bar graphics)
    }

    create() {
        this.scene.start('Preloader');
    }
}
