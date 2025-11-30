// Search functionality for SVS Dashboard
class SearchManager {
    constructor() {
        this.searchInput = null;
        this.searchResults = null;
        this.isSearchVisible = false;
        this.currentData = null;
        this.init();
    }

    init() {
        this.createSearchElements();
        this.bindEvents();
        this.setupKeyboardShortcuts();
    }

    createSearchElements() {
        // Create search container
        const searchContainer = document.createElement('div');
        searchContainer.className = 'search-container';
        searchContainer.innerHTML = `
            <div class="search-box">
                <i class="fas fa-search search-icon"></i>
                <input 
                    type="text" 
                    class="search-input" 
                    placeholder="Spieler, Allianz oder Monarch ID suchen..."
                    aria-label="Suche"
                >
                <button class="search-clear" aria-label="Suche löschen">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="search-results" id="searchResults"></div>
        `;

        // Insert search container after header
        const header = document.querySelector('header');
        if (header) {
            header.parentNode.insertBefore(searchContainer, header.nextSibling);
        }

        this.searchInput = searchContainer.querySelector('.search-input');
        this.searchResults = searchContainer.querySelector('.search-results');
    }

    bindEvents() {
        // Search input events
        this.searchInput.addEventListener('input', (e) => {
            this.performSearch(e.target.value);
        });

        this.searchInput.addEventListener('focus', () => {
            this.showSearch();
        });

        // Clear button
        const clearBtn = document.querySelector('.search-clear');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // Close search when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                this.hideSearch();
            }
        });

        // Get current data from window
        window.addEventListener('dataLoaded', (e) => {
            this.currentData = e.detail;
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.toggleSearch();
            }
            
            // Escape to close search
            if (e.key === 'Escape' && this.isSearchVisible) {
                this.hideSearch();
            }
        });
    }

    toggleSearch() {
        if (this.isSearchVisible) {
            this.hideSearch();
        } else {
            this.showSearch();
            this.searchInput.focus();
        }
    }

    showSearch() {
        this.isSearchVisible = true;
        document.querySelector('.search-container').classList.add('active');
    }

    hideSearch() {
        this.isSearchVisible = false;
        document.querySelector('.search-container').classList.remove('active');
        this.searchResults.innerHTML = '';
    }

    performSearch(query) {
        if (!query || query.length < 2) {
            this.searchResults.innerHTML = '';
            return;
        }

        const results = this.searchData(query);
        this.displayResults(results, query);
    }

    searchData(query) {
        const results = [];
        const lowerQuery = query.toLowerCase();

        // Get current data from global variable or window
        const data = window.currentData || this.currentData;
        if (!data) return results;

        // Search in positive players
        if (data.positive) {
            data.positive.forEach((player, index) => {
                if (this.matchesQuery(player, lowerQuery)) {
                    results.push({
                        type: 'positive',
                        player: player,
                        index: index,
                        score: player.Score || 0
                    });
                }
            });
        }

        // Search in negative players
        if (data.negative) {
            data.negative.forEach((player, index) => {
                if (this.matchesQuery(player, lowerQuery)) {
                    results.push({
                        type: 'negative',
                        player: player,
                        index: index,
                        score: Math.abs(player.Score || 0)
                    });
                }
            });
        }

        // Search in combined rankings
        if (data.combined) {
            data.combined.forEach((player, index) => {
                if (this.matchesQuery(player, lowerQuery)) {
                    results.push({
                        type: 'combined',
                        player: player,
                        index: index,
                        score: player["Total Score"] || 0
                    });
                }
            });
        }

        // Search in alliances
        if (data.alliance) {
            data.alliance.forEach((alliance, index) => {
                if (this.matchesAllianceQuery(alliance, lowerQuery)) {
                    results.push({
                        type: 'alliance',
                        alliance: alliance,
                        index: index,
                        score: alliance["Total Score"] || 0
                    });
                }
            });
        }

        // Search in monarchs
        if (data['all monarchs']) {
            data['all monarchs'].forEach((monarch, index) => {
                if (this.matchesMonarchQuery(monarch, lowerQuery)) {
                    results.push({
                        type: 'monarch',
                        monarch: monarch,
                        index: index,
                        score: 0
                    });
                }
            });
        }

        // Sort by score (descending) then by name
        return results.sort((a, b) => {
            if (b.score !== a.score) {
                return b.score - a.score;
            }
            const nameA = a.player?.Name || a.alliance?.Alliance || a.monarch?.Name || '';
            const nameB = b.player?.Name || b.alliance?.Alliance || b.monarch?.Name || '';
            return nameA.localeCompare(nameB);
        }).slice(0, 10); // Limit to 10 results
    }

    matchesQuery(player, query) {
        const name = (player.Name || '').toLowerCase();
        const alliance = (player.Alliance || '').toLowerCase();
        const monarchId = (player["Monarch ID"] || '').toString().toLowerCase();
        
        return name.includes(query) || 
               alliance.includes(query) || 
               monarchId.includes(query);
    }

    matchesAllianceQuery(alliance, query) {
        const allianceName = (alliance.Alliance || '').toLowerCase();
        return allianceName.includes(query);
    }

    matchesMonarchQuery(monarch, query) {
        const name = (monarch.Name || '').toLowerCase();
        const monarchId = (monarch["Monarch ID"] || '').toString().toLowerCase();
        const alliance = (monarch.Alliance || '').toLowerCase();
        
        return name.includes(query) || 
               monarchId.includes(query) || 
               alliance.includes(query);
    }

    displayResults(results, query) {
        if (results.length === 0) {
            this.searchResults.innerHTML = `
                <div class="search-no-results">
                    <i class="fas fa-search"></i>
                    <p>Keine Ergebnisse für "${query}"</p>
                </div>
            `;
            return;
        }

        const resultsHtml = results.map(result => {
            if (result.type === 'alliance') {
                return this.createAllianceResult(result);
            } else if (result.type === 'monarch') {
                return this.createMonarchResult(result);
            } else {
                return this.createPlayerResult(result);
            }
        }).join('');

        this.searchResults.innerHTML = `
            <div class="search-results-list">
                ${resultsHtml}
            </div>
        `;

        // Bind click events to results
        this.bindResultEvents();
    }

    createPlayerResult(result) {
        const player = result.player;
        const typeIcon = result.type === 'positive' ? 'fa-arrow-up' : 
                        result.type === 'negative' ? 'fa-arrow-down' : 'fa-chart-bar';
        const typeClass = result.type === 'negative' ? 'negative-score' : 'positive-score';
        
        return `
            <div class="search-result-item" data-type="${result.type}" data-index="${result.index}">
                <div class="result-icon">
                    <i class="fas ${typeIcon}"></i>
                </div>
                <div class="result-content">
                    <div class="result-name">${player.Name || 'Unbekannt'}</div>
                    <div class="result-details">
                        <span class="result-alliance">${player.Alliance || 'None'}</span>
                        <span class="result-score ${typeClass}">${this.formatNumber(player.Score || player["Total Score"] || 0)}</span>
                    </div>
                </div>
                <div class="result-action">
                    <i class="fas fa-arrow-right"></i>
                </div>
            </div>
        `;
    }

    createAllianceResult(result) {
        const alliance = result.alliance;
        
        return `
            <div class="search-result-item" data-type="alliance" data-index="${result.index}">
                <div class="result-icon">
                    <i class="fas fa-users"></i>
                </div>
                <div class="result-content">
                    <div class="result-name">${alliance.Alliance || 'Unbekannt'}</div>
                    <div class="result-details">
                        <span class="result-stats">P: ${alliance.Positive || 0} / N: ${alliance.Negative || 0}</span>
                        <span class="result-score">${this.formatNumber(alliance["Total Score"] || 0)}</span>
                    </div>
                </div>
                <div class="result-action">
                    <i class="fas fa-arrow-right"></i>
                </div>
            </div>
        `;
    }

    createMonarchResult(result) {
        const monarch = result.monarch;
        
        return `
            <div class="search-result-item" data-type="monarch" data-index="${result.index}">
                <div class="result-icon">
                    <i class="fas fa-crown"></i>
                </div>
                <div class="result-content">
                    <div class="result-name">${monarch.Name || 'Unbekannt'}</div>
                    <div class="result-details">
                        <span class="result-id">ID: ${monarch["Monarch ID"] || 'N/A'}</span>
                        <span class="result-alliance">${monarch.Alliance || 'None'}</span>
                    </div>
                </div>
                <div class="result-action">
                    <i class="fas fa-arrow-right"></i>
                </div>
            </div>
        `;
    }

    bindResultEvents() {
        const resultItems = this.searchResults.querySelectorAll('.search-result-item');
        resultItems.forEach(item => {
            item.addEventListener('click', () => {
                const type = item.dataset.type;
                const index = parseInt(item.dataset.index);
                this.navigateToResult(type, index);
            });
        });
    }

    navigateToResult(type, index) {
        // Switch to appropriate tab
        const tabMap = {
            'positive': 'positive',
            'negative': 'negative', 
            'combined': 'combined',
            'alliance': 'alliance',
            'monarch': 'monarchs'
        };

        const tabName = tabMap[type];
        if (tabName) {
            // Switch tab
            const tabBtn = document.querySelector(`[onclick="showTab('${tabName}')"]`);
            if (tabBtn) {
                tabBtn.click();
            }

            // Find and highlight the specific card
            setTimeout(() => {
                const container = document.getElementById(`${tabName}Players`);
                if (container) {
                    const cards = container.querySelectorAll('.player-card');
                    if (cards[index]) {
                        // Scroll to card
                        cards[index].scrollIntoView({ behavior: 'smooth', block: 'center' });
                        
                        // Highlight card
                        cards[index].classList.add('search-highlight');
                        setTimeout(() => {
                            cards[index].classList.remove('search-highlight');
                        }, 2000);

                        // Expand card to show details
                        cards[index].classList.add('expanded');
                        setTimeout(() => {
                            cards[index].classList.remove('expanded');
                        }, 3000);
                    }
                }
            }, 100);
        }

        // Hide search after navigation
        this.hideSearch();
        this.clearSearch();
    }

    clearSearch() {
        this.searchInput.value = '';
        this.searchResults.innerHTML = '';
    }

    formatNumber(num) {
        if (num === null || num === undefined) return '0';
        return new Intl.NumberFormat('de-DE').format(Math.round(num));
    }
}

// Initialize search when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.searchManager = new SearchManager();
    
    // Make current data available to search manager
    const originalLoadData = window.loadData;
    if (originalLoadData) {
        window.loadData = function(filename) {
            originalLoadData(filename).then(() => {
                if (window.currentData) {
                    window.searchManager.currentData = window.currentData;
                }
            });
        };
    }
});

// Add CSS animation for search highlight
const style = document.createElement('style');
style.textContent = `
    .search-highlight {
        animation: searchPulse 2s ease-in-out;
        border-color: #667eea !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    @keyframes searchPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
`;
document.head.appendChild(style);