// ─── MeTernak Backend ───────────────────────────────────────────────────────
// Stack: Node.js + Express + SQLite (better-sqlite3)
// Deploy: Render.com or Railway (see README.md)

const express = require('express');
const Database = require('better-sqlite3');
const cors = require('cors');
const path = require('path');

const app = express();
const db = new Database(path.join(__dirname, 'meternak.db'));

app.use(cors({ origin: '*' }));
app.use(express.json({ limit: '10mb' }));

// ─── SCHEMA ─────────────────────────────────────────────────────────────────
db.exec(`
  CREATE TABLE IF NOT EXISTS farmers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    phone       TEXT    NOT NULL,
    address     TEXT    NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS cows (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id   INTEGER NOT NULL,
    cow_number  TEXT    NOT NULL,
    name        TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id)
  );

  CREATE TABLE IF NOT EXISTS tracking (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    cow_id           INTEGER NOT NULL,
    mucus_viscosity  REAL,
    mucus_image_b64  TEXT,
    resistance       REAL,
    temperature      REAL,
    notes            TEXT,
    recorded_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cow_id) REFERENCES cows(id)
  );
`);

// ─── FARMERS ─────────────────────────────────────────────────────────────────
app.post('/api/farmers', (req, res) => {
  const { name, phone, address } = req.body;
  if (!name || !phone || !address)
    return res.status(400).json({ error: 'Nama, No. HP, dan alamat wajib diisi' });
  const r = db.prepare('INSERT INTO farmers (name, phone, address) VALUES (?, ?, ?)').run(name, phone, address);
  res.status(201).json({ id: r.lastInsertRowid, name, phone, address });
});

app.get('/api/farmers/:id', (req, res) => {
  const farmer = db.prepare('SELECT * FROM farmers WHERE id = ?').get(req.params.id);
  if (!farmer) return res.status(404).json({ error: 'Peternak tidak ditemukan' });
  res.json(farmer);
});

// ─── COWS ─────────────────────────────────────────────────────────────────────
app.post('/api/cows', (req, res) => {
  const { farmer_id, cow_number, name } = req.body;
  if (!farmer_id || !cow_number)
    return res.status(400).json({ error: 'farmer_id dan cow_number wajib diisi' });
  const r = db.prepare('INSERT INTO cows (farmer_id, cow_number, name) VALUES (?, ?, ?)').run(farmer_id, cow_number, name || null);
  res.status(201).json({ id: r.lastInsertRowid, farmer_id, cow_number, name });
});

app.get('/api/cows/farmer/:farmerId', (req, res) => {
  const cows = db.prepare('SELECT * FROM cows WHERE farmer_id = ? ORDER BY created_at ASC').all(req.params.farmerId);
  res.json(cows);
});

// ─── TRACKING ────────────────────────────────────────────────────────────────
app.post('/api/tracking', (req, res) => {
  const { cow_id, mucus_viscosity, mucus_image_b64, resistance, temperature, notes } = req.body;
  if (!cow_id)
    return res.status(400).json({ error: 'cow_id wajib diisi' });
  const r = db.prepare(
    'INSERT INTO tracking (cow_id, mucus_viscosity, mucus_image_b64, resistance, temperature, notes) VALUES (?, ?, ?, ?, ?, ?)'
  ).run(cow_id, mucus_viscosity || null, mucus_image_b64 || null, resistance || null, temperature || null, notes || null);
  res.status(201).json({ id: r.lastInsertRowid, cow_id, mucus_viscosity, resistance, temperature });
});

app.get('/api/tracking/cow/:cowId', (req, res) => {
  const limit = parseInt(req.query.limit) || 50;
  const records = db.prepare(
    'SELECT id, cow_id, mucus_viscosity, resistance, temperature, notes, recorded_at FROM tracking WHERE cow_id = ? ORDER BY recorded_at DESC LIMIT ?'
  ).all(req.params.cowId, limit);
  res.json(records);
});

// ─── HEALTH ───────────────────────────────────────────────────────────────────
app.get('/health', (_req, res) => res.json({ status: 'ok', service: 'MeTernak API' }));

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`MeTernak API berjalan di port ${PORT}`));
