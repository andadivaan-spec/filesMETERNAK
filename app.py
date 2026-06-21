# ─── MeTernak Backend (Python) ───────────────────────────────────────────────
# Bahasa: Python + Flask
# Database: SQLite (bawaan Python, tidak perlu install apapun tambahan)
# Cara jalankan: lihat README.md
#
# Tugas backend ini:
# 1. Menerima data dari HTML (hasil deteksi YOLO, suhu, resistansi ESP32)
# 2. Menyimpannya ke database per cattle_id (ID sapi)
# 3. Menghitung "probabilitas estrus" dari riwayat data sapi itu
#    (sementara pakai aturan sederhana, nanti tinggal ganti dengan model LSTM asli)

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # supaya HTML (dibuka dari file:// atau domain lain) boleh akses backend ini

DB_PATH = os.path.join(os.path.dirname(__file__), 'meternak.db')


# ─── SETUP DATABASE ───────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cattle_id TEXT NOT NULL,
            farmer_name TEXT,
            mucus_color TEXT,
            temperature REAL,
            resistance INTEGER,
            probability REAL,
            recorded_at TEXT
        )
    ''')
    conn.commit()
    conn.close()


# ─── LSTM (TRACKING) — bukan pengambil keputusan, cuma baca posisi waktu ─────
# Placeholder. Nanti ganti dengan model LSTM asli (load .h5/.onnx lalu predict).
def lstm_tracking_output(mucus_color):
    if mucus_color == 'transparant':
        return {'estimated_day': 1, 'p_day2': 0.55, 'window_remaining': 2}
    elif mucus_color == 'darah':
        return {'estimated_day': 2, 'p_day2': 0.88, 'window_remaining': 1}
    elif mucus_color == 'kuning':
        return {'estimated_day': 0, 'p_day2': 0.10, 'window_remaining': 0}
    else:
        return {'estimated_day': None, 'p_day2': 0.0, 'window_remaining': None}


# ─── RF (DECISION) — pakai output LSTM + suhu vulva + resistansi lendir ─────
def rf_decision(lstm_out, temperature, resistance):
    suhu_ok = temperature is not None and 38.2 <= temperature <= 39.5
    if lstm_out['estimated_day'] == 0:
        return 'JANGAN_IB'
    if lstm_out['estimated_day'] == 2 and suhu_ok:
        return 'IB_SEKARANG'
    return 'STANDBY'


# ─── ENDPOINT API ─────────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'MeTernak Python Backend'})


# Dipanggil dari HTML setiap parameter sapi berubah (lendir, suhu, resistansi)
@app.route('/api/tracking', methods=['POST'])
def simpan_tracking():
    data = request.get_json()

    cattle_id = data.get('cattle_id')
    farmer_name = data.get('farmer_name')
    mucus_color = data.get('mucus_color')
    temperature = data.get('temperature')
    resistance = data.get('resistance')

    if not cattle_id:
        return jsonify({'error': 'cattle_id wajib diisi'}), 400

    lstm_out = lstm_tracking_output(mucus_color)
    decision = rf_decision(lstm_out, temperature, resistance)

    conn = get_db()
    conn.execute(
        '''INSERT INTO tracking
           (cattle_id, farmer_name, mucus_color, temperature, resistance, probability, recorded_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (cattle_id, farmer_name, mucus_color, temperature, resistance,
         lstm_out['p_day2'], datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    return jsonify({
        'cattle_id': cattle_id,
        'lstm': lstm_out,      # output tracking: posisi hari & probabilitas
        'decision': decision,  # output RF: keputusan akhir
        'message': 'Data tersimpan'
    }), 201


# Dipakai untuk melihat riwayat tracking 1 sapi (untuk grafik time-series nanti)
@app.route('/api/tracking/<cattle_id>', methods=['GET'])
def riwayat_tracking(cattle_id):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM tracking WHERE cattle_id = ? ORDER BY recorded_at DESC LIMIT 50',
        (cattle_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


# ─── JALANKAN SERVER ───────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print('MeTernak Backend (Python) berjalan di http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)
