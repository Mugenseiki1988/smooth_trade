import requests
import yaml
import random
import time
from prometheus_client import Gauge, start_http_server
from helpers import log_info, log_error, fetch_prometheus_metrics  # Import des fonctions depuis helpers.py

PROMETHEUS_URL = "http://localhost:9090/api/v1/query"  # URL de l'instance Prometheus
WEBSOCKET_CONFIG_PATH = "/config/"  # Dossier où sont stockés les fichiers config.yml individuels pour chaque WebSocket
WEB_SOCKET_COUNT = 20  # Nombre de WebSockets à répartir
MAX_PAIRS_PER_WEBSOCKET = 10  # Limite du nombre de paires par WebSocket

# Exposition des métriques via Prometheus
gauge_redistributed_pairs = Gauge("redistributed_pairs", "Nombre de paires redistribuées")
gauge_websocket_load = Gauge("websocket_load", "Charge actuelle des WebSockets", ["websocket_id"])

# Redistribue les paires entre les WebSockets en fonction de la charge
def redistribute_pairs(pairs, load_data):
    sorted_ws_ids = sorted(load_data, key=load_data.get)  # Trier les WebSockets par charge croissante
    redistributed_pairs = {f"ws_{i}": [] for i in range(1, WEB_SOCKET_COUNT + 1)}
    
    random.shuffle(pairs)  # Mélanger les paires pour une distribution aléatoire
    for pair in pairs:
        for ws_id in sorted_ws_ids:
            if len(redistributed_pairs[f"ws_{ws_id}"]) < MAX_PAIRS_PER_WEBSOCKET:
                redistributed_pairs[f"ws_{ws_id}"].append(pair)
                break

    gauge_redistributed_pairs.set(len(pairs))  # Exposer le nombre de paires redistribuées
    log_info(f"{len(pairs)} paires redistribuées entre les WebSockets.")
    return redistributed_pairs

# Met à jour les fichiers config.yml pour chaque WebSocket avec les paires redistribuées
def update_config_files(redistributed_pairs):
    for ws_id, pairs in redistributed_pairs.items():
        config_path = f"{WEBSOCKET_CONFIG_PATH}/{ws_id}_config.yml"
        try:
            with open(config_path, "r") as config_file:
                config_data = yaml.safe_load(config_file)

            # Mise à jour des paires dans la configuration
            config_data["settings"]["assigned_pairs"] = pairs

            with open(config_path, "w") as config_file:
                yaml.dump(config_data, config_file, default_flow_style=False)
            log_info(f"Configuration mise à jour pour {ws_id} avec {len(pairs)} paires.")

        except Exception as e:
            log_error(f"Erreur lors de la mise à jour de {config_path} : {e}")

# Fonction principale pour gérer la répartition dynamique des paires
def main():
    start_http_server(8000)  # Démarrer le serveur HTTP Prometheus sur le port 8000
    log_info("Serveur HTTP Prometheus démarré sur le port 8000.")
    
    while True:
        log_info("Récupération des métriques de charge depuis Prometheus...")
        load_data = fetch_prometheus_metrics(PROMETHEUS_URL, gauge_websocket_load)

        if load_data:
            # Récupérer les paires actives (supposons une fonction `get_active_pairs` disponible)
            pairs = ["BTCUSDT", "ETHBTC", "BNBUSDT"]  # Exemple : remplacer par la fonction réelle
            log_info(f"Redistribution de {len(pairs)} paires entre {WEB_SOCKET_COUNT} WebSockets...")
            redistributed_pairs = redistribute_pairs(pairs, load_data)

            log_info("Mise à jour des fichiers de configuration...")
            update_config_files(redistributed_pairs)

        time.sleep(60)  # Pause de 60 secondes entre chaque redistribution

if __name__ == "__main__":
    main()