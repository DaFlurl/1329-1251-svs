// 3D Notification System
class Notification3D {
    constructor(options = {}) {
        this.container = null;
        this.notifications = [];
        this.maxNotifications = options.maxNotifications || 5;
        this.defaultDuration = options.defaultDuration || 5000;
        this.position = options.position || 'top-right';
        this.stackMode = options.stackMode || true;
        
        this.init();
    }
    
    init() {
        this.createContainer();
        this.setupStyles();
    }
    
    createContainer() {
        this.container = document.createElement('div');
        this.container.className = `notification-3d-container ${this.stackMode ? 'stacked' : ''}`;
        this.container.setAttribute('data-position', this.position);
        
        // Position based on options
        const positions = {
            'top-right': { top: '20px', right: '20px' },
            'top-left': { top: '20px', left: '20px' },
            'bottom-right': { bottom: '20px', right: '20px' },
            'bottom-left': { bottom: '20px', left: '20px' },
            'top-center': { top: '20px', left: '50%', transform: 'translateX(-50%)' },
            'bottom-center': { bottom: '20px', left: '50%', transform: 'translateX(-50%)' }
        };
        
        const pos = positions[this.position] || positions['top-right'];
        Object.assign(this.container.style, pos);
        
        document.body.appendChild(this.container);
    }
    
