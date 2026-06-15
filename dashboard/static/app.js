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

// Generate AI insight on demand
async function generateInsight() {
    try {
        await fetch("/api/generate-insight", {
            method: "POST"
        });
    } catch (error) {
        console.error("Generate insight failed:", error);
    }
}

//
// Functions to update dashboard data and charts
//
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

    document.getElementById("capacity-text").textContent =
        `${data.capacity}%`;

    document.getElementById("capacity-bar").style.height =
        `${data.capacity}%`;

    document.getElementById("bin-status").textContent =
        data.status;

    document.getElementById("ai-insight").textContent =
        data.insight;

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

    document.getElementById("capacity-text").textContent =
        "--%";

    document.getElementById("capacity-bar").style.height =
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
    
    updateWastePieChart({});
}

createCharts();
fetchDashboardData();
setInterval(fetchDashboardData, 5000); // 5 sec interval

document
    .getElementById("generate-insight-btn")
    .addEventListener("click", generateInsight);