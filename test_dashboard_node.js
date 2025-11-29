// Node.js test for dashboard functionality
const fs = require('fs');
const path = require('path');

// Mock DOM environment
global.document = {
    getElementById: (id) => ({
        addEventListener: () => {},
        value: null
    }),
    createElement: () => ({
        appendChild: () => {},
        style: {},
        textContent: ''
    }),
    head: {
        appendChild: () => {}
    }
};

const originalConsole = console;
global.console = {
    log: (...args) => originalConsole.log('[DASHBOARD]', ...args),
    error: (...args) => originalConsole.error('[DASHBOARD ERROR]', ...args)
};

// Mock fetch
global.fetch = async (url) => {
    console.log('Mock fetch:', url);
    
    // Load local test data
    if (url.includes('scoreboard-data.json')) {
        const data = fs.readFileSync(path.join(__dirname, 'data', 'scoreboard-data.json'), 'utf8');
        return {
            ok: true,
            json: async () => JSON.parse(data)
        };
    }
    
    return {
        ok: false,
        status: 404,
        statusText: 'Not Found'
    };
};

// Load and test dashboard code
try {
    console.log('Loading dashboard.js...');
    const dashboardCode = fs.readFileSync(path.join(__dirname, 'dashboard.js'), 'utf8');
    
    // Execute the dashboard code
    eval(dashboardCode);
    
    console.log('✅ Dashboard.js loaded successfully');
    
    // Test creating dashboard instance
    console.log('Creating Dashboard instance...');
    const dashboard = new Dashboard();
    
    console.log('✅ Dashboard instance created');
    
    // Test data loading
    console.log('Testing data loading...');
    dashboard.loadData('./data/scoreboard-data.json')
        .then(() => {
            console.log('✅ Data loading test passed');
            console.log('Dashboard state:', dashboard.state);
            console.log('Current data keys:', dashboard.currentData ? Object.keys(dashboard.currentData) : 'null');
        })
        .catch(error => {
            console.error('❌ Data loading test failed:', error.message);
        });
        
} catch (error) {
    console.error('❌ Dashboard test failed:', error.message);
    console.error(error.stack);
}