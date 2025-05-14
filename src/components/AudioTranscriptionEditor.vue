<template>
  <div class="app-container">
    <h2 class="title">Fichiers Audio & Transcriptions</h2>
    <div v-if="successMessage" class="toast">{{ successMessage }}</div>
    <div v-for="file in visibleFiles" :key="file.id" class="row">
      <div class="column audio-col">
        <p class="filename">⏱ 00:00 → 00:10 — {{ file.name }}</p>
        <audio
          :ref="el => audioRefs[file.id] = el"
          :src="file.src"
          controls
          class="audio-player"
          @play="currentFocusedId = file.id"
        ></audio>
      </div>
      <div class="column transcription-col">
        <textarea
          v-model="file.transcription"
          :class="{ empty: file.transcription === '' }"
          :ref="el => textareas[file.id] = el"
          @focus="currentFocusedId = file.id"
          placeholder="Veuillez entrer la transcription ici..."
        ></textarea>
        <button @click="validate(file.id)" class="edit-btn">Valider</button>
        <details v-if="file.history && file.history.length > 1" class="history-log">
          <summary class="history-title">🕒 Historique des modifications</summary>
          <ul>
            <li v-for="(entry, idx) in file.history.slice(0, -1).reverse()" :key="idx" class="history-entry">
              <span class="timestamp">🗓️ {{ new Date(entry.timestamp).toLocaleString() }}</span><br />
              <span class="content text-sm italic">{{ entry.transcription }}</span>
            </li>
          </ul>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const audioFiles = ref([])
const visibleFiles = ref([])
const successMessage = ref('')
const BATCH_SIZE = 5
let currentIndex = 0

const textareas = {} // Pour navigation clavier
const audioRefs = {} // Pour lecture contrôlée
const currentFocusedId = ref(null)

function loadMore() {
  const next = audioFiles.value.slice(currentIndex, currentIndex + BATCH_SIZE)
  visibleFiles.value.push(...next)
  currentIndex += BATCH_SIZE
}

function handleScroll() {
  if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 50) {
    loadMore()
  }
}

async function validate(id) {
  const file = visibleFiles.value.find(f => f.id === id)
  try {
    const res = await fetch('/api/save-transcription', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: file.name, transcription: file.transcription })
    })
    if (!res.ok) throw new Error('Erreur lors de la sauvegarde.')
    if (!file.history) file.history = []
    file.history.push({ transcription: file.transcription, timestamp: new Date().toISOString() })
    successMessage.value = `✅ Transcription pour « ${file.name} » enregistrée !`
    setTimeout(() => (successMessage.value = ''), 3000)
  } catch (err) {
    console.error(err)
    successMessage.value = `❌ Erreur : ${err.message}`
    setTimeout(() => (successMessage.value = ''), 4000)
  }
}

function handleKeydown(e) {
  if (e.code === 'Space' && document.activeElement.tagName !== 'TEXTAREA') {
    e.preventDefault()
    const audio = audioRefs[currentFocusedId.value]
    if (audio) {
      audio.paused ? audio.play() : audio.pause()
    }
  }
  if (e.ctrlKey && e.key === 'Enter') {
    e.preventDefault()
    validate(currentFocusedId.value)
  }
}

onMounted(async () => {
  const res = await fetch('/api/audio-files')
  audioFiles.value = await res.json()
  loadMore()
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* conservé tel quel */
</style>
