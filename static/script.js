// static/script.js

document.addEventListener('DOMContentLoaded', function() {
    // This message will appear in the browser's developer console.
    // It helps us confirm the script is running.
    console.log("Script loaded and DOM is ready!"); 

    // CHANGE: Load medicines data on initial page load
    loadMedicinesData();
});

// --- Tab Switching ---
function showTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));

    // Remove active class from all buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => button.classList.remove('active'));

    // Show the selected tab content and mark button as active
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');

    // Load data for the specific tab
    if (tabName === 'medicines') {
        loadMedicinesData();
    } else if (tabName === 'alerts') {
        loadAlertsData();
    } else if (tabName === 'batches') {
        loadBatchesData();
    } else if (tabName === 'dashboard') {
        loadDashboardData();
    }
}

// --- Data Fetching and Rendering Functions ---

async function fetchData(endpoint) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Could not fetch data:", error);
        return null;
    }
}

function loadDashboardData() {
    fetchData('/api/dashboard').then(data => {
        if (data) {
            document.getElementById('total-medicines').innerText = data.total_medicines;
            document.getElementById('low-stock-alerts').innerText = data.low_stock_alerts;
            document.getElementById('expiry-alerts').innerText = data.expiry_alerts;
            document.getElementById('critical-expiry-alerts').innerText = data.critical_expiry_alerts;

            const labels = data.top_medicines.map(m => m.name);
            const chartData = data.top_medicines.map(m => m.quantity_sold);
            renderTopMedicinesChart(labels, chartData);
        }
    });
}

function loadMedicinesData() {
    fetchData('/api/medicines').then(data => {
        const tableBody = document.getElementById('medicines-table-body');
        tableBody.innerHTML = ''; // Clear existing rows
        if (data) {
            data.forEach(med => {
                const row = `<tr>
                    <td>${med.medicine_id}</td>
                    <td>${med.name}</td>
                    <td>${med.category}</td>
                    <td>${med.priority_tag}</td>
                    <td>${med.current_stock}</td>
                    <td>${med.safety_stock}</td>
                </tr>`;
                tableBody.innerHTML += row;
            });
        }
    });
}

function loadAlertsData() {
    fetchData('/api/alerts').then(data => {
        const tableBody = document.getElementById('alerts-table-body');
        tableBody.innerHTML = ''; // Clear existing rows
        if (data) {
            data.forEach(alert => {
                const severityClass = alert.severity === 'critical' ? 'critical' : '';
                const row = `<tr class="${severityClass}">
                    <td>${alert.alert_id}</td>
                    <td>${alert.type}</td>
                    <td>${alert.medicine_id}</td>
                    <td>${alert.message}</td>
                    <td>${alert.severity}</td>
                </tr>`;
                tableBody.innerHTML += row;
            });
        }
    });
}

function loadBatchesData() {
    fetchData('/api/batches').then(data => {
        const tableBody = document.getElementById('batches-table-body');
        tableBody.innerHTML = ''; // Clear existing rows
        if (data) {
            data.forEach(batch => {
                const row = `<tr>
                    <td>${batch.batch_code}</td>
                    <td>${batch.medicine_id}</td>
                    <td>${batch.quantity}</td>
                    <td>${batch.expiry_date}</td>
                    <td>${batch.status}</td>
                </tr>`;
                tableBody.innerHTML += row;
            });
        }
    });
}

// --- Chart Rendering ---
let myChart; // Global variable to hold the chart instance

function renderTopMedicinesChart(labels, data) {
    const ctx = document.getElementById('topMedicinesChart').getContext('2d');
    
    if (myChart) {
        myChart.destroy();
    }

    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Quantity Sold',
                data: data,
                backgroundColor: 'rgba(10, 147, 150, 0.6)',
                borderColor: 'rgba(10, 147, 150, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}