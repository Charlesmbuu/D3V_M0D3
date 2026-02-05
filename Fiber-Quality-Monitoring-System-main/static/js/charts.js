// Real-time Charts using Chart.js
document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    let powerChart, latencyChart;

    // Initialize charts
    function initCharts(initialData) {
        const powerCtx = document.getElementById('powerChart').getContext('2d');
        const latencyCtx = document.getElementById('latencyChart').getContext('2d');

        // Power Level Chart (Line)
        powerChart = new Chart(powerCtx, {
            type: 'line',
            data: {
                labels: Object.keys(initialData),
                datasets: [{
                    label: 'Power Level (dBm)',
                    data: Object.values(initialData).map(n => n.power),
                    borderColor: '#2196F3',
                    tension: 0.4,
                    fill: false
                }]
            },
            options: chartOptions('dBm')
        });

        // Latency Chart (Bar)
        latencyChart = new Chart(latencyCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(initialData),
                datasets: [{
                    label: 'Latency (ms)',
                    data: Object.values(initialData).map(n => n.latency),
                    backgroundColor: '#4CAF50',
                    borderColor: '#388E3C',
                    borderWidth: 1
                }]
            },
            options: chartOptions('ms')
        });
    }

    // Common chart options
    function chartOptions(unit) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    title: {
                        display: true,
                        text: unit
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        };
    }

    // Handle real-time updates
    socket.on('network_update', function(data) {
        updateChartData(powerChart, data, 'power');
        updateChartData(latencyChart, data, 'latency');
    });

    // Update chart datasets
    function updateChartData(chart, newData, metric) {
        chart.data.labels = Object.keys(newData);
        chart.data.datasets.forEach(dataset => {
            dataset.data = Object.values(newData).map(node => node[metric]);
        });
        chart.update();
    }

    // Initial chart setup
    socket.on('initial_data', function(initialData) {
        if (!powerChart && !latencyChart) {
            initCharts(initialData);
        }
    });
});