    setupStyles() {
        if (document.getElementById('notification-3d-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'notification-3d-styles';
        style.textContent = `
            .notification-3d-enter {
                animation: notificationEnter 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
            }
            
            .notification-3d-exit {
                animation: notificationExit 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
            }
            
            @keyframes notificationEnter {
                0% {
                    opacity: 0;
                    transform: translateZ(-100px) translateX(100px) rotateY(90deg);
                }
                100% {
                    opacity: 1;
                    transform: translateZ(0) translateX(0) rotateY(0deg);
                }
            }
            
            @keyframes notificationExit {
                0% {
                    opacity: 1;
                    transform: translateZ(0) translateX(0) rotateY(0deg);
                }
                100% {
                    opacity: 0;
                    transform: translateZ(-100px) translateX(100px) rotateY(-90deg);
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    show(message, type = 'info', options = {}) {
        const config = {
            title: options.title || this.getDefaultTitle(type),
            message: message,
            type: type,
            duration: options.duration !== undefined ? options.duration : this.defaultDuration,
            actions: options.actions || [],
            progress: options.progress || null,
            closable: options.closable !== false,
            icon: options.icon || this.getDefaultIcon(type),
            className: options.className || '',
            onClick: options.onClick || null,
            onClose: options.onClose || null
        };
        
        const notification = this.createNotification(config);
        this.addNotification(notification);
        
        return notification;
    }
    
    info(message, options = {}) {
        return this.show(message, 'info', options);
    }
    
    success(message, options = {}) {
        return this.show(message, 'success', options);
    }
    
    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }
    
    error(message, options = {}) {
        return this.show(message, 'error', options);
    }
    
    toast(message, type = 'info', options = {}) {
        options.className = (options.className || '') + ' toast';
        return this.show(message, type, options);
    }
    
    modal(message, type = 'info', options = {}) {
        options.className = (options.className || '') + ' modal';
        options.closable = options.closable !== false;
        options.duration = 0; // Modals don't auto-close
        return this.show(message, type, options);
    }
    
    progress(message, progress = 0, options = {}) {
        options.className = (options.className || '') + ' progress';
        options.progress = progress;
        options.duration = 0; // Progress notifications don't auto-close
        
        const notification = this.show(message, 'info', options);
        notification.updateProgress = (newProgress) => {
            this.updateNotificationProgress(notification.id, newProgress);
        };
        
        return notification;
    }
    
    createNotification(config) {
        const notification = document.createElement('div');
        const id = Date.now() + Math.random();
        notification.id = `notification-${id}`;
        notification.className = `notification-3d ${config.type} ${config.className}`;
        
        // Create particles container
        const particles = document.createElement('div');
        particles.className = 'notification-3d-particles';
        notification.appendChild(particles);
        
        // Create content
        const content = document.createElement('div');
        content.innerHTML = `
            <div class="notification-3d-header">
                <div class="notification-3d-icon">${config.icon}</div>
                <div class="notification-3d-title">${config.title}</div>
                ${config.closable ? '<button class="notification-3d-close">×</button>' : ''}
            </div>
            <div class="notification-3d-message">${config.message}</div>
            ${config.actions.length > 0 ? `
                <div class="notification-3d-actions">
                    ${config.actions.map(action => 
                        `<button class="notification-3d-button" data-action="${action.id}">${action.text}</button>`
                    ).join('')}
                </div>
            ` : ''}
            ${config.progress !== null ? `
                <div class="notification-3d-progress-bar">
                    <div class="notification-3d-progress-fill" style="width: ${config.progress}%"></div>
                </div>
            ` : ''}
        `;
        
        notification.appendChild(content);
        
        // Store notification data
        const notificationData = {
            id: id,
            element: notification,
            config: config,
            timer: null,
            particles: particles
        };
        
        // Setup event listeners
        this.setupNotificationListeners(notification, notificationData);
        
        return notificationData;
    }
    
    setupNotificationListeners(element, data) {
        // Close button
        const closeBtn = element.querySelector('.notification-3d-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.removeNotification(data.id));
        }
        
        // Action buttons
        const buttons = element.querySelectorAll('.notification-3d-button');
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                const actionId = e.target.dataset.action;
                const action = data.config.actions.find(a => a.id === actionId);
                if (action && action.handler) {
                    action.handler(data);
                }
            });
        });
        
        // Click event
        if (data.config.onClick) {
            element.addEventListener('click', (e) => {
                if (e.target === element || e.target.closest('.notification-3d-header') || e.target.closest('.notification-3d-message')) {
                    data.config.onClick(data);
                }
            });
        }
        
        // Hover effects
        element.addEventListener('mouseenter', () => {
            this.createNotificationParticles(data, 'hover');
        });
        
        element.addEventListener('click', () => {
            this.createNotificationParticles(data, 'click');
        });
    }
    
    addNotification(data) {
        // Remove oldest notifications if exceeding max
        while (this.notifications.length >= this.maxNotifications) {
            const oldest = this.notifications.shift();
            this.removeNotificationElement(oldest);
        }
        
        this.notifications.push(data);
        this.container.appendChild(data.element);
        
        // Add enter animation
        data.element.classList.add('notification-3d-enter');
        
        // Create entrance particles
        setTimeout(() => {
            this.createNotificationParticles(data, 'enter');
        }, 100);
        
        // Set auto-close timer
        if (data.config.duration > 0) {
            data.timer = setTimeout(() => {
                this.removeNotification(data.id);
            }, data.config.duration);
        }
        
        // Update stack positions
        if (this.stackMode) {
            this.updateStackPositions();
        }
    }
    
    removeNotification(id) {
        const index = this.notifications.findIndex(n => n.id === id);
        if (index === -1) return;
        
        const data = this.notifications[index];
        
        // Clear timer
        if (data.timer) {
            clearTimeout(data.timer);
        }
        
        // Add exit animation
        data.element.classList.add('notification-3d-exit');
        
        // Create exit particles
        this.createNotificationParticles(data, 'exit');
        
        // Remove after animation
        setTimeout(() => {
            this.removeNotificationElement(data);
            this.notifications.splice(index, 1);
            
            // Update stack positions
            if (this.stackMode) {
                this.updateStackPositions();
            }
            
            // Call onClose callback
            if (data.config.onClose) {
                data.config.onClose(data);
            }
        }, 600);
    }
    
    removeNotificationElement(data) {
        if (data.element && data.element.parentNode) {
            data.element.parentNode.removeChild(data.element);
        }
    }
    
    updateNotificationProgress(id, progress) {
        const notification = this.notifications.find(n => n.id === id);
        if (!notification) return;
        
        const progressFill = notification.element.querySelector('.notification-3d-progress-fill');
        if (progressFill) {
            progressFill.style.width = `${Math.max(0, Math.min(100, progress))}%`;
        }
        
        // Create progress particles
        if (progress % 25 === 0) { // Every 25%
            this.createNotificationParticles(notification, 'progress');
        }
        
        // Auto-complete at 100%
        if (progress >= 100) {
            setTimeout(() => {
                this.removeNotification(id);
            }, 1000);
        }
    }
    
    updateStackPositions() {
        this.notifications.forEach((notification, index) => {
            const offset = index * 10;
            const scale = 1 - (index * 0.05);
            const opacity = 1 - (index * 0.1);
            
            if (index > 0) {
                notification.element.style.transform = `translateZ(${-offset * 2}px) scale(${scale}) translateY(${offset}px)`;
                notification.element.style.opacity = opacity;
            } else {
                notification.element.style.transform = '';
                notification.element.style.opacity = '';
            }
        });
    }
    
    createNotificationParticles(data, type) {
        const colors = {
            info: ['#60a5fa', '#3b82f6'],
            success: ['#22c55e', '#16a34a'],
            warning: ['#f59e0b', '#d97706'],
            error: ['#ef4444', '#dc2626'],
            hover: ['#a78bfa', '#8b5cf6'],
            click: ['#f472b6', '#ec4899'],
            enter: ['#60a5fa', '#a78bfa'],
            exit: ['#ef4444', '#f59e0b'],
            progress: ['#22c55e', '#60a5fa']
        };
        
        const typeColors = colors[type] || colors.info;
        const particleCount = type === 'enter' ? 8 : type === 'exit' ? 6 : 3;
        
        for (let i = 0; i < particleCount; i++) {
            setTimeout(() => {
                const particle = document.createElement('div');
                particle.className = 'notification-3d-particle';
                
                const color = typeColors[Math.floor(Math.random() * typeColors.length)];
                particle.style.background = color;
                particle.style.boxShadow = `0 0 8px ${color}`;
                
                // Random position within notification
                const rect = data.element.getBoundingClientRect();
                const containerRect = this.container.getBoundingClientRect();
                
                particle.style.left = `${Math.random() * rect.width}px`;
                particle.style.top = `${Math.random() * rect.height}px`;
                
                data.particles.appendChild(particle);
                
                // Animate particle
                const duration = 1500 + Math.random() * 500;
                const distance = 30 + Math.random() * 50;
                const angle = Math.random() * Math.PI * 2;
                
                particle.animate([
                    {
                        opacity: 0,
                        transform: 'translateZ(0) translateY(0) scale(0)'
                    },
                    {
                        opacity: 1,
                        transform: `translateZ(20px) translateY(-10px) scale(1)`
                    },
                    {
                        opacity: 0,
                        transform: `translateZ(40px) translateY(${-distance}px) translateX(${Math.cos(angle) * distance}px) scale(0.3)`
                    }
                ], {
                    duration: duration,
                    easing: 'ease-out'
                }).onfinish = () => particle.remove();
            }, i * 50);
        }
    }
    
    getDefaultTitle(type) {
        const titles = {
            info: 'Information',
            success: 'Success',
            warning: 'Warning',
            error: 'Error'
        };
        return titles[type] || 'Notification';
    }
    
    getDefaultIcon(type) {
        const icons = {
            info: 'ℹ️',
            success: '✅',
            warning: '⚠️',
            error: '❌'
        };
        return icons[type] || '📢';
    }
    
    // Public methods
    clear() {
        this.notifications.forEach(notification => {
            this.removeNotificationElement(notification);
            if (notification.timer) {
                clearTimeout(notification.timer);
            }
        });
        this.notifications = [];
    }
    
    count() {
        return this.notifications.length;
    }
    
    getNotification(id) {
        return this.notifications.find(n => n.id === id);
    }
}

// Global notification instance
let notification3D = null;

// Initialize global instance
document.addEventListener('DOMContentLoaded', () => {
    notification3D = new Notification3D();
    
    // Add to global scope
    window.notify3D = {
        info: (message, options) => notification3D.info(message, options),
        success: (message, options) => notification3D.success(message, options),
        warning: (message, options) => notification3D.warning(message, options),
        error: (message, options) => notification3D.error(message, options),
        toast: (message, type, options) => notification3D.toast(message, type, options),
        modal: (message, type, options) => notification3D.modal(message, type, options),
        progress: (message, progress, options) => notification3D.progress(message, progress, options),
        clear: () => notification3D.clear(),
        count: () => notification3D.count()
    };
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Notification3D;
}