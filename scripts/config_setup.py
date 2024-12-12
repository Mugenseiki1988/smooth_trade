import os
import yaml
from utils.setup_logging import log_setup_message, log_setup_error  # Import des fonctions de logging
from utils.helpers import (
    define_stablecoin,
    initialize_keys_and_websockets,
    configure_display,
    save_config
)  # Import des fonctions externalisées vers helpers.py

# Définir le chemin du fichier de configuration
CONFIG_PATH = "config/config.yml"

def main():
    # Définition des paramètres initiaux
    try:
        # Définir le stablecoin
        stablecoin = define_stablecoin()

        # Charger les clés API (remplacer par vos vraies clés API)
        api_keys = ["API_KEY_1", "API_KEY_2", "...", "API_KEY_29"]

        # Initialiser les connexions WebSocket et les configurations
        websockets = initialize_keys_and_websockets(api_keys, num_websockets=20)

        # Configuration initiale de la structure de configuration
        config = {
            "settings": {
                "stablecoin": stablecoin,
                "websockets": websockets,
                "display_options": {"suppress_scientific_notation": True}
            }
        }

        # Appliquer la configuration d'affichage
        configure_display()

        # Sauvegarder la configuration dans le fichier YAML
        save_config(config, CONFIG_PATH)

        log_setup_message("Configuration initiale terminée avec succès.")
    except Exception as e:
        log_setup_error(f"Erreur dans l'initialisation principale : {str(e)}")
        raise

if __name__ == "__main__":
    main()