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
    
    async loadInitialData() {
        // Try to load the most recent data file
        try {
            const response = await fetch('./data/file_list.json');
            if (response.ok) {
                const files = await response.json();
                if (files.length > 0) {
                    // Load the most recent file
                    await this.loadData(files[0]);
                    return;
                }
            }
        } catch (error) {
            console.log('No file list found, using default file');
        }
        
        // Fallback to default file
        await this.loadData('Monday, 24 November 2025 1329+1251 v 683+665.json');
    }
    
    async loadData(filename) {
        if (this.state.isLoading) return;
        
        console.log(`📊 Loading data file: ${filename}`);
        this.state.isLoading = true;
        this.showLoading();
        
        try {
            const response = await fetch(`${this.config.dataPath}${encodeURIComponent(filename)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const rawData = await response.json();
            console.log('✅ Raw data loaded:', {
                keys: Object.keys(rawData),
                hasPositive: !!rawData.positive,
                hasNegative: !!rawData.negative,
                hasCombined: !!rawData.combined
            });
            
            const processedData = this.processData(rawData);
            this.currentData = processedData;
            this.currentFile = filename;
            this.lastUpdate = new Date().toISOString();
            
            this.updateUI();
            this.hideLoading();
            
            console.log('✅ Data loaded and processed successfully');
            
        } catch (error) {
            console.error('❌ Error loading data:', error);
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
            if (!player || !player.Name || player.Name === null || player.Name === '') return null;
            
            return {
                position: parseInt(player.Position) || 0,
                name: player.Name,
                score: parseFloat(player["Total Score"] || player.Score || 0),
                alliance: player.Alliance || 'None',
                monarchId: parseFloat(player["Monarch ID"]) || 0,
                positiveScore: parseFloat(player.Positive || 0),
                negativeScore: parseFloat(player.Negative || 0)
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
        
        console.log('🔄 Updating UI with current data...');
        
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
            
            // Update top players
            this.updateTopPlayers();
            
            // Update alliance ranking
            this.updateAllianceRanking();
            
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
    
    updateTopPlayers() {
        const container = document.getElementById('topPlayersList');
        if (!container) {
            console.warn('⚠️ Top players container not found');
            return;
        }
        
        const players = this.currentData.combined || [];
        const topPlayers = players.slice(0, 10);
        
        if (topPlayers.length === 0) {
            container.innerHTML = '<div class="no-data">Keine Spielerdaten verfügbar</div>';
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
    
    updateAllianceRanking() {
        const container = document.getElementById('allianceRanking');
        if (!container) {
            console.warn('⚠️ Alliance ranking container not found');
            return;
        }
        
        const alliances = this.currentData.alliances || [];
        const topAlliances = alliances.slice(0, 5);
        
        if (topAlliances.length === 0) {
            container.innerHTML = '<div class="no-data">Keine Allianzdaten verfügbar</div>';
            return;
        }
        
        container.innerHTML = topAlliances.map((alliance, index) => `
            <div class="alliance-item fade-in">
                <div class="alliance-rank">#${index + 1}</div>
                <div class="alliance-name">${this.escapeHtml(alliance.name || 'Unbekannt')}</div>
                <div class="alliance-score">${this.formatNumber(alliance.totalScore || 0)}</div>
                <div class="alliance-players">${(alliance.players || []).length} Spieler</div>
            </div>
        `).join('');
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
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 300);
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

window.showAllPlayers = function() {
    console.log('📋 Showing all players...');
    alert('Alle Spieler anzeigen - Funktion wird in Kürze implementiert');
};

window.showAllianceDetails = function() {
    console.log('🏛️ Showing alliance details...');
    alert('Allianz-Details - Funktion wird in Kürze implementiert');
};

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('📱 DOM ready, starting dashboard...');
    window.dashboard = new Dashboard();
});

// Handle errors
window.addEventListener('error', (e) => {
    console.error('❌ Global error:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('❌ Unhandled promise rejection:', e.reason);
});