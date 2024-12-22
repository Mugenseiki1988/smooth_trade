import os
import shutil
import subprocess
import sys

# === Étape 1 : Désinstallation d'Apache Airflow et nettoyage ===
def uninstall_airflow():
    print("=== Désinstallation d'Apache Airflow et nettoyage ===")
    paths_to_remove = [
        "C:\\Users\\Nicolas JF Martin\\airflow",
        "D:\\Airflow_tutorial",
        "D:\\smooth_trade\\prometheus",
        "D:\\smooth_trade\\grafana",
        "D:\\smooth_trade\\postgres_data"
    ]
    for path in paths_to_remove:
        if os.path.exists(path):
            print(f"Suppression du dossier : {path}")
            shutil.rmtree(path, ignore_errors=True)
        else:
            print(f"Dossier introuvable : {path}")
    
    # Désinstaller les paquets Python liés à Airflow (si nécessaire)
    print("Suppression des paquets Python liés à Apache Airflow...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "apache-airflow"], check=False)

    print("=== Désinstallation terminée ===")

# === Étape 2 : Préparer la structure des répertoires ===
def prepare_directories():
    print("=== Préparation des répertoires pour le projet ===")
    base_directory = "D:/smooth_trade"
    folders_to_create = [
        "dags",
        "scripts",
        "config",
        "data/logs",
        "data/trades",
        "exports",
        "prometheus",
        "grafana",
        "postgres_data"
    ]
    for folder in folders_to_create:
        path = os.path.join(base_directory, folder)
        os.makedirs(path, exist_ok=True)
        print(f"Créé : {path}")
    print("=== Répertoires préparés avec succès ===")

# === Étape 3 : Configuration initiale des services ===
def initialize_prometheus_grafana():
    print("=== Initialisation des fichiers de configuration pour Prometheus et Grafana ===")
    
    prometheus_config = """
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'docker'
    static_configs:
      - targets: ['host.docker.internal:9323'] # Prometheus Docker endpoint
    metrics_path: /metrics
"""
    grafana_provisioning = """
apiVersion: 1
providers:
  - name: "Prometheus"
    orgId: 1
    folder: ""
    type: "prometheus"
    url: "http://prometheus:9090"
    access: "proxy"
    isDefault: true
"""
    base_directory = "D:/smooth_trade"
    prometheus_config_path = os.path.join(base_directory, "prometheus", "prometheus.yml")
    grafana_config_path = os.path.join(base_directory, "grafana", "datasource.yml")

    # Créer le fichier prometheus.yml
    with open(prometheus_config_path, "w") as prometheus_file:
        prometheus_file.write(prometheus_config)
    print(f"Fichier Prometheus créé : {prometheus_config_path}")

    # Créer le fichier datasource.yml pour Grafana
    with open(grafana_config_path, "w") as grafana_file:
        grafana_file.write(grafana_provisioning)
    print(f"Fichier Grafana provisioning créé : {grafana_config_path}")

# Exécution des étapes
if __name__ == "__main__":
    uninstall_airflow()
    prepare_directories()
    initialize_prometheus_grafana()