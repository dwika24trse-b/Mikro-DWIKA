// MoniQuarium Frontend Logic

// Global State
let sensorDataHistory = [];
let aquariumChart = null;
const apiEndpoint = `${window.location.origin}/api/data`;

// DOM Elements
const connectionStatus = document.getElementById('connection-status');
const pulseDot = document.querySelector('.pulse-dot');
const apiPostEndpoint = document.getElementById('api-post-endpoint');
const btnCopyEndpoint = document.getElementById('btn-copy-endpoint');

const valTemp = document.getElementById('val-temp');
const barTemp = document.getElementById('bar-temp');
const statusTemp = document.getElementById('status-temp');

const valPh = document.getElementById('val-ph');
const barPh = document.getElementById('bar-ph');
const statusPh = document.getElementById('status-ph');

const valTurb = document.getElementById('val-turb');
const barTurb = document.getElementById('bar-turb');
const statusTurb = document.getElementById('status-turb');

const valLevel = document.getElementById('val-level');
const barLevel = document.getElementById('bar-level');
const statusLevel = document.getElementById('status-level');

const chartSensorSelector = document.getElementById('chart-sensor-selector');
const btnDownloadPng = document.getElementById('btn-download-png');
const btnDownloadCsv = document.getElementById('btn-download-csv');
const limitSelector = document.getElementById('limit-selector');
const tableBody = document.getElementById('table-body');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Show current local server API url
    apiPostEndpoint.textContent = apiEndpoint;
    
    // Copy endpoint helper
    btnCopyEndpoint.addEventListener('click', copyEndpointToClipboard);
    
    // Setup UI event listeners
    limitSelector.addEventListener('change', fetchSensorData);
    chartSensorSelector.addEventListener('change', updateChartDisplay);
    btnDownloadCsv.addEventListener('click', downloadCSV);
    btnDownloadPng.addEventListener('click', downloadPNG);
    
    // Initial fetch and start periodic polling (every 5 seconds)
    fetchSensorData();
    setInterval(fetchSensorData, 5000);
});

