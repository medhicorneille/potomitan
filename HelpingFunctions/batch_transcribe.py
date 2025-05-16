import whisper
import os
import json
from tqdm import tqdm

AUDIO_DIR = "public/audio"
OUTPUT_FILE = "transcription_batch.json"

model = whisper.load_model("large-v3")

# Charger le fichier existant s'il existe
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        results = json.load(f)
else:
    results = []

# Construire un index pour éviter les doublons
existing_files = {entry["name"] for entry in results}

for filename in tqdm(os.listdir(AUDIO_DIR)):
    if filename.endswith(".wav") or filename.endswith(".mp3") and filename not in existing_files:
        filepath = os.path.join(AUDIO_DIR, filename)
        print(f"🔊 Transcription de : {filename}")
        try:
            result = model.transcribe(filepath, language="ht")
            new_entry = {
                "name": filename,
                "transcription": result["text"],
                "updated_by": "medhi"
            }
            results.append(new_entry)

            # Écriture immédiate dans le fichier
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            print(f"✅ Transcrit : {filename}")
            print(f"📄 Transcription : {new_entry['transcription']}")

        except Exception as e:
            print(f"❌ Erreur pour {filename} : {e}")

print("\n📄 Transcription mise à jour dans :", OUTPUT_FILE)
