// AgentDaf1.1 Dashboard - Fixed Version for GitHub Pages
// Handles both flat local JSON format and nested GitHub Pages format
class Dashboard {
    constructor() {
        this.config = {
            dataPath: './data/',
            autoRefreshInterval: 60000,
            enableDebugMode: false
        };
        
        this.state = {
            currentData: null,
            currentFile: null,
            lastUpdate: null,
            isLoading: false
        };
        
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing Dashboard...');
        this.setupEventListeners();
        
        // Hide loading overlay immediately after initialization
        setTimeout(() => {
            this.hideLoading();
        }, 1000);
        
        this.loadInitialData();
        this.setupAutoRefresh();
    }
    
    setupEventListeners() {
        // File selector
        const fileSelect = document.getElementById('dataFileSelect');
        if (fileSelect) {
            fileSelect.addEventListener('change', (e) => {
                if (e.target.value) {
                    this.loadData(e.target.value);
                }
            });
        }
        
        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }
    }
    
    updateFileSelector(files) {
        const fileSelect = document.getElementById('dataFileSelect');
        if (!fileSelect) return;
        
        // Clear existing options
        fileSelect.innerHTML = '';
        
        // Add file options with friendly names
        files.forEach(file => {
            const option = document.createElement('option');
            option.value = file;
            
            // Create friendly display name
            let displayName = file;
            if (file.includes('Monday')) {
                displayName = 'Montag, 24. Nov 2025';
            } else if (file.includes('Sunday')) {
                displayName = 'Sonntag, 16. Nov 2025';
            } else if (file === 'scoreboard-data.json') {
                displayName = 'Aktuelle Spielstände';
            } else if (file === 'monday_data.json') {
                displayName = 'Montag Daten (Backup)';
            }
            
            option.textContent = displayName;
            fileSelect.appendChild(option);
        });
        
        console.log('✅ File selector updated with', files.length, 'files');
    }
    
    async loadInitialData() {
        console.log('🔄 Loading initial data...');
        
        // Try to load the most recent data file
        try {
            console.log('📡 Fetching file list...');
            const response = await fetch('./data/file_list.json');
            console.log('📡 File list response:', response.status, response.statusText);
            
            if (response.ok) {
                const files = await response.json();
                console.log('📁 Found file list:', files);
                
                // Update file selector with all available files
                this.updateFileSelector(files);
                
                if (files.length > 0) {
                    // Load the most recent file
                    console.log('📊 Loading first file:', files[0]);
                    await this.loadData(files[0]);
                    return;
                } else {
                    console.warn('⚠️ File list is empty');
                }
            } else {
                console.warn('⚠️ File list response not ok:', response.status);
            }
        } catch (error) {
            console.error('❌ Error loading file list:', error);
        }
        
        // Fallback to default file
        console.log('📊 Using default file');
        try {
            await this.loadData('scoreboard-data.json');
        } catch (fallbackError) {
            console.error('❌ Fallback file also failed:', fallbackError);
            this.hideLoading();
            this.showError('Keine Daten konnten geladen werden');
        }
    }
    
    async loadData(filename) {
        if (this.state.isLoading) return;
        
        console.log(`📊 Loading data file: ${filename}`);
        this.state.isLoading = true;
        this.showLoading();
        
        try {
            const url = `${this.config.dataPath}${encodeURIComponent(filename)}`;
            console.log('📡 Fetching from:', url);
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const rawData = await response.json();
            console.log('✅ Raw data loaded:', {
                keys: Object.keys(rawData),
                hasPositive: !!rawData.positive,
                hasNegative: !!rawData.negative,
                hasCombined: !!rawData.combined,
                hasAlliance: !!rawData.alliance,
                positiveCount: rawData.positive?.length || 0,
                negativeCount: rawData.negative?.length || 0,
                combinedCount: rawData.combined?.length || 0,
                allianceCount: rawData.alliance?.length || 0
            });
            
            const processedData = this.processData(rawData);
            this.currentData = processedData;
            this.currentFile = filename;
            this.lastUpdate = new Date().toISOString();
            
            console.log('📊 Processed data:', {
                totalPlayers: processedData.metadata?.totalPlayers,
                totalAlliances: processedData.metadata?.totalAlliances,
                combinedCount: processedData.combined?.length,
                allianceCount: processedData.alliances?.length
            });
            
            this.updateUI();
            this.hideLoading();
            
            console.log('✅ Data loaded and processed successfully');
            
        } catch (error) {
            console.error('❌ Error loading data:', error);
            this.hideLoading();
            this.showError(`Fehler beim Laden der Daten: ${error.message}`);
        } finally {
            this.state.isLoading = false;
        }
    }
    
    processData(rawData) {
        console.log('🔄 Processing raw data...', {
            keys: Object.keys(rawData),
            hasPositive: !!rawData.positive,
            hasNegative: !!rawData.negative,
            hasCombined: !!rawData.combined
        });

        // Extract data from flat structure (current format)
        const positiveData = rawData.positive || [];
        const negativeData = rawData.negative || [];
        let combinedData = rawData.combined || [];
        
        // Normalize data field names and filter out invalid entries
        const normalizePlayer = (player) => {
            if (!player || (!player.Name && !player.name) || 
                (player.Name === null && player.name === null) || 
                (player.Name === '' && player.name === '')) return null;
            
            return {
                position: parseInt(player.Position || player.position) || 0,
                name: player.Name || player.name,
                score: parseFloat(player["Total Score"] || player.Score || player.score || 0),
                alliance: player.Alliance || player.alliance || 'None',
                monarchId: parseFloat(player["Monarch ID"] || player.monarchId) || 0,
                positiveScore: parseFloat(player.Positive || player.positiveScore || 0),
                negativeScore: parseFloat(player.Negative || player.negativeScore || 0)
            };
        };
        
        // Normalize and filter data
        const normalizedPositive = positiveData.map(normalizePlayer).filter(p => p !== null);
        const normalizedNegative = negativeData.map(normalizePlayer).filter(p => p !== null);
        let normalizedCombined = combinedData.map(normalizePlayer).filter(p => p !== null);
        
        // If no combined data, create it from positive and negative
        if (normalizedCombined.length === 0 && (normalizedPositive.length > 0 || normalizedNegative.length > 0)) {
            console.log('🔗 Creating combined data from positive and negative datasets');
            const playerMap = new Map();
            
            // Add positive players
            normalizedPositive.forEach(player => {
                const key = `${player.name}_${player.monarchId}`;
                playerMap.set(key, {
                    ...player,
                    positiveScore: player.score,
                    negativeScore: 0
                });
            });
            
            // Add negative players (if they exist)
            normalizedNegative.forEach(player => {
                const key = `${player.name}_${player.monarchId}`;
                if (playerMap.has(key)) {
                    const existing = playerMap.get(key);
                    existing.negativeScore = Math.abs(player.score);
                    existing.score = existing.positiveScore - existing.negativeScore;
                } else {
                    playerMap.set(key, {
                        ...player,
                        score: -Math.abs(player.score),
                        positiveScore: 0,
                        negativeScore: Math.abs(player.score)
                    });
                }
            });
            
            normalizedCombined = Array.from(playerMap.values())
                .filter(p => p.name && p.name !== 'null')
                .sort((a, b) => b.score - a.score);
            
            // Add position rankings
            normalizedCombined.forEach((player, index) => {
                player.position = index + 1;
            });
        }
        
        // Calculate alliances from both combined data and alliance data
        let alliances = this.calculateAlliances(normalizedCombined);
        
        // If we have dedicated alliance data, merge it
        if (rawData.alliance && Array.isArray(rawData.alliance)) {
            const dedicatedAlliances = rawData.alliance
                .filter(a => a && a.Alliance && a.Alliance !== '')
                .map(alliance => ({
                    name: alliance.Alliance,
                    totalScore: parseFloat(alliance["Total Score"] || 0),
                    positiveScore: parseFloat(alliance.Positive || 0),
                    negativeScore: parseFloat(alliance.Negative || 0),
                    players: alliances.find(a => a.name === alliance.Alliance)?.players || []
                }));
            
            // Merge alliance data, preferring calculated player counts
            alliances = dedicatedAlliances.map(dedicated => {
                const calculated = alliances.find(a => a.name === dedicated.name);
                return {
                    ...dedicated,
                    players: calculated?.players || [],
                    averageScore: calculated?.players.length > 0 ? 
                        Math.round(dedicated.totalScore / calculated.players.length) : 0
                };
            });
        }
        
        // Calculate statistics
        const validScores = normalizedCombined.map(p => p.score || 0).filter(s => s !== 0 && !isNaN(s));
        const statistics = {
            totalPlayers: normalizedCombined.length,
            totalAlliances: alliances.length,
            totalScore: validScores.reduce((sum, score) => sum + score, 0),
            averageScore: validScores.length > 0 ? Math.round(validScores.reduce((sum, score) => sum + score, 0) / validScores.length) : 0,
            highestScore: validScores.length > 0 ? Math.max(...validScores) : 0,
            activeGames: normalizedCombined.length
        };
        
        const processed = {
            positive: normalizedPositive,
            negative: normalizedNegative,
            combined: normalizedCombined,
            alliances: alliances,
            statistics: statistics,
            metadata: {
                totalPlayers: statistics.totalPlayers,
                totalAlliances: statistics.totalAlliances,
                lastUpdate: new Date().toISOString(),
                dataFile: this.currentFile,
                source: 'local-json'
            }
        };

        console.log('✅ Data processed successfully:', {
            source: processed.metadata.source,
            totalPlayers: processed.statistics.totalPlayers,
            totalAlliances: processed.statistics.totalAlliances,
            positiveCount: normalizedPositive.length,
            negativeCount: normalizedNegative.length,
            combinedCount: normalizedCombined.length,
            allianceCount: alliances.length
        });

        return processed;
    }
    
    calculateAlliances(players) {
        const allianceMap = new Map();
        
        players.forEach(player => {
            if (player && player.alliance && player.alliance !== 'None' && player.alliance !== null) {
                if (!allianceMap.has(player.alliance)) {
                    allianceMap.set(player.alliance, {
                        name: player.alliance,
                        players: [],
                        totalScore: 0,
                        averageScore: 0,
                        positiveScore: 0,
                        negativeScore: 0
                    });
                }
                const alliance = allianceMap.get(player.alliance);
                alliance.players.push(player);
                alliance.totalScore += (player.score || 0);
                alliance.positiveScore += (player.positiveScore || 0);
                alliance.negativeScore += (player.negativeScore || 0);
            }
        });
        
        // Calculate averages
        allianceMap.forEach(alliance => {
            alliance.averageScore = alliance.players.length > 0 ? Math.round(alliance.totalScore / alliance.players.length) : 0;
        });
        
        return Array.from(allianceMap.values()).sort((a, b) => b.totalScore - a.totalScore);
    }
    
    updateUI() {
        if (!this.currentData) {
            console.warn('⚠️ No current data available for UI update');
            return;
        }
        
        console.log('🔄 Updating UI with current data...', {
            hasData: !!this.currentData,
            totalPlayers: this.currentData.metadata?.totalPlayers,
            totalAlliances: this.currentData.metadata?.totalAlliances,
            positiveLength: this.currentData.positive?.length,
            negativeLength: this.currentData.negative?.length,
            combinedLength: this.currentData.combined?.length,
            alliancesLength: this.currentData.alliances?.length
        });
        
        try {
            // Update header stats
            this.updateElement('totalPlayersDisplay', this.currentData.metadata?.totalPlayers || 0);
            this.updateElement('totalAlliancesDisplay', this.currentData.metadata?.totalAlliances || 0);
            this.updateElement('updateStatus', 'Live');
            
            // Update quick stats
            const stats = this.currentData.statistics || {};
            this.updateElement('totalScore', this.formatNumber(stats.totalScore || 0));
            this.updateElement('avgScore', this.formatNumber(stats.averageScore || 0));
            this.updateElement('highestScore', this.formatNumber(stats.highestScore || 0));
            this.updateElement('activeGames', stats.activeGames || 0);
            
            // Update all tabs
            this.updatePositiveTab();
            this.updateNegativeTab();
            this.updateCombinedTab();
            this.updateAllianceTab();
            this.updateFifthTab();
            
            // Update last update time
            this.updateElement('lastUpdate', new Date().toLocaleTimeString('de-DE'));
            
            // Update file selector
            const fileSelect = document.getElementById('dataFileSelect');
            if (fileSelect && this.currentFile) {
                fileSelect.value = this.currentFile;
            }
            
            console.log('✅ UI updated successfully');
        } catch (error) {
            console.error('❌ Error updating UI:', error);
        }
    }
    
    updatePositiveTab() {
        const container = document.getElementById('positivePlayersList');
        if (!container) return;
        
        const players = this.currentData.positive || [];
        const topPlayers = players.slice(0, 10);
        
        if (topPlayers.length === 0) {
            container.innerHTML = '<div class="no-data">Keine Positive Spieler verfügbar</div>';
            return;
        }
        
        container.innerHTML = topPlayers.map((player, index) => `
            <div class="player-item fade-in">
                <div class="player-rank">#${player.Position || index + 1}</div>
                <div class="player-name">${this.escapeHtml(player.Name || 'Unbekannt')}</div>
                <div class="player-score">${this.formatNumber(player.Score || 0)}</div>
                <div class="player-alliance">${this.escapeHtml(player.Alliance || 'None')}</div>
            </div>
        `).join('');
    }
    
    updateNegativeTab() {
        const container = document.getElementById('negativePlayersList');
        if (!container) return;
        
        const players = this.currentData.negative || [];
        const topPlayers = players.slice(0, 10);
        
        if (topPlayers.length === 0) {
            container.innerHTML = '<div class="no-data">Keine Negative Spieler verfügbar</div>';
            return;
        }
        
        container.innerHTML = topPlayers.map((player, index) => `
            <div class="player-item fade-in negative">
                <div class="player-rank">#${player.Position || index + 1}</div>
                <div class="player-name">${this.escapeHtml(player.Name || 'Unbekannt')}</div>
                <div class="player-score">${this.formatNumber(player.Score || 0)}</div>
                <div class="player-alliance">${this.escapeHtml(player.Alliance || 'None')}</div>
            </div>
        `).join('');
    }
    
    updateCombinedTab() {
        const container = document.getElementById('combinedPlayersList');
        if (!container) return;
        
        const players = this.currentData.combined || [];
        const topPlayers = players.slice(0, 10);
        
        if (topPlayers.length === 0) {
            container.innerHTML = '<div class="no-data">Keine Combined Rankings verfügbar</div>';
            return;
        }
        
        container.innerHTML = topPlayers.map((player, index) => `
            <div class="player-item fade-in">
                <div class="player-rank">#${player.position || index + 1}</div>
                <div class="player-name">${this.escapeHtml(player.name || 'Unbekannt')}</div>
                <div class="player-score">${this.formatNumber(player.score || 0)}</div>
                <div class="player-alliance">${this.escapeHtml(player.alliance || 'None')}</div>
            </div>
        `).join('');
    }
    
    updateAllianceTab() {
        const container = document.getElementById('allianceRanking');
        if (!container) return;
        
        const alliances = this.currentData.alliance || [];
        const topAlliances = alliances.slice(0, 5);
        
        if (topAlliances.length === 0) {
            container.innerHTML = '<div class="no-data">Keine Allianzdaten verfügbar</div>';
            return;
        }
        
        container.innerHTML = topAlliances.map((alliance, index) => `
            <div class="alliance-item fade-in">
                <div class="alliance-rank">#${index + 1}</div>
                <div class="alliance-name">${this.escapeHtml(alliance.Alliance || 'Unbekannt')}</div>
                <div class="alliance-score">${this.formatNumber(alliance["Total Score"] || 0)}</div>
                <div class="alliance-players">${this.formatNumber(alliance.Positive || 0)} / ${this.formatNumber(alliance.Negative || 0)}</div>
            </div>
        `).join('');
    }
    
    updateFifthTab() {
        const container = document.getElementById('fifthTabList');
        if (!container) return;
        
        // Try to find the 5th tab data - could be named differently
        const fifthData = this.currentData.fifth || this.currentData.summary || this.currentData.stats || this.currentData.extra;
        
        if (!fifthData) {
            container.innerHTML = '<div class="no-data">5. Tab Daten nicht verfügbar</div>';
            return;
        }
        
        // If it's an array, show as table
        if (Array.isArray(fifthData)) {
            container.innerHTML = `
                <div class="data-table">
                    <h3>5. Tab - ${fifthData.length} Einträge</h3>
                    <table class="table">
                        <thead>
                            <tr>
                                ${Object.keys(fifthData[0] || {}).map(key => `<th>${key}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${fifthData.slice(0, 10).map(row => `
                                <tr>
                                    ${Object.values(row || {}).map(value => `<td>${value}</td>`).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            // If it's an object, show as key-value pairs
            container.innerHTML = `
                <div class="data-grid">
                    <h3>5. Tab - Übersicht</h3>
                    ${Object.entries(fifthData).map(([key, value]) => `
                        <div class="data-item">
                            <strong>${key}:</strong> ${this.formatNumber(value) || value}
                        </div>
                    `).join('')}
                </div>
            `;
        }
    }
    
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }
    
    formatNumber(num) {
        return num.toLocaleString('de-DE');
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
            overlay.style.opacity = '1';
        }
    }
    
    hideLoading() {
        console.log('🔄 Hiding loading overlay...');
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            // Force hide immediately
            overlay.style.display = 'none';
            overlay.style.opacity = '0';
            console.log('✅ Loading overlay hidden');
        } else {
            console.warn('⚠️ Loading overlay not found');
        }
    }
    
    showError(message) {
        this.hideLoading();
        
        // Create error overlay
        const errorOverlay = document.createElement('div');
        errorOverlay.className = 'loading-overlay';
        errorOverlay.innerHTML = `
            <div class="loading-content">
                <div style="color: #ff6b6b; font-size: 3rem;">❌</div>
                <h2>Fehler</h2>
                <p>${message}</p>
                <button class="btn" onclick="location.reload()">Neu laden</button>
            </div>
        `;
        document.body.appendChild(errorOverlay);
    }
    
    async refreshData() {
        if (this.currentFile) {
            await this.loadData(this.currentFile);
        }
    }
    
    setupAutoRefresh() {
        console.log(`⏰ Setting up auto-refresh every ${this.config.autoRefreshInterval / 1000} seconds`);
        
        setInterval(() => {
            console.log('🔄 Auto-refreshing data...');
            this.refreshData();
        }, this.config.autoRefreshInterval);
    }
}

// Global functions for button clicks
window.loadDataFile = async function(filename) {
    if (window.dashboard) {
        await window.dashboard.loadData(filename);
    }
};

window.refreshData = async function() {
    if (window.dashboard) {
        const btn = event.target.closest('button');
        const icon = btn.querySelector('i');
        if (icon) icon.classList.add('fa-spin');
        
        await window.dashboard.refreshData();
        
        setTimeout(() => {
            if (icon) icon.classList.remove('fa-spin');
        }, 1000);
    }
};

window.switchTab = function(tabName) {
    console.log(`🔄 Switching to tab: ${tabName}`);
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });
    
    // Update tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Show selected tab
    const selectedPane = document.getElementById(`${tabName}-tab`);
    if (selectedPane) {
        selectedPane.classList.add('active');
    }
};

window.showAllPlayers = function(tabType = 'combined') {
    console.log(`📋 Showing all ${tabType} players...`);
    if (window.dashboard && window.dashboard.currentData) {
        const players = window.dashboard.currentData[tabType] || [];
        alert(`Alle ${tabType} Spieler anzeigen (${players.length} Spieler) - Detailansicht wird in Kürze implementiert`);
    }
};

window.showAllianceDetails = function() {
    console.log('🏛️ Showing alliance details...');
    if (window.dashboard && window.dashboard.currentData) {
        const alliances = window.dashboard.currentData.alliance || [];
        alert(`Allianz-Details (${alliances.length} Allianzen) - Detailansicht wird in Kürze implementiert`);
    }
};

window.showFifthTabDetails = function() {
    console.log('📊 Showing 5th tab details...');
    alert('5. Tab Details - Erweiterte Ansicht wird in Kürze implementiert');
};

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('📱 DOM ready, starting dashboard...');
    window.dashboard = new Dashboard();
    
    // Force hide loading overlay after 5 seconds as fallback
    setTimeout(() => {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay && overlay.style.display !== 'none') {
            console.log('⚠️ Force hiding loading overlay after timeout');
            overlay.style.display = 'none';
        }
    }, 5000);
});

// Handle errors
window.addEventListener('error', (e) => {
    console.error('❌ Global error:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('❌ Unhandled promise rejection:', e.reason);
});