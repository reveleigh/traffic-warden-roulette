export default class Preloader extends Phaser.Scene {
    constructor() {
        super('Preloader');
    }

    preload() {
        const width = this.cameras.main.width;
        const height = this.cameras.main.height;

        const progressBar = this.add.graphics();
        const progressBox = this.add.graphics();
        progressBox.fillStyle(0x222222, 0.8);
        progressBox.fillRect(width / 2 - 160, height / 2 - 25, 320, 50);

        this.load.on('progress', (value) => {
            progressBar.clear();
            progressBar.fillStyle(0xffffff, 1);
            progressBar.fillRect(width / 2 - 150, height / 2 - 15, 300 * value, 30);
        });

        this.load.on('complete', () => {
            progressBar.destroy();
            progressBox.destroy();
            this.scene.start('Splash');
        });

        // Load Images
        this.load.image('player', 'assets/images/player.png');
        this.load.image('warden', 'assets/images/warden.png');
        this.load.image('road', 'assets/images/road.png');
        this.load.image('building', 'assets/images/building.png');
        this.load.image('shop', 'assets/images/shop.png');
        this.load.image('park', 'assets/images/park.png');
        this.load.image('shop_bakery', 'assets/images/shop_bakery.png');
        this.load.image('shop_clothing', 'assets/images/shop_clothing.png');
        this.load.image('shop_tech', 'assets/images/shop_tech.png');
        this.load.image('shop_cafe', 'assets/images/shop_cafe.png');
        this.load.image('building_large_office', 'assets/images/building_large_office.png');
        this.load.image('hospital', 'assets/images/hospital.png');
        this.load.image('park_large', 'assets/images/park_large.png');
        this.load.image('ampitheatre', 'assets/images/ampitheatre.png');
        this.load.image('swimming_pool', 'assets/images/swimming_pool.png');
        this.load.image('museum', 'assets/images/museum.png');
        this.load.image('supermarket', 'assets/images/supermarket.png');
        this.load.image('church', 'assets/images/church.png');
        this.load.image('school', 'assets/images/school.png');
        
        // Splash/UI Images
        this.load.image('cotswold_splash_clear', 'assets/images/cotswold_splash_clear.png');
        this.load.image('ciren', 'assets/images/ciren.png');
        this.load.image('cutscene_van', 'assets/images/rupert_car.png');
        this.load.image('cutscene_warden', 'assets/images/cutscene_warden.png');
        
        // Audio
        this.load.audio('music_splash', 'assets/sounds/You_cant_park_there.mp3');
        this.load.audio('music_bg', 'assets/sounds/background_music.mp3');
        this.load.audio('music_gameover', 'assets/sounds/i-see-you.mp3');
        this.load.audio('music_guilt', 'assets/sounds/guilt.mp3');
        this.load.audio('music_rage', 'assets/sounds/yellow.mp3');
        
        this.load.audio('sfx_busted', 'assets/sounds/busted.mp3');
        this.load.audio('sfx_coin', 'assets/sounds/coin.mp3');
        this.load.audio('sfx_blip', 'assets/sounds/blip.mp3');
        this.load.audio('sfx_pay', 'assets/sounds/pay.mp3');
        this.load.audio('sfx_risk', 'assets/sounds/risk.mp3');
    }
}
