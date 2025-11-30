/**
 * AgentDaf1.1 - 3D Data Visualization Components
 * Advanced 3D charts and data visualization for Excel dashboards
 */

class DataVisualization3D {
    constructor() {
        this.charts = new Map();
        this.threeJSCharts = new Map();
        this.isWebGLSupported = this.checkWebGLSupport();
        this.colors = {
            primary: '#00d4ff',
            secondary: '#ff00ff', 
            accent: '#00ff88',
            warning: '#ffaa00',
            danger: '#ff0055',
            success: '#00ff88'
        };
    }

    checkWebGLSupport() {
        try {
            const canvas = document.createElement('canvas');
            return !!(window.WebGLRenderingContext && 
                     (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
        } catch (e) {
            return false;
        }
    }

    // 3D Bar Chart
    create3DBarChart(containerId, data, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        const canvas = document.createElement('canvas');
        canvas.width = container.offsetWidth || 800;
        canvas.height = container.offsetHeight || 400;
        container.innerHTML = '';
        container.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        const chartId = `chart_${Date.now()}`;
        
        this.charts.set(chartId, {
            type: 'bar3d',
            canvas: canvas,
            ctx: ctx,
            data: data,
            options: { ...this.getDefaultOptions(), ...options }
        });

        this.draw3DBarChart(chartId);
        this.addChartInteractivity(chartId);

        return {
            update: (newData) => this.updateChart(chartId, newData),
            destroy: () => this.destroyChart(chartId),
            resize: (width, height) => this.resizeChart(chartId, width, height)
        };
    }

    draw3DBarChart(chartId) {
        const chart = this.charts.get(chartId);
        if (!chart) return;

        const { ctx, canvas, data, options } = chart;
        const width = canvas.width;
        const height = canvas.height;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Chart dimensions
        const padding = 60;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        const barWidth = chartWidth / data.length * 0.6;
        const barSpacing = chartWidth / data.length * 0.4;
        const maxValue = Math.max(...data.map(d => d.value));
        
        // 3D perspective settings
        const perspective = 0.3;
        const depth = 20;
        
        // Sort data for proper 3D rendering
        const sortedData = [...data].sort((a, b) => a.value - b.value);
        
        // Draw grid
        this.draw3DGrid(ctx, padding, chartWidth, chartHeight, maxValue);
        
        // Draw bars from back to front for proper 3D effect
        sortedData.forEach((item, index) => {
            const originalIndex = data.indexOf(item);
            const x = padding + originalIndex * (barWidth + barSpacing);
            const barHeight = (item.value / maxValue) * chartHeight;
            const y = height - padding - barHeight;
            
            // Calculate 3D positions
            const zOffset = index * 2;
            const x3D = x + zOffset * perspective;
            const y3D = y - zOffset * perspective;
            
            // Draw bar shadow
            ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
            ctx.fillRect(x3D + 5, height - padding + 5, barWidth, 10);
            
            // Draw bar sides (3D effect)
            ctx.fillStyle = this.adjustColor(item.color || this.colors.primary, -30);
            ctx.beginPath();
            ctx.moveTo(x3D + barWidth, y3D);
            ctx.lineTo(x3D + barWidth + depth, y3D - depth);
            ctx.lineTo(x3D + barWidth + depth, height - padding - depth);
            ctx.lineTo(x3D + barWidth, height - padding);
            ctx.closePath();
            ctx.fill();
            
            // Draw bar top (3D effect)
            ctx.fillStyle = this.adjustColor(item.color || this.colors.primary, 20);
            ctx.beginPath();
            ctx.moveTo(x3D, y3D);
            ctx.lineTo(x3D + depth, y3D - depth);
            ctx.lineTo(x3D + barWidth + depth, y3D - depth);
            ctx.lineTo(x3D + barWidth, y3D);
            ctx.closePath();
            ctx.fill();
            
            // Draw bar front with gradient
            const gradient = ctx.createLinearGradient(0, y3D, 0, height - padding);
            gradient.addColorStop(0, item.color || this.colors.primary);
            gradient.addColorStop(1, this.adjustColor(item.color || this.colors.primary, -40));
            ctx.fillStyle = gradient;
            ctx.fillRect(x3D, y3D, barWidth, barHeight);
            
            // Draw value label
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 12px Inter';
            ctx.textAlign = 'center';
            ctx.fillText(item.value, x3D + barWidth / 2, y3D - 10);
            
            // Draw x-axis label
            ctx.save();
            ctx.translate(x3D + barWidth / 2, height - padding + 20);
            ctx.rotate(-Math.PI / 6);
            ctx.fillText(item.label, 0, 0);
            ctx.restore();
        });
        
        // Draw title
        if (options.title) {
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 18px Inter';
            ctx.textAlign = 'center';
            ctx.fillText(options.title, width / 2, 30);
        }
    }

    // 3D Pie Chart
    create3DPieChart(containerId, data, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        const canvas = document.createElement('canvas');
        canvas.width = container.offsetWidth || 600;
        canvas.height = container.offsetHeight || 400;
        container.innerHTML = '';
        container.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        const chartId = `pie_${Date.now()}`;
        
        this.charts.set(chartId, {
            type: 'pie3d',
            canvas: canvas,
            ctx: ctx,
            data: data,
            options: { ...this.getDefaultOptions(), ...options }
        });

        this.draw3DPieChart(chartId);
        this.addChartInteractivity(chartId);

        return {
            update: (newData) => this.updateChart(chartId, newData),
            destroy: () => this.destroyChart(chartId),
            resize: (width, height) => this.resizeChart(chartId, width, height)
        };
    }

    draw3DPieChart(chartId) {
        const chart = this.charts.get(chartId);
        if (!chart) return;

        const { ctx, canvas, data, options } = chart;
        const width = canvas.width;
        const height = canvas.height;
        
        ctx.clearRect(0, 0, width, height);
        
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) / 3;
        const depth = 30;
        
        // Calculate total
        const total = data.reduce((sum, item) => sum + item.value, 0);
        
        // Draw 3D pie sides (bottom part)
        let currentAngle = -Math.PI / 2;
        
        data.forEach((item, index) => {
            const sliceAngle = (item.value / total) * Math.PI * 2;
            
            // Draw side walls for 3D effect
            ctx.fillStyle = this.adjustColor(item.color || this.colors.primary, -40);
            ctx.beginPath();
            
            // Bottom edge
            for (let angle = currentAngle; angle <= currentAngle + sliceAngle; angle += 0.1) {
                const x = centerX + Math.cos(angle) * radius;
                const y = centerY + Math.sin(angle) * radius + depth;
                if (angle === currentAngle) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            
            // Top edge
            for (let angle = currentAngle + sliceAngle; angle >= currentAngle; angle -= 0.1) {
                const x = centerX + Math.cos(angle) * radius;
                const y = centerY + Math.sin(angle) * radius;
                ctx.lineTo(x, y);
            }
            
            ctx.closePath();
            ctx.fill();
            
            currentAngle += sliceAngle;
        });
        
        // Draw pie slices
        currentAngle = -Math.PI / 2;
        
        data.forEach((item, index) => {
            const sliceAngle = (item.value / total) * Math.PI * 2;
            
            // Draw slice
            ctx.fillStyle = item.color || this.colors.primary;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.closePath();
            ctx.fill();
            
            // Draw border
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // Draw label
            const labelAngle = currentAngle + sliceAngle / 2;
            const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7);
            const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7);
            
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 12px Inter';
            ctx.textAlign = 'center';
            ctx.fillText(`${item.label}`, labelX, labelY);
            ctx.fillText(`${((item.value / total) * 100).toFixed(1)}%`, labelX, labelY + 15);
            
            currentAngle += sliceAngle;
        });
        
        // Draw title
        if (options.title) {
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 18px Inter';
            ctx.textAlign = 'center';
            ctx.fillText(options.title, width / 2, 30);
        }
    }

