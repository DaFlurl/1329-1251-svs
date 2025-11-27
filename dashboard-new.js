// AgentDaf1.1 Dashboard - Simplified and Working Version
class Dashboard {
    constructor() {
        this.currentData = null;
        this.currentFile = 'monday_data.json';
        this.init();
    }

    async init() {
        console.log('🚀 Initializing AgentDaf1.1 Dashboard...');
        
        // Hide loading overlay after initialization
        setTimeout(() => {
            this.hideLoading();
        }, 2000);

        // Load initial data
        await this.loadData(this.currentFile);
        
        // Setup auto-refresh
        this.setupAutoRefresh();
        
        console.log('✅ Dashboard initialized successfully');
    }

    async loadData(filename) {
        try {
            console.log(`📊 Loading data from: ${filename}`);
            
            const response = await fetch(`data/${filename}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.currentData = this.processData(data);
            this.currentFile = filename;
            
            console.log('✅ Data loaded successfully:', {
                players: this.currentData.combined.length,
                alliances: this.currentData.metadata.totalAlliances,
                file: filename
            });
            
            this.updateUI();
            
        } catch (error) {
            console.error('❌ Error loading data:', error);
            this.showError('Fehler beim Laden der Daten');
        }
    }

    processData(rawData) {
        // Ensure data structure is correct
        const processed = {
            positive: rawData.positive || [],
            negative: rawData.negative || [],
            combined: rawData.combined || [],
            metadata: rawData.metadata || {
                totalPlayers: 0,
                totalAlliances: 0,
                lastUpdate: new Date().toISOString(),
                dataFile: this.currentFile
            }
        };

        // Calculate statistics
        const allPlayers = processed.combined;
        const scores = allPlayers.map(p => p.score).filter(s => s > 0);
        const alliances = this.calculateAlliances(allPlayers);
        
        processed.statistics = {
            totalPlayers: allPlayers.length,
            totalAlliances: alliances.length,
            totalScore: scores.reduce((sum, score) => sum + score, 0),
            averageScore: scores.length > 0 ? Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length) : 0,
            highestScore: scores.length > 0 ? Math.max(...scores) : 0,
            activeGames: allPlayers.length
        };

        return processed;
    }

    calculateAlliances(players) {
        const allianceMap = new Map();
        
        players.forEach(player => {
            if (player.alliance && player.alliance !== 'None') {
                if (!allianceMap.has(player.alliance)) {
                    allianceMap.set(player.alliance, {
                        name: player.alliance,
                        players: [],
                        totalScore: 0,
                        averageScore: 0
                    });
                }
                const alliance = allianceMap.get(player.alliance);
                alliance.players.push(player);
                alliance.totalScore += player.score;
            }
        });
        
        // Calculate averages
        allianceMap.forEach(alliance => {
            alliance.averageScore = Math.round(alliance.totalScore / alliance.players.length);
        });
        
        return Array.from(allianceMap.values()).sort((a, b) => b.totalScore - a.totalScore);
    }

    updateUI() {
        if (!this.currentData) return;
        
        console.log('🔄 Updating UI with current data...');
        
        // Update header stats
        this.updateElement('totalPlayersDisplay', this.currentData.metadata.totalPlayers);
        this.updateElement('totalAlliancesDisplay', this.currentData.metadata.totalAlliances);
        this.updateElement('updateStatus', 'Live');
        
        // Update quick stats
        const stats = this.currentData.statistics;
        this.updateElement('totalScore', this.formatNumber(stats.totalScore));
        this.updateElement('avgScore', this.formatNumber(stats.averageScore));
        this.updateElement('highestScore', this.formatNumber(stats.highestScore));
        this.updateElement('activeGames', stats.activeGames);
        
        // Update top players
        this.updateTopPlayers();
        
        // Update alliance ranking
        this.updateAllianceRanking();
        
        // Update last update time
        this.updateElement('lastUpdate', new Date().toLocaleTimeString('de-DE'));
        
        console.log('✅ UI updated successfully');
    }

    updateTopPlayers() {
        const container = document.getElementById('topPlayersList');
        if (!container) return;
        
        const topPlayers = this.currentData.combined.slice(0, 10);
        
        container.innerHTML = topPlayers.map((player, index) => `
            <div class="player-item fade-in">
                <div class="player-rank">#${player.position || index + 1}</div>
                <div class="player-name">${this.escapeHtml(player.name)}</div>
                <div class="player-score">${this.formatNumber(player.score)}</div>
                <div class="player-alliance">${this.escapeHtml(player.alliance)}</div>
            </div>
        `).join('');
    }

    updateAllianceRanking() {
        const container = document.getElementById('allianceRanking');
        if (!container) return;
        
        const alliances = this.calculateAlliances(this.currentData.combined);
        const topAlliances = alliances.slice(0, 5);
        
        container.innerHTML = topAlliances.map((alliance, index) => `
            <div class="alliance-item fade-in">
                <div class="alliance-rank">#${index + 1}</div>
                <div class="alliance-name">${this.escapeHtml(alliance.name)}</div>
                <div class="alliance-score">${this.formatNumber(alliance.totalScore)}</div>
                <div class="alliance-players">${alliance.players.length} Spieler</div>
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

    setupAutoRefresh() {
        // Refresh data every 60 seconds
        setInterval(async () => {
            console.log('🔄 Auto-refreshing data...');
            await this.loadData(this.currentFile);
        }, 60000);
    }
}

// Global functions for button clicks
window.loadDataFile = async function(filename) {
    if (window.dashboard) {
        await window.dashboard.loadData(filename);
        document.getElementById('dataFileSelect').value = filename;
    }
};

window.refreshData = async function() {
    if (window.dashboard) {
        const btn = event.target.closest('button');
        const icon = btn.querySelector('i');
        icon.classList.add('fa-spin');
        
        await window.dashboard.loadData(window.dashboard.currentFile);
        
        setTimeout(() => {
            icon.classList.remove('fa-spin');
        }, 1000);
    }
};

window.showAllPlayers = function() {
    console.log('📋 Showing all players...');
    // This would open a modal or navigate to a detailed view
    alert('Alle Spieler anzeigen - Funktion wird in Kürze implementiert');
};

window.showAllianceDetails = function() {
    console.log('🏛️ Showing alliance details...');
    // This would open a modal or navigate to a detailed view
    alert('Allianz-Details - Funktion wird in Kürze implementiert');
};

window.installPWA = function() {
    console.log('📱 Installing PWA...');
    alert('PWA Installation - Funktion wird in Kürze implementiert');
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