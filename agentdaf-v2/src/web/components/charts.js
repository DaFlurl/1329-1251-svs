/**
 * Charts - Handles analytics and data visualization
 */
class Charts {
  constructor() {
    this.charts = new Map();
    this.chartColors = this.getChartColors();
    this.defaultOptions = this.getDefaultOptions();
    
    this.init();
  }

  init() {
    // Listen for data updates
    document.addEventListener('dataLoaded', (e) => {
      this.handleDataUpdate(e.detail);
    });

    // Listen for theme changes
    document.addEventListener('themechange', () => {
      this.updateChartsTheme();
    });

    // Listen for tab switches
    document.addEventListener('DOMContentLoaded', () => {
      this.setupTabListener();
    });
  }

  setupTabListener() {
    document.querySelectorAll('.nav-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        if (e.currentTarget.dataset.tab === 'analytics') {
          setTimeout(() => {
            this.updateAllCharts();
          }, 100);
        }
      });
    });
  }

  handleDataUpdate(dataDetail) {
    const { data } = dataDetail;
    this.updateAllCharts(data);
  }

  updateAllCharts(data = null) {
    if (!data && window.dataLoader) {
      data = window.dataLoader.getCurrentData();
    }
    
    if (!data) return;

    this.updateScoreDistributionChart(data);
    this.updateAllianceDistributionChart(data);
    this.updatePerformanceChart(data);
  }

  updateScoreDistributionChart(data) {
    const canvas = document.getElementById('scoreDistributionChart');
    if (!canvas) return;

    const players = data.combined || [];
    const scores = players.map(p => p.score).filter(s => s > 0);
    
    if (scores.length === 0) return;

    // Create score ranges
    const ranges = this.createScoreRanges(scores);
    
    const chartData = {
      labels: ranges.labels,
      datasets: [{
        label: 'Spieleranzahl',
        data: ranges.counts,
        backgroundColor: this.chartColors.primary,
        borderColor: this.chartColors.primaryBorder,
        borderWidth: 2,
        borderRadius: 8,
        hoverBackgroundColor: this.chartColors.primaryHover
      }]
    };

    const options = {
      ...this.defaultOptions,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Anzahl Spieler'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Punktbereich'
          }
        }
      },
      plugins: {
        ...this.defaultOptions.plugins,
        title: {
          display: true,
          text: 'Verteilung der Spielerpunkte'
        }
      }
    };

    this.createOrUpdateChart('scoreDistribution', canvas, 'bar', chartData, options);
  }

  updateAllianceDistributionChart(data) {
    const canvas = document.getElementById('allianceDistributionChart');
    if (!canvas) return;

    const alliances = this.getAllianceStats(data);
    
    if (alliances.length === 0) return;

    const chartData = {
      labels: alliances.map(a => a.name),
      datasets: [{
        label: 'Gesamtpunkte',
        data: alliances.map(a => a.totalScore),
        backgroundColor: this.chartColors.multi.slice(0, alliances.length),
        borderColor: this.chartColors.multiBorder.slice(0, alliances.length),
        borderWidth: 2,
        hoverOffset: 4
      }]
    };

    const options = {
      ...this.defaultOptions,
      plugins: {
        ...this.defaultOptions.plugins,
        title: {
          display: true,
          text: 'Allianz-Punkteverteilung'
        },
        legend: {
          display: false
        }
      }
    };

    this.createOrUpdateChart('allianceDistribution', canvas, 'doughnut', chartData, options);
  }

  updatePerformanceChart(data) {
    const canvas = document.getElementById('performanceChart');
    if (!canvas) return;

    const players = data.combined || [];
    const topPlayers = players.slice(0, 20);
    
    if (topPlayers.length === 0) return;

    const chartData = {
      labels: topPlayers.map(p => p.name),
      datasets: [{
        label: 'Punkte',
        data: topPlayers.map(p => p.score),
        backgroundColor: this.chartColors.primary,
        borderColor: this.chartColors.primaryBorder,
        borderWidth: 2,
        borderRadius: 6,
        tension: 0.4
      }]
    };

    const options = {
      ...this.defaultOptions,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Punkte'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Spieler'
          },
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        }
      },
      plugins: {
        ...this.defaultOptions.plugins,
        title: {
          display: true,
          text: 'Top 20 Spieler Performance'
        }
      }
    };

    this.createOrUpdateChart('performance', canvas, 'line', chartData, options);
  }

  createScoreRanges(scores) {
    const max = Math.max(...scores);
    const min = Math.min(...scores);
    const range = max - min;
    const binCount = Math.min(10, Math.ceil(Math.sqrt(scores.length)));
    const binSize = Math.ceil(range / binCount);
    
    const bins = Array(binCount).fill(0);
    const labels = [];
    
    for (let i = 0; i < binCount; i++) {
      const start = min + (i * binSize);
      const end = Math.min(start + binSize, max);
      labels.push(`${this.formatNumber(start)}-${this.formatNumber(end)}`);
    }
    
    scores.forEach(score => {
      const binIndex = Math.min(Math.floor((score - min) / binSize), binCount - 1);
      bins[binIndex]++;
    });
    
    return { labels, counts: bins };
  }

  getAllianceStats(data) {
    const players = data.combined || [];
    const allianceMap = new Map();
    
    players.forEach(player => {
      if (player.alliance && player.alliance !== 'None') {
        if (!allianceMap.has(player.alliance)) {
          allianceMap.set(player.alliance, {
            name: player.alliance,
            totalScore: 0,
            playerCount: 0
          });
        }
        const alliance = allianceMap.get(player.alliance);
        alliance.totalScore += player.score;
        alliance.playerCount++;
      }
    });
    
    return Array.from(allianceMap.values())
      .sort((a, b) => b.totalScore - a.totalScore)
      .slice(0, 10);
  }

  createOrUpdateChart(chartId, canvas, type, data, options) {
    if (this.charts.has(chartId)) {
      const chart = this.charts.get(chartId);
      chart.data = data;
      chart.options = options;
      chart.update();
    } else {
      const ctx = canvas.getContext('2d');
      const chart = new Chart(ctx, {
        type,
        data,
        options
      });
      this.charts.set(chartId, chart);
    }
  }

  updateChartsTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#ffffff' : '#2c3e50';
    const gridColor = isDark ? '#3a3a52' : '#e9ecef';
    
    this.charts.forEach(chart => {
      chart.options.plugins.legend.labels.color = textColor;
      chart.options.plugins.title.color = textColor;
      
      if (chart.options.scales) {
        Object.values(chart.options.scales).forEach(scale => {
          scale.ticks.color = textColor;
          scale.grid.color = gridColor;
          if (scale.title) {
            scale.title.color = textColor;
          }
        });
      }
      
      chart.update();
    });
  }

  getChartColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    
    return {
      primary: isDark ? 'rgba(0, 255, 136, 0.6)' : 'rgba(102, 126, 234, 0.6)',
      primaryBorder: isDark ? '#00FF88' : '#667eea',
      primaryHover: isDark ? 'rgba(0, 255, 136, 0.8)' : 'rgba(102, 126, 234, 0.8)',
      multi: [
        'rgba(102, 126, 234, 0.6)',
        'rgba(118, 75, 162, 0.6)',
        'rgba(0, 212, 255, 0.6)',
        'rgba(40, 167, 69, 0.6)',
        'rgba(255, 193, 7, 0.6)',
        'rgba(220, 53, 69, 0.6)',
        'rgba(23, 162, 184, 0.6)',
        'rgba(153, 69, 255, 0.6)',
        'rgba(255, 51, 85, 0.6)',
        'rgba(0, 255, 136, 0.6)'
      ],
      multiBorder: [
        '#667eea',
        '#764ba2',
        '#00d4ff',
        '#28a745',
        '#ffc107',
        '#dc3545',
        '#17a2b8',
        '#9945ff',
        '#FF3355',
        '#00FF88'
      ]
    };
  }

  getDefaultOptions() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#ffffff' : '#2c3e50';
    
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: textColor,
            font: {
              family: 'Inter, sans-serif'
            }
          }
        },
        tooltip: {
          backgroundColor: isDark ? '#252538' : '#ffffff',
          titleColor: textColor,
          bodyColor: textColor,
          borderColor: isDark ? '#3a3a52' : '#e9ecef',
          borderWidth: 1,
          cornerRadius: 8,
          displayColors: true,
          callbacks: {
            label: (context) => {
              let label = context.dataset.label || '';
              if (label) {
                label += ': ';
              }
              label += this.formatNumber(context.parsed.y || context.parsed);
              return label;
            }
          }
        }
      },
      animation: {
        duration: 750,
        easing: 'easeInOutQuart'
      }
    };
  }

  formatNumber(num) {
    return num.toLocaleString('de-DE');
  }

  // Public API methods
  exportChart(chartId, filename = null) {
    const chart = this.charts.get(chartId);
    if (!chart) return;

    const url = chart.toBase64Image();
    const link = document.createElement('a');
    link.download = filename || `chart-${chartId}-${new Date().toISOString().split('T')[0]}.png`;
    link.href = url;
    link.click();
  }

  resizeAllCharts() {
    this.charts.forEach(chart => {
      chart.resize();
    });
  }

  destroyChart(chartId) {
    const chart = this.charts.get(chartId);
    if (chart) {
      chart.destroy();
      this.charts.delete(chartId);
    }
  }

  destroyAllCharts() {
    this.charts.forEach(chart => {
      chart.destroy();
    });
    this.charts.clear();
  }

  // Advanced analytics methods
  createTrendChart(dataPoints, canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !dataPoints.length) return;

    const chartData = {
      labels: dataPoints.map((_, index) => `Zeitpunkt ${index + 1}`),
      datasets: [{
        label: 'Durchschnittliche Punkte',
        data: dataPoints,
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        borderColor: '#667eea',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }]
    };

    const options = {
      ...this.defaultOptions,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Punkte'
          }
        }
      }
    };

    this.createOrUpdateChart('trend', canvas, 'line', chartData, options);
  }

  createComparisonChart(datasets, canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !datasets.length) return;

    const chartData = {
      labels: datasets[0].data.map((_, index) => `Eintrag ${index + 1}`),
      datasets: datasets.map((dataset, index) => ({
        label: dataset.label,
        data: dataset.data,
        backgroundColor: this.chartColors.multi[index % this.chartColors.multi.length],
        borderColor: this.chartColors.multiBorder[index % this.chartColors.multiBorder.length],
        borderWidth: 2
      }))
    };

    const options = {
      ...this.defaultOptions,
      scales: {
        y: {
          beginAtZero: true
        }
      }
    };

    this.createOrUpdateChart('comparison', canvas, 'bar', chartData, options);
  }
}

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.charts = new Charts();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Charts;
}