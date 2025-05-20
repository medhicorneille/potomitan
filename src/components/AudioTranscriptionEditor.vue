<template>
  <div class="app-container">
    <div class="sticky-header">
      <h2 class="title">Fichiers Audio & Transcriptions</h2>
      <div v-if="successMessage" class="toast">{{ successMessage }}</div>

      <!-- Navigation rapide -->
      <div class="navigation-controls" v-if="visibleFiles.length">
        <button @click="goToPrevious" :disabled="!hasPrevious" class="nav-btn">← Précédent</button>
        <span class="nav-status">Segment {{ currentIndexDisplay + 1 }} / {{ audioFiles.length }}</span>
        <button @click="goToNext" :disabled="!hasNext" class="nav-btn">Suivant →</button>
      </div>
    </div>

    <div class="audio-transcription-list">
      <div v-for="file in visibleFiles" :key="file.id" class="audio-item">
        <!-- Lecture audio -->
        <audio :src="file.url" controls />

        <!-- Notation de la qualité de la transcription -->
        <div class="star-rating">
          <span
            v-for="n in 5"
            :key="n"
            class="star"
            :class="{ filled: n <= file.rating }"
            @click="onRatingSelected(file, n)"
          >
            ★
          </span>
        </div>

        <!-- Zone de transcription -->
        <textarea
          v-model="file.transcription"
          class="transcription-box"
          placeholder="Entrez la transcription ici..."
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AudioTranscriptionEditor',
  data() {
    return {
      audioFiles: [],
      currentIndex: 0,
      pageSize: 5,
      successMessage: ''
    };
  },
  computed: {
    visibleFiles() {
      const start = this.currentIndex * this.pageSize;
      return this.audioFiles.slice(start, start + this.pageSize);
    },
    hasPrevious() {
      return this.currentIndex > 0;
    },
    hasNext() {
      return (this.currentIndex + 1) * this.pageSize < this.audioFiles.length;
    },
    currentIndexDisplay() {
      return this.currentIndex;
    }
  },
  methods: {
    fetchAudioFiles() {
      axios.get('/api/audio-files')
        .then(response => {
          this.audioFiles = response.data.map(file => ({
            ...file,
            transcription: file.transcription || '',
            rating: file.rating || 0
          }));
        })
        .catch(error => console.error('Erreur fetch audio files:', error));
    },
    goToPrevious() {
      if (this.hasPrevious) this.currentIndex--;
    },
    goToNext() {
      if (this.hasNext) this.currentIndex++;
    },
    onRatingSelected(file, rating) {
      // Met à jour localement
      file.rating = rating;
      // Enregistre la note dans la base de données
      axios.post(`/api/save-rating/${file.id}`, { rating })
        .then(() => {
          this.successMessage = 'Note enregistrée !';
          setTimeout(() => this.successMessage = '', 2000);
        })
        .catch(error => {
          console.error('Erreur enregistrement note:', error);
        });
    }
  },
  mounted() {
    this.fetchAudioFiles();
  }
};
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  padding: 1rem;
}
.sticky-header {
  position: sticky;
  top: 0;
  background-color: var(--header-bg-color);
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 10;
}
.title {
  font-size: 1.5rem;
  color: var(--text-color);
}
.toast {
  background: #4caf50;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  animation: fade-in-out 2s ease-in-out;
}
@keyframes fade-in-out {
  0%, 100% { opacity: 0; }
  10%, 90% { opacity: 1; }
}
.navigation-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.nav-btn {
  background: var(--btn-bg-color);
  color: white;
  cursor: pointer;
  border-radius: 4px;
  font-weight: 500;
  border: none;
  padding: 0.5rem 1rem;
}
.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.nav-status {
  color: var(--text-color);
  font-weight: 500;
}
.audio-transcription-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.audio-item {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.transcription-box {
  width: 100%;
  min-height: 120px;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: inherit;
}
.star-rating {
  display: flex;
  align-items: center;
}
.star {
  font-size: 24px;
  cursor: pointer;
  color: #ccc;
  margin-right: 4px;
}
.star.filled {
  color: gold;
}
</style>
