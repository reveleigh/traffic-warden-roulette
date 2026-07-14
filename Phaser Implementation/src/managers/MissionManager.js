import { LANDMARKS } from '../map/GameMap.js';

export default class MissionManager {
    constructor(scene, stateManager, gameMap) {
        this.scene = scene; // Main game scene
        this.state = stateManager;
        this.map = gameMap;
        
        // Mission Context Variables
        this.currentSpot = null;
        this.locName = "";
        this.taskName = "";
        this.missionCost = 0.00;
        this.potentialReward = 0.00;
        this.durationTicks = 0; // Duration mapped to ticks/frames for the bar
        this.missionBriefing = "";
    }

    generateMission() {
        // 1. Select Random Landmark
        const landmark = Phaser.Utils.Array.GetRandom(LANDMARKS);
        this.locName = landmark.name;

        // 2. Get specific parking spot
        this.locName = landmark.name;
        this.locImageKey = landmark.imageKey;
        this.currentSpot = this.map.getLandmarkMissionSpot(this.locName);
        if (!this.currentSpot) {
            const spots = this.map.getParkingSpots();
            this.currentSpot = spots.length > 0 ? Phaser.Utils.Array.GetRandom(spots) : { x: 0, y: 0 };
        }

        // 3. Task Name
        if (landmark.tasks && landmark.tasks.length > 0) {
            this.taskName = Phaser.Utils.Array.GetRandom(landmark.tasks);
        } else {
            this.taskName = "Errand Run";
        }

        // Narrative Personalization
        const familyNames = ["Ivor", "Fenella", "Clementine", "Rupert", "Uncle Monty", "Auntie Val"];
        const hasName = familyNames.some(name => this.taskName.includes(name));
        
        if (!hasName) {
            const targetName = Phaser.Utils.Array.GetRandom(familyNames);
            if (Math.random() < 0.7) {
                this.taskName += ` for ${targetName}`;
            } else {
                this.taskName += ` (${targetName})`;
            }
        }

        // 4. Financials
        this.missionCost = Phaser.Math.Between(100, 300) / 100.0; // £1.00 - £3.00
        this.potentialReward = Phaser.Math.FloatBetween(5.00, 15.00);
        let extraNote = "";

        // Weekend logic (Saturday=6, Sunday=0 in JS Date)
        const day = this.state.currentDate.getDay();
        const isWeekend = day === 0 || day === 6;

        if (this.locName.toLowerCase().includes("st micheals")) {
            if (isWeekend) {
                this.missionCost = 0.00;
                extraNote = "\n(FREE PARKING courtesy of Hoard Mgmt)";
            }
        }

        // 5. Duration (Difficulty)
        // Probabilities: Quick ~23%, Medium ~61%, Long ~15%
        const rand = Math.random();
        if (rand < 0.23) {
            this.durationTicks = Phaser.Math.Between(30, 75); // Quick
        } else if (rand < 0.84) {
            this.durationTicks = Phaser.Math.Between(90, 150); // Medium
        } else {
            this.durationTicks = Phaser.Math.Between(180, 270); // Long
        }

        // Briefing Text
        this.missionBriefing = `Errand: ${this.taskName}\nLocation: ${this.locName}\nDuration: ${this.durationTicks} mins\nParking Fee: £${this.missionCost.toFixed(2)}\nAudacity Bonus: £${this.potentialReward.toFixed(2)}${extraNote}`;

        return this.currentSpot;
    }
}
