// ==================================================
// Gachon University
// Introduction to Internet of Things (13966_001)
// 2026-1 Semester
//
// Term Project Dashboard JS
// Team C
// ==================================================

let recentChart;
let wastePieChart;

// Build charts using chart.js
function createCharts() {
    // Recent detection count chart
    recentChart = new Chart(document.getElementById("recentChart"), {
        type: "bar",
        data: {
            labels: [],
            datasets: [{
                label: "Detection Count",
                data: [],
                //Bar color
                backgroundColor: "rgba(46, 159, 110, 0.85)",
                borderColor: "rgba(46, 159, 110, 1)",
                borderWidth: 1,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // Waste type ratio chart
    wastePieChart = new Chart(document.getElementById("wastePieChart"), {
        type: "pie",
        data: {
            labels: [],
            datasets: [{
                data: [],
                // Pie chart colors
                backgroundColor: [
                    "#60a5fa",
                    "#34d399",
                    "#fbbf24",
                    "#a78bfa",
                    "#fb7185",
                    "#22d3ee",
                    "#84cc16",
                    "#f97316",
                    "#ec4899",
                    "#14b8a6"
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Fetch dashboard data from Python backend
async function fetchDashboardData() {
    try {
        const response = await fetch("/api/status");
        const result = await response.json();

        if (!result.success) {
            setOffline();
            return;
        }
        updateDashboard(result.data);

    } catch (error) {
        console.error("Fetch failed:", error);
        setOffline();
    }
}

//
// Functions to update dashboard data and charts
//
function updateRecentChart(recentCounts) {
    const entries = Object.entries(recentCounts);

    const labels = entries.map(entry => entry[0]);
    const values = entries.map(entry => entry[1]);

    recentChart.data.labels = labels;
    recentChart.data.datasets[0].data = values;
    recentChart.update();
}

function updateWastePieChart(wasteTypes) {
    const labels = Object.keys(wasteTypes);
    const values = Object.values(wasteTypes);

    wastePieChart.data.labels = labels;
    wastePieChart.data.datasets[0].data = values;
    wastePieChart.update();
}

// Update dashboard UI with latest data
function updateDashboard(data) {
    document.getElementById("temperature").textContent =
        `${data.temperature} °C`;

    document.getElementById("humidity").textContent =
        `${data.humidity} %`;

    document.getElementById("total-count").textContent =
        data.total_count;

    document.getElementById("bin-capacity").textContent =
        `${data.capacity} %`;

    document.getElementById("capacity-text").textContent =
        `${data.capacity}%`;

    document.getElementById("capacity-bar").style.width =
        `${data.capacity}%`;

    document.getElementById("bin-status").textContent =
        data.status;

    document.getElementById("ai-insight").textContent =
        data.insight;

    updateRecentChart(data.recent_counts);
    updateWastePieChart(data.waste_types);

    const badge =
        document.getElementById("status-badge");
    badge.textContent = "ONLINE";
    badge.classList.remove("offline");
    badge.classList.add("online");
}

// If App is offline
function setOffline() {

    document.getElementById("temperature").textContent =
        "-- °C";

    document.getElementById("humidity").textContent =
        "-- %";

    document.getElementById("total-count").textContent =
        "--";

    document.getElementById("bin-capacity").textContent =
        "-- %";

    document.getElementById("capacity-text").textContent =
        "--%";

    document.getElementById("capacity-bar").style.width =
        "0%";

    document.getElementById("bin-status").textContent =
        "Offline";

    document.getElementById("ai-insight").textContent =
        "No connection";

    const badge =
        document.getElementById("status-badge");

    badge.textContent = "OFFLINE";

    badge.classList.remove("online");
    badge.classList.add("offline");

    updateRecentChart({});
    updateWastePieChart({});
}

createCharts();
fetchDashboardData();
setInterval(fetchDashboardData, 5000); // 5 sec interval