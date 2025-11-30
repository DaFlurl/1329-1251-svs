// 3D Hover Effects Throughout Interface
class HoverEffects3D {
    constructor(options = {}) {
        this.options = {
            intensity: options.intensity || 1,
            enableParticles: options.enableParticles !== false,
            enableSound: options.enableSound || false,
            performanceMode: options.performanceMode || false,
            mobileOptimized: options.mobileOptimized !== false
        };
        
        this.mouseX = 0;
        this.mouseY = 0;
        this.elements = [];
        this.particles = [];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeElements();
        this.createParticleContainer();
        this.startAnimation();
    }
    
    setupEventListeners() {
        document.addEventListener('mousemove', this.handleMouseMove.bind(this));
        document.addEventListener('touchmove', this.handleTouchMove.bind(this));
        
        // Performance monitoring
        if (this.options.performanceMode) {
            this.monitorPerformance();
        }
    }
    
    handleMouseMove(event) {
        this.mouseX = (event.clientX / window.innerWidth - 0.5) * 2;
        this.mouseY = (event.clientY / window.innerHeight - 0.5) * 2;
        
        this.updateHoverEffects();
    }
    
    handleTouchMove(event) {
        if (event.touches.length > 0) {
            const touch = event.touches[0];
            this.mouseX = (touch.clientX / window.innerWidth - 0.5) * 2;
            this.mouseY = (touch.clientY / window.innerHeight - 0.5) * 2;
            
            this.updateHoverEffects();
        }
    }
    
    initializeElements() {
        // Find all elements with 3D hover classes
        const hoverClasses = [
            '.hover-3d', '.btn-3d', '.card-3d', '.input-3d',
            '.link-3d', '.img-3d', '.tr-3d', '.badge-3d',
            '.progress-3d', '.modal-3d', '.dropdown-3d', '.tab-3d',
            '.sidebar-3d', '.footer-3d'
        ];
        
        hoverClasses.forEach(selector => {
            document.querySelectorAll(selector).forEach(element => {
                this.addElement(element);
            });
        });
        
        // Auto-add hover effects to common elements
        this.autoAddHoverEffects();
    }
    
    addElement(element) {
        if (this.elements.find(e => e.element === element)) return;
        
        const rect = element.getBoundingClientRect();
        const elementData = {
            element: element,
            originalTransform: element.style.transform || '',
            originalTransition: element.style.transition || '',
            rect: rect,
            centerX: rect.left + rect.width / 2,
            centerY: rect.top + rect.height / 2,
            intensity: this.getElementIntensity(element),
            type: this.getElementType(element)
        };
        
        this.elements.push(elementData);
        
        // Add event listeners
        element.addEventListener('mouseenter', () => this.handleElementHover(elementData, true));
        element.addEventListener('mouseleave', () => this.handleElementHover(elementData, false));
        element.addEventListener('click', () => this.handleElementClick(elementData));
    }
    
    getElementIntensity(element) {
        // Different intensities for different element types
        if (element.classList.contains('btn-3d')) return 1.5;
        if (element.classList.contains('card-3d')) return 1.2;
        if (element.classList.contains('img-3d')) return 1.3;
        if (element.classList.contains('modal-3d')) return 0.8;
        return this.options.intensity;
    }
    
    getElementType(element) {
        if (element.classList.contains('btn-3d')) return 'button';
        if (element.classList.contains('card-3d')) return 'card';
        if (element.classList.contains('input-3d')) return 'input';
        if (element.classList.contains('link-3d')) return 'link';
        if (element.classList.contains('img-3d')) return 'image';
        if (element.classList.contains('modal-3d')) return 'modal';
        return 'default';
    }
    
    autoAddHoverEffects() {
        // Auto-add 3D hover to buttons without specific classes
        document.querySelectorAll('button:not(.btn-3d)').forEach(button => {
            if (!button.classList.contains('no-3d')) {
                button.classList.add('hover-3d');
                this.addElement(button);
            }
        });
        
        // Auto-add to links
        document.querySelectorAll('a:not(.link-3d):not(.no-3d)').forEach(link => {
            link.classList.add('link-3d');
            this.addElement(link);
        });
        
        // Auto-add to images
        document.querySelectorAll('img:not(.img-3d):not(.no-3d)').forEach(img => {
            img.classList.add('img-3d');
            this.addElement(img);
        });
    }
    
