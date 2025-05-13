<template>
  <div class="app-container">
    <h2 class="title">Fichiers Audio & Transcriptions</h2>
    <div v-if="successMessage" class="toast">{{ successMessage }}</div>
    <div v-for="file in visibleFiles" :key="file.id" class="row">
      <div class="column audio-col">
        <p class="filename">{{ file.name }}</p>
        <audio :src="file.src" controls class="audio-player"></audio>
      </div>
      <div class="column transcription-col">
        <textarea
          v-model="file.transcription"
          :class="{ empty: file.transcription === '' }"
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

onMounted(async () => {
  const res = await fetch('/api/audio-files')
  audioFiles.value = await res.json()
  loadMore()
  window.addEventListener('scroll', handleScroll)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
html, body, #app {
  height: 100%;
  margin: 0;
  overflow: auto;
}
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
  box-sizing: border-box;
}
.title {
  text-align: center;
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #111827;
}
.toast {
  max-width: 600px;
  margin: 0 auto 1rem;
  background-color: #d1fae5;
  color: #065f46;
  padding: 0.75rem 1rem;
  border: 1px solid #10b981;
  border-radius: 0.5rem;
  text-align: center;
  font-weight: 500;
}
.row {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background-color: #ffffff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
@media (min-width: 768px) {
  .row {
    flex-direction: row;
    justify-content: space-between;
  }
}
.column {
  flex: 1;
}
.audio-col .filename {
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #1f2937;
}
.audio-player {
  width: 100%;
}
.transcription-col textarea {
  width: 100%;
  min-height: 6rem;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  resize: vertical;
  font-family: inherit;
  margin-bottom: 0.5rem;
}
.transcription-col textarea.empty {
  border-color: #f87171;
  background-color: #fef2f2;
}
.edit-btn {
  padding: 0.5rem 1rem;
  background-color: #10b981;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-weight: 500;
}
.edit-btn:hover {
  background-color: #059669;
}
.history-log {
  margin-top: 0.75rem;
  padding: 0.75rem;
  border-top: 1px solid #e5e7eb;
  font-size: 0.875rem;
  background-color: #fefefe;
  border-radius: 0.25rem;
}
.history-title {
  font-weight: 600;
  cursor: pointer;
  color: #1f2937;
}
.history-entry {
  margin-bottom: 0.5rem;
}
.timestamp {
  font-size: 0.75rem;
  color: #6b7280;
}
</style>
