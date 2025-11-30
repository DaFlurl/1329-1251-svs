// 3D Background with Geometric Shapes
class Background3D {
    constructor(options = {}) {
        this.container = null;
        this.layers = [];
        this.shapes = [];
        this.particles = [];
        this.connections = [];
        
        this.options = {
            shapeCount: options.shapeCount || 15,
            particleCount: options.particleCount || 50,
            connectionCount: options.connectionCount || 8,
            interactive: options.interactive !== false,
            responsive: options.responsive !== false,
            performanceMode: options.performanceMode || false
        };
        
        this.mouseX = 0;
        this.mouseY = 0;
        this.scrollY = 0;
        
        this.init();
    }
    
    init() {
        this.createContainer();
        this.createLayers();
        this.createShapes();
        this.createParticles();
        this.createConnections();
        this.createGrid();
        this.setupEventListeners();
        this.startAnimation();
    }
    
    createContainer() {
        this.container = document.createElement('div');
        this.container.className = `background-3d ${this.options.interactive ? 'interactive' : ''}`;
        document.body.appendChild(this.container);
    }
    
    createLayers() {
        for (let i = 1; i <= 4; i++) {
            const layer = document.createElement('div');
            layer.className = `background-3d-layer background-3d-layer-${i}`;
            this.container.appendChild(layer);
            this.layers.push(layer);
        }
    }
    
    createShapes() {
        const shapeTypes = ['cube', 'pyramid', 'sphere', 'hexagon', 'diamond', 'triangle', 'morph'];
        
        for (let i = 0; i < this.options.shapeCount; i++) {
            const shapeType = shapeTypes[Math.floor(Math.random() * shapeTypes.length)];
            const shape = this.createShape(shapeType);
            
            // Random position
            shape.style.left = `${Math.random() * 100}%`;
            shape.style.top = `${Math.random() * 100}%`;
            
            // Random layer
            const layerIndex = Math.floor(Math.random() * this.layers.length);
            this.layers[layerIndex].appendChild(shape);
            
            this.shapes.push({
                element: shape,
                type: shapeType,
                layer: layerIndex,
                x: parseFloat(shape.style.left),
                y: parseFloat(shape.style.top),
                z: -layerIndex * 100,
                velocity: {
                    x: (Math.random() - 0.5) * 0.5,
                    y: (Math.random() - 0.5) * 0.5,
                    z: (Math.random() - 0.5) * 0.2
                }
            });
        }
    }
    
    createShape(type) {
        const shape = document.createElement('div');
        shape.className = `geo-3d-shape geo-3d-${type}`;
        
        // Add random animation delay
        shape.style.animationDelay = `${Math.random() * 5}s`;
        
        // Random size variation
        const scale = 0.5 + Math.random() * 1;
        shape.style.transform = `scale(${scale})`;
        
        return shape;
    }
    
    createParticles() {
        const particlesContainer = document.createElement('div');
        particlesContainer.className = 'geo-3d-particles';
        this.layers[2].appendChild(particlesContainer); // Middle layer
        
        for (let i = 0; i < this.options.particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'geo-3d-particle';
            
            // Random position
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = `${Math.random() * 100}%`;
            
            // Random animation delay and duration
            particle.style.animationDelay = `${Math.random() * 10}s`;
            particle.style.animationDuration = `${10 + Math.random() * 10}s`;
            
            // Random size
            const size = 1 + Math.random() * 3;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            
            particlesContainer.appendChild(particle);
            
            this.particles.push({
                element: particle,
                x: parseFloat(particle.style.left),
                y: parseFloat(particle.style.top),
                z: (Math.random() - 0.5) * 200,
                velocity: {
                    x: (Math.random() - 0.5) * 0.2,
                    y: -Math.random() * 0.5 - 0.1,
                    z: (Math.random() - 0.5) * 0.1
                }
            });
        }
    }
    
