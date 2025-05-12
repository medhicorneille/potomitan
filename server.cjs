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
app.get('/api/audio-files', (req, res) => {
  const audioFiles = fs.readdirSync(AUDIO_DIR).filter(f => f.endsWith('.wav') || f.endsWith('.mp3'))
  const existingTranscripts = fs.existsSync(TRANSCRIPT_PATH)
    ? JSON.parse(fs.readFileSync(TRANSCRIPT_PATH, 'utf-8'))
    : {}

  const files = audioFiles.map((file, index) => {
    const history = existingTranscripts[file] || []
    return {
      id: index + 1,
      name: file,
      src: `/audio/${file}`,
      transcription: history.length > 0 ? history[history.length - 1].transcription : '',
      history: history
    }
  })
  res.json(files)
})

// Enregistre une nouvelle transcription avec horodatage
app.post('/api/save-transcription', (req, res) => {
  const { name, transcription } = req.body
  if (!name) return res.status(400).send('Nom de fichier requis.')

  const now = new Date().toISOString()
  let data = {}

  if (fs.existsSync(TRANSCRIPT_PATH)) {
    data = JSON.parse(fs.readFileSync(TRANSCRIPT_PATH, 'utf-8'))
  }

  if (!data[name]) {
    data[name] = []
  }

  data[name].push({ transcription, timestamp: now })

  fs.writeFileSync(TRANSCRIPT_PATH, JSON.stringify(data, null, 2))
  res.json({ status: 'ok' })
})

app.use('/audio', express.static(AUDIO_DIR))

// Sert les fichiers statiques du build Vue
app.use(express.static(path.join(__dirname, 'dist')))

// Fallback : toutes les routes non-API renvoient index.html
app.get('/*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'))
})


app.listen(PORT, () => console.log(`✅ Serveur Express lancé sur http://localhost:${PORT}`))