// Clipboard helper
function copyEndpointToClipboard() {
    navigator.clipboard.writeText(apiEndpoint).then(() => {
        const originalHTML = btnCopyEndpoint.innerHTML;
        btnCopyEndpoint.innerHTML = '<i class="fa-solid fa-check" style="color: var(--color-success)"></i>';
        setTimeout(() => {
            btnCopyEndpoint.innerHTML = originalHTML;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}

// Fetch data from backend API
async function fetchSensorData() {
    const limit = limitSelector.value;
    try {
        const response = await fetch(`${apiEndpoint}?limit=${limit}`);
        if (!response.ok) throw new Error('Respon server tidak sukses');
        
        const result = await response.json();
        
        if (result.status === 'success') {
            sensorDataHistory = result.data;
            updateConnectionStatus(true, `Terkoneksi (${result.db_type.toUpperCase()})`);
            
            if (sensorDataHistory.length > 0) {
                // Update the real-time card indicators with the newest record
                const latestData = sensorDataHistory[sensorDataHistory.length - 1];
                updateRealtimeCards(latestData);
                
                // Refresh Table & Charts
                populateTable(sensorDataHistory);
                renderOrUpdateChart();
            } else {
                showEmptyState();
            }
        }
    } catch (error) {
        console.error('Fetch error:', error);
        updateConnectionStatus(false, 'Gagal terhubung dengan server');
    }
}

// Update Server Connection Status Indicator
function updateConnectionStatus(isOnline, message) {
    connectionStatus.textContent = message;
    if (isOnline) {
        pulseDot.className = 'pulse-dot online';
    } else {
        pulseDot.className = 'pulse-dot offline';
    }
}

// Update Real-time parameters Cards (gauges & colors)
function updateRealtimeCards(data) {
    // 1. Temperature Control (Target: 22 - 28 °C)
    const temp = parseFloat(data.temperature).toFixed(1);
    valTemp.textContent = temp;
    barTemp.style.width = `${Math.min(Math.max((temp / 50) * 100, 0), 100)}%`; // scale 0-50°C
    
    if (temp >= 22 && temp <= 28) {
        setStatusBadge(statusTemp, 'Optimal', 'optimal');
    } else if ((temp >= 20 && temp < 22) || (temp > 28 && temp <= 30)) {
        setStatusBadge(statusTemp, 'Warning', 'warning');
    } else {
        setStatusBadge(statusTemp, 'Bahaya', 'danger');
    }
    
    // 2. pH Control (Target: 6.5 - 8.5)
    const ph = parseFloat(data.ph).toFixed(1);
    valPh.textContent = ph;
    barPh.style.width = `${Math.min(Math.max((ph / 14) * 100, 0), 100)}%`; // scale 0-14 pH
    
    if (ph >= 6.5 && ph <= 8.5) {
        setStatusBadge(statusPh, 'Optimal', 'optimal');
    } else if ((ph >= 6.0 && ph < 6.5) || (ph > 8.5 && ph <= 9.0)) {
        setStatusBadge(statusPh, 'Warning', 'warning');
    } else {
        setStatusBadge(statusPh, 'Bahaya', 'danger');
    }
    
    // 3. Turbidity / Kejernihan Air (Target: > 80%)
    const turb = parseFloat(data.turbidity).toFixed(1);
    valTurb.textContent = turb;
    barTurb.style.width = `${Math.min(Math.max(turb, 0), 100)}%`; // scale 0-100%
    
    if (turb >= 80) {
        setStatusBadge(statusTurb, 'Jernih', 'optimal');
    } else if (turb >= 60 && turb < 80) {
        setStatusBadge(statusTurb, 'Keruh Ringan', 'warning');
    } else {
        setStatusBadge(statusTurb, 'Keruh / Kotor', 'danger');
    }
    
    // 4. Water Level / Level Ketinggian Air (Target: 70% - 95%)
    const level = parseFloat(data.water_level).toFixed(1);
    valLevel.textContent = level;
    barLevel.style.width = `${Math.min(Math.max(level, 0), 100)}%`; // scale 0-100%
    
    if (level >= 70 && level <= 95) {
        setStatusBadge(statusLevel, 'Optimal', 'optimal');
    } else if ((level >= 50 && level < 70) || (level > 95)) {
        setStatusBadge(statusLevel, 'Warning', 'warning');
    } else {
        setStatusBadge(statusLevel, 'Bahaya', 'danger');
    }
}

// Utility to change status badges on cards
function setStatusBadge(element, text, statusClass) {
    element.textContent = text;
    element.className = `status-badge ${statusClass}`;
}

// Populate the log table
function populateTable(dataList) {
    // We want to show table in reverse chronological order (newest first)
    const reversedData = [...dataList].reverse();
    
    tableBody.innerHTML = '';
    
    reversedData.forEach((row, index) => {
        const tr = document.createElement('tr');
        
        // Format Time
        const dateStr = formatDateTime(row.created_at);
        
        // System status evaluation for table
        let systemStatusHtml = '<span class="status-badge optimal">Normal</span>';
        const isTempAlert = row.temperature < 20 || row.temperature > 30;
        const isPhAlert = row.ph < 6.0 || row.ph > 9.0;
        const isTurbAlert = row.turbidity < 60;
        const isLevelAlert = row.water_level < 50;
        
        if (isTempAlert || isPhAlert || isTurbAlert || isLevelAlert) {
            systemStatusHtml = '<span class="status-badge danger">Bahaya</span>';
        } else if (row.temperature < 22 || row.temperature > 28 || row.ph < 6.5 || row.ph > 8.5 || row.turbidity < 80 || row.water_level < 70) {
            systemStatusHtml = '<span class="status-badge warning">Perlu Cek</span>';
        }
        
        tr.innerHTML = `
            <td>${index + 1}</td>
            <td class="time-cell">${dateStr}</td>
            <td class="bold-val" style="color: var(--color-temp)">${parseFloat(row.temperature).toFixed(1)} °C</td>
            <td class="bold-val" style="color: var(--color-ph)">${parseFloat(row.ph).toFixed(1)} pH</td>
            <td class="bold-val" style="color: var(--color-turb)">${parseFloat(row.turbidity).toFixed(1)} %</td>
            <td class="bold-val" style="color: var(--color-level)">${parseFloat(row.water_level).toFixed(1)} %</td>
            <td>${systemStatusHtml}</td>
        `;
        
        tableBody.appendChild(tr);
    });
}

function showEmptyState() {
    tableBody.innerHTML = `
        <tr>
            <td colspan="7" class="loading-cell">
                <i class="fa-solid fa-circle-info" style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block; color: var(--color-warning)"></i>
                Database kosong. Silakan kirim data dari Arduino, ESP32 atau gunakan Simulator!
            </td>
        </tr>
    `;
}

// Format raw ISO/MySQL Timestamp to human-readable date and time
function formatDateTime(rawString) {
    try {
        const date = new Date(rawString);
        return date.toLocaleString('id-ID', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    } catch (e) {
        return rawString;
    }
}

// Chart.js implementation
function renderOrUpdateChart() {
    const ctx = document.getElementById('aquariumChart').getContext('2d');
    
    // Prepare chart labels (Timestamps)
    const labels = sensorDataHistory.map(row => {
        const date = new Date(row.created_at);
        return date.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    });
    
    // Prepare datasets
    const datasets = [
        {
            label: 'Suhu (°C)',
            data: sensorDataHistory.map(row => row.temperature),
            borderColor: '#ff5e62',
            backgroundColor: 'rgba(255, 94, 98, 0.05)',
            borderWidth: 3,
            tension: 0.4,
            fill: true,
            yAxisID: 'y'
        },
        {
            label: 'pH Air',
            data: sensorDataHistory.map(row => row.ph),
            borderColor: '#a855f7',
            backgroundColor: 'rgba(168, 85, 247, 0.05)',
            borderWidth: 3,
            tension: 0.4,
            fill: true,
            yAxisID: 'y'
        },
        {
            label: 'Kejernihan (%)',
            data: sensorDataHistory.map(row => row.turbidity),
            borderColor: '#06b6d4',
            backgroundColor: 'rgba(6, 182, 212, 0.05)',
            borderWidth: 3,
            tension: 0.4,
            fill: true,
            yAxisID: 'y'
        },
        {
            label: 'Level Air (%)',
            data: sensorDataHistory.map(row => row.water_level),
            borderColor: '#0088ff',
            backgroundColor: 'rgba(0, 136, 255, 0.05)',
            borderWidth: 3,
            tension: 0.4,
            fill: true,
            yAxisID: 'y'
        }
    ];

    if (aquariumChart) {
        // Update existing chart data
        aquariumChart.data.labels = labels;
        aquariumChart.data.datasets.forEach((dataset, index) => {
            dataset.data = datasets[index].data;
        });
        aquariumChart.update('none'); // Update without full animation for smoother polling
        updateChartDisplay(); // Apply current visibility filter
    } else {
        // Create new Chart
        aquariumChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#94a3b8',
                            font: { family: 'Outfit', size: 12, weight: '500' }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(10, 20, 44, 0.95)',
                        titleFont: { family: 'Outfit', size: 12, weight: 'bold' },
                        bodyFont: { family: 'Outfit', size: 12 },
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 10
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.03)' },
                        ticks: { color: '#94a3b8', font: { family: 'Outfit' } }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: { color: 'rgba(255, 255, 255, 0.03)' },
                        ticks: { color: '#94a3b8', font: { family: 'Outfit' } },
                        min: 0,
                        max: 100
                    }
                }
            }
        });
    }
}