    createConnections() {
        const connectionsContainer = document.createElement('div');
        connectionsContainer.className = 'geo-3d-connections';
        this.layers[1].appendChild(connectionsContainer); // Background layer
        
        for (let i = 0; i < this.options.connectionCount; i++) {
            const connection = document.createElement('div');
            connection.className = 'geo-3d-connection';
            
            // Random position and size
            const x1 = Math.random() * 100;
            const y1 = Math.random() * 100;
            const x2 = Math.random() * 100;
            const y2 = Math.random() * 100;
            
            const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
            const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
            
            connection.style.left = `${x1}%`;
            connection.style.top = `${y1}%`;
            connection.style.width = `${length}%`;
            connection.style.transform = `rotate(${angle}deg) translateZ(-50px)`;
            
            connection.style.animationDelay = `${Math.random() * 8}s`;
            
            connectionsContainer.appendChild(connection);
            
            this.connections.push({
                element: connection,
                x1: x1,
                y1: y1,
                x2: x2,
                y2: y2,
                angle: angle,
                length: length
            });
        }
    }
    
    createGrid() {
        const grid = document.createElement('div');
        grid.className = 'geo-3d-grid';
        this.layers[0].appendChild(grid); // Far background layer
    }
    
    setupEventListeners() {
        if (this.options.interactive) {
            document.addEventListener('mousemove', this.handleMouseMove.bind(this));
            window.addEventListener('scroll', this.handleScroll.bind(this));
        }
        
        if (this.options.responsive) {
            window.addEventListener('resize', this.handleResize.bind(this));
        }
    }
    
    handleMouseMove(event) {
        this.mouseX = (event.clientX / window.innerWidth - 0.5) * 2;
        this.mouseY = (event.clientY / window.innerHeight - 0.5) * 2;
        
        this.updateInteractiveElements();
    }
    
    handleScroll() {
        this.scrollY = window.scrollY;
        this.updateParallax();
    }
    
    handleResize() {
        // Adjust shape positions for new viewport
        this.shapes.forEach(shape => {
            shape.x = Math.min(shape.x, 100);
            shape.y = Math.min(shape.y, 100);
        });
    }
    
    updateInteractiveElements() {
        if (!this.options.interactive) return;
        
        // Update shapes based on mouse position
        this.shapes.forEach((shape, index) => {
            const intensity = (index + 1) / this.shapes.length;
            const moveX = this.mouseX * 10 * intensity;
            const moveY = this.mouseY * 10 * intensity;
            
            shape.element.style.transform = `
                translateX(${moveX}px) 
                translateY(${moveY}px) 
                translateZ(${shape.z + Math.abs(this.mouseX * this.mouseY * 20)}px)
                rotateX(${this.mouseY * 20 * intensity}deg)
                rotateY(${this.mouseX * 20 * intensity}deg)
            `;
        });
        
        // Update particles
        this.particles.forEach((particle, index) => {
            const intensity = (index + 1) / this.particles.length;
            const moveX = this.mouseX * 5 * intensity;
            const moveY = this.mouseY * 5 * intensity;
            
            particle.element.style.transform = `
                translateX(${moveX}px) 
                translateY(${moveY}px) 
                translateZ(${particle.z + this.mouseX * 10}px)
            `;
        });
    }
    
    updateParallax() {
        // Parallax effect on scroll
        this.layers.forEach((layer, index) => {
            const speed = (index + 1) * 0.1;
            const yPos = -this.scrollY * speed;
            layer.style.transform = `translateY(${yPos}px) translateZ(${-index * 100}px)`;
        });
    }
    
    startAnimation() {
        if (this.options.performanceMode) return;
        
        const animate = () => {
            this.animateShapes();
            this.animateParticles();
            this.animateConnections();
            
            requestAnimationFrame(animate);
        };
        
        animate();
    }
    
