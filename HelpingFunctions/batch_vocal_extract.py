import argparse
import os

from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter

def extract_vocals(audio_path, output_dir):
    """
    Extrait la partie vocale d'un fichier MP3 et la sauvegarde dans un fichier WAV.

    :param input_audio_path: Chemin vers le fichier MP3 d'entrée.
    :param output_dir: Répertoire de sortie pour les fichiers séparés.
    """
    # Créer le répertoire de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialiser le séparateur de sources
    separator = Separator('spleeter:2stems')

    # Charger l'audio
    audio_loader = AudioAdapter.default()
    waveform, sample_rate = audio_loader.load(audio_path, sample_rate=16000)

    # Séparer les sources
    prediction = separator.separate(waveform)

    # Sauvegarder les sources séparées
    vocals = prediction['vocals']

    # Sauvegarder la partie vocale
    output_path = os.path.join(output_dir, os.path.basename(audio_path).replace('.mp3', '_vocals.wav'))
    audio_loader.save(output_path, vocals, sample_rate)

    print(f"La partie vocale a été extraite et sauvegardée dans le fichier '{output_path}'.")

def process_directory(input_dir, output_dir):
    """
    Traite tous les fichiers MP3 dans un répertoire donné.

    :param input_dir: Répertoire contenant les fichiers MP3.
    :param output_dir: Répertoire de sortie pour les fichiers séparés.
    """
    # Lister tous les fichiers dans le répertoire d'entrée
    for filename in os.listdir(input_dir):
        if filename.endswith('.mp3'):
            audio_path = os.path.join(input_dir, filename)
            extract_vocals(audio_path, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extraire la partie vocale de tous les fichiers MP3 dans un répertoire.')
    parser.add_argument('input_dir', type=str, help='Répertoire contenant les fichiers MP3 d\'entrée.')
    parser.add_argument('output_dir', type=str, help='Répertoire de sortie pour les fichiers séparés.')

    args = parser.parse_args()

    process_directory(args.input_dir, args.output_dir)