    // 3D Line Chart
    create3DLineChart(containerId, data, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        const canvas = document.createElement('canvas');
        canvas.width = container.offsetWidth || 800;
        canvas.height = container.offsetHeight || 400;
        container.innerHTML = '';
        container.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        const chartId = `line_${Date.now()}`;
        
        this.charts.set(chartId, {
            type: 'line3d',
            canvas: canvas,
            ctx: ctx,
            data: data,
            options: { ...this.getDefaultOptions(), ...options }
        });

        this.draw3DLineChart(chartId);
        this.addChartInteractivity(chartId);

        return {
            update: (newData) => this.updateChart(chartId, newData),
            destroy: () => this.destroyChart(chartId),
            resize: (width, height) => this.resizeChart(chartId, width, height)
        };
    }

    draw3DLineChart(chartId) {
        const chart = this.charts.get(chartId);
        if (!chart) return;

        const { ctx, canvas, data, options } = chart;
        const width = canvas.width;
        const height = canvas.height;
        
        ctx.clearRect(0, 0, width, height);
        
        const padding = 60;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        
        // Find max value for scaling
        const allValues = data.flatMap(dataset => dataset.data);
        const maxValue = Math.max(...allValues);
        
        // Draw 3D grid
        this.draw3DGrid(ctx, padding, chartWidth, chartHeight, maxValue);
        
        // Draw each dataset
        data.forEach((dataset, datasetIndex) => {
            const points = [];
            const depth = datasetIndex * 15;
            
            // Calculate points
            dataset.data.forEach((value, index) => {
                const x = padding + (index / (dataset.data.length - 1)) * chartWidth;
                const y = height - padding - (value / maxValue) * chartHeight;
                points.push({ x, y });
            });
            
            // Draw line shadow
            ctx.strokeStyle = 'rgba(0, 0, 0, 0.2)';
            ctx.lineWidth = 3;
            ctx.beginPath();
            points.forEach((point, index) => {
                const x = point.x + depth * 0.3;
                const y = point.y + depth;
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            ctx.stroke();
            
            // Draw 3D line
            const gradient = ctx.createLinearGradient(0, padding, 0, height - padding);
            gradient.addColorStop(0, dataset.color || this.colors.primary);
            gradient.addColorStop(1, this.adjustColor(dataset.color || this.colors.primary, -30));
            
            ctx.strokeStyle = gradient;
            ctx.lineWidth = 3;
            ctx.beginPath();
            points.forEach((point, index) => {
                const x = point.x + depth * 0.3;
                const y = point.y - depth * 0.5;
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            ctx.stroke();
            
            // Draw data points
            points.forEach((point, index) => {
                const x = point.x + depth * 0.3;
                const y = point.y - depth * 0.5;
                
                // Point shadow
                ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
                ctx.beginPath();
                ctx.arc(x + 2, y + 2, 6, 0, Math.PI * 2);
                ctx.fill();
                
                // Point
                ctx.fillStyle = dataset.color || this.colors.primary;
                ctx.beginPath();
                ctx.arc(x, y, 5, 0, Math.PI * 2);
                ctx.fill();
                
                // Point highlight
                ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
                ctx.beginPath();
                ctx.arc(x - 2, y - 2, 2, 0, Math.PI * 2);
                ctx.fill();
            });
        });
        
        // Draw title
        if (options.title) {
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 18px Inter';
            ctx.textAlign = 'center';
            ctx.fillText(options.title, width / 2, 30);
        }
    }

    // Helper methods
    draw3DGrid(ctx, padding, chartWidth, chartHeight, maxValue) {
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.lineWidth = 1;
        
        // Horizontal grid lines
        for (let i = 0; i <= 5; i++) {
            const y = padding + (i / 5) * chartHeight;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(padding + chartWidth, y);
            ctx.stroke();
            
            // Y-axis labels
            ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
            ctx.font = '11px Inter';
            ctx.textAlign = 'right';
            const value = maxValue - (i / 5) * maxValue;
            ctx.fillText(value.toFixed(0), padding - 10, y + 4);
        }
        
        // Vertical grid lines
        for (let i = 0; i <= 10; i++) {
            const x = padding + (i / 10) * chartWidth;
            ctx.beginPath();
            ctx.moveTo(x, padding);
            ctx.lineTo(x, padding + chartHeight);
            ctx.stroke();
        }
    }

    adjustColor(color, amount) {
        const num = parseInt(color.replace('#', ''), 16);
        const r = Math.max(0, Math.min(255, (num >> 16) + amount));
        const g = Math.max(0, Math.min(255, ((num >> 8) & 0x00FF) + amount));
        const b = Math.max(0, Math.min(255, (num & 0x0000FF) + amount));
        return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
    }

    getDefaultOptions() {
        return {
            title: '',
            showLegend: true,
            showGrid: true,
            animated: true,
            colors: [this.colors.primary, this.colors.secondary, this.colors.accent, this.colors.warning, this.colors.danger]
        };
    }

    addChartInteractivity(chartId) {
        const chart = this.charts.get(chartId);
        if (!chart) return;

        const { canvas } = chart;
        
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Add hover effects based on chart type
            this.handleChartHover(chartId, x, y);
        });
        
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            this.handleChartClick(chartId, x, y);
        });
    }

