import whisper
import os
import json
from datetime import datetime
from tqdm import tqdm

import torch

# Vérifie si CUDA est disponible
device = "cuda" if torch.cuda.is_available() else "cpu"

# Affiche le device sélectionné
print(f"Using device: {device}")


# It will print out the GPU that you are using.

AUDIO_DIR = "public/audio"
OUTPUT_FILE = "transcription_batch.json"

model = whisper.load_model("large-v3")

# Charger les transcriptions existantes si elles existent
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        results = json.load(f)
else:
    results = []

# Conserver une liste des fichiers déjà traités
existing = {entry["name"] for entry in results}

for filename in tqdm(os.listdir(AUDIO_DIR)):
    if (filename.endswith(".wav") or filename.endswith(".mp3")) and filename not in existing:
        filepath = os.path.join(AUDIO_DIR, filename)
        print(f"🔊 Transcription de : {filename}")
        try:
            result = model.transcribe(filepath, language="ht", device = device)

            entry = {
                "name": filename,
                "transcription": result["text"],
                "author": "whisper-large-v3",
                "timestamp": datetime.utcnow().isoformat()
            }

            results.append(entry)

            # Sauvegarder immédiatement après chaque transcription
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            print(f"✅ Fichier traité : {filename}")
            print(f"📄 Transcription : {entry['transcription']}\n")


        except Exception as e:
            print(f"❌ Erreur pour {filename} : {e}")

print("\n📄 Transcriptions sauvegardées dans :", OUTPUT_FILE)