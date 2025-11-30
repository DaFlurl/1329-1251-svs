/**
 * AgentDaf1.1 - 3D JavaScript Framework
 * Advanced 3D interactions and animations with Three.js integration
 */

class AgentDaf3D {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.particles = [];
        this.is3DSupported = this.check3DSupport();
        this.isInitialized = false;
        this.mouseX = 0;
        this.mouseY = 0;
        
        if (this.is3DSupported) {
            this.init();
        }
    }

    check3DSupport() {
        try {
            const canvas = document.createElement('canvas');
            return !!(window.WebGLRenderingContext && 
                     (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
        } catch (e) {
            return false;
        }
    }

    init() {
        if (this.isInitialized) return;
        
        this.createParticleField();
        this.setupEventListeners();
        this.initialize3DCards();
        this.startAnimationLoop();
        this.isInitialized = true;
        
        console.log('🚀 AgentDaf 3D Framework Initialized');
    }

    createParticleField() {
        const particleContainer = document.createElement('div');
        particleContainer.className = 'particles-3d';
        particleContainer.id = 'particle-field';
        
        // Create multiple particle layers
        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle-3d';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 10 + 's';
            particle.style.animationDuration = (10 + Math.random() * 10) + 's';
            
            // Random size
            const size = 2 + Math.random() * 4;
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            
            particleContainer.appendChild(particle);
            this.particles.push(particle);
        }
        
        document.body.appendChild(particleContainer);
    }

    setupEventListeners() {
        // Mouse movement for 3D effects
        document.addEventListener('mousemove', (e) => {
            this.mouseX = (e.clientX / window.innerWidth) * 2 - 1;
            this.mouseY = (e.clientY / window.innerHeight) * 2 - 1;
            this.update3DEffects(e);
        });

        // Scroll-based 3D parallax
        document.addEventListener('scroll', () => {
            this.updateParallax();
        });

        // Window resize handling
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    update3DEffects(e) {
        const cards = document.querySelectorAll('.card-3d, .feature-card-3d, .btn-3d');
        
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            const cardX = rect.left + rect.width / 2;
            const cardY = rect.top + rect.height / 2;
            
            const angleX = (e.clientY - cardY) * 0.01;
            const angleY = (e.clientX - cardX) * 0.01;
            
            card.style.transform = `translateZ(20px) rotateX(${-angleX}deg) rotateY(${angleY}deg)`;
        });
    }

    updateParallax() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.hero-content-3d, .feature-card-3d');
        
        parallaxElements.forEach((element, index) => {
            const speed = 0.5 + (index * 0.1);
            const yPos = -(scrolled * speed);
            element.style.transform = `translateZ(${20 + index * 10}px) translateY(${yPos}px)`;
        });
    }

    handleResize() {
        // Reposition particles on resize
        this.particles.forEach(particle => {
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
        });
    }

    initialize3DCards() {
        // Add 3D effects to existing cards
        const cards = document.querySelectorAll('.card, .feature-card');
        cards.forEach(card => {
            card.classList.add('card-3d');
        });

        // Add 3D effects to buttons
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            btn.classList.add('btn-3d');
        });

        // Add 3D effects to upload area
        const uploadAreas = document.querySelectorAll('.upload-area');
        uploadAreas.forEach(area => {
            area.classList.add('upload-3d');
        });
    }

    startAnimationLoop() {
        const animate = () => {
            this.animateParticles();
            requestAnimationFrame(animate);
        };
        animate();
    }

    animateParticles() {
        this.particles.forEach((particle, index) => {
            const time = Date.now() * 0.001;
            const offset = index * 0.1;
            
            // Subtle floating animation
            const floatY = Math.sin(time + offset) * 10;
            const floatX = Math.cos(time + offset) * 5;
            
            particle.style.transform = `translate(${floatX}px, ${floatY}px) translateZ(${Math.sin(time + offset) * 20}px)`;
        });
    }

    // 3D Chart Creation
    create3DChart(canvasId, data, options = {}) {
        if (!this.is3DSupported) {
            console.warn('3D charts not supported on this device');
            return null;
        }

        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        const chartContainer = canvas.parentElement;
        chartContainer.classList.add('chart-3d');

        // Enhanced 3D chart visualization
        this.draw3DBarChart(ctx, data, canvas.width, canvas.height, options);
        
        return {
            update: (newData) => this.draw3DBarChart(ctx, newData, canvas.width, canvas.height, options),
            destroy: () => this.cleanupChart(canvasId)
        };
    }

    draw3DBarChart(ctx, data, width, height, options) {
        const padding = 40;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        const barWidth = chartWidth / data.length * 0.6;
        const barSpacing = chartWidth / data.length * 0.4;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw 3D bars
        data.forEach((item, index) => {
            const x = padding + index * (barWidth + barSpacing);
            const barHeight = (item.value / 100) * chartHeight;
            const y = height - padding - barHeight;
            
            // Bar depth effect
            const depth = 10;
            
            // Draw bar sides (3D effect)
            ctx.fillStyle = 'rgba(0, 212, 255, 0.3)';
            ctx.beginPath();
            ctx.moveTo(x + barWidth, y);
            ctx.lineTo(x + barWidth + depth, y - depth);
            ctx.lineTo(x + barWidth + depth, height - padding - depth);
            ctx.lineTo(x + barWidth, height - padding);
            ctx.closePath();
            ctx.fill();
            
            // Draw bar top (3D effect)
            ctx.fillStyle = 'rgba(0, 212, 255, 0.5)';
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x + depth, y - depth);
            ctx.lineTo(x + barWidth + depth, y - depth);
            ctx.lineTo(x + barWidth, y);
            ctx.closePath();
            ctx.fill();
            
            // Draw bar front
            const gradient = ctx.createLinearGradient(0, y, 0, height - padding);
            gradient.addColorStop(0, '#00d4ff');
            gradient.addColorStop(1, '#0099cc');
            ctx.fillStyle = gradient;
            ctx.fillRect(x, y, barWidth, barHeight);
            
            // Draw label
            ctx.fillStyle = '#ffffff';
            ctx.font = '12px Inter';
            ctx.textAlign = 'center';
            ctx.fillText(item.label, x + barWidth / 2, height - padding + 20);
        });
    }

    cleanupChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    }

    // 3D Notification System
    show3DNotification(title, message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = 'notification-3d';
        notification.innerHTML = `
            <div class="notification-3d-content">
                <div class="notification-header">
                    <span class="notification-title">${title}</span>
                    <button class="notification-close" onclick="this.closest('.notification-3d').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="notification-body">${message}</div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Trigger animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Auto-remove
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 400);
        }, 5000);
    }

    // 3D Upload Enhancement
    enhance3DUpload() {
        const uploadAreas = document.querySelectorAll('.upload-3d');
        
        uploadAreas.forEach(area => {
            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('dragover');
                this.createUploadParticles(area);
            });
            
            area.addEventListener('dragleave', () => {
                area.classList.remove('dragover');
                this.clearUploadParticles(area);
            });
            
            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('dragover');
                this.clearUploadParticles(area);
                this.createUploadSuccessEffect(area);
            });
        });
    }

    createUploadParticles(element) {
        const rect = element.getBoundingClientRect();
        
        for (let i = 0; i < 10; i++) {
            const particle = document.createElement('div');
            particle.className = 'upload-particle';
            particle.style.cssText = `
                position: absolute;
                width: 6px;
                height: 6px;
                background: #00ff88;
                border-radius: 50%;
                left: ${Math.random() * rect.width}px;
                top: ${Math.random() * rect.height}px;
                pointer-events: none;
                animation: upload-particle-float 1s ease-out forwards;
                box-shadow: 0 0 10px #00ff88;
            `;
            
            element.appendChild(particle);
        }
    }

    clearUploadParticles(element) {
        const particles = element.querySelectorAll('.upload-particle');
        particles.forEach(p => p.remove());
    }

    createUploadSuccessEffect(element) {
        const effect = document.createElement('div');
        effect.className = 'upload-success-effect';
        effect.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100px;
            height: 100px;
            background: radial-gradient(circle, rgba(0, 255, 136, 0.8), transparent);
            border-radius: 50%;
            animation: upload-success-pulse 0.6s ease-out forwards;
            pointer-events: none;
        `;
        
        element.appendChild(effect);
        
        setTimeout(() => {
            effect.remove();
        }, 600);
    }

    // Performance optimization
    optimizePerformance() {
        // Reduce motion for users who prefer it
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.body.classList.add('reduce-motion');
        }
        
        // Detect low-end devices
        if (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4) {
            this.reduceParticleCount();
        }
    }

    reduceParticleCount() {
        const particles = document.querySelectorAll('.particle-3d');
        particles.forEach((particle, index) => {
            if (index > 20) {
                particle.remove();
            }
        });
    }
}

// Initialize 3D framework when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.agentDaf3D = new AgentDaf3D();
    
    // Add 3D enhancements to existing elements
    setTimeout(() => {
        window.agentDaf3D.enhance3DUpload();
        window.agentDaf3D.optimizePerformance();
    }, 1000);
});

// Add custom CSS animations
const style3D = document.createElement('style');
style3D.textContent = `
    @keyframes upload-particle-float {
        0% {
            transform: translateY(0) scale(1);
            opacity: 1;
        }
        100% {
            transform: translateY(-30px) scale(0);
            opacity: 0;
        }
    }
    
    @keyframes upload-success-pulse {
        0% {
            transform: translate(-50%, -50%) scale(0);
            opacity: 1;
        }
        100% {
            transform: translate(-50%, -50%) scale(3);
            opacity: 0;
        }
    }
    
    .upload-particle {
        animation: upload-particle-float 1s ease-out forwards;
    }
    
    .upload-success-effect {
        animation: upload-success-pulse 0.6s ease-out forwards;
    }
`;
document.head.appendChild(style3D);

// Export for global access
window.AgentDaf3D = AgentDaf3D;