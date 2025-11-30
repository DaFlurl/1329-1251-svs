/**
 * AgentDaf1.1 Enterprise Dashboard
 * Premium Gaming Dashboard with Advanced Animations and Real-time Features
 */

class EnterpriseDashboard {
    constructor() {
        this.currentData = null;
        this.currentPage = 1;
        this.itemsPerPage = 50;
        this.charts = {};
        this.websocket = null;
        this.config = null;
        this.searchTerm = '';
        this.allianceFilter = '';
        this.sortColumn = 'score';
        this.sortDirection = 'desc';
        
        this.init();
    }

    async init() {
        console.log('🚀 Initializing AgentDaf1.1 Enterprise Dashboard...');
        
        // Initialize GSAP animations
        gsap.registerPlugin(ScrollTrigger);
        
        // Load configuration
        await this.loadConfig();
        
        // Initialize components
        this.initializeCharts();
        this.setupEventListeners();
        this.setupWebSocket();
        
        // Load initial data
        await this.loadData();
        
        // Setup auto-refresh
        this.setupAutoRefresh();
        
        // Initialize animations
        this.initializeAnimations();
        
        // Hide loading overlay with animation
        setTimeout(() => {
            this.hideLoadingOverlay();
        }, 2000);
        
        console.log('✅ Enterprise Dashboard initialized successfully');
    }

    async loadConfig() {
        try {
            const response = await fetch('../config/config.json');
            this.config = await response.json();
            console.log('✅ Configuration loaded');
        } catch (error) {
            console.error('❌ Error loading configuration:', error);
            this.config = this.getDefaultConfig();
        }
    }

    getDefaultConfig() {
        return {
            dashboard: {
                auto_refresh_interval: 30000,
                max_players_display: 1000,
                animations_enabled: true
            }
        };
    }

