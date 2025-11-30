/**
 * Main Application Controller
 * Coordinates all components and handles application lifecycle
 */
class MainApp {
  constructor() {
    this.components = new Map();
    this.isInitialized = false;
    this.loadingScreen = null;
    
    this.init();
  }

  async init() {
    try {
      this.showLoadingScreen();
      await this.initializeComponents();
      this.setupEventListeners();
      this.setupPWA();
      this.hideLoadingScreen();
      this.isInitialized = true;
      
      console.log('AgentDaf1.1 Dashboard initialized successfully');
    } catch (error) {
      console.error('Failed to initialize application:', error);
      this.showError('Anwendung konnte nicht gestartet werden');
    }
  }

  showLoadingScreen() {
    this.loadingScreen = document.getElementById('loadingScreen');
    if (this.loadingScreen) {
      this.loadingScreen.classList.remove('hidden');
    }
  }

  hideLoadingScreen() {
    if (this.loadingScreen) {
      setTimeout(() => {
        this.loadingScreen.classList.add('hidden');
      }, 500);
    }
  }

  async initializeComponents() {
    // Wait for DOM to be ready
    if (document.readyState !== 'complete') {
      await new Promise(resolve => {
        window.addEventListener('load', resolve);
      });
    }

    // Initialize components in order
    const componentOrder = [
      { name: 'themeManager', required: false },
      { name: 'dataLoader', required: true },
      { name: 'scoreboard', required: true },
      { name: 'charts', required: false }
    ];

    for (const component of componentOrder) {
      try {
        if (window[component.name]) {
          this.components.set(component.name, window[component.name]);
          console.log(`✓ ${component.name} initialized`);
        } else if (component.required) {
          throw new Error(`Required component ${component.name} not found`);
        }
      } catch (error) {
        if (component.required) {
          throw error;
        } else {
          console.warn(`⚠ ${component.name} initialization failed:`, error);
        }
      }
    }

    // Load initial data
    const dataLoader = this.components.get('dataLoader');
    if (dataLoader) {
      try {
        await dataLoader.loadData();
      } catch (error) {
        console.warn('Initial data loading failed:', error);
      }
    }
  }

