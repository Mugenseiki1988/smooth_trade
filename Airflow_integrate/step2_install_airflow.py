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
        print("Docker n'est pas installé. Veuillez installer Docker avant de continuer.")
        return

    # Créer les répertoires nécessaires
    directories = [
        "dags", "scripts", "config", "data/logs", "data/trades",
        "exports", "prometheus", "grafana", "postgres_data"
    ]
    for directory in directories:
        path = os.path.join(airflow_home, directory)
        os.makedirs(path, exist_ok=True)

    # Créer le fichier Docker Compose
    docker_compose_content = """
version: '3.7'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    ports:
      - "5432:5432"
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
    restart: always

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus:/etc/prometheus
    command:
      - --config.file=/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    restart: always

  grafana:
    image: grafana/grafana:latest
    volumes:
      - ./grafana:/etc/grafana/provisioning/datasources
    ports:
      - "3000:3000"
    restart: always

  redis:
    image: redis:7.2-bookworm
    ports:
      - "6379:6379"
    restart: always

  airflow-webserver:
    image: apache/airflow:2.10.4
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
      AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    ports:
      - "8080:8080"
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    restart: always

  airflow-scheduler:
    image: apache/airflow:2.10.4
    command: scheduler
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
      AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    restart: always

volumes:
  postgres_data:
  prometheus:
  grafana:
  dags:
  logs:
  plugins:
"""

    docker_compose_path = os.path.join(airflow_home, "docker-compose.yml")
    with open(docker_compose_path, "w") as file:
        file.write(docker_compose_content)
    print(f"Fichier docker-compose.yml créé à l'emplacement {docker_compose_path}")

    # Initialiser les services avec Docker Compose
    print("Initialisation de Docker Compose pour Airflow, PostgreSQL, Prometheus et Grafana...")
    subprocess.run(["docker-compose", "up", "airflow-init"], cwd=airflow_home, check=True)
    subprocess.run(["docker-compose", "up", "-d"], cwd=airflow_home, check=True)

    print("=== Installation terminée ===")
    print("Accédez à Airflow sur http://localhost:8080")
    print("Accédez à Prometheus sur http://localhost:9090")
    print("Accédez à Grafana sur http://localhost:3000")

# Exécution
if __name__ == "__main__":
    install_airflow_with_docker()