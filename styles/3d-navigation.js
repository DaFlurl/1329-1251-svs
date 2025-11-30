// 3D Navigation with Parallax Scrolling
class Navigation3D {
    constructor() {
        this.nav = document.querySelector('.nav-3d');
        this.navContainer = document.querySelector('.nav-3d-container');
        this.mobileToggle = document.querySelector('.nav-3d-mobile-toggle');
        this.mobileMenu = document.querySelector('.nav-3d-mobile-menu');
        this.mobileOverlay = document.querySelector('.nav-3d-mobile-overlay');
        this.links = document.querySelectorAll('.nav-3d-link');
        this.dropdowns = document.querySelectorAll('.nav-3d-dropdown');
        
        this.scrollY = 0;
        this.mouseX = 0;
        this.mouseY = 0;
        this.isMenuOpen = false;
        
        this.init();
    }
    
    init() {
        this.createParallaxLayers();
        this.setupEventListeners();
        this.initializeAnimations();
        this.setupIntersectionObserver();
    }
    
    createParallaxLayers() {
        if (!this.navContainer) return;
        
        // Create parallax background layers
        for (let i = 1; i <= 2; i++) {
            const layer = document.createElement('div');
            layer.className = `parallax-nav-layer parallax-nav-layer-${i}`;
            this.navContainer.appendChild(layer);
        }
    }
    
    setupEventListeners() {
        // Scroll events for parallax
        window.addEventListener('scroll', this.handleScroll.bind(this));
        
        // Mouse movement for 3D effects
        document.addEventListener('mousemove', this.handleMouseMove.bind(this));
        
        // Mobile menu toggle
        if (this.mobileToggle) {
            this.mobileToggle.addEventListener('click', this.toggleMobileMenu.bind(this));
        }
        
        if (this.mobileOverlay) {
            this.mobileOverlay.addEventListener('click', this.closeMobileMenu.bind(this));
        }
        
        // Navigation link hover effects
        this.links.forEach(link => {
            link.addEventListener('mouseenter', this.handleLinkHover.bind(this));
            link.addEventListener('mouseleave', this.handleLinkLeave.bind(this));
            link.addEventListener('click', this.handleLinkClick.bind(this));
        });
        
        // Window resize
        window.addEventListener('resize', this.handleResize.bind(this));
    }
    
    handleScroll() {
        this.scrollY = window.scrollY;
        
        if (this.nav) {
            const scrolled = this.scrollY > 50;
            this.nav.classList.toggle('scrolled', scrolled);
            
            // 3D transform based on scroll
            const rotateX = Math.min(this.scrollY * 0.01, 5);
            const translateZ = Math.min(this.scrollY * 0.5, 30);
            
            this.nav.style.transform = `rotateX(${rotateX}deg) translateZ(${-translateZ}px)`;
        }
        
        // Parallax layers
        this.updateParallaxLayers();
    }
    
    handleMouseMove(event) {
        this.mouseX = event.clientX;
        this.mouseY = event.clientY;
        
        if (this.nav && !this.isMenuOpen) {
            const rect = this.nav.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            
            const angleX = (this.mouseY - centerY) * 0.01;
            const angleY = (this.mouseX - centerX) * 0.01;
            
            // Subtle 3D tilt based on mouse position
            this.nav.style.transform = `
                rotateX(${angleX}deg) 
                rotateY(${angleY}deg) 
                translateZ(${-Math.min(this.scrollY * 0.5, 30)}px)
            `;
        }
    }
    
    updateParallaxLayers() {
        const layers = document.querySelectorAll('.parallax-nav-layer');
        layers.forEach((layer, index) => {
            const speed = (index + 1) * 0.5;
            const yPos = -(this.scrollY * speed);
            layer.style.transform = `translateY(${yPos}px) translateZ(${-index * 10}px)`;
        });
    }
    
    handleLinkHover(event) {
        const link = event.currentTarget;
        const rect = link.getBoundingClientRect();
        
        // Create floating particles
        this.createHoverParticles(rect);
        
        // Add glow effect
        link.style.boxShadow = `
            0 10px 30px rgba(96, 165, 250, 0.3),
            0 0 20px rgba(96, 165, 250, 0.2),
            inset 0 0 20px rgba(96, 165, 250, 0.1)
        `;
    }
    
    handleLinkLeave(event) {
        const link = event.currentTarget;
        link.style.boxShadow = '';
    }
    
    handleLinkClick(event) {
        const link = event.currentTarget;
        
        // Add ripple effect
        this.createRippleEffect(event, link);
        
        // Update active state
        this.links.forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        
        // Smooth scroll to section if it's an anchor
        const href = link.getAttribute('href');
        if (href && href.startsWith('#')) {
            event.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }
    }
    
