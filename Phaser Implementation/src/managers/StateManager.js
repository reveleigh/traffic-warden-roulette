export default class StateManager {
    constructor(scene) {
        this.scene = scene; // The Phaser Scene (usually Game.js) to access registry
        this.registry = scene.registry;
        this.init();
    }

    init() {
        // Initial Game State Data
        this.registry.set('money', 1000.00);
        // We use a timestamp for easier math, January 1st, 2024
        this.registry.set('currentDate', new Date('2024-01-01T00:00:00').getTime());
        this.registry.set('endDate', new Date('2024-12-31T00:00:00').getTime());
        
        this.registry.set('rewardLevel', 0); // 0-10+
        this.registry.set('fineLevel', 0);   // 0-5+
        
        this.registry.set('ambushActive', false);
        this.registry.set('guiltChance', 0.04);
        this.registry.set('guiltModeActive', false);
        this.registry.set('isRageModeActive', false);
    }

    reset() {
        this.init();
    }

    // Accessors
    get money() { return this.registry.get('money'); }
    set money(val) { this.registry.set('money', val); }

    get currentDate() { return new Date(this.registry.get('currentDate')); }
    advanceDay() {
        const msPerDay = 24 * 60 * 60 * 1000;
        this.registry.set('currentDate', this.registry.get('currentDate') + msPerDay);
    }
    
    get isYearEnd() {
        return this.registry.get('currentDate') > this.registry.get('endDate');
    }

    get rewardLevel() { return this.registry.get('rewardLevel'); }
    set rewardLevel(val) { this.registry.set('rewardLevel', val); }

    get fineLevel() { return this.registry.get('fineLevel'); }
    set fineLevel(val) { this.registry.set('fineLevel', val); }

    get ambushActive() { return this.registry.get('ambushActive'); }
    set ambushActive(val) { this.registry.set('ambushActive', val); }

    get guiltChance() { return this.registry.get('guiltChance'); }
    set guiltChance(val) { this.registry.set('guiltChance', val); }

    get guiltModeActive() { return this.registry.get('guiltModeActive'); }
    set guiltModeActive(val) { this.registry.set('guiltModeActive', val); }

    get isRageModeActive() { return this.registry.get('isRageModeActive'); }
    set isRageModeActive(val) { this.registry.set('isRageModeActive', val); }
}
