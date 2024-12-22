import time
from helpers import get_gpu_metrics, push_prometheus_metric, log_action

PROMETHEUS_PUSHGATEWAY_URL = "http://localhost:9091/metrics/job/gpu_monitor"

def monitor_gpu(interval: int = 10):
    """
    Surveille les métriques GPU à intervalle régulier et les envoie à Prometheus.
    
    Args:
        interval (int): Intervalle de temps en secondes entre deux collectes de métriques.
    """
    log_action("Lancement du GPU Monitor")
    while True:
        try:
            metrics = get_gpu_metrics()
            if metrics:
                # Pousser les métriques GPU vers Prometheus
                push_prometheus_metric("gpu_utilization", metrics["gpu_utilization"], PROMETHEUS_PUSHGATEWAY_URL)
                push_prometheus_metric("gpu_memory_used", metrics["memory_used"], PROMETHEUS_PUSHGATEWAY_URL)
                push_prometheus_metric("gpu_power_draw", metrics["power_draw"], PROMETHEUS_PUSHGATEWAY_URL)
                push_prometheus_metric("gpu_temperature", metrics["temperature"], PROMETHEUS_PUSHGATEWAY_URL)
                log_action("Métriques GPU collectées et envoyées à Prometheus")
            else:
                log_action("Pas de métriques GPU disponibles")
        except Exception as e:
            log_action(f"Erreur dans GPU Monitor : {e}", details="Erreur critique")
        time.sleep(interval)

if __name__ == "__main__":
    monitor_gpu()