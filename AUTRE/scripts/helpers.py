import os
import json
import yaml
import sqlite3
import logging
import requests
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, List

# -----------------------------
# CONFIGURATION DU LOGGER
# -----------------------------

logger = logging.getLogger("helpers")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# -----------------------------
# GESTION DES FICHIERS JSON ET YAML
# -----------------------------

# Fichiers transversaux centralisés
FILES = {
    "config": "../config/config.yaml",
    "metrics": "../data/metrics.json",
    "pairs_data": "../data/pairs_data.json",
    "arbitrage_loops": "../data/arbitrage_loops.json",
    "execution_results": "../data/execution_results.json",
    "trade_data": "../data/trade_data.json",
}

# Fonctions génériques pour JSON
def load_json(file_path: str) -> Any:
    """Charge un fichier JSON et retourne son contenu."""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            logger.info(f"JSON chargé avec succès depuis {file_path}")
            return data
    except FileNotFoundError:
        logger.error(f"Fichier JSON introuvable : {file_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de parsing JSON pour {file_path} : {e}")
        return None

def save_json(data: Any, file_path: str) -> None:
    """Enregistre des données dans un fichier JSON."""
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            logger.info(f"JSON sauvegardé avec succès dans {file_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde dans {file_path} : {e}")

def validate_json(data: Any, schema: Dict[str, Any]) -> bool:
    """Valide la structure d'un JSON selon un schéma donné."""
    try:
        from jsonschema import validate
        validate(instance=data, schema=schema)
        logger.info("Validation JSON réussie.")
        return True
    except Exception as e:
        logger.error(f"Validation JSON échouée : {e}")
        return False

# Fonctions génériques pour YAML
def load_yaml(file_path: str) -> Any:
    """Charge un fichier YAML et retourne son contenu."""
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            logger.info(f"YAML chargé avec succès depuis {file_path}")
            return data
    except FileNotFoundError:
        logger.error(f"Fichier YAML introuvable : {file_path}")
        return None
    except yaml.YAMLError as e:
        logger.error(f"Erreur de parsing YAML pour {file_path} : {e}")
        return None

def save_yaml(data: Any, file_path: str) -> None:
    """Enregistre des données dans un fichier YAML."""
    try:
        with open(file_path, 'w') as file:
            yaml.dump(data, file, default_flow_style=False)
            logger.info(f"YAML sauvegardé avec succès dans {file_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde dans {file_path} : {e}")

# -----------------------------
# FONCTIONS POUR LA BASE SQLITE
# -----------------------------

def connect_sqlite(db_path: str) -> sqlite3.Connection:
    """Établit une connexion avec une base SQLite."""
    try:
        conn = sqlite3.connect(db_path)
        logger.info(f"Connexion SQLite établie avec succès : {db_path}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Erreur de connexion SQLite : {e}")
        raise


def execute_sql_query(conn: sqlite3.Connection, query: str, params: tuple = ()) -> List[tuple]:
    """Exécute une requête SQL et retourne les résultats."""
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        logger.info(f"Requête SQL exécutée avec succès : {query}")
        return results
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de l'exécution de la requête SQL : {e}")
        return []

def save_to_sqlite(conn: sqlite3.Connection, table: str, data: List[Dict[str, Any]]) -> None:
    """Insère des données dans une table SQLite."""
    try:
        if not data:
            logger.warning("Aucune donnée à insérer dans la table SQLite.")
            return
        columns = ', '.join(data[0].keys())
        placeholders = ', '.join(['?'] * len(data[0]))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor = conn.cursor()
        cursor.executemany(query, [tuple(row.values()) for row in data])
        conn.commit()
        logger.info(f"Données insérées avec succès dans la table {table}")
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de l'insertion dans SQLite : {e}")

def clean_sqlite_table(conn: sqlite3.Connection, table: str, older_than_days: int) -> None:
    """Nettoie les enregistrements plus anciens que X jours dans une table SQLite."""
    try:
        query = f"DELETE FROM {table} WHERE date < date('now', '-{older_than_days} days')"
        execute_sql_query(conn, query)
        logger.info(f"Nettoyage terminé pour la table {table}.")
    except sqlite3.Error as e:
        logger.error(f"Erreur lors du nettoyage de la table {table} : {e}")

# -----------------------------
# FONCTIONS POUR PROMETHEUS
# -----------------------------

def push_prometheus_metric(metric_name: str, value: float, prometheus_url: str) -> None:
    """Pousse une métrique vers le Pushgateway de Prometheus."""
    try:
        payload = f"{metric_name} {value}\n"
        response = requests.post(prometheus_url, data=payload)
        if response.status_code == 200:
            logger.info(f"Métrique {metric_name} poussée avec succès.")
        else:
            logger.error(f"Échec de l'envoi de {metric_name} : {response.status_code}")
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de métriques à Prometheus : {e}")


