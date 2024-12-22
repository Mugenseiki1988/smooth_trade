import logging
import json
from datetime import datetime
from helpers import save_json, load_json, push_prometheus_metric

# -----------------------------
# CONFIGURATION DU LOGGER
# -----------------------------

logger = logging.getLogger("error_logging")
logger.setLevel(logging.ERROR)
file_handler = logging.FileHandler("../data/error_logs.json", mode='a')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# -----------------------------
# GESTION DES ERREURS
# -----------------------------

ERROR_LOG_FILE = "../data/error_logs.json"

def log_critical_error(message: str, details: str = "", prometheus_url: str = None) -> None:
    """
    Enregistre une erreur critique dans le fichier JSON et pousse une alerte vers Prometheus si configurée.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_entry = {
        "timestamp": timestamp,
        "level": "CRITICAL",
        "message": message,
        "details": details
    }

    # Ajout au fichier JSON
    existing_logs = load_json(ERROR_LOG_FILE) or []
    existing_logs.append(error_entry)
    save_json(existing_logs, ERROR_LOG_FILE)

    # Log dans le logger standard
    logger.critical(f"{message} - {details}")

    # Alerte vers Prometheus
    if prometheus_url:
        metric_name = "pipeline_critical_errors"
        push_prometheus_metric(metric_name, 1, prometheus_url)

def log_warning(message: str, details: str = "") -> None:
    """
    Enregistre un avertissement dans le fichier JSON et les logs locaux.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    warning_entry = {
        "timestamp": timestamp,
        "level": "WARNING",
        "message": message,
        "details": details
    }

    # Ajout au fichier JSON
    existing_logs = load_json(ERROR_LOG_FILE) or []
    existing_logs.append(warning_entry)
    save_json(existing_logs, ERROR_LOG_FILE)

    # Log dans le logger standard
    logger.warning(f"{message} - {details}")

def get_recent_errors(limit: int = 10) -> list:
    """
    Récupère les erreurs les plus récentes enregistrées dans le fichier JSON.
    """
    logs = load_json(ERROR_LOG_FILE) or []
    return logs[-limit:]

# -----------------------------
# TEST DES FONCTIONS (FACULTATIF)
# -----------------------------

if __name__ == "__main__":
    # Exemple d'erreur critique
    log_critical_error(
        message="Connexion échouée à l'API Binance",
        details="Code d'erreur 500",
        prometheus_url="http://localhost:9091"
    )

    # Exemple d'avertissement
    log_warning(
        message="Latence élevée détectée",
        details="Temps de réponse : 5s"
    )

    # Récupération des erreurs récentes
    print(get_recent_errors(limit=5))