    initializeCharts() {
        // Score Distribution Chart
        const scoreCtx = document.getElementById('scoreChart').getContext('2d');
        this.charts.score = new Chart(scoreCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Punkte',
                    data: [],
                    backgroundColor: 'rgba(59, 130, 246, 0.5)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 2,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                }
            }
        });

        // Alliance Performance Chart
        const allianceCtx = document.getElementById('allianceChart').getContext('2d');
        this.charts.alliance = new Chart(allianceCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(139, 92, 246, 0.8)',
                        'rgba(236, 72, 153, 0.8)',
                        'rgba(34, 197, 94, 0.8)',
                        'rgba(251, 146, 60, 0.8)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            padding: 20
                        }
                    }
                }
            }
        });
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase();
            this.currentPage = 1;
            this.updatePlayersTable();
        });

        // Alliance filter
        const allianceFilter = document.getElementById('allianceFilter');
        allianceFilter.addEventListener('change', (e) => {
            this.allianceFilter = e.target.value;
            this.currentPage = 1;
            this.updatePlayersTable();
        });

        // File upload
        const fileInput = document.getElementById('fileInput');
        fileInput.addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files[0]);
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'r':
                        e.preventDefault();
                        this.refreshData();
                        break;
                    case 'u':
                        e.preventDefault();
                        this.showUploadModal();
                        break;
                    case '/':
                        e.preventDefault();
                        searchInput.focus();
                        break;
                }
            }
        });
    }

    setupWebSocket() {
        try {
            this.websocket = new WebSocket('ws://localhost:8004/ws');
            
            this.websocket.onopen = () => {
                console.log('📡 WebSocket connected');
                this.showToast('Verbunden mit Echtzeit-Updates', 'success');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleRealtimeUpdate(data);
            };
            
            this.websocket.onclose = () => {
                console.log('📡 WebSocket disconnected');
                setTimeout(() => this.setupWebSocket(), 5000); // Reconnect after 5 seconds
            };
            
            this.websocket.onerror = (error) => {
                console.error('📡 WebSocket error:', error);
            };
        } catch (error) {
            console.warn('📡 WebSocket not available, falling back to polling');
        }
    }

    async loadData() {
        try {
            console.log('📊 Loading dashboard data...');
            
            // Load players data
            const playersResponse = await fetch('/api/data/players');
            const players = await playersResponse.json();
            
            // Load alliances data
            const alliancesResponse = await fetch('/api/data/alliances');
            const alliances = await alliancesResponse.json();
            
            // Load statistics
            const statsResponse = await fetch('/api/data/statistics');
            const stats = await statsResponse.json();
            
            this.currentData = {
                players: players,
                alliances: alliances,
                statistics: stats
            };
            
            // Update UI components
            this.updateMetrics(stats);
            this.updateCharts(players, alliances);
            this.updatePlayersTable();
            this.updateAllianceGrid(alliances);
            this.populateAllianceFilter(alliances);
            
            console.log('✅ Data loaded successfully');
            
        } catch (error) {
            console.error('❌ Error loading data:', error);
            this.showToast('Fehler beim Laden der Daten', 'error');
        }
    }

    updateMetrics(stats) {
        // Animate metric updates
        this.animateValue('totalPlayers', 0, stats.total_players || 0, 2000);
        this.animateValue('totalAlliances', 0, stats.total_alliances || 0, 2000);
        this.animateValue('totalScore', 0, stats.total_score || 0, 2000);
        this.animateValue('avgScore', 0, Math.round(stats.avg_score || 0), 2000);
    }

    animateValue(elementId, start, end, duration) {
        const element = document.getElementById(elementId);
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = this.formatNumber(Math.round(current));
        }, 16);
    }

    formatNumber(num) {
        return new Intl.NumberFormat('de-DE').format(num);
    }

    updateCharts(players, alliances) {
        // Update score distribution chart
        const scoreRanges = this.calculateScoreRanges(players);
        this.charts.score.data.labels = scoreRanges.labels;
        this.charts.score.data.datasets[0].data = scoreRanges.data;
        this.charts.score.update('active');

        // Update alliance performance chart
        const topAlliances = alliances.slice(0, 5);
        this.charts.alliance.data.labels = topAlliances.map(a => a.name);
        this.charts.alliance.data.datasets[0].data = topAlliances.map(a => a.total_score);
        this.charts.alliance.update('active');
    }

    calculateScoreRanges(players) {
        const ranges = [
            { label: '0-1000', min: 0, max: 1000 },
            { label: '1001-5000', min: 1001, max: 5000 },
            { label: '5001-10000', min: 5001, max: 10000 },
            { label: '10001-20000', min: 10001, max: 20000 },
            { label: '20000+', min: 20001, max: Infinity }
        ];

        const data = ranges.map(range => 
            players.filter(p => p.score >= range.min && p.score <= range.max).length
        );

        return {
            labels: ranges.map(r => r.label),
            data: data
        };
    }

    updatePlayersTable() {
        if (!this.currentData) return;

        let filteredPlayers = this.currentData.players;

        // Apply search filter
        if (this.searchTerm) {
            filteredPlayers = filteredPlayers.filter(player =>
                player.name.toLowerCase().includes(this.searchTerm) ||
                player.alliance.toLowerCase().includes(this.searchTerm)
            );
        }

        // Apply alliance filter
        if (this.allianceFilter) {
            filteredPlayers = filteredPlayers.filter(player =>
                player.alliance === this.allianceFilter
            );
        }

        // Apply sorting
        filteredPlayers.sort((a, b) => {
            let aVal = a[this.sortColumn];
            let bVal = b[this.sortColumn];
            
            if (typeof aVal === 'string') {
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
            }
            
            if (this.sortDirection === 'asc') {
                return aVal > bVal ? 1 : -1;
            } else {
                return aVal < bVal ? 1 : -1;
            }
        });

        // Pagination
        const totalPlayers = filteredPlayers.length;
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = Math.min(startIndex + this.itemsPerPage, totalPlayers);
        const paginatedPlayers = filteredPlayers.slice(startIndex, endIndex);

        // Update table body
        const tbody = document.getElementById('playersTableBody');
        tbody.innerHTML = paginatedPlayers.map((player, index) => {
            const rank = startIndex + index + 1;
            const rankClass = rank <= 3 ? `rank-${rank}` : 'rank-default';
            const changeClass = player.change > 0 ? 'positive' : player.change < 0 ? 'negative' : '';
            const changeIcon = player.change > 0 ? 'fa-arrow-up' : player.change < 0 ? 'fa-arrow-down' : 'fa-minus';
            
            return `
                <tr class="fade-in">
                    <td>
                        <span class="rank-badge ${rankClass}">${rank}</span>
                    </td>
                    <td class="font-semibold">${this.escapeHtml(player.name)}</td>
                    <td>${this.escapeHtml(player.alliance)}</td>
                    <td class="font-bold">${this.formatNumber(player.score)}</td>
                    <td>
                        ${player.change !== undefined ? `
                            <span class="score-change ${changeClass}">
                                <i class="fas ${changeIcon}"></i>
                                ${Math.abs(player.change)}
                            </span>
                        ` : '-'}
                    </td>
                    <td>
                        <span class="badge badge-info">Aktiv</span>
                    </td>
                </tr>
            `;
        }).join('');

        // Update pagination info
        document.getElementById('showingFrom').textContent = startIndex + 1;
        document.getElementById('showingTo').textContent = endIndex;
        document.getElementById('totalPlayersCount').textContent = totalPlayers;

        // Update pagination buttons
        document.getElementById('prevBtn').disabled = this.currentPage === 1;
        document.getElementById('nextBtn').disabled = endIndex >= totalPlayers;

        // Animate table rows
        gsap.fromTo('#playersTableBody tr', 
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.3, stagger: 0.05 }
        );
    }

    updateAllianceGrid(alliances) {
        const grid = document.getElementById('allianceGrid');
        grid.innerHTML = alliances.slice(0, 6).map((alliance, index) => `
            <div class="card fade-in">
                <div class="flex items-center justify-between mb-4">
                    <h4 class="text-lg font-bold text-white">${this.escapeHtml(alliance.name)}</h4>
                    <span class="rank-badge rank-default">${index + 1}</span>
                </div>
                <div class="space-y-2">
                    <div class="flex justify-between">
                        <span class="text-white/70">Gesamtpunkte</span>
                        <span class="font-bold">${this.formatNumber(alliance.total_score)}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-white/70">Mitglieder</span>
                        <span class="font-bold">${alliance.member_count}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-white/70">Durchschnitt</span>
                        <span class="font-bold">${this.formatNumber(Math.round(alliance.average_score))}</span>
                    </div>
                </div>
                <div class="mt-4">
                    <div class="progress">
                        <div class="progress-bar" style="width: ${(alliance.total_score / Math.max(...alliances.map(a => a.total_score))) * 100}%"></div>
                    </div>
                </div>
            </div>
        `).join('');

        // Animate cards
        gsap.fromTo('#allianceGrid .card',
            { opacity: 0, scale: 0.9 },
            { opacity: 1, scale: 1, duration: 0.5, stagger: 0.1 }
        );
    }

    populateAllianceFilter(alliances) {
        const filter = document.getElementById('allianceFilter');
        const uniqueAlliances = [...new Set(alliances.map(a => a.name))].sort();
        
        filter.innerHTML = '<option value="">Alle Allianzen</option>' +
            uniqueAlliances.map(alliance => 
                `<option value="${alliance}">${alliance}</option>`
            ).join('');
    }

    initializeAnimations() {
        // Animate metric cards on scroll
        gsap.utils.toArray('.stat-card-enterprise').forEach((card, index) => {
            gsap.fromTo(card,
                { opacity: 0, y: 50 },
                {
                    opacity: 1,
                    y: 0,
                    duration: 0.8,
                    delay: index * 0.1,
                    scrollTrigger: {
                        trigger: card,
                        start: 'top 80%'
                    }
                }
            );
        });

        // Animate floating action button
        gsap.to('.fab-enterprise', {
            rotation: 360,
            duration: 20,
            repeat: -1,
            ease: 'none'
        });
    }

    setupAutoRefresh() {
        const interval = this.config?.dashboard?.auto_refresh_interval || 30000;
        
        setInterval(async () => {
            console.log('🔄 Auto-refreshing data...');
            await this.loadData();
            this.showToast('Daten aktualisiert', 'success');
        }, interval);
    }

    handleRealtimeUpdate(data) {
        console.log('📡 Real-time update received:', data);
        
        switch(data.type) {
            case 'player_update':
                this.updatePlayerData(data.player);
                break;
            case 'alliance_update':
                this.updateAllianceData(data.alliance);
                break;
            case 'new_data':
                this.loadData();
                break;
        }
    }

    updatePlayerData(player) {
        const index = this.currentData.players.findIndex(p => p.name === player.name);
        if (index !== -1) {
            this.currentData.players[index] = player;
            this.updatePlayersTable();
        }
    }

    updateAllianceData(alliance) {
        const index = this.currentData.alliances.findIndex(a => a.name === alliance.name);
        if (index !== -1) {
            this.currentData.alliances[index] = alliance;
            this.updateAllianceGrid(this.currentData.alliances);
        }
    }

    hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        gsap.to(overlay, {
            opacity: 0,
            duration: 1,
            onComplete: () => {
                overlay.classList.add('hidden');
            }
        });
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} show`;
        
        const icon = type === 'success' ? 'fa-check-circle' : 
                     type === 'error' ? 'fa-exclamation-circle' : 
                     type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle';
        
        toast.innerHTML = `
            <div class="flex items-center gap-3">
                <i class="fas ${icon}"></i>
                <span>${message}</span>
            </div>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Public methods for button clicks
    async refreshData() {
        const btn = event.target.closest('button');
        const icon = btn.querySelector('i');
        
        // Add spinning animation
        gsap.to(icon, { rotation: 360, duration: 1, repeat: 3, ease: 'none' });
        
        await this.loadData();
        this.showToast('Daten aktualisiert', 'success');
    }

    showUploadModal() {
        document.getElementById('uploadModal').classList.add('active');
    }

    closeUploadModal() {
        document.getElementById('uploadModal').classList.remove('active');
    }

    async uploadFile() {
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        
        if (!file) {
            this.showToast('Bitte wählen Sie eine Datei aus', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/data/upload/excel', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                this.showToast(`Datei erfolgreich hochgeladen: ${result.players_processed} Spieler verarbeitet`, 'success');
                this.closeUploadModal();
                await this.loadData();
            } else {
                throw new Error('Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showToast('Fehler beim Hochladen der Datei', 'error');
        }
    }

    handleFileUpload(file) {
        if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
            this.showToast(`Datei ausgewählt: ${file.name}`, 'info');
        } else {
            this.showToast('Bitte wählen Sie eine Excel-Datei (.xlsx oder .xls)', 'warning');
        }
    }

    toggleTheme() {
        const body = document.body;
        const currentTheme = body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        body.setAttribute('data-theme', newTheme);
        
        const icon = document.getElementById('themeIcon');
        icon.className = newTheme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
        
        localStorage.setItem('theme', newTheme);
    }

    showNotifications() {
        this.showToast('3 neue Benachrichtigungen', 'info');
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.updatePlayersTable();
        }
    }

    nextPage() {
        const totalPlayers = this.getFilteredPlayersCount();
        const maxPage = Math.ceil(totalPlayers / this.itemsPerPage);
        
        if (this.currentPage < maxPage) {
            this.currentPage++;
            this.updatePlayersTable();
        }
    }

    getFilteredPlayersCount() {
        if (!this.currentData) return 0;

        let filteredPlayers = this.currentData.players;

        if (this.searchTerm) {
            filteredPlayers = filteredPlayers.filter(player =>
                player.name.toLowerCase().includes(this.searchTerm) ||
                player.alliance.toLowerCase().includes(this.searchTerm)
            );
        }

        if (this.allianceFilter) {
            filteredPlayers = filteredPlayers.filter(player =>
                player.alliance === this.allianceFilter
            );
        }

        return filteredPlayers.length;
    }
}

// Global functions for button clicks
window.refreshData = function() {
    if (window.enterpriseDashboard) {
        window.enterpriseDashboard.refreshData();
    }
};

window.showUploadModal = function() {
    if (window.enterpriseDashboard) {
        window.enterpriseDashboard.showUploadModal();
    }
};

window.closeUploadModal = function() {
    if (window.enterpriseDashboard) {
        window.enterpriseDashboard.closeUploadModal();
    }
};

window.uploadFile = function() {
    if (window.enterpriseDashboard) {
        window.enterpriseDashboard.uploadFile();
    }
};

window.toggleTheme = function() {
    if (window.enterpriseDashboard) {
        window.enterpriseDashboard.toggleTheme();
    }
};

window.showNotifications = function() {
    if (window.enterpriseDashboard) {
        window.enterpriseDashboard.showNotifications();
    }
};

window.previousPage = function() {
    if (window.enterpriseDashboard) {
        window.enterpriseDashboard.previousPage();
    }
};

window.nextPage = function() {
    if (window.enterpriseDashboard) {
        window.enterpriseDashboard.nextPage();
    }
};

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.enterpriseDashboard = new EnterpriseDashboard();
});