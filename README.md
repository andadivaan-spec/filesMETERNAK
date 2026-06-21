# MeTernak Backend

REST API untuk data peternak, sapi, dan tracking parameter kesuburan.

## Jalankan Lokal

```bash
npm install
npm start
# API tersedia di http://localhost:3001
```

## Deploy ke Render.com (Gratis)

1. Push folder ini ke GitHub
2. Buka [render.com](https://render.com) → New → Web Service
3. Hubungkan repo, isi:
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`
4. Klik Deploy — URL otomatis tersedia

## Endpoint API

| Method | Path | Keterangan |
|--------|------|------------|
| POST | `/api/farmers` | Daftarkan peternak baru |
| GET | `/api/farmers/:id` | Info peternak |
| POST | `/api/cows` | Tambah sapi betina |
| GET | `/api/cows/farmer/:farmerId` | List sapi peternak |
| POST | `/api/tracking` | Catat parameter sapi |
| GET | `/api/tracking/cow/:cowId` | Riwayat tracking sapi |
| GET | `/health` | Cek status server |

## Contoh Request

```bash
# Daftar peternak
curl -X POST http://localhost:3001/api/farmers \
  -H "Content-Type: application/json" \
  -d '{"name":"Budi Santoso","phone":"081234567890","address":"Kec. Waru, Sidoarjo"}'

# Tambah sapi
curl -X POST http://localhost:3001/api/cows \
  -H "Content-Type: application/json" \
  -d '{"farmer_id":1,"cow_number":"#102","name":"Berta"}'

# Catat tracking
curl -X POST http://localhost:3001/api/tracking \
  -H "Content-Type: application/json" \
  -d '{"cow_id":1,"mucus_viscosity":1.8,"resistance":42.5,"temperature":38.7}'
```
