"""
Point d'entrée principal de l'application, executer ce fichier lance le serveur web du Dashboard.
"""

from config import CLEAN_DATA_PATH, RAW_DATA_PATH
import os

def initialize_data():
    """
    Vérifie si les données sont présentes, sinon, lance automatiquement le téléchargement (get_data) et le nettoyage (clean_data).
    """
    if not os.path.exists(CLEAN_DATA_PATH):
        print("Données manquantes détectées.")
        
        # Importation des utilitaires
        from src.utils.get_data import get_data
        from src.utils.clean_data import load_and_rename_raw_data, clean_etab_to_depart, clean_etab_to_commune
        
        # Vérification / Téléchargement des données brutes
        if not os.path.exists(RAW_DATA_PATH):
            print("Lancement du téléchargement des données (get_data)...")
            get_data()
        
        # Nettoyage et transformation
        print("Lancement du nettoyage des données (clean_data)...")
        df_raw = load_and_rename_raw_data()
        clean_etab_to_depart(df_raw)
        clean_etab_to_commune(df_raw)
        print("Données prêtes.")
        
if __name__ == '__main__':
    initialize_data()
    
    from src.pages.dashboard import app

    app.run(debug=True)