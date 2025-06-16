let soilChart, tempChart, humChart, phChart;

async function fetchChartData() {
  try {
    const res = await fetch('/api/chart-data');
    const data = await res.json();
    updateCharts(data.labels, data);
  } catch (err) {
    console.error('Fetch chart-data failed:', err);
  }
}

function createLineChart(ctx, label, values, color, labels) {
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: label,
        data: values,
        borderColor: color,
        backgroundColor: color,
        fill: false,
        tension: 0.25,
        pointRadius: 2,
        borderWidth: 1.5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          ticks: { font: { size: 9 }, maxRotation: 45 }
        },
        y: {
          beginAtZero: false,
          ticks: { font: { size: 9 } }
        }
      }
    }
  });
}

function updateCharts(labels, data) {
  if (soilChart) soilChart.destroy();
  if (tempChart) tempChart.destroy();
  if (humChart) humChart.destroy();
  if (phChart) phChart.destroy();

  soilChart = createLineChart(
    document.getElementById('soilChart').getContext('2d'),
    'Soil Moisture',
    data.soil,
    '#2a9d8f',
    labels
  );

  tempChart = createLineChart(
    document.getElementById('tempChart').getContext('2d'),
    'Temperature (°C)',
    data.temperature,
    '#e76f51',
    labels
  );

  humChart = createLineChart(
    document.getElementById('humChart').getContext('2d'),
    'Humidity (%)',
    data.humidity,
    '#264653',
    labels
  );

  phChart = createLineChart(
    document.getElementById('phChart').getContext('2d'),
    'pH Level',
    data.ph,
    '#f4a261',
    labels
  );
}

// Update grafik setiap 2 detik
setInterval(fetchChartData, 2000);
fetchChartData();
