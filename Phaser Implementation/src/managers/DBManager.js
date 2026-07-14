export default class DBManager {
    static STORAGE_KEY = 'twr_highscores';

    static getScores(limit = 50) {
        try {
            const scores = localStorage.getItem(this.STORAGE_KEY);
            if (scores) {
                return JSON.parse(scores).slice(0, limit);
            }
        } catch (e) {
            console.error("Error reading from localStorage", e);
        }
        return [];
    }

    static saveScore(name, score) {
        try {
            const scores = this.getScores(100); // get more to sort
            scores.push({ 
                name, 
                score: Math.floor(score), // Match integer behavior of python db
                date_achieved: new Date().toISOString() 
            });
            // Sort descending
            scores.sort((a, b) => b.score - a.score);
            
            // Keep top 50
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(scores.slice(0, 50)));
            console.log(`Score ${score} for ${name} saved to LocalStorage.`);
        } catch (e) {
            console.error("Error saving to localStorage", e);
        }
    }
}
