let lastRelayStatus = null;

async function fetchSensorStatus() {
  const res = await fetch('/api/status');
  const data = await res.json();

  document.getElementById('soilValue').textContent =
    data.soil_percent !== undefined && data.soil_percent !== null
      ? data.soil_percent + '%'
      : '--';

  document.getElementById('soilLabel').textContent =
    data.soil_label ?? '--';

  document.getElementById('phValue').textContent =
    data.soil_temp !== undefined && data.soil_temp !== null
      ? parseFloat(data.soil_temp).toFixed(2)
      : '--';

  document.getElementById('phLabel').textContent =
    data.ph_label ?? '--';

  document.getElementById('humidityValue').textContent = data.env_hum + '%';
  document.getElementById('temperatureValue').textContent = data.env_temp + '°C';
  document.getElementById('relayStatus').textContent = data.relay_status;
  document.getElementById('modeStatus').textContent = data.mode;

  if (lastRelayStatus !== null && lastRelayStatus !== data.relay_status) {
    if (data.relay_status === "ON") {
      alert("💧 Penyiraman dimulai (Relay ON)");
    } else {
      alert("✅ Penyiraman selesai (Relay OFF)");
    }
  }
  lastRelayStatus = data.relay_status;
}

document.getElementById('manualRelayBtn').addEventListener('click', async () => {
  try {
    await fetch('/api/relay-toggle', { method: 'POST' });
    fetchSensorStatus(); // ⬅ refresh
  } catch (error) {
    console.error('Gagal toggle relay:', error);
  }
});

document.getElementById('autoRelayBtn').addEventListener('click', async () => {
  try {
    await fetch('/api/auto-mode-toggle', { method: 'POST' });
    fetchSensorStatus(); // ⬅ refresh
  } catch (error) {
    console.error('Gagal toggle mode:', error);
  }
});


window.onload = () => {
  fetchSensorStatus();
  setInterval(fetchSensorStatus, 5000);
};
