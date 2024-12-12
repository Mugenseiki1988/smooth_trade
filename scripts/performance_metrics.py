import json
import logging
from datetime import datetime

# Configuration du logger
logging.basicConfig(
    filename='../data/logs/performance_metrics.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Chemins des fichiers nécessaires
FILES = {
    "execution_results": "../data/execution_results.json",
    "metrics": "../data/metrics.json",
    "trade_data": "../data/trade_data.json"
}

# Chargement des fichiers JSON
def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            logging.info(f"Fichier chargé avec succès : {file_path}")
            return data
    except FileNotFoundError:
        logging.error(f"Fichier introuvable : {file_path}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Erreur de parsing JSON dans {file_path} : {e}")
        return None

# Sauvegarde des données JSON
def save_json(data, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            logging.info(f"Données sauvegardées avec succès dans : {file_path}")
    except Exception as e:
        logging.error(f"Erreur lors de la sauvegarde dans {file_path} : {e}")

# Calcul des indicateurs avancés
def calculate_performance_metrics():
    execution_results = load_json(FILES["execution_results"])
    metrics = load_json(FILES["metrics"])
    trade_data = load_json(FILES["trade_data"])

    if not execution_results or not metrics or not trade_data:
        logging.error("Impossible de calculer les métriques : données manquantes.")
        return

    # Calcul des indicateurs
    total_transactions = execution_results.get("summary", {}).get("total_transactions", 0)
    successful_transactions = execution_results.get("summary", {}).get("successful_transactions", 0)
    failed_transactions = execution_results.get("summary", {}).get("failed_transactions", 0)
    total_profit = execution_results.get("summary", {}).get("total_profit", 0.0)
    average_execution_time = execution_results.get("summary", {}).get("average_execution_time_seconds", 0.0)

    active_orders = len(trade_data.get("active_orders", []))

    # Calcul du ratio de succès
    success_ratio = (successful_transactions / total_transactions) * 100 if total_transactions > 0 else 0

    # Mises à jour des métriques
    performance_data = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_transactions": total_transactions,
        "successful_transactions": successful_transactions,
        "failed_transactions": failed_transactions,
        "success_ratio": success_ratio,
        "total_profit": total_profit,
        "average_execution_time": average_execution_time,
        "active_orders": active_orders
    }

    # Ajout aux métriques locales
    metrics["performance"] = performance_data
    save_json(metrics, FILES["metrics"])

    logging.info(f"Indicateurs de performance calculés et mis à jour : {performance_data}")

# Exécution principale
if __name__ == "__main__":
    logging.info("Début du calcul des indicateurs avancés de performance.")
    calculate_performance_metrics()
    logging.info("Calcul des indicateurs de performance terminé.")