// Toggle visibility of chart series based on dropdown select
function updateChartDisplay() {
    if (!aquariumChart) return;
    
    const selectedValue = chartSensorSelector.value;
    
    // Map dropdown options to dataset index
    // 0: Suhu, 1: pH, 2: Kejernihan, 3: Level Air
    aquariumChart.data.datasets.forEach((dataset, index) => {
        if (selectedValue === 'all') {
            dataset.hidden = false;
        } else if (selectedValue === 'temperature' && index === 0) {
            dataset.hidden = false;
        } else if (selectedValue === 'ph' && index === 1) {
            dataset.hidden = false;
        } else if (selectedValue === 'turbidity' && index === 2) {
            dataset.hidden = false;
        } else if (selectedValue === 'water_level' && index === 3) {
            dataset.hidden = false;
        } else {
            dataset.hidden = true;
        }
    });
    
    // Dynamically adjust scale limit for single-view ph to show more detail
    if (selectedValue === 'ph') {
        aquariumChart.options.scales.y.min = 0;
        aquariumChart.options.scales.y.max = 14;
    } else if (selectedValue === 'temperature') {
        aquariumChart.options.scales.y.min = 0;
        aquariumChart.options.scales.y.max = 50;
    } else {
        aquariumChart.options.scales.y.min = 0;
        aquariumChart.options.scales.y.max = 100;
    }
    
    aquariumChart.update();
}

// Download table data as CSV file
function downloadCSV() {
    if (sensorDataHistory.length === 0) {
        alert('Tidak ada data sensor untuk diunduh.');
        return;
    }
    
    // Header
    let csvContent = "No,Waktu Pengambilan,Suhu (C),pH Air,Kejernihan Air (%),Ketinggian Air (%)\r\n";
    
    // Body Rows
    sensorDataHistory.forEach((row, index) => {
        const timeStr = formatDateTime(row.created_at).replace(/,/g, ''); // avoid commas in time
        csvContent += `${index + 1},${timeStr},${row.temperature},${row.ph},${row.turbidity},${row.water_level}\r\n`;
    });
    
    // Create download blob
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const timestampStr = new Date().toISOString().slice(0, 19).replace(/:/g, "-");
    
    link.setAttribute("href", url);
    link.setAttribute("download", `sensor_data_aquarium_${timestampStr}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Download chart as PNG image
function downloadPNG() {
    if (!aquariumChart) {
        alert('Grafik belum siap.');
        return;
    }
    
    // Render the chart to a temporary image
    const imageURI = aquariumChart.toBase64Image();
    const link = document.createElement('a');
    const timestampStr = new Date().toISOString().slice(0, 19).replace(/:/g, "-");
    
    link.setAttribute('href', imageURI);
    link.setAttribute('download', `aquarium_chart_${timestampStr}.png`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