# -----------------------------
# FONCTIONS POUR LES FICHIERS TRANSVERSAUX
# -----------------------------

def load_config() -> Dict[str, Any]:
    """Charge le fichier config.json."""
    return load_yaml(FILES["config"])

def save_config(data: Dict[str, Any]) -> None:
    """Sauvegarde les données dans config.json."""
    save_yaml(data, FILES["config"])

def load_metrics() -> Dict[str, Any]:
    """Charge le fichier metrics.json."""
    return load_json(FILES["metrics"])

def save_metrics(data: Dict[str, Any]) -> None:
    """Sauvegarde les données dans metrics.json."""
    save_json(data, FILES["metrics"])

def load_pairs_data() -> Dict[str, Any]:
    """Charge le fichier pairs_data.json."""
    return load_json(FILES["pairs_data"])

def save_pairs_data(data: Dict[str, Any]) -> None:
    """Sauvegarde les données dans pairs_data.json."""
    save_json(data, FILES["pairs_data"])

def load_arbitrage_loops() -> Dict[str, Any]:
    """Charge le fichier arbitrage_loops.json."""
    return load_json(FILES["arbitrage_loops"])

def save_arbitrage_loops(data: Dict[str, Any]) -> None:
    """Sauvegarde les données dans arbitrage_loops.json."""
    save_json(data, FILES["arbitrage_loops"])

def load_execution_results() -> Dict[str, Any]:
    """Charge le fichier execution_results.json."""
    return load_json(FILES["execution_results"])

def save_execution_results(data: Dict[str, Any]) -> None:
    """Sauvegarde les données dans execution_results.json."""
    save_json(data, FILES["execution_results"])

def load_trade_data() -> Dict[str, Any]:
    """Charge le fichier trade_data.json."""
    return load_json(FILES["trade_data"])

def save_trade_data(data: Dict[str, Any]) -> None:
    """Sauvegarde les données dans trade_data.json."""
    save_json(data, FILES["trade_data"])

def update_trade_data(key: str, value: Any) -> None:
    """Met à jour une clé spécifique dans trade_data.json."""
    data = load_trade_data() or {}
    data[key] = value
    save_trade_data(data)

# -----------------------------
# AUTRES FONCTIONS UTILES
# -----------------------------

def log_action(action: str, details: str = "") -> None:
    """Enregistre une action dans les logs."""
    logger.info(f"Action : {action} - Détails : {details}")

def current_timestamp() -> str:
    """Retourne le timestamp actuel."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -----------------------------
# FONCTIONS GPU
# -----------------------------

def get_gpu_metrics() -> Dict[str, Any]:
    """Récupère les métriques GPU via nvidia-smi."""
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,power.draw,temperature.gpu",
                                 "--format=csv,noheader,nounits"], capture_output=True, text=True, check=True)
        metrics = result.stdout.strip().split("\n")[0].split(", ")
        return {
            "gpu_utilization": float(metrics[0]),
            "memory_used": float(metrics[1]),
            "power_draw": float(metrics[2]),
            "temperature": float(metrics[3])
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques GPU : {e}")
        return {}

# -----------------------------
# FONCTIONS DIGITAL OCEAN
# -----------------------------

def get_digital_ocean_metrics(api_token: str) -> Dict[str, Any]:
    """Récupère les métriques Digital Ocean via son API."""
    headers = {"Authorization": f"Bearer {api_token}"}
    url = "https://api.digitalocean.com/v2/monitoring/metrics/droplet"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques Digital Ocean : {e}")
        return {}

# -----------------------------
# EXTENSIONS POUR LES LOGS
# -----------------------------

def log_info(message: str, details: str = "") -> None:
    """Enregistre un message d'information dans les logs."""
    logger.info(f"INFO : {message} - Détails : {details}")

def log_error(message: str, details: str = "") -> None:
    """Enregistre un message d'erreur dans les logs."""
    logger.error(f"ERREUR : {message} - Détails : {details}")

def log_warning(message: str, details: str = "") -> None:
    """Enregistre un message d'avertissement dans les logs."""
    logger.warning(f"AVERTISSEMENT : {message} - Détails : {details}")

def log_debug(message: str, details: str = "") -> None:
    """Enregistre un message de débogage dans les logs."""
    logger.debug(f"DEBUG : {message} - Détails : {details}")
    
# -----------------------------
# FONCTIONS POUR LE RAPPORT FISCAL BINANCE
# -----------------------------