    handleElementHover(elementData, isHovering) {
        if (this.options.performanceMode && !isHovering) return;
        
        if (isHovering) {
            elementData.element.style.transform = `${elementData.originalTransform} translateZ(20px)`;
            
            // Create hover particles
            if (this.options.enableParticles) {
                this.createHoverParticles(elementData);
            }
            
            // Play hover sound
            if (this.options.enableSound) {
                this.playHoverSound(elementData.type);
            }
        } else {
            elementData.element.style.transform = elementData.originalTransform;
        }
    }
    
    handleElementClick(elementData) {
        // Create click particles
        if (this.options.enableParticles) {
            this.createClickParticles(elementData);
        }
        
        // Play click sound
        if (this.options.enableSound) {
            this.playClickSound(elementData.type);
        }
        
        // Add click ripple effect
        this.createRippleEffect(elementData);
    }
    
    updateHoverEffects() {
        if (this.options.performanceMode) return;
        
        this.elements.forEach(elementData => {
            const rect = elementData.element.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            
            // Calculate distance from mouse
            const distanceX = (this.mouseX * window.innerWidth / 2) - centerX;
            const distanceY = (this.mouseY * window.innerHeight / 2) - centerY;
            const distance = Math.sqrt(distanceX * distanceX + distanceY * distanceY);
            
            // Apply 3D transform based on mouse proximity
            if (distance < 200) {
                const intensity = (1 - distance / 200) * elementData.intensity;
                const rotateX = -distanceY * 0.05 * intensity;
                const rotateY = distanceX * 0.05 * intensity;
                const translateZ = intensity * 10;
                
                elementData.element.style.transform = `
                    ${elementData.originalTransform}
                    rotateX(${rotateX}deg)
                    rotateY(${rotateY}deg)
                    translateZ(${translateZ}px)
                `;
            }
        });
    }
    
    createParticleContainer() {
        if (!this.options.enableParticles) return;
        
        this.particleContainer = document.createElement('div');
        this.particleContainer.className = 'hover-3d-particles';
        this.particleContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9998;
        `;
        document.body.appendChild(this.particleContainer);
    }
    
    createHoverParticles(elementData) {
        const rect = elementData.element.getBoundingClientRect();
        const particleCount = 5;
        const colors = this.getParticleColors(elementData.type);
        
        for (let i = 0; i < particleCount; i++) {
            setTimeout(() => {
                this.createParticle({
                    x: rect.left + rect.width / 2,
                    y: rect.top + rect.height / 2,
                    colors: colors,
                    velocity: {
                        x: (Math.random() - 0.5) * 2,
                        y: (Math.random() - 0.5) * 2 - 1,
                        z: Math.random() * 2
                    }
                });
            }, i * 50);
        }
    }
    
    createClickParticles(elementData) {
        const rect = elementData.element.getBoundingClientRect();
        const particleCount = 8;
        const colors = this.getParticleColors(elementData.type);
        
        for (let i = 0; i < particleCount; i++) {
            const angle = (Math.PI * 2 * i) / particleCount;
            this.createParticle({
                x: rect.left + rect.width / 2,
                y: rect.top + rect.height / 2,
                colors: colors,
                velocity: {
                    x: Math.cos(angle) * 3,
                    y: Math.sin(angle) * 3,
                    z: 2
                }
            });
        }
    }
    
    createParticle(config) {
        const particle = document.createElement('div');
        particle.className = 'hover-3d-particle';
        
        const color = config.colors[Math.floor(Math.random() * config.colors.length)];
        const size = 2 + Math.random() * 4;
        
        particle.style.cssText = `
            position: fixed;
            width: ${size}px;
            height: ${size}px;
            background: ${color};
            border-radius: 50%;
            pointer-events: none;
            left: ${config.x}px;
            top: ${config.y}px;
            transform: translateZ(0);
            box-shadow: 0 0 10px ${color};
        `;
        
        this.particleContainer.appendChild(particle);
        
        // Animate particle
        const duration = 1000 + Math.random() * 1000;
        const startTime = Date.now();
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = elapsed / duration;
            
            if (progress >= 1) {
                particle.remove();
                return;
            }
            
            const x = config.x + config.velocity.x * progress * 50;
            const y = config.y + config.velocity.y * progress * 50;
            const z = config.velocity.z * progress * 30;
            const opacity = 1 - progress;
            
            particle.style.left = `${x}px`;
            particle.style.top = `${y}px`;
            particle.style.transform = `translateZ(${z}px)`;
            particle.style.opacity = opacity;
            
            requestAnimationFrame(animate);
        };
        
        requestAnimationFrame(animate);
    }
    
    getParticleColors(type) {
        const colorSchemes = {
            button: ['#60a5fa', '#3b82f6', '#2563eb'],
            card: ['#a78bfa', '#8b5cf6', '#7c3aed'],
            input: ['#22c55e', '#16a34a', '#15803d'],
            link: ['#f59e0b', '#d97706', '#b45309'],
            image: ['#ef4444', '#dc2626', '#b91c1c'],
            modal: ['#8b5cf6', '#7c3aed', '#6d28d9'],
            default: ['#60a5fa', '#a78bfa', '#f472b6']
        };
        
        return colorSchemes[type] || colorSchemes.default;
    }
    
    createRippleEffect(elementData) {
        const rect = elementData.element.getBoundingClientRect();
        const ripple = document.createElement('div');
        
        const size = Math.max(rect.width, rect.height);
        const x = this.mouseX * window.innerWidth / 2 - rect.left;
        const y = this.mouseY * window.innerHeight / 2 - rect.top;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            left: ${x - size / 2}px;
            top: ${y - size / 2}px;
            transform: translateZ(10px) scale(0);
            animation: rippleEffect 0.6s ease-out forwards;
            pointer-events: none;
        `;
        
        elementData.element.style.position = 'relative';
        elementData.element.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }
    