    animateShapes() {
        this.shapes.forEach(shape => {
            // Update position
            shape.x += shape.velocity.x;
            shape.y += shape.velocity.y;
            shape.z += shape.velocity.z;
            
            // Boundary check
            if (shape.x < 0 || shape.x > 100) shape.velocity.x *= -1;
            if (shape.y < 0 || shape.y > 100) shape.velocity.y *= -1;
            if (shape.z < -200 || shape.z > 200) shape.velocity.z *= -1;
            
            // Apply position if not in interactive mode
            if (!this.options.interactive) {
                shape.element.style.left = `${shape.x}%`;
                shape.element.style.top = `${shape.y}%`;
            }
        });
    }
    
    animateParticles() {
        this.particles.forEach(particle => {
            // Update position
            particle.x += particle.velocity.x;
            particle.y += particle.velocity.y;
            particle.z += particle.velocity.z;
            
            // Reset particle when it goes off screen
            if (particle.y < -10) {
                particle.y = 110;
                particle.x = Math.random() * 100;
                particle.z = (Math.random() - 0.5) * 200;
            }
            
            if (particle.x < -10 || particle.x > 110) {
                particle.velocity.x *= -1;
            }
            
            // Apply position if not in interactive mode
            if (!this.options.interactive) {
                particle.element.style.left = `${particle.x}%`;
                particle.element.style.top = `${particle.y}%`;
            }
        });
    }
    
    animateConnections() {
        this.connections.forEach(connection => {
            // Subtle pulsing effect
            const time = Date.now() * 0.001;
            const pulse = Math.sin(time + connection.length) * 0.1 + 1;
            
            connection.element.style.opacity = 0.1 * pulse;
            connection.element.style.transform = `
                rotate(${connection.angle}deg) 
                translateZ(${-50 + Math.sin(time) * 20}px)
                scaleX(${pulse})
            `;
        });
    }
    
    // Public methods
    addShape(type, position = null) {
        const shape = this.createShape(type);
        
        if (position) {
            shape.style.left = `${position.x}%`;
            shape.style.top = `${position.y}%`;
        } else {
            shape.style.left = `${Math.random() * 100}%`;
            shape.style.top = `${Math.random() * 100}%`;
        }
        
        const layerIndex = Math.floor(Math.random() * this.layers.length);
        this.layers[layerIndex].appendChild(shape);
        
        this.shapes.push({
            element: shape,
            type: type,
            layer: layerIndex,
            x: parseFloat(shape.style.left),
            y: parseFloat(shape.style.top),
            z: -layerIndex * 100,
            velocity: {
                x: (Math.random() - 0.5) * 0.5,
                y: (Math.random() - 0.5) * 0.5,
                z: (Math.random() - 0.5) * 0.2
            }
        });
        
        return shape;
    }
    
    removeShape(index) {
        if (index >= 0 && index < this.shapes.length) {
            const shape = this.shapes[index];
            shape.element.remove();
            this.shapes.splice(index, 1);
        }
    }
    
    setInteractive(interactive) {
        this.options.interactive = interactive;
        this.container.classList.toggle('interactive', interactive);
    }
    
    setPerformanceMode(enabled) {
        this.options.performanceMode = enabled;
        
        if (enabled) {
            // Disable animations for performance
            this.shapes.forEach(shape => {
                shape.element.style.animation = 'none';
            });
            this.particles.forEach(particle => {
                particle.element.style.animation = 'none';
            });
        } else {
            // Re-enable animations
            this.shapes.forEach(shape => {
                shape.element.style.animation = '';
            });
            this.particles.forEach(particle => {
                particle.element.style.animation = '';
            });
            this.startAnimation();
        }
    }
    
    destroy() {
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
        
        // Remove event listeners
        document.removeEventListener('mousemove', this.handleMouseMove);
        window.removeEventListener('scroll', this.handleScroll);
        window.removeEventListener('resize', this.handleResize);
    }
}

// Auto-initialize background
document.addEventListener('DOMContentLoaded', () => {
    // Check if background should be created
    const shouldCreateBackground = !document.body.classList.contains('no-3d-background');
    
    if (shouldCreateBackground) {
        window.background3D = new Background3D({
            interactive: true,
            responsive: true,
            performanceMode: window.matchMedia('(prefers-reduced-motion: reduce)').matches
        });
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Background3D;
}