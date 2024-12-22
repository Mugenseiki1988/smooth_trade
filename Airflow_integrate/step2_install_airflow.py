import os
import subprocess

# === Étape 2 : Installer Apache Airflow avec Docker ===
def install_airflow_with_docker():
    print("=== Installation d'Apache Airflow avec PostgreSQL, Prometheus et Grafana ===")
    airflow_home = "D:/smooth_trade"

    # Vérifier Docker
    try:
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.DEVNULL)
        print("Docker est installé.")
    except FileNotFoundError:
        print("Docker n'est pas installé. Veuillez l'installer avant de continuer.")
        return

    # Répertoires nécessaires
    directories = [
        "dags", "scripts", "config", "data/logs", "data/trades",
        "exports", "prometheus", "grafana/datasources", "grafana/dashboards", 
        "postgres_data", "airflow", "grafana", "prometheus", "postgres"
    ]
    for directory in directories:
        path = os.path.join(airflow_home, directory)
        os.makedirs(path, exist_ok=True)

    # Créer les fichiers nécessaires
    files = {
        "prometheus/prometheus.yml": """
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
""",
        "grafana/datasources/datasource.yml": """
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
""",
        "grafana/dashboards/example_dashboard.json": """
{
  "dashboard": {
    "id": null,
    "uid": "example-dashboard",
    "title": "Example Dashboard",
    "panels": [],
    "version": 1
  }
}
""",
        "postgres/init.sql": """
CREATE TABLE IF NOT EXISTS airflow_metadata (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    value TEXT
);
"""
    }

    for file_path, content in files.items():
        full_path = os.path.join(airflow_home, file_path)
        if not os.path.exists(full_path):
            with open(full_path, "w") as file:
                file.write(content.strip())
            print(f"Fichier créé : {full_path}")

    # Créer les Dockerfiles
    dockerfiles = {
        "airflow/Dockerfile": """
FROM apache/airflow:2.10.4
RUN pip install psycopg2-binary pandas prometheus_client
COPY ./dags /opt/airflow/dags
COPY ./plugins /opt/airflow/plugins
USER root
RUN chmod -R 755 /opt/airflow/dags /opt/airflow/plugins
USER airflow
""",
        "prometheus/Dockerfile": """
FROM prom/prometheus:latest
COPY prometheus.yml /etc/prometheus/prometheus.yml
""",
        "grafana/Dockerfile": """
FROM grafana/grafana:latest
COPY ./datasources /etc/grafana/provisioning/datasources
COPY ./dashboards /etc/grafana/provisioning/dashboards
""",
        "postgres/Dockerfile": """
FROM postgres:15
COPY ./init.sql /docker-entrypoint-initdb.d/
"""
    }

    for dockerfile_path, content in dockerfiles.items():
        full_path = os.path.join(airflow_home, dockerfile_path)
        with open(full_path, "w") as dockerfile:
            dockerfile.write(content.strip())
        print(f"Dockerfile créé : {full_path}")

    # Docker Compose
    docker_compose_content = """
version: '3.7'

services:
  postgres:
    build:
      context: ./postgres
    ports:
      - "5432:5432"

  prometheus:
    build:
      context: ./prometheus
    ports:
      - "9090:9090"

  grafana:
    build:
      context: ./grafana
    ports:
      - "3000:3000"

  redis:
    image: redis:7.2-bookworm
    ports:
      - "6379:6379"

  airflow-webserver:
    build:
      context: ./airflow
    ports:
      - "8080:8080"

  airflow-scheduler:
    build:
      context: ./airflow
    command: scheduler
"""
    docker_compose_path = os.path.join(airflow_home, "docker-compose.yml")
    with open(docker_compose_path, "w") as file:
        file.write(docker_compose_content.strip())
    print(f"Fichier docker-compose.yml créé à l'emplacement {docker_compose_path}")

    # Démarrage Docker Compose
    print("Démarrage des services Docker Compose...")
    subprocess.run(["docker-compose", "up", "-d"], cwd=airflow_home, check=True)

    print("=== Installation terminée ===")
    print("Airflow : http://localhost:8080")
    print("Prometheus : http://localhost:9090")
    print("Grafana : http://localhost:3000")

if __name__ == "__main__":
    install_airflow_with_docker()