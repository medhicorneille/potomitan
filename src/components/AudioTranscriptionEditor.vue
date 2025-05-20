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
        <audio :src="file.url" controls @ended="onAudioEnded(index)" />
        <!-- Système de notation par étoiles -->
        <star-rating
          :star-size="24"
          v-model="file.rating"
          :show-rating="false"
          @rating-selected="onRatingSelected(file)"
        />
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
import StarRating from 'vue-star-rating';

export default {
  name: 'AudioTranscriptionEditor',
  components: {
    StarRating,
  },
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
        // Ajouter la propriété transcription et rating à chaque fichier
        this.audioFiles = response.data.map(file => ({
          ...file,
          transcription: file.transcription || '',
          rating: file.rating || 0,
        }));
      });
    },
    goToPrevious() {
      if (this.hasPrevious) {
        this.currentIndex--;
      }
    },
    goToNext() {
      if (this.hasNext) {
        this.currentIndex++;
      }
    },
    onRatingSelected(file) {
      // Envoie la note au serveur dès la sélection
      axios.post(`/api/save-rating/${file.id}`, {
        rating: file.rating
      });
    },
    onAudioEnded(index) {
      const globalIndex = this.currentIndex * this.pageSize + index;
      const file = this.audioFiles[globalIndex];
      axios.post(`/api/save-transcription/${file.id}`, {
        transcription: file.transcription,
        rating: file.rating,
      }).then(() => {
        this.successMessage = 'Transcription et note enregistrées avec succès!';
        setTimeout(() => this.successMessage = '', 3000);
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
</style>
