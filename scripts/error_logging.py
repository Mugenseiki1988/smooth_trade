import logging
from helpers import load_config, save_json, push_prometheus_metric, current_timestamp

# -----------------------------
# CONFIGURATION DU LOGGER D'ERREURS
# -----------------------------

def setup_error_logger() -> logging.Logger:
    """
    Configure un logger dédié aux erreurs critiques.
    """
    # Charger la configuration depuis config.yaml
    config = load_config()
    log_file = config.get("error_logging", {}).get("error_file", "../data/error_logs.json")

    # Configurer le logger
    error_logger = logging.getLogger("error_logger")
    error_logger.setLevel(logging.ERROR)

    # Gestionnaire pour écrire les erreurs dans un fichier
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    error_logger.addHandler(file_handler)

    # Gestionnaire pour afficher les erreurs critiques dans la console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    error_logger.addHandler(console_handler)

    return error_logger

# -----------------------------
# ENREGISTREMENT DES ERREURS DANS UN FICHIER JSON
# -----------------------------

def log_error_to_json(error_message: str, details: str = "") -> None:
    """
    Enregistre une erreur dans le fichier error_logs.json.
    """
    config = load_config()
    error_file = config.get("error_logging", {}).get("error_file", "../data/error_logs.json")

    # Charger les logs existants ou initialiser une liste vide
    try:
        error_logs = load_json(error_file) or []
    except Exception as e:
        error_logs = []
        logger = setup_error_logger()
        logger.error(f"Impossible de charger error_logs.json : {e}")

    # Ajouter une nouvelle entrée de log
    error_logs.append({
        "timestamp": current_timestamp(),
        "error_message": error_message,
        "details": details
    })

    # Sauvegarder les logs dans error_logs.json
    save_json(error_logs, error_file)

# -----------------------------
# ENVOI D'ALERTES VIA PROMETHEUS
# -----------------------------

def send_error_alert_to_prometheus(error_message: str, prometheus_url: str = None) -> None:
    """
    Envoie une alerte à Prometheus via le Pushgateway.
    """
    if not prometheus_url:
        config = load_config()
        prometheus_url = config.get("monitoring", {}).get("prometheus_push_url", None)

    if prometheus_url:
        try:
            metric_name = "pipeline_critical_errors"
            value = 1
            push_prometheus_metric(metric_name, value, prometheus_url)
        except Exception as e:
            logger = setup_error_logger()
            logger.error(f"Impossible d'envoyer une alerte Prometheus : {e}")

# -----------------------------
# UTILISATION DU LOGGER D'ERREURS
# -----------------------------

if __name__ == "__main__":
    # Configuration du logger d'erreurs
    error_logger = setup_error_logger()

    # Exemple d'utilisation
    try:
        # Simuler une erreur critique
        raise ValueError("Exemple d'erreur critique")
    except Exception as e:
        error_message = str(e)
        error_logger.error(error_message)
        log_error_to_json(error_message, details="Erreur simulée pour démonstration")
        send_error_alert_to_prometheus(error_message)