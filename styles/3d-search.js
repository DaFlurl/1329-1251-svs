/**
 * 3D Search Manager
 * Advanced search functionality with 3D effects and dark theme support
 */

class SearchManager3D {
    constructor(options = {}) {
        this.options = {
            apiEndpoint: options.apiEndpoint || '/api/search',
            minQueryLength: options.minQueryLength || 2,
            maxResults: options.maxResults || 10,
            debounceDelay: options.debounceDelay || 300,
            enableFilters: options.enableFilters !== false,
            enableSuggestions: options.enableSuggestions !== false,
            ...options
        };
        
        this.query = '';
        this.filters = new Set();
        this.results = [];
        this.suggestions = [];
        this.isLoading = false;
        this.debounceTimer = null;
        
        this.init();
    }

    init() {
        this.createSearchHTML();
        this.bindEvents();
        this.setupKeyboardShortcuts();
        this.loadSearchHistory();
    }

    /**
     * Create search HTML structure
     */
    createSearchHTML() {
        const searchHTML = `
            <div class="search-container-3d">
                <div class="search-wrapper-3d">
                    <input 
                        type="text" 
                        class="search-input-3d" 
                        placeholder="Search dashboard, files, analytics..."
                        autocomplete="off"
                        role="searchbox"
                        aria-label="Search"
                    >
                    <div class="search-loading-3d"></div>
                    <button class="search-button-3d" type="button" aria-label="Submit search">
                        <svg class="search-icon-3d" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8"></circle>
                            <path d="m21 21-4.35-4.35"></path>
                        </svg>
                    </button>
                    
                    <div class="search-suggestions-3d">
                        <!-- Suggestions will be populated dynamically -->
                    </div>
                </div>
                
                ${this.options.enableFilters ? `
                    <div class="search-filters-3d">
                        <button class="filter-chip-3d" data-filter="all">All</button>
                        <button class="filter-chip-3d" data-filter="dashboard">Dashboard</button>
                        <button class="filter-chip-3d" data-filter="files">Files</button>
                        <button class="filter-chip-3d" data-filter="analytics">Analytics</button>
                        <button class="filter-chip-3d" data-filter="settings">Settings</button>
                    </div>
                ` : ''}
                
                <div class="search-results-3d">
                    <!-- Results will be populated dynamically -->
                </div>
            </div>
        `;

        // Insert search container at the beginning of main content
        const mainContent = document.querySelector('.main-content') || document.body;
        mainContent.insertAdjacentHTML('afterbegin', searchHTML);
        
        // Cache DOM elements
        this.elements = {
            container: document.querySelector('.search-container-3d'),
            input: document.querySelector('.search-input-3d'),
            button: document.querySelector('.search-button-3d'),
            loading: document.querySelector('.search-loading-3d'),
            suggestions: document.querySelector('.search-suggestions-3d'),
            results: document.querySelector('.search-results-3d'),
            filters: document.querySelectorAll('.filter-chip-3d')
        };
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Input events
        this.elements.input.addEventListener('input', (e) => this.handleInput(e));
        this.elements.input.addEventListener('focus', () => this.showSuggestions());
        this.elements.input.addEventListener('blur', () => {
            setTimeout(() => this.hideSuggestions(), 200);
        });

        // Button click
        this.elements.button.addEventListener('click', () => this.performSearch());

        // Filter clicks
        this.elements.filters.forEach(filter => {
            filter.addEventListener('click', () => this.toggleFilter(filter.dataset.filter));
        });

        // Keyboard navigation
        this.elements.input.addEventListener('keydown', (e) => this.handleKeydown(e));

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!this.elements.container.contains(e.target)) {
                this.hideSuggestions();
            }
        });

        // Theme change listener
        document.addEventListener('themechange', () => {
            this.updateSearchTheme();
        });
    }

    /**
     * Handle input changes with debouncing
     */
    handleInput(e) {
        const query = e.target.value.trim();
        this.query = query;

        // Clear previous debounce timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        if (query.length < this.options.minQueryLength) {
            this.hideSuggestions();
            this.clearResults();
            return;
        }

        // Debounce search
        this.debounceTimer = setTimeout(() => {
            if (this.options.enableSuggestions) {
                this.fetchSuggestions(query);
            }
            this.performSearch();
        }, this.options.debounceDelay);
    }

    /**
     * Handle keyboard navigation
     */
    handleKeydown(e) {
        const suggestions = this.elements.suggestions.querySelectorAll('.suggestion-item-3d');
        
        switch (e.key) {
            case 'Enter':
                e.preventDefault();
                if (suggestions.length > 0 && this.selectedSuggestionIndex >= 0) {
                    this.selectSuggestion(suggestions[this.selectedSuggestionIndex]);
                } else {
                    this.performSearch();
                }
                break;
                
            case 'Escape':
                this.hideSuggestions();
                this.elements.input.blur();
                break;
                
            case 'ArrowDown':
                e.preventDefault();
                this.navigateSuggestions(1);
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.navigateSuggestions(-1);
                break;
        }
    }

    /**
     * Navigate suggestions with keyboard
     */
    navigateSuggestions(direction) {
        const suggestions = this.elements.suggestions.querySelectorAll('.suggestion-item-3d');
        
        if (suggestions.length === 0) return;

        // Remove previous selection
        if (this.selectedSuggestionIndex >= 0) {
            suggestions[this.selectedSuggestionIndex].classList.remove('selected');
        }

        // Calculate new index
        this.selectedSuggestionIndex = Math.max(0, Math.min(
            suggestions.length - 1,
            (this.selectedSuggestionIndex || -1) + direction
        ));

        // Add selection to new item
        suggestions[this.selectedSuggestionIndex].classList.add('selected');
        this.elements.input.value = suggestions[this.selectedSuggestionIndex].querySelector('.suggestion-text-3d').textContent;
    }

    /**
     * Perform search
     */
    async performSearch() {
        if (this.query.length < this.options.minQueryLength) return;

        this.setLoading(true);
        
        try {
            const results = await this.fetchSearchResults(this.query);
            this.displayResults(results);
            this.saveSearchHistory(this.query);
        } catch (error) {
            console.error('Search error:', error);
            this.displayError('Search failed. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Fetch search results from API
     */
    async fetchSearchResults(query) {
        const filters = Array.from(this.filters).join(',');
        const params = new URLSearchParams({
            q: query,
            limit: this.options.maxResults,
            ...(filters && { filters })
        });

        const response = await fetch(`${this.options.apiEndpoint}?${params}`);
        
        if (!response.ok) {
            throw new Error(`Search failed: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Fetch suggestions
     */
    async fetchSuggestions(query) {
        try {
            const response = await fetch(`${this.options.apiEndpoint}/suggestions?q=${encodeURIComponent(query)}`);
            
            if (response.ok) {
                const suggestions = await response.json();
                this.displaySuggestions(suggestions);
            }
        } catch (error) {
            console.error('Suggestions error:', error);
        }
    }

    /**
     * Display suggestions
     */
    displaySuggestions(suggestions) {
        if (!suggestions || suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        const suggestionsHTML = suggestions.map(suggestion => `
            <div class="suggestion-item-3d" data-value="${suggestion.value}">
                <span class="suggestion-icon-3d">${this.getSuggestionIcon(suggestion.type)}</span>
                <span class="suggestion-text-3d">${suggestion.text}</span>
                <span class="suggestion-type-3d">${suggestion.type}</span>
            </div>
        `).join('');

        this.elements.suggestions.innerHTML = suggestionsHTML;
        
        // Bind click events to suggestions
        this.elements.suggestions.querySelectorAll('.suggestion-item-3d').forEach(item => {
            item.addEventListener('click', () => this.selectSuggestion(item));
        });

        this.showSuggestions();
    }

    /**
     * Get icon for suggestion type
     */
    getSuggestionIcon(type) {
        const icons = {
            dashboard: '📊',
            files: '📁',
            analytics: '📈',
            settings: '⚙️',
            user: '👤',
            data: '💾'
        };
        return icons[type] || '🔍';
    }

    /**
     * Select suggestion
     */
    selectSuggestion(item) {
        const value = item.dataset.value;
        this.elements.input.value = value;
        this.query = value;
        this.hideSuggestions();
        this.performSearch();
    }

    /**
     * Display search results
     */
    displayResults(results) {
        this.results = results;
        
        if (!results || results.length === 0) {
            this.displayNoResults();
            return;
        }

        const resultsHTML = results.map(result => `
            <div class="result-card-3d" data-type="${result.type}">
                <h3 class="result-title-3d">${this.highlightQuery(result.title)}</h3>
                <p class="result-description-3d">${this.highlightQuery(result.description)}</p>
                <div class="result-meta-3d">
                    <span class="result-tag-3d">${result.type}</span>
                    <span class="result-date-3d">${this.formatDate(result.date)}</span>
                    ${result.score ? `<span class="result-score-3d">Score: ${result.score}</span>` : ''}
                </div>
            </div>
        `).join('');

        this.elements.results.innerHTML = resultsHTML;
        this.elements.results.classList.add('active');

        // Bind click events to results
        this.elements.results.querySelectorAll('.result-card-3d').forEach(card => {
            card.addEventListener('click', () => this.handleResultClick(card));
        });
    }

    /**
     * Highlight query in text
     */
    highlightQuery(text) {
        if (!this.query) return text;
        
        const regex = new RegExp(`(${this.query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    /**
     * Display no results message
     */
    displayNoResults() {
        this.elements.results.innerHTML = `
            <div class="no-results-3d">
                <div class="no-results-icon-3d">🔍</div>
                <h3>No results found</h3>
                <p>Try different keywords or adjust your filters</p>
            </div>
        `;
        this.elements.results.classList.add('active');
    }

    /**
     * Display error message
     */
    displayError(message) {
        this.elements.results.innerHTML = `
            <div class="search-error-3d">
                <div class="error-icon-3d">⚠️</div>
                <h3>Search Error</h3>
                <p>${message}</p>
            </div>
        `;
        this.elements.results.classList.add('active');
    }

    /**
     * Handle result click
     */
    handleResultClick(card) {
        const result = this.results.find(r => r.type === card.dataset.type);
        if (result && result.url) {
            window.location.href = result.url;
        }
        
        // Track click analytics
        this.trackSearchClick(result);
    }

    /**
     * Toggle filter
     */
    toggleFilter(filter) {
        const filterButton = document.querySelector(`[data-filter="${filter}"]`);
        
        if (filter === 'all') {
            this.filters.clear();
            this.elements.filters.forEach(f => f.classList.remove('active'));
            filterButton.classList.add('active');
        } else {
            document.querySelector('[data-filter="all"]').classList.remove('active');
            
            if (this.filters.has(filter)) {
                this.filters.delete(filter);
                filterButton.classList.remove('active');
            } else {
                this.filters.add(filter);
                filterButton.classList.add('active');
            }
        }

        // Re-run search with new filters
        if (this.query) {
            this.performSearch();
        }
    }

    /**
     * Set loading state
     */
    setLoading(loading) {
        this.isLoading = loading;
        this.elements.loading.classList.toggle('active', loading);
        this.elements.button.disabled = loading;
    }

    /**
     * Show/hide suggestions
     */
    showSuggestions() {
        if (this.elements.suggestions.children.length > 0) {
            this.elements.suggestions.classList.add('active');
        }
    }

    hideSuggestions() {
        this.elements.suggestions.classList.remove('active');
        this.selectedSuggestionIndex = -1;
    }

    /**
     * Clear results
     */
    clearResults() {
        this.elements.results.innerHTML = '';
        this.elements.results.classList.remove('active');
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for search focus
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.elements.input.focus();
                this.elements.input.select();
            }
            
            // Escape to clear search
            if (e.key === 'Escape' && document.activeElement === this.elements.input) {
                this.clearSearch();
            }
        });
    }

    /**
     * Clear search
     */
    clearSearch() {
        this.elements.input.value = '';
        this.query = '';
        this.clearResults();
        this.hideSuggestions();
    }

    /**
     * Update search theme
     */
    updateSearchTheme() {
        // Theme is handled by CSS, but we can add any JS-specific theme updates here
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        
        // Update any theme-specific JavaScript behavior
        if (isDark) {
            this.elements.input.setAttribute('aria-label', 'Search (Dark mode)');
        } else {
            this.elements.input.setAttribute('aria-label', 'Search (Light mode)');
        }
    }

    /**
     * Save search history
     */
    saveSearchHistory(query) {
        const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
        const newHistory = [query, ...history.filter(q => q !== query)].slice(0, 10);
        localStorage.setItem('searchHistory', JSON.stringify(newHistory));
    }

    /**
     * Load search history
     */
    loadSearchHistory() {
        const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
        // Can be used to show recent searches
    }

    /**
     * Track search analytics
     */
    trackSearchClick(result) {
        // Send analytics data
        if (typeof gtag !== 'undefined') {
            gtag('event', 'search_click', {
                query: this.query,
                result_type: result.type,
                result_title: result.title
            });
        }
    }

    /**
     * Format date
     */
    formatDate(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
        if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
        return `${Math.floor(diffDays / 365)} years ago`;
    }

    /**
     * Get current search state
     */
    getState() {
        return {
            query: this.query,
            filters: Array.from(this.filters),
            results: this.results,
            isLoading: this.isLoading
        };
    }

    /**
     * Set search state
     */
    setState(state) {
        if (state.query) {
            this.elements.input.value = state.query;
            this.query = state.query;
        }
        
        if (state.filters) {
            this.filters.clear();
            state.filters.forEach(filter => this.toggleFilter(filter));
        }
        
        if (state.results) {
            this.displayResults(state.results);
        }
    }
}

// Auto-initialize when DOM is ready
let searchManager3D;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        searchManager3D = new SearchManager3D();
    });
} else {
    searchManager3D = new SearchManager3D();
}

// Global access
window.SearchManager3D = SearchManager3D;
window.searchManager3D = searchManager3D;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SearchManager3D;
}