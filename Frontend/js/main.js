async function fetchSensorStatus() {
  const res = await fetch('/api/status');
  const data = await res.json();

  // Update tampilan sensor
  document.getElementById('soilValue').textContent =
    data.soil_percent !== null ? `${data.soil_percent}%` : '--';

  document.getElementById('soilLabel').textContent =
    data.soil_label || '--';

  document.getElementById('phValue').textContent = data.soil_temp || '--';
  document.getElementById('humidityValue').textContent = data.env_hum + '%' || '--';
  document.getElementById('temperatureValue').textContent = data.env_temp + '°C' || '--';
  document.getElementById('relayStatus').textContent = data.relay_status;
  document.getElementById('modeStatus').textContent = data.mode;

  // Kontrol tombol manual tergantung mode
  document.getElementById('manualRelayBtn').disabled = data.mode === "AUTO";

  // Live status auto mode
  const autoInfo = document.getElementById('autoInfo');
  if (data.mode === "AUTO" && data.soil_percent !== null) {
    if (data.soil_percent < 60) {
      autoInfo.textContent = `Auto aktif: Soil Moisture rendah (${data.soil_percent}%) → Relay ON`;
    } else {
      autoInfo.textContent = `Auto aktif: Soil Moisture cukup (${data.soil_percent}%) → Relay OFF`;
    }
  } else if (data.mode === "AUTO") {
    autoInfo.textContent = `Auto aktif: Menunggu data Soil Moisture...`;
  } else {
    autoInfo.textContent = ''; // kosongkan jika mode manual
  }
}

// Tombol Manual ON/OFF
document.getElementById('manualRelayBtn').addEventListener('click', async () => {
  const res = await fetch('/api/relay-toggle', { method: 'POST' });
  const data = await res.json();
  document.getElementById('relayStatus').textContent = data.relay_status;
});

// Tombol Auto Mode ON/OFF
document.getElementById('autoRelayBtn').addEventListener('click', async () => {
  const res = await fetch('/api/auto-mode-toggle', { method: 'POST' });
  const data = await res.json();
  document.getElementById('modeStatus').textContent = data.mode;
  fetchSensorStatus();
});

// Jalankan refresh data tiap 3 detik
setInterval(fetchSensorStatus, 3000);
fetchSensorStatus();
