const { Pool } = require('pg')

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false } // requis pour Render
})


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

// Liste les fichiers audio et leur transcription (avec historique)
app.get('/api/audio-files', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT filename, transcription, timestamp
      FROM transcriptions
      ORDER BY filename, timestamp ASC
    `)

    // Regroupe par fichier
    const grouped = {}
    result.rows.forEach(row => {
      if (!grouped[row.filename]) grouped[row.filename] = []
      grouped[row.filename].push({
        transcription: row.transcription,
        timestamp: row.timestamp
      })
    })

    const files = Object.entries(grouped).map(([filename, history], i) => ({
      id: i + 1,
      name: filename,
      src: `/audio/${filename}`,
      transcription: history[history.length - 1].transcription,
      history
    }))

    res.json(files)
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: 'Erreur de récupération des transcriptions' })
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