import os
from utils.helpers import (
    fetch_tax_report,
    save_tax_report,
    calculate_flat_tax,
    load_config
)
from utils.setup_logging import log_action, log_error

def main():
    try:
        # Charger la configuration globale
        config = load_config()

        # Récupérer les clés API fiscales
        tax_api_key = config.get("tax", {}).get("api_key", "")
        secret_key = config.get("tax", {}).get("secret_key", "")

        if not tax_api_key or not secret_key:
            log_error("Clés API fiscales non configurées. Veuillez vérifier le fichier de configuration.")
            return

        # Année cible pour le rapport fiscal
        year = config.get("tax", {}).get("target_year", 2024)

        # Récupérer le rapport fiscal depuis l'API Binance
        tax_report = fetch_tax_report(tax_api_key, secret_key, year)

        if not tax_report:
            log_error(f"Le rapport fiscal pour l'année {year} n'a pas pu être récupéré.")
            return

        # Sauvegarder le rapport fiscal
        save_tax_report(tax_report)

        # Calculer la flat tax
        tax_due = calculate_flat_tax(tax_report)

        log_action("Rapport fiscal généré avec succès.", f"Montant de la flat tax : {tax_due:.2f} EUR.")
        print(f"Flat tax calculée pour l'année {year} : {tax_due:.2f} EUR.")
    except Exception as e:
        log_error(f"Erreur lors de l'exécution du script fiscal : {str(e)}")
        raise

if __name__ == "__main__":
    main()