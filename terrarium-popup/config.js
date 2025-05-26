// Helper module for json file
const fs = require('fs');
const path = require('path');

const configPath = path.join(__dirname, 'config.json');

function loadConfig() {
    try {
        return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    } catch (e) {
        console.error('failed to load config', e);
            return{};
        }
    }

function saveConfig(config) {
    try {
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf-8');
    } catch (e) {
        console.error('Failed to write to config', e);
    }
}

module.exports = {
    loadConfig,
    saveConfig,
    configPath,
};