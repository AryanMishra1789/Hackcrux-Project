const fs = require('fs');
const path = require('path');
const { app } = require('electron');

class HistoryService {
    constructor() {
        this.initialized = false;
        this.historyPath = path.join(app.getPath('userData'), 'history.json');
    }

    async initialize() {
        if (this.initialized) return;
        
        try {
            // Create history file if it doesn't exist
            if (!fs.existsSync(this.historyPath)) {
                fs.writeFileSync(this.historyPath, JSON.stringify([], null, 2));
            }
            
            this.initialized = true;
        } catch (error) {
            console.error('Failed to initialize history service:', error);
            throw error;
        }
    }

    async saveToHistory(prompt, email) {
        await this.initialize();
        
        try {
            let history = await this.loadHistory();
            
            history.unshift({
                prompt,
                email,
                timestamp: new Date().toISOString()
            });
            
            // Keep only last 50 entries
            history = history.slice(0, 50);
            
            fs.writeFileSync(this.historyPath, JSON.stringify(history, null, 2));
            return true;
        } catch (error) {
            console.error('Error saving to history:', error);
            throw new Error('Failed to save to history');
        }
    }

    async loadHistory() {
        await this.initialize();
        
        try {
            if (fs.existsSync(this.historyPath)) {
                return JSON.parse(fs.readFileSync(this.historyPath, 'utf8'));
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
        return [];
    }

    async clearHistory() {
        await this.initialize();
        
        try {
            fs.writeFileSync(this.historyPath, JSON.stringify([], null, 2));
            return true;
        } catch (error) {
            console.error('Error clearing history:', error);
            throw new Error('Failed to clear history');
        }
    }
}

module.exports = new HistoryService(); 