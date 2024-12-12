import requests
import yaml
import time
from prometheus_client import Gauge, start_http_server
from helpers import log_info, log_error  # Centralisé dans helpers.py

# Charger la configuration depuis le fichier YAML
def load_config(filename='config.yml'):
    try:
        with open(filename, 'r') as file:
            config = yaml.safe_load(file)
        log_info("Configuration chargée depuis config.yml.")
        return config
    except Exception as e:
        log_error(f"Erreur lors du chargement de la configuration : {e}")
        raise

# Récupérer les métriques de Prometheus
def fetch_metrics(prometheus_url, query):
    try:
        response = requests.get(f"{prometheus_url}/api/v1/query", params={'query': query})
        response.raise_for_status()
        result = response.json()
        log_info(f"Métriques récupérées pour la requête : {query}")
        return result.get("data", {}).get("result", [])
    except requests.exceptions.RequestException as e:
        log_error(f"Erreur lors de la récupération des métriques : {e}")
        return []

# Vérifier les métriques et générer des alertes en cas de surcharge
def check_metrics(metrics, threshold, metric_name):
    alert_triggered = False
    for metric in metrics:
        value = float(metric['value'][1])
        if value > threshold:
            log_error(f"ALERTE : {metric_name} dépasse le seuil critique ! Valeur : {value}, Seuil : {threshold}")
            alert_triggered = True
        else:
            log_info(f"{metric_name} : {value} est en dessous du seuil de {threshold}.")
    return alert_triggered

# Fonction principale de surveillance des ressources
def monitor_resources(config):
    prometheus_url = config.get('prometheus_url', 'http://localhost:9090')
    websocket_latency_threshold = config['resource_thresholds']['websocket_latency']
    api_rate_limit_threshold = config['resource_thresholds']['api_rate_limit']
    monitor_interval = config['monitor_interval']

    # Requêtes Prometheus pour surveiller la latence des websockets et le taux d'utilisation de l'API
    websocket_latency_query = 'avg_over_time(websocket_latency[1m])'
    api_rate_query = 'rate(api_requests_total[1m])'

    # Initialiser Prometheus pour Grafana
    ws_latency_gauge = Gauge('websocket_latency', 'Latence moyenne des WebSockets (en secondes)')
    api_rate_gauge = Gauge('api_rate_limit', 'Taux d\'utilisation de l\'API REST (requêtes/min)')

    # Démarrer un serveur HTTP Prometheus pour exposer les métriques
    start_http_server(9100)
    log_info("Serveur HTTP Prometheus démarré sur le port 9100 pour exposer les métriques.")

    while True:
        try:
            # Récupérer les métriques
            websocket_metrics = fetch_metrics(prometheus_url, websocket_latency_query)
            api_rate_metrics = fetch_metrics(prometheus_url, api_rate_query)

            # Mettre à jour les métriques exposées pour Grafana
            if websocket_metrics:
                ws_latency_value = float(websocket_metrics[0]['value'][1])
                ws_latency_gauge.set(ws_latency_value)
            else:
                ws_latency_gauge.set(0)
                log_info("Aucune donnée de latence WebSocket disponible.")

            if api_rate_metrics:
                api_rate_value = float(api_rate_metrics[0]['value'][1])
                api_rate_gauge.set(api_rate_value)
            else:
                api_rate_gauge.set(0)
                log_info("Aucune donnée de taux d'utilisation de l'API REST disponible.")

            # Vérifier les seuils et générer des alertes
            ws_alert = check_metrics(websocket_metrics, websocket_latency_threshold, "Latence WebSocket")
            api_alert = check_metrics(api_rate_metrics, api_rate_limit_threshold, "Taux d'utilisation de l'API REST")

            if not ws_alert and not api_alert:
                log_info("Toutes les métriques sont dans les limites acceptables.")

        except Exception as e:
            log_error(f"Erreur lors de la surveillance des ressources : {e}")

        # Pause avant la prochaine vérification
        time.sleep(monitor_interval)

# Charger la configuration et démarrer la surveillance
if __name__ == "__main__":
    try:
        config = load_config()
        monitor_resources(config)
    except Exception as e:
        log_error(f"Erreur fatale dans le script resource_monitor.py : {e}")