require('dotenv').config(); // Pour utiliser en local
const { Pool } = require('pg');

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


const express = require('express')
const fs = require('fs')
const path = require('path')
const cors = require('cors')
const bodyParser = require('body-parser')

const app = express()
const PORT = 3001

const AUDIO_DIR = path.join(__dirname, 'public', 'audio')
const TRANSCRIPT_PATH = path.join(__dirname, 'transcriptions.json')

app.use(cors())
app.use(bodyParser.json())

// Liste les fichiers audio + transcription (avec historique complet)
app.get('/api/audio-files', async (req, res) => {
  try {
    // 1) Lire TOUS les fichiers .wav/.mp3 du dossier
    const diskFiles = fs
      .readdirSync(AUDIO_DIR)
      .filter((f) => f.endsWith('.wav') || f.endsWith('.mp3'))

    // 2) Récupérer TOUT l’historique depuis la BDD
    const result = await pool.query(
      `SELECT filename, transcription, timestamp
       FROM transcriptions
       ORDER BY timestamp ASC`
    )

    // 3) Regrouper ces entrées par fichier
    const historyMap = {}
    result.rows.forEach(({ filename, transcription, timestamp }) => {
      if (!historyMap[filename]) historyMap[filename] = []
      historyMap[filename].push({ transcription, timestamp })
    })

    // 4) Construire le JSON final : un objet par fichier, même sans historique
    const files = diskFiles.map((filename, idx) => {
      const history = historyMap[filename] || []
      return {
        id: idx + 1,
        name: filename,
        src: `/audio/${filename}`,
        transcription: history.length
          ? history[history.length - 1].transcription
          : '',
        history,
      }
    })

    res.json(files)
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: 'Erreur de récupération des fichiers' })
  }
})

app.get('/api/init-db', async (req, res) => {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS transcriptions (
        id SERIAL PRIMARY KEY,
        filename TEXT NOT NULL,
        transcription TEXT NOT NULL,
        timestamp TIMESTAMPTZ DEFAULT NOW()
      )
    `)
    res.send('✅ Table transcriptions créée avec succès.')
  } catch (err) {
    console.error(err)
    res.status(500).send('❌ Erreur lors de la création de la table.')
  }
})



// Enregistre une nouvelle transcription avec horodatage
app.post('/api/save-transcription', async (req, res) => {
  const { name, transcription } = req.body
  if (!name || !transcription) return res.status(400).send('Champs requis.')

  try {
    await pool.query(
      `INSERT INTO transcriptions (filename, transcription) VALUES ($1, $2)`,
      [name, transcription]
    )
    res.json({ status: 'ok' })
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: 'Erreur lors de l\'enregistrement' })
  }
})


app.use('/audio', express.static(AUDIO_DIR))

// Sert d’abord les fichiers statiques du build
app.use(express.static(path.join(__dirname, 'dist')))

// Fallback SPA : on utilise une regex pour matcher tout chemin
app.get(/.*/, (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'))
})


app.listen(PORT, () => console.log(`✅ Serveur Express lancé sur http://localhost:${PORT}`))