    playHoverSound(type) {
        // Placeholder for sound effects
        // In a real implementation, you would use Web Audio API
        console.log(`Playing hover sound for ${type}`);
    }
    
    playClickSound(type) {
        // Placeholder for sound effects
        console.log(`Playing click sound for ${type}`);
    }
    
    monitorPerformance() {
        let frameCount = 0;
        let lastTime = performance.now();
        
        const checkPerformance = () => {
            frameCount++;
            const currentTime = performance.now();
            
            if (currentTime - lastTime >= 1000) {
                const fps = frameCount;
                frameCount = 0;
                lastTime = currentTime;
                
                // Adjust quality based on performance
                if (fps < 30) {
                    this.options.performanceMode = true;
                    this.options.enableParticles = false;
                } else if (fps > 50) {
                    this.options.performanceMode = false;
                    this.options.enableParticles = true;
                }
            }
            
            requestAnimationFrame(checkPerformance);
        };
        
        requestAnimationFrame(checkPerformance);
    }
    
    startAnimation() {
        if (this.options.performanceMode) return;
        
        const animate = () => {
            this.updateHoverEffects();
            requestAnimationFrame(animate);
        };
        
        requestAnimationFrame(animate);
    }
    
    // Public methods
    addElementBySelector(selector) {
        document.querySelectorAll(selector).forEach(element => {
            this.addElement(element);
        });
    }
    
    removeElement(element) {
        const index = this.elements.findIndex(e => e.element === element);
        if (index !== -1) {
            this.elements.splice(index, 1);
        }
    }
    
    setIntensity(intensity) {
        this.options.intensity = intensity;
        this.elements.forEach(elementData => {
            elementData.intensity = this.getElementIntensity(elementData.element);
        });
    }
    
    enableParticles(enabled) {
        this.options.enableParticles = enabled;
        if (!enabled && this.particleContainer) {
            this.particleContainer.innerHTML = '';
        }
    }
    
    destroy() {
        // Remove event listeners
        document.removeEventListener('mousemove', this.handleMouseMove);
        document.removeEventListener('touchmove', this.handleTouchMove);
        
        // Remove particle container
        if (this.particleContainer) {
            this.particleContainer.remove();
        }
        
        // Reset elements
        this.elements.forEach(elementData => {
            elementData.element.style.transform = elementData.originalTransform;
            elementData.element.style.transition = elementData.originalTransition;
        });
        
        this.elements = [];
    }
}

// Add CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    @keyframes rippleEffect {
        0% {
            transform: translateZ(10px) scale(0);
            opacity: 1;
        }
        100% {
            transform: translateZ(20px) scale(2);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Auto-initialize hover effects
document.addEventListener('DOMContentLoaded', () => {
    // Check if hover effects should be enabled
    const shouldEnable = !document.body.classList.contains('no-3d-hover');
    
    if (shouldEnable) {
        window.hoverEffects3D = new HoverEffects3D({
            enableParticles: !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
            mobileOptimized: window.innerWidth <= 768
        });
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HoverEffects3D;
}