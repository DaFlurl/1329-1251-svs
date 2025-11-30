/**
 * 3D Dark Theme Manager
 * Comprehensive dark theme functionality for 3D dashboard
 */

class DarkThemeManager3D {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.isTransitioning = false;
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.createThemeToggle();
        this.setupKeyboardShortcuts();
        this.setupSystemThemeDetection();
        this.addThemeTransitionEffects();
    }

    /**
     * Apply theme to the document
     */
    applyTheme(theme) {
        if (this.isTransitioning) return;
        
        this.isTransitioning = true;
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        localStorage.setItem('theme', theme);
        
        // Update theme toggle button
        this.updateThemeToggle();
        
        // Trigger theme change event
        this.dispatchThemeChangeEvent(theme);
        
        // Add transition effect
        this.addTransitionEffect();
        
        setTimeout(() => {
            this.isTransitioning = false;
        }, 300);
    }

    /**
     * Create theme toggle button
     */
    createThemeToggle() {
        // Remove existing toggle if present
        const existingToggle = document.querySelector('.theme-toggle-3d');
        if (existingToggle) {
            existingToggle.remove();
        }

        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle-3d';
        toggle.setAttribute('aria-label', 'Toggle dark theme');
        toggle.innerHTML = `
            <span class="icon">${this.getThemeIcon()}</span>
            <span class="text">${this.getThemeText()}</span>
        `;

        toggle.addEventListener('click', () => this.toggleTheme());
        
        // Add hover effects
        this.addToggleHoverEffects(toggle);
        
        document.body.appendChild(toggle);
    }

    /**
     * Toggle between light and dark themes
     */
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    /**
     * Get current theme icon
     */
    getThemeIcon() {
        return this.currentTheme === 'light' ? '🌙' : '☀️';
    }

    /**
     * Get current theme text
     */
    getThemeText() {
        return this.currentTheme === 'light' ? 'Dark' : 'Light';
    }

    /**
     * Update theme toggle button
     */
    updateThemeToggle() {
        const toggle = document.querySelector('.theme-toggle-3d');
        if (toggle) {
            const icon = toggle.querySelector('.icon');
            const text = toggle.querySelector('.text');
            
            if (icon) icon.textContent = this.getThemeIcon();
            if (text) text.textContent = this.getThemeText();
            
            // Add pulse animation
            toggle.style.animation = 'pulse-3d 0.5s ease';
            setTimeout(() => {
                toggle.style.animation = '';
            }, 500);
        }
    }

    /**
     * Add hover effects to toggle button
     */
    addToggleHoverEffects(toggle) {
        toggle.addEventListener('mouseenter', () => {
            if (!this.isTransitioning) {
                toggle.style.transform = 'scale(1.05) rotateY(10deg)';
            }
        });

        toggle.addEventListener('mouseleave', () => {
            if (!this.isTransitioning) {
                toggle.style.transform = 'scale(1) rotateY(0deg)';
            }
        });

        toggle.addEventListener('mousedown', () => {
            toggle.style.transform = 'scale(0.95) rotateY(-5deg)';
        });

        toggle.addEventListener('mouseup', () => {
            toggle.style.transform = 'scale(1.05) rotateY(10deg)';
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Shift + D for theme toggle
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                this.toggleTheme();
            }
            
            // Ctrl/Cmd + Shift + L for light theme
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'L') {
                e.preventDefault();
                this.applyTheme('light');
            }
            
            // Ctrl/Cmd + Shift + N for dark theme
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'N') {
                e.preventDefault();
                this.applyTheme('dark');
            }
        });
    }

    /**
     * Setup system theme detection
     */
    setupSystemThemeDetection() {
        // Check if user prefers dark mode
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Only apply system theme if user hasn't manually set one
        if (!localStorage.getItem('theme')) {
            this.applyTheme(prefersDark.matches ? 'dark' : 'light');
        }

        // Listen for system theme changes
        prefersDark.addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    /**
     * Add theme transition effects
     */
    addThemeTransitionEffects() {
        // Create transition overlay
        const overlay = document.createElement('div');
        overlay.className = 'theme-transition-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, transparent 0%, rgba(0, 212, 255, 0.1) 100%);
            pointer-events: none;
            opacity: 0;
            z-index: 9999;
            transition: opacity 0.3s ease;
        `;
        
        document.body.appendChild(overlay);
    }

    /**
     * Add transition effect when theme changes
     */
    addTransitionEffect() {
        const overlay = document.querySelector('.theme-transition-overlay');
        if (overlay) {
            overlay.style.opacity = '1';
            setTimeout(() => {
                overlay.style.opacity = '0';
            }, 300);
        }

        // Add particle effect for dark theme
        if (this.currentTheme === 'dark') {
            this.createThemeParticles();
        }
    }

    /**
     * Create theme transition particles
     */
    createThemeParticles() {
        const particleCount = 20;
        const colors = ['#00d4ff', '#ff006e', '#ffbe0b', '#00f5a0'];
        
        for (let i = 0; i < particleCount; i++) {
            setTimeout(() => {
                const particle = document.createElement('div');
                particle.className = 'theme-particle';
                particle.style.cssText = `
                    position: fixed;
                    width: 4px;
                    height: 4px;
                    background: ${colors[Math.floor(Math.random() * colors.length)]};
                    border-radius: 50%;
                    pointer-events: none;
                    z-index: 9998;
                    left: ${Math.random() * 100}%;
                    top: ${Math.random() * 100}%;
                    box-shadow: 0 0 10px currentColor;
                    animation: particle-float-3d 2s ease-out forwards;
                `;
                
                document.body.appendChild(particle);
                
                setTimeout(() => particle.remove(), 2000);
            }, i * 50);
        }
    }

    /**
     * Dispatch theme change event
     */
    dispatchThemeChangeEvent(theme) {
        const event = new CustomEvent('themechange', {
            detail: { theme, previousTheme: this.currentTheme === 'light' ? 'dark' : 'light' }
        });
        document.dispatchEvent(event);
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * Set theme programmatically
     */
    setTheme(theme) {
        if (theme === 'light' || theme === 'dark') {
            this.applyTheme(theme);
        }
    }

    /**
     * Reset to system theme
     */
    resetToSystemTheme() {
        localStorage.removeItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
        this.applyTheme(prefersDark.matches ? 'dark' : 'light');
    }

    /**
     * Get theme statistics
     */
    getThemeStats() {
        return {
            current: this.currentTheme,
            system: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
            isCustom: localStorage.getItem('theme') !== null,
            supported: true
        };
    }

    /**
     * Export theme settings
     */
    exportThemeSettings() {
        return {
            theme: this.currentTheme,
            customSettings: {
                transitionEffects: true,
                particleEffects: true,
                keyboardShortcuts: true,
                systemDetection: true
            }
        };
    }

    /**
     * Import theme settings
     */
    importThemeSettings(settings) {
        if (settings.theme) {
            this.applyTheme(settings.theme);
        }
        // Additional settings can be implemented here
    }
}

// Add particle animation CSS
const particleCSS = `
@keyframes particle-float-3d {
    0% {
        transform: translateY(0) scale(0);
        opacity: 1;
    }
    50% {
        transform: translateY(-50px) scale(1);
        opacity: 0.8;
    }
    100% {
        transform: translateY(-100px) scale(0);
        opacity: 0;
    }
}
`;

// Inject particle CSS
const styleSheet = document.createElement('style');
styleSheet.textContent = particleCSS;
document.head.appendChild(styleSheet);

// Initialize dark theme manager
let darkThemeManager;

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        darkThemeManager = new DarkThemeManager3D();
    });
} else {
    darkThemeManager = new DarkThemeManager3D();
}

// Global access
window.DarkThemeManager3D = DarkThemeManager3D;
window.darkThemeManager = darkThemeManager;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DarkThemeManager3D;
}