BINANCE_TAX_API_URL = "https://api.binance.com/api/v3/tax/report"  # URL fictive pour illustration

def fetch_tax_report(api_key: str, secret_key: str, year: int) -> Dict[str, Any]:
    """Récupère le rapport fiscal depuis l'API Binance pour une année donnée."""
    headers = {
        "X-MBX-APIKEY": api_key
    }
    params = {
        "year": year
    }
    try:
        response = requests.get(BINANCE_TAX_API_URL, headers=headers, params=params)
        response.raise_for_status()
        logger.info(f"Rapport fiscal récupéré avec succès pour l'année {year}.")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Erreur lors de la récupération du rapport fiscal : {e}")
        return {}

def save_tax_report(data: Dict[str, Any], file_path: str = "../data/tax_report.json") -> None:
    """Sauvegarde le rapport fiscal dans un fichier JSON."""
    try:
        save_json(data, file_path)
        logger.info(f"Rapport fiscal sauvegardé avec succès dans {file_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du rapport fiscal : {e}")

def calculate_flat_tax(data: Dict[str, Any], flat_tax_rate: float = 0.30) -> float:
    """Calcule la flat tax à 30% sur le gain annuel total."""
    try:
        total_gain = sum(transaction["gain"] for transaction in data.get("transactions", []))
        tax_due = total_gain * flat_tax_rate
        logger.info(f"Flat tax calculée : {tax_due} EUR pour un gain total de {total_gain} EUR.")
        return tax_due
    except Exception as e:
        logger.error(f"Erreur lors du calcul de la flat tax : {e}")
        return 0.0
        
        
# -----------------------------
# VALIDATION DES CLÉS API ET GESTION DES LIMITES DE TAUX
# -----------------------------

# Structure pour suivre les utilisations des clés API
API_USAGE_TRACKER = {}

def initialize_api_tracker(api_keys: List[str], reset_interval: int = 60) -> None:
    """
    Initialise le tracker des clés API pour surveiller les limites d'utilisation.
    Chaque clé API est associée à un compteur de requêtes.

    :param api_keys: Liste des clés API à initialiser.
    :param reset_interval: Intervalle de réinitialisation en secondes (par défaut : 60 secondes).
    """
    for key in api_keys:
        API_USAGE_TRACKER[key] = {"requests": 0, "last_reset": time.time()}
    logger.info(f"Tracker des clés API initialisé avec un intervalle de réinitialisation de {reset_interval} secondes.")

def validate_api_key(api_key: str, max_requests: int = 1200, reset_interval: int = 60) -> bool:
    """
    Vérifie si une clé API peut encore être utilisée dans les limites autorisées.

    :param api_key: La clé API à vérifier.
    :param max_requests: Nombre maximum de requêtes autorisées par intervalle.
    :param reset_interval: Intervalle de réinitialisation en secondes.
    :return: True si la clé API peut être utilisée, False sinon.
    """
    if api_key not in API_USAGE_TRACKER:
        logger.error(f"Clé API inconnue : {api_key}. Assurez-vous qu'elle est enregistrée dans le tracker.")
        return False

    usage_data = API_USAGE_TRACKER[api_key]
    current_time = time.time()

    # Réinitialiser le compteur si l'intervalle est dépassé
    if current_time - usage_data["last_reset"] > reset_interval:
        API_USAGE_TRACKER[api_key] = {"requests": 0, "last_reset": current_time}
        logger.info(f"Réinitialisation du compteur pour la clé API : {api_key}")

    # Vérifier si la clé API dépasse les limites
    if usage_data["requests"] < max_requests:
        API_USAGE_TRACKER[api_key]["requests"] += 1
        logger.debug(f"Clé API {api_key} validée : {usage_data['requests']} requêtes utilisées.")
        return True
    else:
        logger.warning(f"Clé API {api_key} a atteint la limite de {max_requests} requêtes.")
        return False

def get_available_api_key(max_requests: int = 1200, reset_interval: int = 60) -> str:
    """
    Renvoie une clé API disponible qui respecte les limites d'utilisation.

    :param max_requests: Nombre maximum de requêtes autorisées par intervalle.
    :param reset_interval: Intervalle de réinitialisation en secondes.
    :return: Une clé API valide ou None si aucune n'est disponible.
    """
    for api_key, usage_data in API_USAGE_TRACKER.items():
        if validate_api_key(api_key, max_requests, reset_interval):
            logger.info(f"Clé API disponible trouvée : {api_key}")
            return api_key

    logger.error("Aucune clé API disponible dans les limites actuelles.")
    return None