    handleChartHover(chartId, x, y) {
        // Implementation for hover effects
        const chart = this.charts.get(chartId);
        if (!chart || !chart.options.animated) return;
        
        // Add hover highlighting logic here
    }

    handleChartClick(chartId, x, y) {
        // Implementation for click interactions
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        // Add click interaction logic here
    }

    updateChart(chartId, newData) {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        chart.data = newData;
        
        switch (chart.type) {
            case 'bar3d':
                this.draw3DBarChart(chartId);
                break;
            case 'pie3d':
                this.draw3DPieChart(chartId);
                break;
            case 'line3d':
                this.draw3DLineChart(chartId);
                break;
        }
    }

    resizeChart(chartId, width, height) {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        chart.canvas.width = width;
        chart.canvas.height = height;
        
        // Redraw chart with new dimensions
        this.updateChart(chartId, chart.data);
    }

    destroyChart(chartId) {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        // Clean up event listeners
        chart.canvas.removeEventListener('mousemove', this.handleChartHover);
        chart.canvas.removeEventListener('click', this.handleChartClick);
        
        // Remove from charts map
        this.charts.delete(chartId);
    }

    // Excel Data Integration
    createExcelDashboard(containerId, excelData, options = {}) {
        const dashboard = document.getElementById(containerId);
        if (!dashboard) return null;

        dashboard.innerHTML = '';
        dashboard.className = 'dashboard-3d';
        
        // Create multiple chart types for comprehensive data visualization
        const charts = {};
        
        // Summary statistics
        if (excelData.summary) {
            const summaryContainer = document.createElement('div');
            summaryContainer.className = 'summary-3d';
            summaryContainer.innerHTML = this.createSummaryCards(excelData.summary);
            dashboard.appendChild(summaryContainer);
        }
        
        // Bar chart for categories
        if (excelData.categories) {
            const barContainer = document.createElement('div');
            barContainer.id = `bar_${Date.now()}`;
            barContainer.className = 'chart-container-3d';
            dashboard.appendChild(barContainer);
            
            charts.bar = this.create3DBarChart(barContainer.id, excelData.categories, {
                title: 'Category Analysis'
            });
        }
        
        // Pie chart for distribution
        if (excelData.distribution) {
            const pieContainer = document.createElement('div');
            pieContainer.id = `pie_${Date.now()}`;
            pieContainer.className = 'chart-container-3d';
            dashboard.appendChild(pieContainer);
            
            charts.pie = this.create3DPieChart(pieContainer.id, excelData.distribution, {
                title: 'Data Distribution'
            });
        }
        
        // Line chart for trends
        if (excelData.trends) {
            const lineContainer = document.createElement('div');
            lineContainer.id = `line_${Date.now()}`;
            lineContainer.className = 'chart-container-3d';
            dashboard.appendChild(lineContainer);
            
            charts.line = this.create3DLineChart(lineContainer.id, excelData.trends, {
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

    createSummaryCards(summary) {
        return `
            <div class="summary-grid-3d">
                ${Object.entries(summary).map(([key, value]) => `
                    <div class="summary-card-3d">
                        <div class="summary-value-3d">${value}</div>
                        <div class="summary-label-3d">${key}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }
}

// Initialize 3D Data Visualization
document.addEventListener('DOMContentLoaded', () => {
    window.dataViz3D = new DataVisualization3D();
    
    // Auto-initialize charts with data-chart attributes
    const chartElements = document.querySelectorAll('[data-chart]');
    chartElements.forEach(element => {
        const chartType = element.dataset.chart;
        const chartData = JSON.parse(element.dataset.data || '{}');
        const chartOptions = JSON.parse(element.dataset.options || '{}');
        
        if (window.dataViz3D[`create3D${chartType.charAt(0).toUpperCase() + chartType.slice(1)}Chart`]) {
            window.dataViz3D[`create3D${chartType.charAt(0).toUpperCase() + chartType.slice(1)}Chart`](
                element.id,
                chartData,
                chartOptions
            );
        }
    });
});

// Export for global access
window.DataVisualization3D = DataVisualization3D;