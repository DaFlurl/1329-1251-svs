/**
 * AgentDaf1.1 - Advanced 3D Charts with Three.js Integration
 * Interactive 3D charts and graphs for Excel data visualization
 */

class Advanced3DCharts {
    constructor() {
        this.charts = new Map();
        this.threeJSLoaded = false;
        this.colors = {
            primary: '#00d4ff',
            secondary: '#ff00ff',
            accent: '#00ff88',
            warning: '#ffaa00',
            danger: '#ff0055',
            success: '#00ff88'
        };
        
        this.loadThreeJS();
    }

    async loadThreeJS() {
        if (window.THREE) {
            this.threeJSLoaded = true;
            return;
        }

        // Load Three.js from CDN
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
        script.onload = () => {
            this.threeJSLoaded = true;
            console.log('🎮 Three.js loaded for 3D charts');
        };
        document.head.appendChild(script);
    }

    // 3D Surface Plot for Excel Data
    create3DSurfacePlot(containerId, data, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        if (!this.threeJSLoaded) {
            console.warn('Three.js not loaded yet, falling back to 2D visualization');
            return this.createFallbackChart(containerId, data, 'surface');
        }

        const width = container.offsetWidth || 800;
        const height = container.offsetHeight || 400;

        // Three.js scene setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        
        renderer.setSize(width, height);
        renderer.setClearColor(0x000000, 0);
        container.innerHTML = '';
        container.appendChild(renderer.domElement);

        // Create surface mesh from data
        const geometry = new THREE.BufferGeometry();
        const vertices = [];
        const colors = [];

        const rows = data.length;
        const cols = data[0].length;
        const maxValue = Math.max(...data.flat());

        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                const x = (j - cols / 2) * 2;
                const y = (data[i][j] / maxValue) * 10;
                const z = (i - rows / 2) * 2;
                
                vertices.push(x, y, z);
                
                // Color based on height
                const colorValue = data[i][j] / maxValue;
                const color = new THREE.Color();
                color.setHSL(0.6 - colorValue * 0.4, 1, 0.5);
                colors.push(color.r, color.g, color.b);
            }
        }

        geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

        // Create surface triangles
        const indices = [];
        for (let i = 0; i < rows - 1; i++) {
            for (let j = 0; j < cols - 1; j++) {
                const a = i * cols + j;
                const b = i * cols + j + 1;
                const c = (i + 1) * cols + j;
                const d = (i + 1) * cols + j + 1;

                indices.push(a, b, c);
                indices.push(b, d, c);
            }
        }

        geometry.setIndex(indices);
        geometry.computeVertexNormals();

        const material = new THREE.MeshPhongMaterial({
            vertexColors: true,
            side: THREE.DoubleSide,
            shininess: 100,
            specular: new THREE.Color(0x222222)
        });

        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        scene.add(directionalLight);

        const pointLight = new THREE.PointLight(0x00d4ff, 1, 100);
        pointLight.position.set(0, 20, 0);
        scene.add(pointLight);

        // Camera position
        camera.position.set(20, 20, 20);
        camera.lookAt(0, 0, 0);

        // Animation
        const chartId = `surface_${Date.now()}`;
        let animationId;

        const animate = () => {
            animationId = requestAnimationFrame(animate);
            
            mesh.rotation.y += 0.005;
            
            renderer.render(scene, camera);
        };

        animate();

        // Mouse interaction
        let mouseX = 0, mouseY = 0;
        const handleMouseMove = (event) => {
            const rect = container.getBoundingClientRect();
            mouseX = ((event.clientX - rect.left) / width) * 2 - 1;
            mouseY = -((event.clientY - rect.top) / height) * 2 + 1;
        };

        container.addEventListener('mousemove', handleMouseMove);

        // Store chart reference
        this.charts.set(chartId, {
            type: 'surface3d',
            scene: scene,
            camera: camera,
            renderer: renderer,
            mesh: mesh,
            animationId: animationId,
            container: container
        });

        return {
            update: (newData) => this.updateSurfacePlot(chartId, newData),
            destroy: () => this.destroyChart(chartId),
            resize: (w, h) => this.resizeChart(chartId, w, h)
        };
    }

    // 3D Scatter Plot
    create3DScatterPlot(containerId, data, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        if (!this.threeJSLoaded) {
            return this.createFallbackChart(containerId, data, 'scatter');
        }

        const width = container.offsetWidth || 800;
        const height = container.offsetHeight || 400;

        // Three.js setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        
        renderer.setSize(width, height);
        renderer.setClearColor(0x000000, 0);
        container.innerHTML = '';
        container.appendChild(renderer.domElement);

        // Create scatter points
        const group = new THREE.Group();
        
        data.forEach((point, index) => {
            const geometry = new THREE.SphereGeometry(point.size || 0.5, 16, 16);
            const material = new THREE.MeshPhongMaterial({
                color: point.color || this.colors.primary,
                emissive: point.color || this.colors.primary,
                emissiveIntensity: 0.2
            });
            
            const sphere = new THREE.Mesh(geometry, material);
            sphere.position.set(point.x || 0, point.y || 0, point.z || 0);
            
            group.add(sphere);
        });

        scene.add(group);

        // Add grid
        const gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x222222);
        scene.add(gridHelper);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        scene.add(directionalLight);

        // Camera position
        camera.position.set(15, 15, 15);
        camera.lookAt(0, 0, 0);

        // Animation
        const chartId = `scatter_${Date.now()}`;
        let animationId;

        const animate = () => {
            animationId = requestAnimationFrame(animate);
            
            group.rotation.y += 0.003;
            
            renderer.render(scene, camera);
        };

        animate();

        // Store chart reference
        this.charts.set(chartId, {
            type: 'scatter3d',
            scene: scene,
            camera: camera,
            renderer: renderer,
            group: group,
            animationId: animationId,
            container: container
        });

        return {
            update: (newData) => this.updateScatterPlot(chartId, newData),
            destroy: () => this.destroyChart(chartId),
            resize: (w, h) => this.resizeChart(chartId, w, h)
        };
    }

    // 3D Bar Chart with Three.js
    create3DBarChartAdvanced(containerId, data, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        if (!this.threeJSLoaded) {
            return this.createFallbackChart(containerId, data, 'bar');
        }

        const width = container.offsetWidth || 800;
        const height = container.offsetHeight || 400;

        // Three.js setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        
        renderer.setSize(width, height);
        renderer.setClearColor(0x000000, 0);
        container.innerHTML = '';
        container.appendChild(renderer.domElement);

        // Create 3D bars
        const group = new THREE.Group();
        const maxValue = Math.max(...data.map(d => d.value));
        const barWidth = 1;
        const barDepth = 1;
        const spacing = 0.5;

        data.forEach((item, index) => {
            const barHeight = (item.value / maxValue) * 10;
            const geometry = new THREE.BoxGeometry(barWidth, barHeight, barDepth);
            
            const material = new THREE.MeshPhongMaterial({
                color: item.color || this.colors.primary,
                emissive: item.color || this.colors.primary,
                emissiveIntensity: 0.1
            });
            
            const bar = new THREE.Mesh(geometry, material);
            bar.position.set(
                index * (barWidth + spacing) - (data.length * (barWidth + spacing)) / 2,
                barHeight / 2,
                0
            );
            
            group.add(bar);

            // Add value label
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = 128;
            canvas.height = 64;
            context.fillStyle = '#ffffff';
            context.font = '24px Arial';
            context.textAlign = 'center';
            context.fillText(item.value.toString(), 64, 40);

            const texture = new THREE.CanvasTexture(canvas);
            const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
            const sprite = new THREE.Sprite(spriteMaterial);
            sprite.position.set(
                index * (barWidth + spacing) - (data.length * (barWidth + spacing)) / 2,
                barHeight + 1,
                0
            );
            sprite.scale.set(2, 1, 1);
            
            group.add(sprite);
        });

        scene.add(group);

        // Add base platform
        const platformGeometry = new THREE.BoxGeometry(data.length * (barWidth + spacing), 0.1, 5);
        const platformMaterial = new THREE.MeshPhongMaterial({ color: 0x333333 });
        const platform = new THREE.Mesh(platformGeometry, platformMaterial);
        platform.position.y = -0.05;
        scene.add(platform);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        scene.add(directionalLight);

        const pointLight = new THREE.PointLight(0x00d4ff, 0.5, 100);
        pointLight.position.set(0, 10, 0);
        scene.add(pointLight);

        // Camera position
        camera.position.set(15, 10, 15);
        camera.lookAt(0, 2, 0);

        // Animation
        const chartId = `bar3d_${Date.now()}`;
        let animationId;

        const animate = () => {
            animationId = requestAnimationFrame(animate);
            
            group.rotation.y += 0.005;
            
            renderer.render(scene, camera);
        };

        animate();

        // Store chart reference
        this.charts.set(chartId, {
            type: 'bar3d',
            scene: scene,
            camera: camera,
            renderer: renderer,
            group: group,
            animationId: animationId,
            container: container
        });

        return {
            update: (newData) => this.updateBarChart(chartId, newData),
            destroy: () => this.destroyChart(chartId),
            resize: (w, h) => this.resizeChart(chartId, w, h)
        };
    }

    // 3D Line Chart
    create3DLineChartAdvanced(containerId, datasets, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        if (!this.threeJSLoaded) {
            return this.createFallbackChart(containerId, datasets, 'line');
        }

        const width = container.offsetWidth || 800;
        const height = container.offsetHeight || 400;

        // Three.js setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        
        renderer.setSize(width, height);
        renderer.setClearColor(0x000000, 0);
        container.innerHTML = '';
        container.appendChild(renderer.domElement);

        // Create 3D lines
        const group = new THREE.Group();
        
        datasets.forEach((dataset, datasetIndex) => {
            const points = [];
            const maxValue = Math.max(...dataset.data);
            
            dataset.data.forEach((value, index) => {
                const x = index * 2 - dataset.data.length;
                const y = (value / maxValue) * 10;
                const z = datasetIndex * 2 - datasets.length / 2;
                
                points.push(new THREE.Vector3(x, y, z));
            });

            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const material = new THREE.LineBasicMaterial({
                color: dataset.color || this.colors.primary,
                linewidth: 3
            });
            
            const line = new THREE.Line(geometry, material);
            group.add(line);

            // Add data points
            points.forEach((point, index) => {
                const sphereGeometry = new THREE.SphereGeometry(0.2, 8, 8);
                const sphereMaterial = new THREE.MeshPhongMaterial({
                    color: dataset.color || this.colors.primary,
                    emissive: dataset.color || this.colors.primary,
                    emissiveIntensity: 0.3
                });
                
                const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
                sphere.position.copy(point);
                group.add(sphere);
            });
        });

        scene.add(group);

        // Add grid
        const gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x222222);
        scene.add(gridHelper);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        scene.add(directionalLight);

        // Camera position
        camera.position.set(15, 10, 15);
        camera.lookAt(0, 0, 0);

        // Animation
        const chartId = `line3d_${Date.now()}`;
        let animationId;

        const animate = () => {
            animationId = requestAnimationFrame(animate);
            
            group.rotation.y += 0.003;
            
            renderer.render(scene, camera);
        };

        animate();

        // Store chart reference
        this.charts.set(chartId, {
            type: 'line3d',
            scene: scene,
            camera: camera,
            renderer: renderer,
            group: group,
            animationId: animationId,
            container: container
        });

        return {
            update: (newData) => this.updateLineChart(chartId, newData),
            destroy: () => this.destroyChart(chartId),
            resize: (w, h) => this.resizeChart(chartId, w, h)
        };
    }

    // Fallback 2D charts for older browsers
    createFallbackChart(containerId, data, type) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        const canvas = document.createElement('canvas');
        canvas.width = container.offsetWidth || 800;
        canvas.height = container.offsetHeight || 400;
        container.innerHTML = '';
        container.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        
        // Simple 2D visualization based on type
        switch (type) {
            case 'surface':
                this.draw2DSurface(ctx, data, canvas.width, canvas.height);
                break;
            case 'scatter':
                this.draw2DScatter(ctx, data, canvas.width, canvas.height);
                break;
            case 'bar':
                this.draw2DBars(ctx, data, canvas.width, canvas.height);
                break;
            case 'line':
                this.draw2DLines(ctx, data, canvas.width, canvas.height);
                break;
        }

        return {
            update: () => console.log('Fallback chart - update not implemented'),
            destroy: () => container.innerHTML = '',
            resize: (w, h) => {
                canvas.width = w;
                canvas.height = h;
            }
        };
    }

    draw2DSurface(ctx, data, width, height) {
        const rows = data.length;
        const cols = data[0].length;
        const maxValue = Math.max(...data.flat());
        
        const cellWidth = width / cols;
        const cellHeight = height / rows;
        
        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                const value = data[i][j];
                const intensity = value / maxValue;
                
                const hue = 240 - intensity * 60; // Blue to cyan
                ctx.fillStyle = `hsl(${hue}, 100%, ${50 + intensity * 30}%)`;
                
                ctx.fillRect(j * cellWidth, i * cellHeight, cellWidth, cellHeight);
            }
        }
    }

    draw2DScatter(ctx, data, width, height) {
        data.forEach(point => {
            ctx.beginPath();
            ctx.arc(
                (point.x + 10) * width / 20,
                (point.y + 10) * height / 20,
                point.size || 5,
                0,
                Math.PI * 2
            );
            ctx.fillStyle = point.color || this.colors.primary;
            ctx.fill();
        });
    }

    draw2DBars(ctx, data, width, height) {
        const padding = 40;
        const barWidth = (width - padding * 2) / data.length;
        const maxValue = Math.max(...data.map(d => d.value));
        
        data.forEach((item, index) => {
            const barHeight = (item.value / maxValue) * (height - padding * 2);
            const x = padding + index * barWidth;
            const y = height - padding - barHeight;
            
            ctx.fillStyle = item.color || this.colors.primary;
            ctx.fillRect(x, y, barWidth * 0.8, barHeight);
        });
    }

    draw2DLines(ctx, datasets, width, height) {
        const padding = 40;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        
        datasets.forEach(dataset => {
            const maxValue = Math.max(...dataset.data);
            
            ctx.strokeStyle = dataset.color || this.colors.primary;
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            dataset.data.forEach((value, index) => {
                const x = padding + (index / (dataset.data.length - 1)) * chartWidth;
                const y = height - padding - (value / maxValue) * chartHeight;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
        });
    }

    // Update methods
    updateSurfacePlot(chartId, newData) {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        // Implementation for updating surface plot
        console.log('Updating 3D surface plot with new data:', newData);
    }

    updateScatterPlot(chartId, newData) {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        // Implementation for updating scatter plot
        console.log('Updating 3D scatter plot with new data:', newData);
    }

    updateBarChart(chartId, newData) {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        // Implementation for updating bar chart
        console.log('Updating 3D bar chart with new data:', newData);
    }

    updateLineChart(chartId, newData) {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        // Implementation for updating line chart
        console.log('Updating 3D line chart with new data:', newData);
    }

    // Resize chart
    resizeChart(chartId, width, height) {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        chart.camera.aspect = width / height;
        chart.camera.updateProjectionMatrix();
        chart.renderer.setSize(width, height);
    }

    // Destroy chart
    destroyChart(chartId) {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        if (chart.animationId) {
            cancelAnimationFrame(chart.animationId);
        }
        
        if (chart.renderer) {
            chart.renderer.dispose();
        }
        
        if (chart.container && chart.renderer.domElement) {
            chart.container.removeChild(chart.renderer.domElement);
        }
        
        this.charts.delete(chartId);
    }

    // Excel data integration
    createExcelDashboard3D(containerId, excelData, options = {}) {
        const dashboard = document.getElementById(containerId);
        if (!dashboard) return null;

        dashboard.innerHTML = '';
        dashboard.className = 'dashboard-3d-advanced';

        const charts = {};

        // 3D Surface Plot for data correlation
        if (excelData.correlation) {
            const surfaceContainer = document.createElement('div');
            surfaceContainer.id = `surface_${Date.now()}`;
            surfaceContainer.className = 'chart-container-3d';
            surfaceContainer.style.height = '400px';
            dashboard.appendChild(surfaceContainer);

            charts.surface = this.create3DSurfacePlot(surfaceContainer.id, excelData.correlation, {
                title: 'Data Correlation Matrix'
            });
        }

        // 3D Scatter Plot for data clusters
        if (excelData.clusters) {
            const scatterContainer = document.createElement('div');
            scatterContainer.id = `scatter_${Date.now()}`;
            scatterContainer.className = 'chart-container-3d';
            scatterContainer.style.height = '400px';
            dashboard.appendChild(scatterContainer);

            charts.scatter = this.create3DScatterPlot(scatterContainer.id, excelData.clusters, {
                title: 'Data Clusters'
            });
        }

        // 3D Bar Chart for categories
        if (excelData.categories) {
            const barContainer = document.createElement('div');
            barContainer.id = `bar_${Date.now()}`;
            barContainer.className = 'chart-container-3d';
            barContainer.style.height = '400px';
            dashboard.appendChild(barContainer);

            charts.bar = this.create3DBarChartAdvanced(barContainer.id, excelData.categories, {
                title: 'Category Analysis'
            });
        }

        // 3D Line Chart for trends
        if (excelData.trends) {
            const lineContainer = document.createElement('div');
            lineContainer.id = `line_${Date.now()}`;
            lineContainer.className = 'chart-container-3d';
            lineContainer.style.height = '400px';
            dashboard.appendChild(lineContainer);

            charts.line = this.create3DLineChartAdvanced(lineContainer.id, excelData.trends, {
                title: 'Trend Analysis'
            });
        }

        return {
            update: (newData) => {
                Object.keys(charts).forEach(key => {
                    if (newData[key] && charts[key]) {
                        charts[key].update(newData[key]);
                    }
                });
            },
            destroy: () => {
                Object.values(charts).forEach(chart => {
                    if (chart && chart.destroy) {
                        chart.destroy();
                    }
                });
            }
        };
    }
}

// Initialize Advanced 3D Charts
document.addEventListener('DOMContentLoaded', () => {
    window.advanced3DCharts = new Advanced3DCharts();
    
    // Auto-initialize charts with data-3d-chart attributes
    const chartElements = document.querySelectorAll('[data-3d-chart]');
    chartElements.forEach(element => {
        const chartType = element.dataset['3dChart'];
        const chartData = JSON.parse(element.dataset.data || '{}');
        const chartOptions = JSON.parse(element.dataset.options || '{}');
        
        setTimeout(() => {
            if (window.advanced3DCharts[`create3D${chartType.charAt(0).toUpperCase() + chartType.slice(1)}`]) {
                window.advanced3DCharts[`create3D${chartType.charAt(0).toUpperCase() + chartType.slice(1)}`](
                    element.id,
                    chartData,
                    chartOptions
                );
            }
        }, 1000); // Delay to ensure Three.js is loaded
    });
});

// Export for global access
window.Advanced3DCharts = Advanced3DCharts;