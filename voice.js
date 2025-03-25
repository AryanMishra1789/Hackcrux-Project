const { ipcMain } = require('electron');

class VoiceService {
    constructor() {
        this.initialized = false;
        this.recognition = null;
    }

    async initialize() {
        if (this.initialized) return;

        try {
            // Initialize speech recognition
            if ('webkitSpeechRecognition' in window) {
                this.recognition = new webkitSpeechRecognition();
                this.recognition.continuous = false;
                this.recognition.interimResults = false;
                this.recognition.lang = 'en-US';

                this.recognition.onresult = (event) => {
                    const text = event.results[0][0].transcript;
                    ipcMain.emit('voice-text', text);
                };

                this.recognition.onerror = (event) => {
                    console.error('Speech recognition error:', event.error);
                    ipcMain.emit('voice-error', event.error);
                };

                this.recognition.onend = () => {
                    ipcMain.emit('voice-recording-stopped');
                };
            } else {
                throw new Error('Speech recognition not supported in this browser');
            }

            this.initialized = true;
        } catch (error) {
            console.error('Failed to initialize voice service:', error);
            throw error;
        }
    }

    async startRecording() {
        await this.initialize();
        
        try {
            this.recognition.start();
            return true;
        } catch (error) {
            console.error('Failed to start recording:', error);
            throw error;
        }
    }

    async stopRecording() {
        if (!this.recognition) {
            throw new Error('Speech recognition not initialized');
        }
        
        try {
            this.recognition.stop();
            return true;
        } catch (error) {
            console.error('Failed to stop recording:', error);
            throw error;
        }
    }
}

module.exports = new VoiceService(); 