  setupEventListeners() {
    // Global error handling
    window.addEventListener('error', (e) => {
      console.error('Global error:', e.error);
      this.showToast('Ein Fehler ist aufgetreten', 'error');
    });

    // Unhandled promise rejections
    window.addEventListener('unhandledrejection', (e) => {
      console.error('Unhandled promise rejection:', e.reason);
      this.showToast('Ein Fehler ist aufgetreten', 'error');
    });

    // Keyboard shortcuts
    this.setupKeyboardShortcuts();

    // Fullscreen functionality
    this.setupFullscreen();

    // Window resize handling
    this.setupResizeHandling();

    // Online/Offline detection
    this.setupConnectivityHandling();
  }

  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + R: Refresh data
      if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        this.refreshData();
      }

      // Ctrl/Cmd + E: Export data
      if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        this.exportData();
      }

      // F11: Toggle fullscreen
      if (e.key === 'F11') {
        e.preventDefault();
        this.toggleFullscreen();
      }

      // Escape: Exit fullscreen
      if (e.key === 'Escape' && document.fullscreenElement) {
        this.exitFullscreen();
      }
    });
  }

  setupFullscreen() {
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    if (fullscreenBtn) {
      fullscreenBtn.addEventListener('click', () => {
        this.toggleFullscreen();
      });
    }

    // Update button when fullscreen state changes
    document.addEventListener('fullscreenchange', () => {
      this.updateFullscreenButton();
    });
  }

  setupResizeHandling() {
    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        this.handleResize();
      }, 250);
    });
  }

  setupConnectivityHandling() {
    window.addEventListener('online', () => {
      this.showToast('Verbindung wiederhergestellt', 'success');
      this.refreshData();
    });

    window.addEventListener('offline', () => {
      this.showToast('Verbindung unterbrochen', 'warning');
    });
  }

  setupPWA() {
    // PWA install prompt
    let deferredPrompt;
    
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      this.showInstallButton();
    });

    const installBtn = document.getElementById('installBtn');
    if (installBtn) {
      installBtn.addEventListener('click', async () => {
        if (deferredPrompt) {
          deferredPrompt.prompt();
          const { outcome } = await deferredPrompt.userChoice;
          deferredPrompt = null;
          
          if (outcome === 'accepted') {
            this.showToast('Anwendung installiert', 'success');
            installBtn.style.display = 'none';
          }
        }
      });
    }
  }

  // Application methods
  async refreshData() {
    const dataLoader = this.components.get('dataLoader');
    if (dataLoader) {
      try {
        await dataLoader.loadData();
        this.showToast('Daten aktualisiert', 'success');
      } catch (error) {
        this.showToast('Fehler bei der Aktualisierung', 'error');
      }
    }
  }

  exportData() {
    const scoreboard = this.components.get('scoreboard');
    if (scoreboard) {
      scoreboard.exportToCSV();
    }
  }

  toggleFullscreen() {
    if (!document.fullscreenElement) {
      this.enterFullscreen();
    } else {
      this.exitFullscreen();
    }
  }

  async enterFullscreen() {
    try {
      await document.documentElement.requestFullscreen();
    } catch (error) {
      console.warn('Fullscreen not supported:', error);
    }
  }

  async exitFullscreen() {
    try {
      await document.exitFullscreen();
    } catch (error) {
      console.warn('Error exiting fullscreen:', error);
    }
  }

  updateFullscreenButton() {
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    if (!fullscreenBtn) return;

    const icon = fullscreenBtn.querySelector('i');
    if (document.fullscreenElement) {
      icon.className = 'fas fa-compress';
      fullscreenBtn.title = 'Vollbild beenden';
    } else {
      icon.className = 'fas fa-expand';
      fullscreenBtn.title = 'Vollbild';
    }
  }

  handleResize() {
    // Resize charts
    const charts = this.components.get('charts');
    if (charts) {
      charts.resizeAllCharts();
    }

    // Update mobile layout if needed
    this.updateMobileLayout();
  }

  updateMobileLayout() {
    const isMobile = window.innerWidth < 768;
    document.body.classList.toggle('mobile-layout', isMobile);
  }

  showInstallButton() {
    const installBtn = document.getElementById('installBtn');
    if (installBtn) {
      installBtn.style.display = 'flex';
    }
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

  showError(message) {
    this.hideLoadingScreen();
    
    // Create error overlay
    const errorOverlay = document.createElement('div');
    errorOverlay.className = 'error-overlay';
    errorOverlay.innerHTML = `
      <div class="error-content">
        <i class="fas fa-exclamation-triangle"></i>
        <h2>Fehler</h2>
        <p>${message}</p>
        <button onclick="location.reload()">Neu laden</button>
      </div>
    `;
    
    document.body.appendChild(errorOverlay);
  }

  // Component access methods
  getComponent(name) {
    return this.components.get(name);
  }

  isComponentReady(name) {
    return this.components.has(name);
  }

  // Application state
  getState() {
    return {
      initialized: this.isInitialized,
      components: Array.from(this.components.keys()),
      theme: document.documentElement.getAttribute('data-theme'),
      online: navigator.onLine,
      fullscreen: !!document.fullscreenElement,
      mobile: window.innerWidth < 768
    };
  }

  // Cleanup
  destroy() {
    // Destroy components
    this.components.forEach((component, name) => {
      if (component.destroy) {
        component.destroy();
      }
    });

    // Clear references
    this.components.clear();
    this.isInitialized = false;
  }
}

// Global utility functions
function showAllPlayers() {
  const scoreboard = window.scoreboard;
  if (scoreboard) {
    // Switch to players tab
    const playersTab = document.querySelector('[data-tab="players"]');
    if (playersTab) {
      playersTab.click();
    }
  }
}

function showAllianceDetails() {
  const alliancesTab = document.querySelector('[data-tab="alliances"]');
  if (alliancesTab) {
    alliancesTab.click();
  }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.app = new MainApp();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MainApp;
}