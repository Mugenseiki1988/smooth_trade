import logging
from helpers import load_config

# -----------------------------
# CONFIGURATION DU LOGGER CENTRALISÉ
# -----------------------------

def setup_logging() -> logging.Logger:
    """
    Configure et retourne un logger centralisé basé sur les paramètres définis dans config.yaml.
    """
    # Charger la configuration depuis config.yaml
    config = load_config()
    log_level = config.get("logging", {}).get("log_level", "INFO").upper()
    log_file = config.get("logging", {}).get("log_file", "../data/logs/app.log")

    # Créer et configurer le logger
    logger = logging.getLogger("pipeline_logger")
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Configuration du gestionnaire de logs dans un fichier
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    # Configuration du gestionnaire de logs dans la console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    logger.info("Logger configuré avec succès.")
    return logger

# -----------------------------
# UTILISATION DU LOGGER CENTRALISÉ
# -----------------------------

if __name__ == "__main__":
    # Exemple d'utilisation du logger configuré
    logger = setup_logging()
    logger.info("Ceci est un message d'information.")
    logger.warning("Ceci est un message d'avertissement.")
    logger.error("Ceci est un message d'erreur.")