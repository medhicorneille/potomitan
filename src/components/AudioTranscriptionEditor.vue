<template>
  <div class="container-wrapper" @scroll.passive="handleScroll" ref="scrollContainer">
    <h2 class="title">Fichiers Audio & Transcriptions</h2>
    <div v-if="successMessage" class="toast">{{ successMessage }}</div>
    <div
      v-for="file in visibleFiles"
      :key="file.id"
      class="row"
    >
      <!-- Colonne Audio -->
      <div class="column audio-col">
        <p class="filename">{{ file.name }}</p>
        <audio :src="file.src" controls class="audio-player"></audio>
      </div>

      <!-- Colonne Transcription -->
      <div class="column transcription-col">
        <textarea
          v-model="file.transcription"
          :class="{ empty: file.transcription === '' }"
          placeholder="Veuillez entrer la transcription ici..."
        ></textarea>
        <button @click="validate(file.id)" class="edit-btn">Valider</button>

        <!-- Historique des modifications -->
        <details v-if="file.history && file.history.length > 1" class="history-log">
          <summary class="history-title">🕒 Historique des modifications</summary>
          <ul>
            <li
              v-for="(entry, idx) in file.history.slice(0, -1).reverse()"
              :key="idx"
              class="history-entry"
            >
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
import { ref, onMounted } from 'vue'

const audioFiles = ref([])
const visibleFiles = ref([])
const successMessage = ref('')
const BATCH_SIZE = 5
let currentIndex = 0

const scrollContainer = ref(null)

onMounted(async () => {
  const res = await fetch('/api/audio-files')
  audioFiles.value = await res.json()
  loadMore()
})

function loadMore() {
  const next = audioFiles.value.slice(currentIndex, currentIndex + BATCH_SIZE)
  visibleFiles.value.push(...next)
  currentIndex += BATCH_SIZE
}

function handleScroll() {
  const el = scrollContainer.value
  if (el.scrollTop + el.clientHeight >= el.scrollHeight - 50) {
    loadMore()
  }
}

async function validate(id) {
  const file = visibleFiles.value.find(f => f.id === id)
  try {
    const res = await fetch('/api/save-transcription', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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
</script>

<style scoped>
/* Un seul scroll sur container-wrapper */
html, body, #app {
  height: 100%;
  margin: 0;
  overflow: hidden;
}
.container-wrapper {
  height: 100vh;
  overflow-y: auto;
  padding: 16px;
  background-color: #f3f4f6;
}

.title {
  text-align: center;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #111827;
}
.toast {
  background-color: #d1fae5;
  color: #065f46;
  padding: 12px;
  border: 1px solid #10b981;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 16px;
  font-weight: 500;
}
.row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: box-shadow 0.3s ease;
}
.row:nth-child(odd) {
  background-color: #ffffff;
}
.row:nth-child(even) {
  background-color: #f9fafb;
}
.row:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.column {
  width: 48%;
}
.audio-col .filename {
  font-weight: 500;
  margin-bottom: 8px;
  color: #1f2937;
}
.audio-player {
  width: 100%;
}
.transcription-col textarea {
  width: 100%;
  height: 96px;
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  resize: none;
  font-family: inherit;
  margin-bottom: 8px;
  background-color: #ffffff;
  color: #111827;
}
.transcription-col textarea.empty {
  border-color: #f87171;
  background-color: #fef2f2;
}
.edit-btn {
  padding: 8px 16px;
  background-color: #10b981;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}
.edit-btn:hover {
  background-color: #059669;
}
.history-log {
  margin-top: 8px;
  padding: 12px;
  border-top: 1px solid #e5e7eb;
  font-size: 14px;
  background-color: #fefefe;
  color: #1f2937;
  border-radius: 6px;
}
.history-title {
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  color: #1f2937;
}
.history-entry {
  margin-bottom: 6px;
}
.timestamp {
  font-size: 12px;
  color: #6b7280;
}
</style>
