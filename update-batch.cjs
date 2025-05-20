const fs = require('fs');
const path = require('path');
const { Pool } = require('pg');

// Charger les variables d'environnement uniquement en local
if (process.env.NODE_ENV !== 'production') {
  require('dotenv').config();
}

// Construire un chemin absolu compatible Windows/Linux
const dataFilePath = path.resolve(__dirname, 'transcription_batch.json');

const poolConfig = {
  connectionString: process.env.DATABASE_URL,
};

// Ajouter SSL uniquement en production (utile pour Render, Heroku, etc.)
if (process.env.NODE_ENV === 'production') {
  poolConfig.ssl = { rejectUnauthorized: false };
}

const pool = new Pool(poolConfig);

async function updateBatch() {
  let data;

  try {
    const fileContent = fs.readFileSync(dataFilePath, 'utf-8');
    data = JSON.parse(fileContent);
  } catch (err) {
    console.error('❌ Erreur lors de la lecture ou du parsing du fichier JSON :', err.message);
    return;
  }

  for (const item of data) {
    const { name, transcription, timestamp, author } = item;

    try {
      await pool.query(
        `INSERT INTO transcriptions (filename, transcription, timestamp, author)
         VALUES ($1, $2, $3, $4)
         ON CONFLICT (filename, transcription)
         DO NOTHING;`,
        [name, transcription, timestamp, author || 'whisper-large-v3']
      );

      console.log(`✅ Donnée insérée ou ignorée (doublon) : ${name}`);
    } catch (err) {
      console.error(`❌ Erreur d'insertion pour ${name} :`, err.message);
    }
  }

  await pool.end();
  console.log('📦 Traitement terminé');
}

updateBatch();
