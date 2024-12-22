import time
from helpers import get_digital_ocean_metrics, push_prometheus_metric, log_action

PROMETHEUS_PUSHGATEWAY_URL = "http://localhost:9091/metrics/job/digital_ocean_monitor"
DIGITAL_OCEAN_API_TOKEN = "YOUR_API_TOKEN"  # Remplacer par votre clé API

def monitor_digital_ocean(interval: int = 10):
    """
    Surveille les métriques de Digital Ocean à intervalle régulier et les envoie à Prometheus.
    
    Args:
        interval (int): Intervalle de temps en secondes entre deux collectes de métriques.
    """
    log_action("Lancement du Digital Ocean Monitor")
    while True:
        try:
            metrics = get_digital_ocean_metrics(DIGITAL_OCEAN_API_TOKEN)
            if metrics:
                # Pousser les métriques Digital Ocean vers Prometheus
                for metric_name, value in metrics.items():
                    push_prometheus_metric(metric_name, value, PROMETHEUS_PUSHGATEWAY_URL)
                log_action("Métriques Digital Ocean collectées et envoyées à Prometheus")
            else:
                log_action("Pas de métriques Digital Ocean disponibles")
        except Exception as e:
            log_action(f"Erreur dans Digital Ocean Monitor : {e}", details="Erreur critique")
        time.sleep(interval)

if __name__ == "__main__":
    monitor_digital_ocean()