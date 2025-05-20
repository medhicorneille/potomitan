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
      <div v-for="(file, index) in visibleFiles" :key="file.id" class="audio-item">
        <!-- Écoute audio simple, sans sauvegarde automatique à la fin -->
        <audio :src="file.url" controls />

        <!-- Système de notation par étoiles personnalisé -->
        <div class="star-rating">
          <span
            v-for="n in 5"
            :key="n"
            class="star"
            @click="selectStar(file, n)"
          >
            {{ n <= file.rating ? '★' : '☆' }}
          </span>
        </div>

        <!-- Zone de transcription avec bouton de sauvegarde manuelle -->
        <textarea
          v-model="file.transcription"
          class="transcription-box"
          placeholder="Entrez la transcription ici..."
        ></textarea>
        <button @click="saveFeedback(file)" class="save-btn">Enregistrer</button>
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
      successMessage: '',
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
      axios.get('/api/audio-files').then(response => {
        this.audioFiles = response.data.map(file => ({
          ...file,
          transcription: file.transcription || '',
          rating: file.rating || 0,
        }));
      });
    },
    goToPrevious() {
      if (this.hasPrevious) this.currentIndex--;
    },
    goToNext() {
      if (this.hasNext) this.currentIndex++;
    },
    selectStar(file, rating) {
      file.rating = rating;
      this.saveFeedback(file);
    },
    saveFeedback(file) {
      axios.post(`/api/save-transcription/${file.id}`, {
        transcription: file.transcription,
        rating: file.rating,
      }).then(() => {
        this.successMessage = 'Transcription et note enregistrées avec succès!';
        setTimeout(() => (this.successMessage = ''), 3000);
      }).catch(err => {
        console.error('Erreur sauvegarde feedback:', err);
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
  animation: fade-in-out 3s ease-in-out;
}

@keyframes fade-in-out {
  0%, 100% { opacity: 0; }
  10%, 90% { opacity: 1; }
}

.navigation-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-btn {
  background: var(--btn-bg-color);
  color: white;
  cursor: pointer;
  border-radius: 4px;
  font-weight: 500;
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-status {
  color: var(--text-color);
  font-weight: 500;
}

.star-rating {
  margin: 0.5rem 0;
}

.star {
  cursor: pointer;
  font-size: 24px;
  margin-right: 4px;
  color: gold;
}

.transcription-box {
  width: 100%;
  min-height: 100px;
  margin-top: 0.5rem;
}

.save-btn {
  margin-top: 0.5rem;
  background: var(--btn-bg-color);
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
