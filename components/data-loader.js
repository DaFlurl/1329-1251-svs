/**
 * Data Loader - Handles JSON data loading and processing
 */
class DataLoader {
  constructor() {
    this.cache = new Map();
    this.loadingPromises = new Map();
    this.basePath = './data/';
    this.currentDataFile = 'monday_data.json';
    this.data = null;
    this.lastUpdate = null;
    this.refreshInterval = 60000; // 1 minute
    this.autoRefresh = null;
    
    this.init();
  }

  init() {
    this.setupDataSelector();
    this.setupRefreshButton();
    this.startAutoRefresh();
  }

  async loadData(filename = null) {
    const fileToLoad = filename || this.currentDataFile;
    
    // Check cache first
    if (this.cache.has(fileToLoad)) {
      const cached = this.cache.get(fileToLoad);
      if (Date.now() - cached.timestamp < this.refreshInterval) {
        return cached.data;
      }
    }

    // Check if already loading
    if (this.loadingPromises.has(fileToLoad)) {
      return this.loadingPromises.get(fileToLoad);
    }

    // Start loading
    const loadingPromise = this.fetchData(fileToLoad);
    this.loadingPromises.set(fileToLoad, loadingPromise);

    try {
      const data = await loadingPromise;
      this.cache.set(fileToLoad, {
        data,
        timestamp: Date.now()
      });
      this.data = data;
      this.lastUpdate = new Date();
      return data;
    } catch (error) {
      console.error('Error loading data:', error);
      throw error;
    } finally {
      this.loadingPromises.delete(fileToLoad);
    }
  }

