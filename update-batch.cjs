// require('dotenv').config();
const fs = require('fs');
const { Pool } = require('pg');

//const pool = new Pool({
//  connectionString: process.env.DATABASE_URL,
//  ssl: { rejectUnauthorized: false }
//});

// Charger les variables d'environnement uniquement en local
if (process.env.NODE_ENV !== 'production') {
  require('dotenv').config();
}

const poolConfig = {
  connectionString: process.env.DATABASE_URL,
};

// Ajoutez la configuration SSL uniquement pour l'environnement distant
if (process.env.NODE_ENV === 'production') {
  poolConfig.ssl = { rejectUnauthorized: false };
}

const pool = new Pool(poolConfig);


async function updateBatch() {
  const data = JSON.parse(fs.readFileSync('transcription_batch.json', 'utf-8'));

  for (const item of data) {
    const { name, transcription, timestamp, author } = item;

    try {
      const result = await pool.query(
        `INSERT INTO transcriptions (filename, transcription, timestamp, author)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (filename, transcription)
        DO NOTHING;`,
        [name, transcription, timestamp, author || 'whisper-large-v3']
      );

      console.log(`✅ Donnée insérée ou mise à jour pour : ${name}`);
    } catch (err) {
      console.error(`❌ Oups cette proposition a déjà) été faite ${name} :`, err.message);
    }
  }

  await pool.end();
  console.log('📦 Traitement terminé');
}

updateBatch();
