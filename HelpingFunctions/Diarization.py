import os
import json
import logging
import torch


from pyannote.audio import Pipeline

# Prioriser les variables d'environnement système
HUGGING_FACE_KEY = os.getenv("HuggingFace_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_MCF")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
if torch.cuda.is_available():
    logging.info(f"GPU trouvé! on utilise CUDA. Device: {device}")

else:
    logging.info(f"Pas de GPU de disponible... Device: {device}")



# Charger les modèles
# diarization_model = Pipeline.from_pretrained("pyannote/speaker-diarization")
def load_pipeline_diarization(model):
    pipeline_diarization = Pipeline.from_pretrained(
        model,
        # cache_dir= HF_cache,
        use_auth_token = HUGGING_FACE_KEY,
    )

    if torch.cuda.is_available():
        pipeline_diarization.to(torch.device("cuda"))

    logging.info(f"Pipeline Diarization déplacée sur {device}")

    return pipeline_diarization

diarization_model = load_pipeline_diarization("pyannote/speaker-diarization-3.1")



file_path = f"/tmp/{file.filename}"
# Détection de l'extension du fichier
file_extension = os.path.splitext(file_path)[1].lower()
logging.info(f"Extension détectée {file_extension}.")


try:
    # Sauvegarder temporairement le fichier uploadé
    with open(file_path, "wb") as f:
        f.write(await file.read())
    logging.info(f"Fichier {file.filename} sauvegardé avec succès.")

    file_type = filetype.guess(file_path)
    logging.info(f"Type de fichier : {file_type.mime}, Extension : {file_type.extension}")

    extraction_status = json.dumps({'extraction_audio_status': 'extraction_audio_ongoing', 'message': 'Extraction audio en cours ...'})

    # Si le fichier est un fichier audio (formats courants)
    if file_extension in ['.mp3', '.wav', '.aac', '.ogg', '.flac', '.m4a']:
        logging.info(f"fichier audio détecté: {file_extension}.")

        audio = AudioSegment.from_file(file_path)


    elif file_extension in ['.mp4', '.mov', '.3gp', '.mkv']:
        logging.info(f"fichier vidéo détecté: {file_extension}.")
        VideoFileClip(file_path)
        logging.info("Extraction Audio démarrée ...")

        logging.info(extraction_status)

        audio = AudioSegment.from_file(file_path, format=file_type.extension)

        logging.info(extraction_status)

    logging.info(f"Conversion du {file.filename} en mono 16kHz.")
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    audio_path = f"{file_path}.wav"
    logging.info(f"Sauvegarde de la piste audio dans {audio_path}.")
    audio.export(audio_path, format="wav")

    # Vérification si le fichier existe
    if not os.path.exists(audio_path):
        logging.error(f"Le fichier {audio_path} n'existe pas.")

    # Étape 1 : Diarisation
    logging.info(f"Démarrage de la diarisation du fichier {audio_path}")

    async def live_process_audio():
        extraction_status = json.dumps({'extraction_audio_status': 'extraction_audio_done', 'message': 'Extraction audio terminée!'})
        yield f"{extraction_status}\n"
        logging.info(extraction_status)

        # Envoi du statut "en cours"
        start_diarization = json.dumps({'status': 'diarization_processing', 'message': 'Séparation des voix en cours, patience est mère de vertu ...'})
        yield f"{start_diarization}\n"
        logging.info(start_diarization)

        logging.debug(f"Diarization démarrée pour le fichier {audio_path}")

        try:
            with ProgressHook() as hook:
                diarization = diarization_model(audio_path, hook=hook)
            # diarization = diarization_model(audio_path)
        except Exception as e:
            logging.error(f"Erreur pendant la diarisation :-( : {str(e)}")

        # Envoi final du statut pour indiquer la fin
        end_diarization = json.dumps({'status': 'diarization_done', 'message': 'Séparation des voix terminée.'})
        yield f"{end_diarization}\n"

        logging.debug(f"Diarization terminée")

        # diarization_json = convert_tracks_to_json(diarization)

        try:
            diarization_json = convert_tracks_to_json(diarization)
            logging.info(f"Taille des données de diarisation en JSON : {len(json.dumps(diarization_json))} octets")
        except Exception as e:
            logging.error(f"Erreur pendant la conversion de la diarisation en JSON : {str(e)}")
            yield json.dumps({"status": "error", "message": f"Erreur pendant la conversion en JSON : {str(e)}"}) + "\n"
            return

        logging.debug(f"Résultat de la diarization {diarization_json}")

        logging.info(end_diarization)

        diarization_json = convert_tracks_to_json(diarization)

        # Envoyer la diarisation complète d'abord
        logging.info(f"{json.dumps({'diarization': diarization_json})}")
        yield f"{json.dumps({'diarization': diarization_json})}\n"

        # Exporter les segments pour chaque locuteur
        total_chunks = len(list(diarization.itertracks(yield_label=True))) 
        logging.info(f"total_turns: {total_chunks}")
        
        turn_number = 0
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            turn_number += 1
            logging.info(f"Tour {turn_number}/{total_chunks}")

            # Étape 2 : Transcription pour chaque segment
            start_ms = int(turn.start * 1000)  # Convertir de secondes en millisecondes
            end_ms = int(turn.end * 1000)

            # Extraire le segment audio correspondant au speaker
            segment_audio = audio[start_ms:end_ms]

            # Sauvegarder le segment temporairement pour Whisper
            segment_path = f"/tmp/segment_{start_ms}_{end_ms}.wav"
            segment_audio.export(segment_path, format="wav")
