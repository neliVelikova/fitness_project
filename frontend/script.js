let chart;

async function predict() {

    const steps = Number(document.getElementById("steps").value);

    const sleep = Number(document.getElementById("sleep").value);

    const energy = Number(document.getElementById("energy").value);

    const weight = Number(document.getElementById("weight").value);

    const age = Number(document.getElementById("age").value);

    const workout = Number(document.getElementById("workout").value);

    if (
        !steps ||
        !sleep ||
        !energy ||
        workout === ""
    ) {
        alert("Please fill all required fields.");
        return;
    }

    const response = await fetch(
        "http://127.0.0.1:5000/predict",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                steps,
                sleep,
                energy,
                weight,
                age,
                workout
            })
        }
    );

    const data = await response.json();

    document.getElementById("result").innerText =
        data.health_prediction;

    
    document.getElementById("dashboard").style.display = "block";
    // recommendations
    let html = "<h3>Recommendations</h3><ul>";

    data.recommendations.forEach(r => {
        html += `<li>${r}</li>`;
    });

    html += "</ul>";

    document.getElementById(
        "recommendations"
    ).innerHTML = html;

    loadCharts(steps, sleep, workout);

    // =========================
    // HEALTH INSIGHTS
    // =========================

    let insights = "";

    if (sleep < 6) {
        insights += "Your sleep is below recommended levels. ";
    }
    else {
        insights += "Normal sleep patterns. ";
    }

    if (steps > 10000) {
        insights += "Excellent physical activity level. ";
    }
    else if (steps > 5000) {
        insights += "Moderate activity level. ";
    }
    else {
        insights += "Low activity detected. ";
    }

    if (workout == 2) {
        insights += "Intensive workouts improve cardiovascular health.";
    }
    else if (workout == 1) {
        insights += "Moderate workouts support overall fitness.";
    }
    else {
        insights += "Sedentary lifestyle dominant.";
    }

    document.getElementById("insightText").innerText =
        insights;
}

let progressChart;
let scoreChart;
let sleepChart;

function loadCharts(steps, sleep, workout) {

    // destroy old charts
    if (progressChart) progressChart.destroy();
    if (scoreChart) scoreChart.destroy();
    if (sleepChart) sleepChart.destroy();

    // =========================
    // WELLNESS SCORE
    // =========================

    let score = 0;

    if (steps >= 10000) score += 40;
    else if (steps >= 6000) score += 25;
    else score += 10;

    if (sleep >= 8) score += 30;
    else if (sleep >= 6) score += 20;
    else score += 5;

    if (workout == 2) score += 30;
    else if (workout == 1) score += 20;
    else score += 5;

    // =========================
    // GOALS CHART
    // =========================

    progressChart = new Chart(
        document.getElementById("chart1"),
        {
            type: "bar",
            data: {
                labels: ["Steps"],
                datasets: [
                    {
                        label: "Your Steps",
                        data: [steps]
                    },
                    {
                        label: "Recommended",
                        data: [10000]
                    }
                ]
            }
        }
    );

    // =========================
    // SCORE CHART
    // =========================

    scoreChart = new Chart(
        document.getElementById("scoreChart"),
        {
            type: "doughnut",
            data: {
                labels: ["Wellness Score", "Improvement Needed"],
                datasets: [{
                    data: [score, 100 - score]
                }]
            }
        }
    );

    // =========================
    // SLEEP PROGRESS CHART
    // =========================

    sleepChart = new Chart(
        document.getElementById("sleepProgress"),
        {
            type: "bar",
            data: {
                labels: ["Your Sleep", "Recommended Sleep"],
                datasets: [{
                    label: "Hours",
                    data: [sleep, 8]
                }]
            }
        }
    );
}