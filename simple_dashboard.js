// Minimal working dashboard for debugging
class SimpleDashboard {
    constructor() {
        console.log('🚀 SimpleDashboard constructor called');
        this.currentData = null;
        this.init();
    }
    
    async init() {
        console.log('🔄 Initializing SimpleDashboard...');
        try {
            await this.loadData();
            this.updateUI();
        } catch (error) {
            console.error('❌ SimpleDashboard error:', error);
        }
    }
    
    async loadData() {
        console.log('📊 Loading data...');
        const filename = 'Monday, 24 November 2025 1329+1251 v 683+665.json';
        const url = `./data/${encodeURIComponent(filename)}`;
        
        console.log('📡 Fetching:', url);
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const rawData = await response.json();
        console.log('✅ Data loaded:', {
            keys: Object.keys(rawData),
            positiveCount: rawData.positive?.length || 0,
            combinedCount: rawData.combined?.length || 0
        });
        
        this.currentData = rawData;
    }
    
    updateUI() {
        console.log('🔄 Updating UI...');
        
        // Update player count
        const playerCount = this.currentData?.combined?.length || 0;
        const playerElement = document.getElementById('totalPlayersDisplay');
        if (playerElement) {
            playerElement.textContent = playerCount;
            console.log(`✅ Updated player count: ${playerCount}`);
        } else {
            console.error('❌ Player count element not found');
        }
        
        // Update alliance count
        const allianceCount = this.currentData?.alliance?.length || 0;
        const allianceElement = document.getElementById('totalAlliancesDisplay');
        if (allianceElement) {
            allianceElement.textContent = allianceCount;
            console.log(`✅ Updated alliance count: ${allianceCount}`);
        } else {
            console.error('❌ Alliance count element not found');
        }
        
        // Hide loading
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
            console.log('✅ Hidden loading overlay');
        }
        
        // Update status
        const statusElement = document.getElementById('updateStatus');
        if (statusElement) {
            statusElement.textContent = 'Live';
            console.log('✅ Updated status');
        }
        
        console.log('✅ UI update complete');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('📱 DOM ready, starting SimpleDashboard...');
    window.simpleDashboard = new SimpleDashboard();
});