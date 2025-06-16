# Smart Garden Monitoring System 🌱

Dashboard berbasis Flask + Redis untuk monitoring kelembapan tanah, suhu, kelembapan udara, dan pH. Mendukung kontrol relay otomatis/manual.

## Fitur
- Live streaming data soil, humidity, temp, pH
- Auto Relay Mode (berbasis threshold kelembapan)
- Manual ON/OFF kontrol relay
- Integrasi MQTT + Redis

## Cara Menjalankan
```bash
cd backend
python app.py