    createHoverParticles(rect) {
        const particleCount = 5;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'nav-3d-particle';
            particle.style.cssText = `
                position: fixed;
                width: 4px;
                height: 4px;
                background: linear-gradient(45deg, #60a5fa, #a78bfa);
                border-radius: 50%;
                pointer-events: none;
                z-index: 1002;
                left: ${rect.left + rect.width / 2}px;
                top: ${rect.top + rect.height / 2}px;
                transform: translateZ(50px);
                animation: navParticleFloat 2s ease-out forwards;
            `;
            
            document.body.appendChild(particle);
            
            // Animate particle
            const angle = (Math.PI * 2 * i) / particleCount;
            const velocity = 100 + Math.random() * 50;
            
            particle.animate([
                {
                    transform: 'translateZ(50px) translate(0, 0) scale(1)',
                    opacity: 1
                },
                {
                    transform: `translateZ(100px) translate(${Math.cos(angle) * velocity}px, ${Math.sin(angle) * velocity}px) scale(0)`,
                    opacity: 0
                }
            ], {
                duration: 2000,
                easing: 'ease-out'
            }).onfinish = () => particle.remove();
        }
    }
    
    createRippleEffect(event, element) {
        const ripple = document.createElement('div');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            left: ${x}px;
            top: ${y}px;
            transform: translateZ(10px);
            animation: rippleEffect 0.6s ease-out forwards;
            pointer-events: none;
        `;
        
        element.appendChild(ripple);
        
        ripple.animate([
            { transform: 'translateZ(10px) scale(0)', opacity: 1 },
            { transform: 'translateZ(20px) scale(2)', opacity: 0 }
        ], {
            duration: 600,
            easing: 'ease-out'
        }).onfinish = () => ripple.remove();
    }
    
    toggleMobileMenu() {
        this.isMenuOpen = !this.isMenuOpen;
        
        if (this.mobileMenu) {
            this.mobileMenu.classList.toggle('active', this.isMenuOpen);
        }
        
        if (this.mobileOverlay) {
            this.mobileOverlay.classList.toggle('active', this.isMenuOpen);
        }
        
        // 3D animation for mobile menu
        if (this.isMenuOpen) {
            this.mobileMenu?.style.setProperty('--rotate-y', '0deg');
        } else {
            this.mobileMenu?.style.setProperty('--rotate-y', '-90deg');
        }
    }
    
    closeMobileMenu() {
        this.isMenuOpen = false;
        
        if (this.mobileMenu) {
            this.mobileMenu.classList.remove('active');
        }
        
        if (this.mobileOverlay) {
            this.mobileOverlay.classList.remove('active');
        }
    }
    
    initializeAnimations() {
        // Add entrance animations to navigation items
        this.links.forEach((link, index) => {
            link.style.opacity = '0';
            link.style.transform = 'translateY(-20px) translateZ(-50px)';
            
            setTimeout(() => {
                link.animate([
                    { opacity: 0, transform: 'translateY(-20px) translateZ(-50px)' },
                    { opacity: 1, transform: 'translateY(0) translateZ(20px)' }
                ], {
                    duration: 600,
                    delay: index * 100,
                    easing: 'ease-out',
                    fill: 'forwards'
                });
            }, 100);
        });
    }
    
    setupIntersectionObserver() {
        // Observe sections for active navigation state
        const sections = document.querySelectorAll('section[id]');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.getAttribute('id');
                    this.updateActiveNavigation(id);
                }
            });
        }, { threshold: 0.3 });
        
        sections.forEach(section => observer.observe(section));
    }
    
    updateActiveNavigation(activeId) {
        this.links.forEach(link => {
            const href = link.getAttribute('href');
            if (href === `#${activeId}`) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }
    
    handleResize() {
        // Recalculate positions on resize
        if (window.innerWidth > 768 && this.isMenuOpen) {
            this.closeMobileMenu();
        }
    }
    
    // Public methods for external control
    scrollToTop() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    setActiveLink(href) {
        this.links.forEach(link => {
            link.classList.toggle('active', link.getAttribute('href') === href);
        });
    }
    
    addNavigationItem(text, href, icon = null) {
        const li = document.createElement('li');
        li.className = 'nav-3d-item';
        
        const link = document.createElement('a');
        link.href = href;
        link.className = 'nav-3d-link';
        link.textContent = text;
        
        if (icon) {
            const iconElement = document.createElement('span');
            iconElement.className = 'nav-3d-icon';
            iconElement.innerHTML = icon;
            link.prepend(iconElement);
        }
        
        li.appendChild(link);
        
        // Add to mobile menu as well
        const menu = document.querySelector('.nav-3d-menu');
        if (menu) {
            menu.appendChild(li);
        }
        
        // Re-setup event listeners for new link
        link.addEventListener('mouseenter', this.handleLinkHover.bind(this));
        link.addEventListener('mouseleave', this.handleLinkLeave.bind(this));
        link.addEventListener('click', this.handleLinkClick.bind(this));
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes navParticleFloat {
        0% { transform: translateZ(50px) translate(0, 0) scale(1); }
        100% { transform: translateZ(100px) translate(var(--tx), var(--ty)) scale(0); }
    }
    
    @keyframes rippleEffect {
        0% { transform: translateZ(10px) scale(0); opacity: 1; }
        100% { transform: translateZ(20px) scale(2); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize navigation when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.navigation3D = new Navigation3D();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Navigation3D;
}