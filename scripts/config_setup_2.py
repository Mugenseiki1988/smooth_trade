import os
import yaml
from utils.setup_logging import log_setup_message, log_setup_error
from utils.helpers import (
    define_stablecoin,
    initialize_keys_and_websockets,
    configure_display,
    save_config
)

# Définir le chemin du fichier de configuration
CONFIG_PATH = "config/config.yml"

def main():
    try:
        # Définir le stablecoin
        stablecoin = define_stablecoin()

        # Charger les clés API pour le trading
        trading_api_keys = ["API_KEY_1", "API_KEY_2", "...", "API_KEY_29"]

        # Charger les clés API fiscales
        tax_api_key = "TAX_API_KEY"
        tax_secret_key = "TAX_SECRET_KEY"

        # Initialiser les connexions WebSocket et les configurations
        websockets = initialize_keys_and_websockets(trading_api_keys, num_websockets=20)

        # Année cible pour la fiscalité
        target_year = 2024

        # Configuration initiale
        config = {
            "settings": {
                "stablecoin": stablecoin,
                "websockets": websockets,
                "display_options": {"suppress_scientific_notation": True}
            },
            "tax": {
                "api_key": tax_api_key,
                "secret_key": tax_secret_key,
                "target_year": target_year,
                "report_file": "../data/tax_report.json"
            }
        }

        # Appliquer la configuration d'affichage
        configure_display()

        # Sauvegarder la configuration dans le fichier YAML
        save_config(config, CONFIG_PATH)

        log_setup_message("Configuration initiale (incluant la fiscalité) terminée avec succès.")
    except Exception as e:
        log_setup_error(f"Erreur dans l'initialisation principale : {str(e)}")
        raise

if __name__ == "__main__":
    main()