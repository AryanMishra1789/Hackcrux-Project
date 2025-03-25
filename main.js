const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const axios = require('axios');
const fs = require('fs');
const ps = require('ps-node');

let mainWindow;
let loginWindow;
let floatingWindow;
let isBackendRunning = false;
let backendProcess = null;
let isAuthenticated = false;
let lastActiveApp = null;

// Lazy loading of features
const features = {
    llm: null,
    voice: null,
    history: null
};

// Initialize feature only when needed
async function initializeFeature(featureName) {
    if (features[featureName]) return features[featureName];

    switch (featureName) {
        case 'llm':
            features.llm = require('./llm');
            return features.llm;
        case 'voice':
            features.voice = require('./voice');
            return features.voice;
        case 'history':
            features.history = require('./history');
            return features.history;
        default:
            throw new Error(`Unknown feature: ${featureName}`);
    }
}

function createLoginWindow() {
    loginWindow = new BrowserWindow({
        width: 400,
        height: 600,
        frame: false,
        transparent: true,
        resizable: false,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    loginWindow.loadFile('login.html');
    
    // Open DevTools in development
    if (process.argv.includes('--debug')) {
        loginWindow.webContents.openDevTools();
    }
}

function createFloatingWindow() {
    floatingWindow = new BrowserWindow({
        width: 100,
        height: 100,
        frame: false,
        transparent: true,
        alwaysOnTop: true,
        skipTaskbar: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    floatingWindow.loadFile('floating-assistant.html');
}

function createMainWindow() {
    // Get screen dimensions after app is ready
    const { screen } = require('electron');
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;
    
    // Calculate window dimensions (half width, full height)
    const windowWidth = Math.floor(width / 2);
    const windowHeight = height;

    mainWindow = new BrowserWindow({
        width: windowWidth,
        height: windowHeight,
        x: width - windowWidth,
        y: 0,
        frame: false,
        transparent: true,
        alwaysOnTop: true,
        skipTaskbar: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    mainWindow.loadFile('index.html');
    
    // Open DevTools in development
    if (process.argv.includes('--debug')) {
        mainWindow.webContents.openDevTools();
    }

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // Handle window close
    mainWindow.on('close', (event) => {
        if (!app.isQuiting) {
            event.preventDefault();
            mainWindow.hide();
            return false;
        }
    });
}

// Handle app quit
app.on('before-quit', () => {
    app.isQuiting = true;
    if (backendProcess) {
        backendProcess.kill();
    }
});

app.whenReady().then(() => {
    createLoginWindow();
    
    // Start process monitoring after app is ready
    setInterval(startProcessMonitoring, 1000);
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createLoginWindow();
    } else {
        loginWindow.show();
    }
});

// Login handlers
ipcMain.handle('login', async (event, credentials) => {
    try {
        // Here you would typically validate credentials against your backend
        // For demo purposes, we'll accept any email/password
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
        isAuthenticated = true;
        return { status: 'success' };
    } catch (error) {
        return { status: 'error', message: 'Invalid credentials' };
    }
});

ipcMain.on('login-success', () => {
    if (loginWindow) {
        loginWindow.close();
    }
    createMainWindow();
});

// Permission handlers
ipcMain.on('request-calendar-permission', async () => {
    try {
        // Implement Google Calendar OAuth flow
        // For now, we'll just simulate it
        await new Promise(resolve => setTimeout(resolve, 1000));
        dialog.showMessageBox({
            type: 'info',
            title: 'Calendar Access Granted',
            message: 'Successfully connected to Google Calendar'
        });
    } catch (error) {
        dialog.showErrorBox('Calendar Error', 'Failed to connect to Google Calendar');
    }
});

ipcMain.on('request-email-permission', async () => {
    try {
        // Implement Gmail OAuth flow
        // For now, we'll just simulate it
        await new Promise(resolve => setTimeout(resolve, 1000));
        dialog.showMessageBox({
            type: 'info',
            title: 'Email Access Granted',
            message: 'Successfully connected to Gmail'
        });
    } catch (error) {
        dialog.showErrorBox('Email Error', 'Failed to connect to Gmail');
    }
});

ipcMain.on('show-app-password-guide', () => {
    dialog.showMessageBox({
        type: 'info',
        title: 'App Password Guide',
        message: 'To generate an App Password:\n\n' +
                 '1. Go to your Google Account settings\n' +
                 '2. Navigate to Security\n' +
                 '3. Enable 2-Step Verification if not already enabled\n' +
                 '4. Go to App Passwords\n' +
                 '5. Generate a new app password for "Mail"\n' +
                 '6. Copy the 16-character password'
    });
});

ipcMain.on('complete-setup', async (event, { appPassword }) => {
    try {
        // Save app password securely
        // For demo purposes, we'll just simulate it
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Create floating window
        createFloatingWindow();
        
        // Start process monitoring
        startProcessMonitoring();
        
        dialog.showMessageBox({
            type: 'info',
            title: 'Setup Complete',
            message: 'Your AI Assistant is ready to use!'
        });
    } catch (error) {
        dialog.showErrorBox('Setup Error', 'Failed to complete setup');
    }
});

// Process monitoring
async function startProcessMonitoring() {
    try {
        const processes = await new Promise((resolve, reject) => {
            ps.list({}, (err, resultList) => {
                if (err) reject(err);
                else resolve(resultList);
            });
        });

        // Get the active window process
        const activeProcess = processes.find(p => p.windowTitle);
        
        if (activeProcess && activeProcess.windowTitle !== lastActiveApp) {
            lastActiveApp = activeProcess.windowTitle;
            
            // Send update to floating window
            if (floatingWindow) {
                floatingWindow.webContents.send('active-app-update', {
                    name: activeProcess.windowTitle,
                    status: 'Active',
                    icon: '' // You would need to implement icon fetching
                });
            }
        }
    } catch (error) {
        console.error('Process monitoring error:', error);
    }
}

// Main app window handlers
ipcMain.on('open-main-app', () => {
    if (mainWindow) {
        mainWindow.show();
    } else {
        createMainWindow();
    }
});

// IPC handlers with lazy loading
ipcMain.handle('generate-email', async (event, prompt) => {
    try {
        if (!isBackendRunning) {
            await startBackendService();
        }

        const llm = await initializeFeature('llm');
        const result = await llm.generateEmail(prompt);

        // Save to history if enabled
        const history = await initializeFeature('history');
        await history.saveToHistory(prompt, result.email);

        return { status: 'success', email: result.email };
    } catch (error) {
        console.error('Error generating email:', error);
        return { status: 'error', message: error.message };
    }
});

ipcMain.handle('start-recording', async () => {
    try {
        const voice = await initializeFeature('voice');
        await voice.startRecording();
        return { status: 'success' };
    } catch (error) {
        console.error('Error starting recording:', error);
        return { status: 'error', message: error.message };
    }
});

ipcMain.handle('stop-recording', async () => {
    try {
        const voice = await initializeFeature('voice');
        await voice.stopRecording();
        return { status: 'success' };
    } catch (error) {
        console.error('Error stopping recording:', error);
        return { status: 'error', message: error.message };
    }
});

ipcMain.handle('load-history', async () => {
    try {
        const history = await initializeFeature('history');
        return await history.loadHistory();
    } catch (error) {
        console.error('Error loading history:', error);
        return [];
    }
});

ipcMain.handle('clear-history', async () => {
    try {
        const history = await initializeFeature('history');
        await history.clearHistory();
        return { status: 'success' };
    } catch (error) {
        console.error('Error clearing history:', error);
        return { status: 'error', message: error.message };
    }
});

ipcMain.on('minimize-window', () => {
    mainWindow.minimize();
});

ipcMain.on('close-window', () => {
    mainWindow.hide();
});

// Start backend service only when needed
async function startBackendService() {
    if (isBackendRunning) return;

    try {
        const { spawn } = require('child_process');
        const pythonPath = process.env.PYTHON_PATH || 'python';
        
        backendProcess = spawn(pythonPath, ['run.py'], {
            stdio: 'pipe',
            shell: true
        });

        backendProcess.stdout.on('data', (data) => {
            console.log(`Backend: ${data}`);
            if (data.toString().includes('Application startup complete')) {
                isBackendRunning = true;
            }
        });

        backendProcess.stderr.on('data', (data) => {
            console.error(`Backend Error: ${data}`);
        });

        backendProcess.on('close', (code) => {
            console.log(`Backend process exited with code ${code}`);
            isBackendRunning = false;
        });
    } catch (error) {
        console.error('Failed to start backend service:', error);
        isBackendRunning = false;
    }
}

// Settings management
function loadSettings() {
    try {
        const settingsPath = path.join(app.getPath('userData'), 'settings.json');
        if (fs.existsSync(settingsPath)) {
            return JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
    return {
        saveToHistory: true,
        aiSuggestions: true,
        theme: 'light'
    };
}

function saveSettings(settings) {
    try {
        const settingsPath = path.join(app.getPath('userData'), 'settings.json');
        fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2));
    } catch (error) {
        console.error('Error saving settings:', error);
    }
}

// IPC handlers for settings and history
ipcMain.handle('load-settings', () => {
    return loadSettings();
});

ipcMain.handle('save-settings', (event, settings) => {
    saveSettings(settings);
    return { status: 'success' };
}); 