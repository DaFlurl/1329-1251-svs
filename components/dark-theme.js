/**
 * Dark Theme Manager for SVS Gaming Dashboard
 * Simple and effective dark theme functionality
 */

class DarkThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('svs-theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.createThemeToggle();
        this.setupKeyboardShortcuts();
        this.setupSystemThemeDetection();
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        localStorage.setItem('svs-theme', theme);
        this.updateThemeToggle();
        
        // Dispatch theme change event
        const event = new CustomEvent('themechange', {
            detail: { theme, previousTheme: theme === 'light' ? 'dark' : 'light' }
        });
        document.dispatchEvent(event);
    }

    createThemeToggle() {
        // Remove existing toggle
        const existing = document.querySelector('.theme-toggle');
        if (existing) existing.remove();

        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle';
        toggle.setAttribute('aria-label', 'Toggle dark theme');
        toggle.innerHTML = `
            <span class="icon">${this.getThemeIcon()}</span>
            <span class="text">${this.getThemeText()}</span>
        `;

        toggle.addEventListener('click', () => this.toggleTheme());
        
        document.body.appendChild(toggle);
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    getThemeIcon() {
        return this.currentTheme === 'light' ? '🌙' : '☀️';
    }

    getThemeText() {
        return this.currentTheme === 'light' ? 'Dark' : 'Light';
    }

    updateThemeToggle() {
        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            const icon = toggle.querySelector('.icon');
            const text = toggle.querySelector('.text');
            
            if (icon) icon.textContent = this.getThemeIcon();
            if (text) text.textContent = this.getThemeText();
            
            // Add pulse animation
            toggle.style.animation = 'pulse-dark 0.5s ease';
            setTimeout(() => {
                toggle.style.animation = '';
            }, 500);
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Shift + D for theme toggle
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
    }

    setupSystemThemeDetection() {
        // Check if user prefers dark mode
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Only apply system theme if user hasn't manually set one
        if (!localStorage.getItem('svs-theme')) {
            this.applyTheme(prefersDark.matches ? 'dark' : 'light');
        }

        // Listen for system theme changes
        prefersDark.addEventListener('change', (e) => {
            if (!localStorage.getItem('svs-theme')) {
                this.applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    getCurrentTheme() {
        return this.currentTheme;
    }

    setTheme(theme) {
        if (theme === 'light' || theme === 'dark') {
            this.applyTheme(theme);
        }
    }
}

// Initialize dark theme manager
let darkThemeManager;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        darkThemeManager = new DarkThemeManager();
    });
} else {
    darkThemeManager = new DarkThemeManager();
}

// Global access
window.DarkThemeManager = DarkThemeManager;
window.darkThemeManager = darkThemeManager;