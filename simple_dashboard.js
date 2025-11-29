// Simple Dashboard - Working Version
console.log('🚀 Simple Dashboard loading...');

// Simple global state
let currentData = null;

// Simple functions
async function loadSimpleData() {
    console.log('🔄 Loading data...');
    
    try {
        // Try file list first
        const fileResponse = await fetch('./data/file_list.json');
        if (fileResponse.ok) {
            const files = await fileResponse.json();
            console.log('📁 Files:', files);
            
            if (files.length > 0) {
                await loadSpecificFile(files[0]);
                return;
            }
        }
        
        // Fallback to scoreboard data
        await loadSpecificFile('scoreboard-data.json');
        
    } catch (error) {
        console.error('❌ Error loading data:', error);
        showError('Failed to load data');
    }
}

async function loadSpecificFile(filename) {
    console.log(`📊 Loading file: ${filename}`);
    
    try {
        const response = await fetch(`./data/${encodeURIComponent(filename)}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Data loaded:', data);
        
        currentData = data;
        updateSimpleUI();
        hideLoading();
        
    } catch (error) {
        console.error('❌ Error:', error);
        showError(`Error loading ${filename}: ${error.message}`);
    }
}

function updateSimpleUI() {
    if (!currentData) return;
    
    console.log('🔄 Updating UI...');
    
    // Update player count
    const playerCount = currentData.positive ? currentData.positive.length : 0;
    updateElement('totalPlayersDisplay', playerCount);
    
    // Update alliance count
    const allianceCount = currentData.alliance ? currentData.alliance.length : 0;
    updateElement('totalAlliancesDisplay', allianceCount);
    
    // Update status
    updateElement('updateStatus', 'Live');
    
    // Update total score
    const totalScore = currentData.positive ? 
        currentData.positive.reduce((sum, p) => sum + (p.score || 0), 0) : 0;
    updateElement('totalScore', formatNumber(totalScore));
    
    // Update average score
    const avgScore = playerCount > 0 ? Math.round(totalScore / playerCount) : 0;
    updateElement('avgScore', formatNumber(avgScore));
    
    // Update highest score
    const highestScore = currentData.positive ? 
        Math.max(...currentData.positive.map(p => p.score || 0)) : 0;
    updateElement('highestScore', formatNumber(highestScore));
    
    // Update active games
    updateElement('activeGames', playerCount);
    
    // Update top players
    updateTopPlayers();
    
    // Update alliances
    updateAlliances();
    
    // Update last update time
    updateElement('lastUpdate', new Date().toLocaleTimeString('de-DE'));
    
    console.log('✅ UI updated');
}

function updateTopPlayers() {
    const container = document.getElementById('topPlayersList');
    if (!container || !currentData || !currentData.positive) {
        return;
    }
    
    const topPlayers = currentData.positive.slice(0, 10);
    
    if (topPlayers.length === 0) {
        container.innerHTML = '<div class="no-data">Keine Spielerdaten verfügbar</div>';
        return;
    }
    
    container.innerHTML = topPlayers.map((player, index) => `
        <div class="player-item" style="display: flex; justify-content: space-between; padding: 10px; margin: 5px 0; background: white; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="font-weight: bold;">#${index + 1}</div>
            <div style="flex: 1; margin: 0 10px;">${player.name || 'Unknown'}</div>
            <div style="font-weight: bold; color: #667eea;">${formatNumber(player.score || 0)}</div>
            <div style="margin-left: 10px; color: #666;">${player.alliance || 'None'}</div>
        </div>
    `).join('');
}

function updateAlliances() {
    const container = document.getElementById('allianceRanking');
    if (!container || !currentData || !currentData.alliance) {
        return;
    }
    
    const topAlliances = currentData.alliance.slice(0, 5);
    
    if (topAlliances.length === 0) {
        container.innerHTML = '<div class="no-data">Keine Allianzdaten verfügbar</div>';
        return;
    }
    
    container.innerHTML = topAlliances.map((alliance, index) => `
        <div class="alliance-item" style="display: flex; justify-content: space-between; padding: 10px; margin: 5px 0; background: white; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="font-weight: bold;">#${index + 1}</div>
            <div style="flex: 1; margin: 0 10px;">${alliance.Alliance || 'Unknown'}</div>
            <div style="font-weight: bold; color: #667eea;">${formatNumber(alliance["Total Score"] || 0)}</div>
        </div>
    `).join('');
}

function updateElement(id, content) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = content;
    }
}

function formatNumber(num) {
    return num.toLocaleString('de-DE');
}

function hideLoading() {
    console.log('🔄 Hiding loading...');
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

function showError(message) {
    hideLoading();
    console.error('❌ Error:', message);
    updateElement('topPlayersList', `❌ ${message}`);
    updateElement('allianceRanking', `❌ ${message}`);
}

// Global functions for buttons
window.loadDataFile = loadSpecificFile;
window.refreshData = loadSimpleData;
window.showAllPlayers = () => alert('Alle Spieler anzeigen - Coming soon');
window.showAllianceDetails = () => alert('Allianz-Details - Coming soon');

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 DOM ready - Starting simple dashboard...');
    
    // Emergency fallback - hide loading after 5 seconds
    setTimeout(() => {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay && overlay.style.display !== 'none') {
            console.log('⚠️ Emergency hide loading');
            overlay.style.display = 'none';
        }
    }, 5000);
    
    // Start loading data
    loadSimpleData();
});

console.log('✅ Simple dashboard script loaded');