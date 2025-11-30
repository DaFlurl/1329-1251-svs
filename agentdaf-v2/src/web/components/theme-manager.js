/**
 * Theme Manager - Handles theme switching and persistence
 */
class ThemeManager {
  constructor() {
    this.themes = ['light', 'dark', 'high-contrast'];
    this.currentTheme = this.loadTheme();
    this.init();
  }

  init() {
    // Apply saved theme
    this.applyTheme(this.currentTheme);
    
    // Setup theme toggle button
    this.setupThemeToggle();
    
    // Listen for system theme changes
    this.setupSystemThemeDetection();
    
    // Add keyboard shortcuts
    this.setupKeyboardShortcuts();
  }

  loadTheme() {
    // Check localStorage first
    const savedTheme = localStorage.getItem('agentdaf-theme');
    if (savedTheme && this.themes.includes(savedTheme)) {
      return savedTheme;
    }
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    return 'light';
  }

  saveTheme(theme) {
    localStorage.setItem('agentdaf-theme', theme);
  }

  applyTheme(theme) {
    if (!this.themes.includes(theme)) return;
    
    // Remove all theme classes
    this.themes.forEach(t => {
      document.documentElement.removeAttribute(`data-theme-${t}`);
    });
    
    // Apply new theme
    document.documentElement.setAttribute('data-theme', theme);
    this.currentTheme = theme;
    
    // Update theme toggle button
    this.updateThemeToggle();
    
    // Update meta theme-color
    this.updateMetaThemeColor();
    
    // Save theme
    this.saveTheme(theme);
    
    // Dispatch theme change event
    this.dispatchThemeChange(theme);
  }

  setupThemeToggle() {
    const toggleBtn = document.getElementById('themeToggle');
    if (!toggleBtn) return;

    toggleBtn.addEventListener('click', () => {
      this.cycleTheme();
    });
  }

  cycleTheme() {
    const currentIndex = this.themes.indexOf(this.currentTheme);
    const nextIndex = (currentIndex + 1) % this.themes.length;
    this.applyTheme(this.themes[nextIndex]);
  }

  updateThemeToggle() {
    const toggleBtn = document.getElementById('themeToggle');
    if (!toggleBtn) return;

    const icon = toggleBtn.querySelector('i');
    if (!icon) return;

    // Update icon based on current theme
    switch (this.currentTheme) {
      case 'light':
        icon.className = 'fas fa-moon';
        toggleBtn.title = 'Zum dunklen Theme wechseln';
        break;
      case 'dark':
        icon.className = 'fas fa-sun';
        toggleBtn.title = 'Zum hellen Theme wechseln';
        break;
      case 'high-contrast':
        icon.className = 'fas fa-adjust';
        toggleBtn.title = 'Zum normalen Theme wechseln';
        break;
    }
  }

  updateMetaThemeColor() {
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (!metaThemeColor) return;

    const colors = {
      light: '#667eea',
      dark: '#00FF88',
      'high-contrast': '#00ff00'
    };

    metaThemeColor.content = colors[this.currentTheme] || colors.light;
  }

  setupSystemThemeDetection() {
    if (!window.matchMedia) return;

    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    darkModeQuery.addEventListener('change', (e) => {
      // Only auto-switch if user hasn't manually set a theme
      if (!localStorage.getItem('agentdaf-theme')) {
        this.applyTheme(e.matches ? 'dark' : 'light');
      }
    });
  }

  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + Shift + T to cycle themes
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        this.cycleTheme();
      }
      
      // Ctrl/Cmd + Shift + D for dark mode
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        this.applyTheme('dark');
      }
      
      // Ctrl/Cmd + Shift + L for light mode
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'L') {
        e.preventDefault();
        this.applyTheme('light');
      }
    });
  }

  dispatchThemeChange(theme) {
    const event = new CustomEvent('themechange', {
      detail: { theme, previousTheme: this.currentTheme }
    });
    document.dispatchEvent(event);
  }

  // Public API
  getTheme() {
    return this.currentTheme;
  }

  setTheme(theme) {
    this.applyTheme(theme);
  }

  getAvailableThemes() {
    return [...this.themes];
  }

  // Reset to system preference
  resetToSystemTheme() {
    localStorage.removeItem('agentdaf-theme');
    const systemTheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches 
      ? 'dark' 
      : 'light';
    this.applyTheme(systemTheme);
  }

  // Get theme info
  getThemeInfo(theme = this.currentTheme) {
    const themeInfo = {
      light: {
        name: 'Hell',
        description: 'Helles Theme für Tagesnutzung',
        icon: 'fas fa-sun'
      },
      dark: {
        name: 'Dunkel',
        description: 'Dunkles GitStyle Theme mit Neon-Effekten',
        icon: 'fas fa-moon'
      },
      'high-contrast': {
        name: 'Hoher Kontrast',
        description: 'Barrierefreies Theme mit maximalem Kontrast',
        icon: 'fas fa-adjust'
      }
    };

    return themeInfo[theme] || themeInfo.light;
  }
}

// Initialize theme manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.themeManager = new ThemeManager();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ThemeManager;
}