  async fetchData(filename) {
    try {
      let dataUrl;
      
      // Determine URL pattern based on environment
      if (window.location.hostname === 'daflurl.github.io') {
        // GitHub Pages - files are in root
        dataUrl = filename;
      } else {
        // Local development - files are in data directory
        dataUrl = `${this.basePath}${filename}`;
      }
      
      console.log(`📡 Fetching data from: ${dataUrl}`);
      
      const response = await fetch(dataUrl);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status} for URL: ${dataUrl}`);
      }
      
      const data = await response.json();
      console.log('📋 Raw data received:', {
        keys: Object.keys(data),
        hasPositive: !!data.Positive,
        hasCombined: !!data.Combined
      });
      
      return this.processData(data);
    } catch (error) {
      console.error('❌ Failed to fetch data:', error);
      console.error('❌ Error details:', {
        filename: filename,
        hostname: window.location.hostname,
        error: error.message
      });
      // Try fallback data
      return this.getFallbackData();
    }
  }

  processData(rawData) {
    console.log('🔄 Processing raw data...', {
      keys: Object.keys(rawData),
      hasPositive: !!rawData.Positive,
      hasCombined: !!rawData.Combined,
      hasPositiveFlat: !!rawData.positive,
      hasCombinedFlat: !!rawData.combined
    });

    // Process and normalize data structure
    const processed = {
      positive: [],
      negative: [],
      combined: [],
      alliances: [],
      metadata: {
        totalPlayers: 0,
        totalAlliances: 0,
        lastUpdate: new Date().toISOString(),
        dataFile: this.currentDataFile,
        source: 'unknown'
      }
    };

    // Determine data source and extract accordingly
    if (rawData.Positive && rawData.Positive.sheets) {
      // GitHub Pages nested format
      processed.metadata.source = 'github-pages';
      
      // Extract positive data
      if (rawData.Positive.sheets.Positive && rawData.Positive.sheets.Positive.data) {
        processed.positive = rawData.Positive.sheets.Positive.data
          .filter(player => player.Name && player.Name !== null)
          .map((player, index) => ({
            position: parseInt(player.Position) || index + 1,
            name: player.Name,
            score: parseFloat(player.Score || 0),
            alliance: player.Alliance || 'None',
            monarchId: player['Monarch ID'] || 'N/A'
          }));
      }

      // Extract negative data
      if (rawData.Negative && rawData.Negative.sheets && rawData.Negative.sheets.Negative && rawData.Negative.sheets.Negative.data) {
        processed.negative = rawData.Negative.sheets.Negative.data
          .filter(player => player.Name && player.Name !== null)
          .map((player, index) => ({
            position: parseInt(player.Position) || index + 1,
            name: player.Name,
            score: parseFloat(player.Score || 0),
            alliance: player.Alliance || 'None',
            monarchId: player['Monarch ID'] || 'N/A'
          }));
      }

      // Extract combined data
      if (rawData.Combined && rawData.Combined.sheets && rawData.Combined.sheets.Combined && rawData.Combined.sheets.Combined.data) {
        processed.combined = rawData.Combined.sheets.Combined.data
          .filter(player => player.Name && player.Name !== null)
          .map((player, index) => ({
            position: parseInt(player.Position) || index + 1,
            name: player.Name,
            score: parseFloat(player['Total Score'] || 0),
            positiveScore: parseFloat(player.Positive || 0),
            negativeScore: parseFloat(player.Negative || 0),
            alliance: player.Alliance || 'None',
            monarchId: player['Monarch ID'] || 'N/A'
          }));
      }

      // Extract alliance data
      if (rawData.Alliance && rawData.Alliance.sheets && rawData.Alliance.sheets.Alliance && rawData.Alliance.sheets.Alliance.data) {
        processed.alliances = rawData.Alliance.sheets.Alliance.data
          .filter(alliance => alliance.Alliance && alliance.Alliance !== null)
          .map((alliance, index) => ({
            position: parseInt(alliance.Position) || index + 1,
            name: alliance.Alliance,
            totalScore: parseFloat(alliance['Total Score'] || 0),
            positiveScore: parseFloat(alliance.Positive || 0),
            negativeScore: parseFloat(alliance.Negative || 0)
          }));
      }

    } else {
      // Local flat format
      processed.metadata.source = 'local';
      
      // Process positive data
      if (rawData.positive && Array.isArray(rawData.positive)) {
        processed.positive = rawData.positive.map((player, index) => ({
          position: player.position || index + 1,
          name: player.name || player.Name || 'Unknown',
          score: parseInt(player.score || player.Score || 0),
          alliance: player.alliance || player.Alliance || 'None',
          monarchId: player.monarchId || player['Monarch ID'] || 'N/A'
        }));
      }

      // Process negative data
      if (rawData.negative && Array.isArray(rawData.negative)) {
        processed.negative = rawData.negative.map((player, index) => ({
          position: player.position || index + 1,
          name: player.name || player.Name || 'Unknown',
          score: parseInt(player.score || player.Score || 0),
          alliance: player.alliance || player.Alliance || 'None',
          monarchId: player.monarchId || player['Monarch ID'] || 'N/A'
        }));
      }

      // Process combined data
      if (rawData.combined && Array.isArray(rawData.combined)) {
        processed.combined = rawData.combined.map((player, index) => ({
          position: player.position || index + 1,
          name: player.name || player.Name || 'Unknown',
          score: parseInt(player.score || player.Score || 0),
          alliance: player.alliance || player.Alliance || 'None',
          monarchId: player.monarchId || player['Monarch ID'] || 'N/A'
        }));
      }
    }

    // If no combined data, create it from positive and negative
    if (processed.combined.length === 0 && (processed.positive.length > 0 || processed.negative.length > 0)) {
      const playerMap = new Map();
      
      // Add positive players
      processed.positive.forEach(player => {
        const key = player.name || player.monarchId;
        playerMap.set(key, {
          ...player,
          netScore: player.score,
          positiveScore: player.score,
          negativeScore: 0
        });
      });
      
      // Add negative players
      processed.negative.forEach(player => {
        const key = player.name || player.monarchId;
        if (playerMap.has(key)) {
          const existing = playerMap.get(key);
          existing.negativeScore = Math.abs(player.score);
          existing.netScore = existing.positiveScore - existing.negativeScore;
          existing.score = existing.netScore;
        } else {
          playerMap.set(key, {
            ...player,
            netScore: -Math.abs(player.score),
            positiveScore: 0,
            negativeScore: Math.abs(player.score),
            score: -Math.abs(player.score)
          });
        }
      });
      
      processed.combined = Array.from(playerMap.values())
        .filter(p => p.name && p.name !== 'null')
        .sort((a, b) => b.score - a.score);
      
      // Add position rankings
      processed.combined.forEach((player, index) => {
        player.position = index + 1;
      });
    }

    // Calculate metadata
    const allPlayers = [...processed.positive, ...processed.negative, ...processed.combined];
    const alliances = new Set(allPlayers.map(p => p.alliance).filter(a => a && a !== 'None'));
    
    processed.metadata.totalPlayers = processed.combined.length || allPlayers.length;
    processed.metadata.totalAlliances = alliances.size;

    console.log('✅ Data processed successfully:', {
      source: processed.metadata.source,
      positiveCount: processed.positive.length,
      negativeCount: processed.negative.length,
      combinedCount: processed.combined.length,
      allianceCount: processed.alliances.length,
      totalPlayers: processed.metadata.totalPlayers,
      totalAlliances: processed.metadata.totalAlliances
    });

    return processed;
  }

  getFallbackData() {
    return {
      positive: [],
      negative: [],
      combined: [],
      metadata: {
        totalPlayers: 0,
        totalAlliances: 0,
        lastUpdate: new Date().toISOString(),
        dataFile: 'fallback',
        error: true
      }
    };
  }

  setupDataSelector() {
    const selector = document.getElementById('dataSelector');
    if (!selector) return;

    selector.addEventListener('change', async (e) => {
      const selectedFile = e.target.value;
      this.currentDataFile = selectedFile;
      
      try {
        await this.loadData(selectedFile);
        this.dispatchDataLoaded();
        this.showToast('Daten erfolgreich geladen', 'success');
      } catch (error) {
        this.showToast('Fehler beim Laden der Daten', 'error');
      }
    });
  }

  setupRefreshButton() {
    const refreshBtn = document.getElementById('refreshBtn');
    if (!refreshBtn) return;

    refreshBtn.addEventListener('click', async () => {
      const icon = refreshBtn.querySelector('i');
      icon.classList.add('fa-spin');
      
      try {
        // Clear cache for current file
        this.cache.delete(this.currentDataFile);
        await this.loadData(this.currentDataFile);
        this.dispatchDataLoaded();
        this.showToast('Daten aktualisiert', 'success');
      } catch (error) {
        this.showToast('Fehler bei der Aktualisierung', 'error');
      } finally {
        icon.classList.remove('fa-spin');
      }
    });
  }

  startAutoRefresh() {
    this.autoRefresh = setInterval(async () => {
      try {
        await this.loadData(this.currentDataFile);
        this.dispatchDataLoaded();
        this.updateLastUpdateTime();
      } catch (error) {
        console.error('Auto refresh failed:', error);
      }
    }, this.refreshInterval);
  }

  stopAutoRefresh() {
    if (this.autoRefresh) {
      clearInterval(this.autoRefresh);
      this.autoRefresh = null;
    }
  }

  updateLastUpdateTime() {
    const updateElement = document.getElementById('lastUpdate');
    const statusElement = document.getElementById('updateStatus');
    
    if (updateElement) {
      updateElement.textContent = 'Live';
      updateElement.classList.add('pulse');
    }
    
    if (statusElement && this.lastUpdate) {
      const timeString = this.lastUpdate.toLocaleTimeString('de-DE');
      statusElement.textContent = `Zuletzt aktualisiert: ${timeString}`;
    }
  }

  dispatchDataLoaded() {
    console.log('Dispatching dataLoaded event with:', {
      dataKeys: this.data ? Object.keys(this.data) : 'null',
      playersCount: this.data ? this.data.combined?.length || 0 : 0,
      dataFile: this.currentDataFile
    });
    
    const event = new CustomEvent('dataLoaded', {
      detail: {
        data: this.data,
        lastUpdate: this.lastUpdate,
        dataFile: this.currentDataFile
      }
    });
    document.dispatchEvent(event);
  }

  showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}-state`;
    toast.innerHTML = `
      <div class="toast-content">
        <i class="fas ${this.getToastIcon(type)}"></i>
        <span>${message}</span>
      </div>
    `;

    container.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }, 3000);
  }

  getToastIcon(type) {
    const icons = {
      success: 'fa-check-circle',
      error: 'fa-exclamation-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
  }

  // Public API
  getCurrentData() {
    return this.data;
  }

  getPlayersByType(type = 'combined') {
    return this.data ? this.data[type] || [] : [];
  }

  getAllPlayers() {
    if (!this.data) return [];
    return [
      ...this.data.positive,
      ...this.data.negative,
      ...this.data.combined
    ];
  }

  getAlliances() {
    const players = this.getAllPlayers();
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

  searchPlayers(query, type = 'combined') {
    const players = this.getPlayersByType(type);
    if (!query) return players;
    
    const lowerQuery = query.toLowerCase();
    return players.filter(player => 
      player.name.toLowerCase().includes(lowerQuery) ||
      player.alliance.toLowerCase().includes(lowerQuery) ||
      player.monarchId.toLowerCase().includes(lowerQuery)
    );
  }

  filterByAlliance(alliance, type = 'combined') {
    const players = this.getPlayersByType(type);
    if (!alliance) return players;
    
    return players.filter(player => player.alliance === alliance);
  }

  getTopPlayers(count = 10, type = 'combined') {
    return this.getPlayersByType(type).slice(0, count);
  }

  getStatistics() {
    if (!this.data) return null;
    
    const allPlayers = this.getAllPlayers();
    const scores = allPlayers.map(p => p.score).filter(s => s > 0);
    
    return {
      totalPlayers: allPlayers.length,
      totalAlliances: this.getAlliances().length,
      totalScore: scores.reduce((sum, score) => sum + score, 0),
      averageScore: scores.length > 0 ? Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length) : 0,
      highestScore: scores.length > 0 ? Math.max(...scores) : 0,
      lowestScore: scores.length > 0 ? Math.min(...scores) : 0,
      medianScore: this.calculateMedian(scores)
    };
  }

  calculateMedian(scores) {
    if (scores.length === 0) return 0;
    
    const sorted = [...scores].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    
    return sorted.length % 2 === 0 
      ? Math.round((sorted[mid - 1] + sorted[mid]) / 2)
      : sorted[mid];
  }

  destroy() {
    this.stopAutoRefresh();
    this.cache.clear();
    this.loadingPromises.clear();
  }
}

// Initialize data loader when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.dataLoader = new DataLoader();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DataLoader;
}