/**
 * Scoreboard - Handles player rankings and display
 */
class Scoreboard {
  constructor() {
    this.currentView = 'combined';
    this.currentSort = 'position';
    this.currentFilter = '';
    this.currentPage = 1;
    this.itemsPerPage = 25;
    this.players = [];
    this.filteredPlayers = [];
    
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.setupSearch();
    this.setupFilters();
    
    // Listen for data updates
    document.addEventListener('dataLoaded', (e) => {
      this.handleDataUpdate(e.detail);
    });
  }

  setupEventListeners() {
    // Tab switching
    document.querySelectorAll('.nav-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        const targetTab = e.currentTarget.dataset.tab;
        this.switchTab(targetTab);
      });
    });
  }

  setupSearch() {
    const searchInput = document.getElementById('playerSearch');
    if (!searchInput) return;

    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        this.handleSearch(e.target.value);
      }, 300);
    });
  }

  setupFilters() {
    const allianceFilter = document.getElementById('allianceFilter');
    if (!allianceFilter) return;

    allianceFilter.addEventListener('change', (e) => {
      this.handleAllianceFilter(e.target.value);
    });
  }

  handleDataUpdate(dataDetail) {
    const { data } = dataDetail;
    this.players = data.combined || [];
    this.filteredPlayers = [...this.players];
    
    // Update UI components
    this.updateOverview();
    this.updatePlayersTable();
    this.updateAllianceStats();
    this.updateAllianceFilter();
    this.updateHeaderStats(data.metadata);
  }

  switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.nav-tab').forEach(tab => {
      tab.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
      content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');

    // Load tab-specific data
    this.loadTabContent(tabName);
  }

  loadTabContent(tabName) {
    switch (tabName) {
      case 'overview':
        this.updateOverview();
        break;
      case 'players':
        this.updatePlayersTable();
        break;
      case 'alliances':
        this.updateAllianceStats();
        break;
      case 'analytics':
        // Charts will be updated by charts.js
        break;
    }
  }

  updateOverview() {
    this.updateTopPlayers();
    this.updateAllianceRanking();
    this.updateQuickStats();
  }

  updateTopPlayers() {
    const container = document.getElementById('topPlayersList');
    if (!container) return;

    const topPlayers = this.getTopPlayers(10);
    
    container.innerHTML = topPlayers.map((player, index) => `
      <div class="player-item">
        <div class="player-rank">#${player.position}</div>
        <div class="player-name">${this.escapeHtml(player.name)}</div>
        <div class="player-score">${this.formatScore(player.score)}</div>
        <div class="player-alliance">${this.escapeHtml(player.alliance)}</div>
      </div>
    `).join('');
  }

  updateAllianceRanking() {
    const container = document.getElementById('allianceRanking');
    if (!container) return;

    const alliances = this.getTopAlliances(5);
    
    container.innerHTML = alliances.map((alliance, index) => `
      <div class="alliance-item">
        <div class="alliance-rank">#${index + 1}</div>
        <div class="alliance-name">${this.escapeHtml(alliance.name)}</div>
        <div class="alliance-score">${this.formatScore(alliance.totalScore)}</div>
        <div class="alliance-players">${alliance.players.length} Spieler</div>
      </div>
    `).join('');
  }

  updateQuickStats() {
    const stats = this.getStatistics();
    
    this.updateElement('totalScore', this.formatScore(stats.totalScore));
    this.updateElement('avgScore', this.formatScore(stats.averageScore));
    this.updateElement('highestScore', this.formatScore(stats.highestScore));
    this.updateElement('activeGames', stats.totalPlayers);
  }

  updatePlayersTable() {
    const container = document.getElementById('playersTable');
    if (!container) return;

    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    const pagePlayers = this.filteredPlayers.slice(startIndex, endIndex);

    container.innerHTML = `
      <table class="data-table">
        <thead>
          <tr>
            <th onclick="scoreboard.sortBy('position')">#</th>
            <th onclick="scoreboard.sortBy('name')">Spieler</th>
            <th onclick="scoreboard.sortBy('alliance')">Allianz</th>
            <th onclick="scoreboard.sortBy('score')">Punkte</th>
            <th>Monarch ID</th>
          </tr>
        </thead>
        <tbody>
          ${pagePlayers.map(player => `
            <tr>
              <td>${player.position}</td>
              <td>${this.escapeHtml(player.name)}</td>
              <td>${this.escapeHtml(player.alliance)}</td>
              <td>${this.formatScore(player.score)}</td>
              <td>${this.escapeHtml(player.monarchId)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      ${this.createPagination()}
    `;
  }

  updateAllianceStats() {
    const container = document.getElementById('allianceStats');
    if (!container) return;

    const alliances = this.getAlliances();
    
    container.innerHTML = alliances.map(alliance => `
      <div class="alliance-stat-card">
        <div class="alliance-name">${this.escapeHtml(alliance.name)}</div>
        <div class="alliance-metrics">
          <div class="metric">
            <div class="metric-value">${alliance.players.length}</div>
            <div class="metric-label">Spieler</div>
          </div>
          <div class="metric">
            <div class="metric-value">${this.formatScore(alliance.totalScore)}</div>
            <div class="metric-label">Gesamtpunkte</div>
          </div>
          <div class="metric">
            <div class="metric-value">${this.formatScore(alliance.averageScore)}</div>
            <div class="metric-label">Durchschnitt</div>
          </div>
          <div class="metric">
            <div class="metric-value">${this.formatScore(alliance.highestScore)}</div>
            <div class="metric-label">Höchste Punktzahl</div>
          </div>
        </div>
      </div>
    `).join('');
  }

  updateAllianceFilter() {
    const filter = document.getElementById('allianceFilter');
    if (!filter) return;

    const alliances = this.getAlliances();
    const currentValue = filter.value;
    
    filter.innerHTML = '<option value="">Alle Allianzen</option>' +
      alliances.map(alliance => `
        <option value="${this.escapeHtml(alliance.name)}">${this.escapeHtml(alliance.name)} (${alliance.players.length})</option>
      `).join('');
    
    filter.value = currentValue;
  }

  updateHeaderStats(metadata) {
    this.updateElement('totalPlayers', metadata.totalPlayers);
    this.updateElement('totalAlliances', metadata.totalAlliances);
  }

  handleSearch(query) {
    this.currentFilter = query.toLowerCase();
    this.applyFilters();
  }

  handleAllianceFilter(alliance) {
    this.currentAlliance = alliance;
    this.applyFilters();
  }

  applyFilters() {
    this.filteredPlayers = this.players.filter(player => {
      const matchesSearch = !this.currentFilter || 
        player.name.toLowerCase().includes(this.currentFilter) ||
        player.alliance.toLowerCase().includes(this.currentFilter) ||
        player.monarchId.toLowerCase().includes(this.currentFilter);
      
      const matchesAlliance = !this.currentAlliance || player.alliance === this.currentAlliance;
      
      return matchesSearch && matchesAlliance;
    });
    
    this.currentPage = 1;
    this.updatePlayersTable();
  }

  sortBy(field) {
    if (this.currentSort === field) {
      this.filteredPlayers.reverse();
    } else {
      this.currentSort = field;
      this.filteredPlayers.sort((a, b) => {
        switch (field) {
          case 'position':
            return a.position - b.position;
          case 'name':
            return a.name.localeCompare(b.name);
          case 'alliance':
            return a.alliance.localeCompare(b.alliance);
          case 'score':
            return b.score - a.score;
          default:
            return 0;
        }
      });
    }
    
    this.updatePlayersTable();
  }

  createPagination() {
    const totalPages = Math.ceil(this.filteredPlayers.length / this.itemsPerPage);
    if (totalPages <= 1) return '';

    let pagination = '<div class="pagination">';
    
    // Previous button
    if (this.currentPage > 1) {
      pagination += `<button onclick="scoreboard.goToPage(${this.currentPage - 1})">Vorherige</button>`;
    }
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
      if (i === 1 || i === totalPages || (i >= this.currentPage - 2 && i <= this.currentPage + 2)) {
        pagination += `<button class="${i === this.currentPage ? 'active' : ''}" onclick="scoreboard.goToPage(${i})">${i}</button>`;
      } else if (i === this.currentPage - 3 || i === this.currentPage + 3) {
        pagination += '<span>...</span>';
      }
    }
    
    // Next button
    if (this.currentPage < totalPages) {
      pagination += `<button onclick="scoreboard.goToPage(${this.currentPage + 1})">Nächste</button>`;
    }
    
    pagination += '</div>';
    return pagination;
  }

  goToPage(page) {
    this.currentPage = page;
    this.updatePlayersTable();
  }

  // Data helper methods
  getTopPlayers(count = 10) {
    return this.players.slice(0, count);
  }

  getTopAlliances(count = 5) {
    const alliances = this.getAlliances();
    return alliances.slice(0, count);
  }

  getAlliances() {
    const allianceMap = new Map();
    
    this.players.forEach(player => {
      if (player.alliance && player.alliance !== 'None') {
        if (!allianceMap.has(player.alliance)) {
          allianceMap.set(player.alliance, {
            name: player.alliance,
            players: [],
            totalScore: 0,
            averageScore: 0,
            highestScore: 0
          });
        }
        const alliance = allianceMap.get(player.alliance);
        alliance.players.push(player);
        alliance.totalScore += player.score;
        alliance.highestScore = Math.max(alliance.highestScore, player.score);
      }
    });
    
    // Calculate averages
    allianceMap.forEach(alliance => {
      alliance.averageScore = Math.round(alliance.totalScore / alliance.players.length);
    });
    
    return Array.from(allianceMap.values()).sort((a, b) => b.totalScore - a.totalScore);
  }

  getStatistics() {
    const scores = this.players.map(p => p.score).filter(s => s > 0);
    
    return {
      totalPlayers: this.players.length,
      totalAlliances: this.getAlliances().length,
      totalScore: scores.reduce((sum, score) => sum + score, 0),
      averageScore: scores.length > 0 ? Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length) : 0,
      highestScore: scores.length > 0 ? Math.max(...scores) : 0,
      lowestScore: scores.length > 0 ? Math.min(...scores) : 0
    };
  }

  // Utility methods
  formatScore(score) {
    return score.toLocaleString('de-DE');
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  updateElement(id, content) {
    const element = document.getElementById(id);
    if (element) {
      element.textContent = content;
    }
  }

  // Public API
  refresh() {
    this.handleDataUpdate({ data: window.dataLoader?.getCurrentData() });
  }

  setItemsPerPage(count) {
    this.itemsPerPage = count;
    this.currentPage = 1;
    this.updatePlayersTable();
  }

  exportToCSV() {
    const headers = ['Position', 'Name', 'Allianz', 'Punkte', 'Monarch ID'];
    const rows = this.filteredPlayers.map(player => [
      player.position,
      player.name,
      player.alliance,
      player.score,
      player.monarchId
    ]);
    
    const csv = [headers, ...rows]
      .map(row => row.map(cell => `"${cell}"`).join(','))
      .join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agentdaf-scoreboard-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }
}

// Initialize scoreboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.scoreboard = new Scoreboard();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Scoreboard;
}