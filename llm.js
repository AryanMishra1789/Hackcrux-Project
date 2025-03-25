const axios = require('axios');

class LLMService {
    constructor() {
        this.initialized = false;
    }

    async initialize() {
        if (this.initialized) return;
        
        // Initialize any LLM-specific resources here
        this.initialized = true;
    }

    async generateEmail(prompt) {
        await this.initialize();
        
        try {
            const response = await axios.post('http://localhost:5002/generate-email', {
                prompt: prompt,
                context: {}
            });
            return response.data;
        } catch (error) {
            console.error('Error in LLM service:', error);
            throw new Error('Failed to generate email');
        }
    }
}

module.exports = new LLMService(); 