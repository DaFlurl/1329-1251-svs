/**
 * AgentDaf1.1 Frontend API Integration
 * Complete integration with backend services
 */

class AgentDafAPI {
    constructor(baseURL = 'http://localhost:8080') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('agentdaf_token');
        this.refreshToken = localStorage.getItem('agentdaf_refresh_token');
        this.socket = null;
        this.setupSocketIO();
    }

    // ===== AUTHENTICATION =====
    
    async login(username, password) {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.token = data.tokens.access_token;
                this.refreshToken = data.tokens.refresh_token;
                
                localStorage.setItem('agentdaf_token', this.token);
                localStorage.setItem('agentdaf_refresh_token', this.refreshToken);
                localStorage.setItem('agentdaf_user', JSON.stringify(data.user));
                
                return { success: true, user: data.user };
            } else {
                return { success: false, error: data.error };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: 'Network error' };
        }
    }

    async logout() {
        try {
            if (this.token) {
                await fetch(`${this.baseURL}/api/auth/logout`, {
                    method: 'POST',
                    headers: this.getAuthHeaders()
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.clearAuth();
        }
    }

    async refreshToken() {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refresh_token: this.refreshToken })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.token = data.tokens.access_token;
                localStorage.setItem('agentdaf_token', this.token);
                return true;
            } else {
                this.clearAuth();
                return false;
            }
        } catch (error) {
            console.error('Token refresh error:', error);
            this.clearAuth();
            return false;
        }
    }

    clearAuth() {
        this.token = null;
        this.refreshToken = null;
        localStorage.removeItem('agentdaf_token');
        localStorage.removeItem('agentdaf_refresh_token');
        localStorage.removeItem('agentdaf_user');
    }

    isAuthenticated() {
        return !!this.token;
    }

    getCurrentUser() {
        const userStr = localStorage.getItem('agentdaf_user');
        return userStr ? JSON.parse(userStr) : null;
    }

    // ===== API HELPER METHODS =====
    
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getAuthHeaders(),
            ...options
        };

        try {
            let response = await fetch(url, config);
            
            // Handle token expiration
            if (response.status === 401 && this.refreshToken) {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    config.headers = this.getAuthHeaders();
                    response = await fetch(url, config);
                }
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request error for ${endpoint}:`, error);
            throw error;
        }
    }

    // ===== PLAYER API =====
    
    async getPlayers() {
        return this.makeRequest('/api/players');
    }

    async getPlayerDetails(username) {
        return this.makeRequest(`/api/player/${username}`);
    }

    async createPlayer(playerData) {
        return this.makeRequest('/api/player', {
            method: 'POST',
            body: JSON.stringify(playerData)
        });
    }

    async updatePlayer(username, updates) {
        return this.makeRequest(`/api/player/${username}`, {
            method: 'PUT',
            body: JSON.stringify(updates)
        });
    }

    // ===== ALLIANCE API =====
    
    async getAlliances() {
        return this.makeRequest('/api/alliances');
    }

    async createAlliance(allianceData) {
        return this.makeRequest('/api/alliance', {
            method: 'POST',
            body: JSON.stringify(allianceData)
        });
    }

    // ===== GAME SESSIONS =====
    
    async logGameSession(sessionData) {
        return this.makeRequest('/api/session', {
            method: 'POST',
            body: JSON.stringify(sessionData)
        });
    }

    // ===== FILE UPLOAD =====
    
    async uploadExcelFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.baseURL}/api/upload/excel`, {
            method: 'POST',
            headers: this.token ? { 'Authorization': `Bearer ${this.token}` } : {},
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        return await response.json();
    }

    // ===== SYSTEM API =====
    
    async getSystemStats() {
        return this.makeRequest('/api/stats');
    }

    async getSystemLogs(level = null, limit = 100) {
        const params = new URLSearchParams();
        if (level) params.append('level', level);
        params.append('limit', limit.toString());
        
        return this.makeRequest(`/api/logs?${params}`);
    }

    async logSystemEvent(level, message, module = 'frontend') {
        return this.makeRequest('/api/log', {
            method: 'POST',
            body: JSON.stringify({ level, message, module })
        });
    }

    async healthCheck() {
        return this.makeRequest('/api/health');
    }

    // ===== WEBSOCKET INTEGRATION =====
    
    setupSocketIO() {
        if (typeof io === 'undefined') {
            console.warn('Socket.IO not loaded');
            return;
        }

        this.socket = io(this.baseURL);
        
        this.socket.on('connect', () => {
            console.log('Connected to AgentDaf1.1 WebSocket');
            this.socket.emit('join_dashboard');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from AgentDaf1.1 WebSocket');
        });

        this.socket.on('data_updated', (data) => {
            console.log('Data updated:', data);
            this.onDataUpdated(data);
        });

        this.socket.on('player_created', (data) => {
            console.log('Player created:', data);
            this.onPlayerCreated(data);
        });

        this.socket.on('player_updated', (data) => {
            console.log('Player updated:', data);
            this.onPlayerUpdated(data);
        });

        this.socket.on('stats_update', (data) => {
            console.log('Stats updated:', data);
            this.onStatsUpdate(data);
        });

        this.socket.on('error', (data) => {
            console.error('WebSocket error:', data);
            this.onError(data);
        });
    }

    // Event handlers (to be overridden by implementing classes)
    onDataUpdated(data) {}
    onPlayerCreated(data) {}
    onPlayerUpdated(data) {}
    onStatsUpdate(data) {}
    onError(data) {}

    // Request real-time stats update
    requestStatsUpdate() {
        if (this.socket) {
            this.socket.emit('request_stats');
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// ===== ENHANCED DASHBOARD CLASS =====

class EnhancedDashboard {
    constructor() {
        this.api = new AgentDafAPI();
        this.currentData = {
            players: [],
            alliances: [],
            stats: {}
        };
        this.filters = {
            search: '',
            alliance: '',
            minScore: 0,
            maxScore: Infinity
        };
        this.sortBy = 'score';
        this.sortOrder = 'desc';
        this.init();
    }

    async init() {
        console.log('🚀 Initializing Enhanced AgentDaf1.1 Dashboard...');
        
        // Check authentication
        if (!this.api.isAuthenticated()) {
            this.showLoginModal();
            return;
        }

        // Load initial data
        await this.loadAllData();
        
        // Setup UI
        this.setupUI();
        
        // Setup real-time updates
        this.setupRealTimeUpdates();
        
        // Hide loading overlay
        this.hideLoading();
        
        console.log('✅ Enhanced Dashboard initialized successfully');
    }

    showLoginModal() {
        // Create login modal
        const modal = document.createElement('div');
        modal.className = 'login-modal';
        modal.innerHTML = `
            <div class="login-content">
                <h2>🔐 AgentDaf1.1 Login</h2>
                <form id="loginForm">
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" id="username" required>
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type="password" id="password" required>
                    </div>
                    <button type="submit">Login</button>
                </form>
                <div id="loginError" class="error-message"></div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Handle login
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            const result = await this.api.login(username, password);
            
            if (result.success) {
                document.body.removeChild(modal);
                this.init(); // Reinitialize after login
            } else {
                document.getElementById('loginError').textContent = result.error;
            }
        });
    }

    async loadAllData() {
        try {
            // Load data in parallel
            const [playersData, alliancesData, statsData] = await Promise.all([
                this.api.getPlayers(),
                this.api.getAlliances(),
                this.api.getSystemStats()
            ]);

            this.currentData.players = playersData.data || [];
            this.currentData.alliances = alliancesData.data || [];
            this.currentData.stats = statsData.data || {};

            console.log('✅ All data loaded successfully');
        } catch (error) {
            console.error('❌ Error loading data:', error);
            this.showError('Failed to load data: ' + error.message);
        }
    }

    setupUI() {
        // Setup search and filters
        this.setupSearchAndFilters();
        
        // Setup sorting
        this.setupSorting();
        
        // Setup file upload
        this.setupFileUpload();
        
        // Setup player management
        this.setupPlayerManagement();
        
        // Update UI with current data
        this.updateUI();
    }

    setupSearchAndFilters() {
        const searchInput = document.getElementById('searchInput');
        const allianceFilter = document.getElementById('allianceFilter');
        const minScoreFilter = document.getElementById('minScoreFilter');
        const maxScoreFilter = document.getElementById('maxScoreFilter');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filters.search = e.target.value.toLowerCase();
                this.updateUI();
            });
        }

        if (allianceFilter) {
            allianceFilter.addEventListener('change', (e) => {
                this.filters.alliance = e.target.value;
                this.updateUI();
            });
        }

        if (minScoreFilter) {
            minScoreFilter.addEventListener('input', (e) => {
                this.filters.minScore = parseInt(e.target.value) || 0;
                this.updateUI();
            });
        }

        if (maxScoreFilter) {
            maxScoreFilter.addEventListener('input', (e) => {
                this.filters.maxScore = parseInt(e.target.value) || Infinity;
                this.updateUI();
            });
        }
    }

    setupSorting() {
        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                const [sortBy, sortOrder] = e.target.value.split('-');
                this.sortBy = sortBy;
                this.sortOrder = sortOrder;
                this.updateUI();
            });
        }
    }

    setupFileUpload() {
        const fileInput = document.getElementById('fileInput');
        const uploadButton = document.getElementById('uploadButton');

        if (fileInput && uploadButton) {
            uploadButton.addEventListener('click', async () => {
                const file = fileInput.files[0];
                if (!file) {
                    alert('Please select a file');
                    return;
                }

                try {
                    uploadButton.disabled = true;
                    uploadButton.textContent = 'Uploading...';

                    const result = await this.api.uploadExcelFile(file);
                    
                    if (result.success) {
                        alert('File uploaded successfully!');
                        await this.loadAllData(); // Reload data
                    } else {
                        alert('Upload failed: ' + result.error);
                    }
                } catch (error) {
                    alert('Upload error: ' + error.message);
                } finally {
                    uploadButton.disabled = false;
                    uploadButton.textContent = 'Upload';
                }
            });
        }
    }

    setupPlayerManagement() {
        const addPlayerButton = document.getElementById('addPlayerButton');
        if (addPlayerButton) {
            addPlayerButton.addEventListener('click', () => {
                this.showAddPlayerModal();
            });
        }
    }

    showAddPlayerModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Add New Player</h3>
                <form id="addPlayerForm">
                    <div class="form-group">
                        <label>Name:</label>
                        <input type="text" id="playerName" required>
                    </div>
                    <div class="form-group">
                        <label>Score:</label>
                        <input type="number" id="playerScore" value="0">
                    </div>
                    <div class="form-group">
                        <label>Alliance:</label>
                        <input type="text" id="playerAlliance">
                    </div>
                    <div class="form-group">
                        <label>Level:</label>
                        <input type="number" id="playerLevel" value="1">
                    </div>
                    <div class="form-actions">
                        <button type="submit">Add Player</button>
                        <button type="button" onclick="this.closest('.modal').remove()">Cancel</button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        document.getElementById('addPlayerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const playerData = {
                name: document.getElementById('playerName').value,
                score: parseInt(document.getElementById('playerScore').value) || 0,
                alliance: document.getElementById('playerAlliance').value,
                level: parseInt(document.getElementById('playerLevel').value) || 1
            };

            try {
                const result = await this.api.createPlayer(playerData);
                if (result.success) {
                    document.body.removeChild(modal);
                    await this.loadAllData(); // Reload data
                } else {
                    alert('Failed to add player: ' + result.error);
                }
            } catch (error) {
                alert('Error adding player: ' + error.message);
            }
        });
    }

    setupRealTimeUpdates() {
        // Setup WebSocket event handlers
        this.api.onDataUpdated = (data) => {
            console.log('Real-time data update:', data);
            this.loadAllData(); // Reload all data
        };

        this.api.onPlayerCreated = (data) => {
            console.log('Real-time player creation:', data);
            this.loadAllData(); // Reload all data
        };

        this.api.onPlayerUpdated = (data) => {
            console.log('Real-time player update:', data);
            this.loadAllData(); // Reload all data
        };

        this.api.onStatsUpdate = (data) => {
            console.log('Real-time stats update:', data);
            this.currentData.stats = data;
            this.updateStatsDisplay();
        };

        this.api.onError = (data) => {
            console.error('Real-time error:', data);
            this.showError('Real-time update error: ' + data.message);
        };
    }

    getFilteredAndSortedPlayers() {
        let players = [...this.currentData.players];

        // Apply filters
        if (this.filters.search) {
            players = players.filter(player => 
                player.name.toLowerCase().includes(this.filters.search) ||
                (player.alliance && player.alliance.toLowerCase().includes(this.filters.search))
            );
        }

        if (this.filters.alliance) {
            players = players.filter(player => player.alliance === this.filters.alliance);
        }

        players = players.filter(player => 
            player.score >= this.filters.minScore && player.score <= this.filters.maxScore
        );

        // Apply sorting
        players.sort((a, b) => {
            let aVal = a[this.sortBy];
            let bVal = b[this.sortBy];

            if (typeof aVal === 'string') aVal = aVal.toLowerCase();
            if (typeof bVal === 'string') bVal = bVal.toLowerCase();

            if (this.sortOrder === 'asc') {
                return aVal > bVal ? 1 : -1;
            } else {
                return aVal < bVal ? 1 : -1;
            }
        });

        return players;
    }

    updateUI() {
        this.updatePlayerTable();
        this.updateAllianceTable();
        this.updateStatsDisplay();
        this.updateFilters();
    }

    updatePlayerTable() {
        const tbody = document.getElementById('playerTableBody');
        if (!tbody) return;

        const players = this.getFilteredAndSortedPlayers();
        
        tbody.innerHTML = players.map((player, index) => `
            <tr>
                <td>${index + 1}</td>
                <td>${this.escapeHtml(player.name)}</td>
                <td>${player.score.toLocaleString()}</td>
                <td>${this.escapeHtml(player.alliance || 'None')}</td>
                <td>${player.level || 1}</td>
                <td>
                    <button onclick="dashboard.editPlayer('${player.name}')" class="btn-small">Edit</button>
                    <button onclick="dashboard.viewPlayerDetails('${player.name}')" class="btn-small">View</button>
                </td>
            </tr>
        `).join('');
    }

    updateAllianceTable() {
        const tbody = document.getElementById('allianceTableBody');
        if (!tbody) return;

        tbody.innerHTML = this.currentData.alliances.map((alliance, index) => `
            <tr>
                <td>${index + 1}</td>
                <td>${this.escapeHtml(alliance.name)}</td>
                <td>${alliance.total_score.toLocaleString()}</td>
                <td>${alliance.members}</td>
                <td>${this.escapeHtml(alliance.description || '')}</td>
            </tr>
        `).join('');
    }

    updateStatsDisplay() {
        const stats = this.currentData.stats;
        
        // Update player stats
        this.updateElement('totalPlayers', stats.players?.total || 0);
        this.updateElement('activePlayers', stats.players?.active || 0);
        
        // Update alliance stats
        this.updateElement('totalAlliances', stats.alliances?.total || 0);
        this.updateElement('activeAlliances', stats.alliances?.active || 0);
        
        // Update system stats
        this.updateElement('databaseSize', stats.database?.database_size_mb || 0);
        this.updateElement('lastUpdate', new Date().toLocaleString());
    }

    updateFilters() {
        // Update alliance filter options
        const allianceFilter = document.getElementById('allianceFilter');
        if (allianceFilter) {
            const alliances = [...new Set(this.currentData.players.map(p => p.alliance).filter(Boolean))];
            const currentValue = allianceFilter.value;
            
            allianceFilter.innerHTML = '<option value="">All Alliances</option>' +
                alliances.map(alliance => 
                    `<option value="${this.escapeHtml(alliance)}">${this.escapeHtml(alliance)}</option>`
                ).join('');
            
            allianceFilter.value = currentValue;
        }
    }

    async editPlayer(username) {
        const player = this.currentData.players.find(p => p.name === username);
        if (!player) return;

        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Edit Player: ${this.escapeHtml(username)}</h3>
                <form id="editPlayerForm">
                    <div class="form-group">
                        <label>Score:</label>
                        <input type="number" id="editPlayerScore" value="${player.score}">
                    </div>
                    <div class="form-group">
                        <label>Alliance:</label>
                        <input type="text" id="editPlayerAlliance" value="${this.escapeHtml(player.alliance || '')}">
                    </div>
                    <div class="form-group">
                        <label>Level:</label>
                        <input type="number" id="editPlayerLevel" value="${player.level || 1}">
                    </div>
                    <div class="form-actions">
                        <button type="submit">Update</button>
                        <button type="button" onclick="this.closest('.modal').remove()">Cancel</button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        document.getElementById('editPlayerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const updates = {
                score: parseInt(document.getElementById('editPlayerScore').value) || 0,
                alliance: document.getElementById('editPlayerAlliance').value,
                level: parseInt(document.getElementById('editPlayerLevel').value) || 1
            };

            try {
                const result = await this.api.updatePlayer(username, updates);
                if (result.success) {
                    document.body.removeChild(modal);
                    await this.loadAllData(); // Reload data
                } else {
                    alert('Failed to update player: ' + result.error);
                }
            } catch (error) {
                alert('Error updating player: ' + error.message);
            }
        });
    }

    async viewPlayerDetails(username) {
        try {
            const result = await this.api.getPlayerDetails(username);
            if (result.success) {
                this.showPlayerDetailsModal(result.data);
            } else {
                alert('Failed to get player details: ' + result.error);
            }
        } catch (error) {
            alert('Error getting player details: ' + error.message);
        }
    }

    showPlayerDetailsModal(data) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Player Details: ${this.escapeHtml(data.player.name)}</h3>
                <div class="player-details">
                    <p><strong>Score:</strong> ${data.player.score.toLocaleString()}</p>
                    <p><strong>Alliance:</strong> ${this.escapeHtml(data.player.alliance || 'None')}</p>
                    <p><strong>Level:</strong> ${data.player.level || 1}</p>
                    <p><strong>Created:</strong> ${new Date(data.player.created_at).toLocaleString()}</p>
                    <p><strong>Last Updated:</strong> ${new Date(data.player.updated_at).toLocaleString()}</p>
                </div>
                
                <h4>Recent Game Sessions</h4>
                <div class="sessions-list">
                    ${data.sessions.length > 0 ? data.sessions.map(session => `
                        <div class="session-item">
                            <span>${session.session_type}</span>
                            <span>Score: ${session.score_change > 0 ? '+' : ''}${session.score_change}</span>
                            <span>${new Date(session.created_at).toLocaleString()}</span>
                        </div>
                    `).join('') : '<p>No recent sessions</p>'}
                </div>
                
                <div class="form-actions">
                    <button onclick="this.closest('.modal').remove()">Close</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
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
        alert('Error: ' + message);
    }

    // Cleanup
    destroy() {
        this.api.disconnect();
    }
}

// Global instance
let dashboard;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new EnhancedDashboard();
});

// Export for use in other scripts
window.AgentDafAPI = AgentDafAPI;
window.EnhancedDashboard = EnhancedDashboard;
window.dashboard = dashboard;