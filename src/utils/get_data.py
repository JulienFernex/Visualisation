"""
Module de récupération des données, télécharge les ressources brutes depuis internet vers le dossier local data/raw/.
"""

import os
import requests
from config import RAW_DIR, GEOJSON_URL, GEOJSON_PATH, DATA_URL, RAW_DATA_PATH, POPULATION_URL, RAW_POPULATION_PATH

def download_file(url, save_path):
    """
    Télécharge un fichier depuis une URL vers un chemin local.

    Args:
        url: L'adresse web de la ressource.
        save_path: Le chemin local où sauvegarder le fichier.
    """
    if not url:
        print(f"Pas d'URL fournie pour {os.path.basename(save_path)}")
        return

    try:
        print(f"Téléchargement de {url} ...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Succès : {save_path}")
    except Exception as e:
        print(f"Erreur lors du téléchargement de {url} : {e}")

def get_data():
    """
    Fonction principale d'extraction.
    """
    # Création du répertoire raw s'il n'existe pas
    os.makedirs(RAW_DIR, exist_ok=True)

    # Récupération des différentes données
    if not os.path.exists(GEOJSON_PATH):
        download_file(GEOJSON_URL, GEOJSON_PATH)
    else:
        print(f"Fichier existant : {GEOJSON_PATH}")

    if not os.path.exists(RAW_DATA_PATH):
        download_file(DATA_URL, RAW_DATA_PATH)
    else:
        print(f"Fichier existant : {RAW_DATA_PATH}")

    if not os.path.exists(RAW_POPULATION_PATH):
        download_file(POPULATION_URL, RAW_POPULATION_PATH)
    else:
        print(f"Fichier existant : {RAW_POPULATION_PATH}")

if __name__ == "__main__":
    get_data()