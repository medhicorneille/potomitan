import argparse
import os

import hashlib
import random
import string

from tqdm import tqdm

# from spleeter.separator import Separator
# from spleeter.audio.adapter import AudioAdapter

import torch
from demucs import pretrained
from demucs.audio import AudioFile, save_audio

def generate_random_hash(length=8):
    # Générer une chaîne aléatoire de caractères
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    # Créer un hash SHA-256 de la chaîne aléatoire
    hash_object = hashlib.sha256(random_string.encode())
    # Retourner les premiers 8 caractères du hash
    return hash_object.hexdigest()[:length]


def extract_vocals(audio_path, output_dir):
    """
    Extrait la partie vocale d'un fichier MP3 et la sauvegarde dans un fichier WAV.

    :param input_audio_path: Chemin vers le fichier MP3 d'entrée.
    :param output_dir: Répertoire de sortie pour les fichiers séparés.
    """
    try:
        # Créer le répertoire de sortie s'il n'existe pas
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Charger le modèle Demucs
        model = pretrained.get_model('demucs')

        # Charger l'audio
        audio_file = AudioFile(audio_path)
        waveform = audio_file.read(streaming=False)
        sample_rate = audio_file.sample_rate

        # Séparer les sources
        sources = model.separate(waveform[None])

        # Sauvegarder la partie vocale
        vocals = sources[0, 0].cpu().numpy()
        random_hash = generate_random_hash()
        output_path = os.path.join(output_dir, f'{random_hash}_vocals.wav')
        save_audio(output_path, vocals, sample_rate)

        print(f"La partie vocale a été extraite et sauvegardée dans le fichier '{output_path}'.")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

        
def process_directory(input_dir, output_dir):
    """
    Traite tous les fichiers MP3 dans un répertoire donné.

    :param input_dir: Répertoire contenant les fichiers MP3.
    :param output_dir: Répertoire de sortie pour les fichiers séparés.
    """
    # Lister tous les fichiers dans le répertoire d'entrée
    for filename in tqdm(os.listdir(input_dir), desc="Processing files"):
        if filename.lower().endswith(('.mp3', '.wav')):
            audio_path = os.path.join(input_dir, filename)
            extract_vocals(audio_path, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extraire la partie vocale de tous les fichiers MP3 dans un répertoire.')
    parser.add_argument('input_dir', type=str, help='Répertoire contenant les fichiers MP3 d\'entrée.')
    parser.add_argument('output_dir', type=str, help='Répertoire de sortie pour les fichiers séparés.')

    args = parser.parse_args()

    process_directory(args.input_dir, args.output_dir)
