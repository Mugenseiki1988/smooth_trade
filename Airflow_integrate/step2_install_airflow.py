import os
import subprocess

# === Étape 2 : Installer Apache Airflow avec Docker et Dockerfiles personnalisés ===
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
        "exports", "prometheus", "grafana", "postgres_data", "airflow", "grafana", "prometheus", "postgres"
    ]
    for directory in directories:
        path = os.path.join(airflow_home, directory)
        os.makedirs(path, exist_ok=True)

    # Créer les Dockerfiles pour chaque service
    dockerfiles = {
        "airflow/Dockerfile": """
FROM apache/airflow:2.10.4

# Installer des bibliothèques supplémentaires
RUN pip install psycopg2-binary pandas prometheus_client

# Copier les DAGs et plugins
COPY ./dags /opt/airflow/dags
COPY ./plugins /opt/airflow/plugins

# Configurer les permissions
USER root
RUN chmod -R 755 /opt/airflow/dags /opt/airflow/plugins
USER airflow
""",
        "prometheus/Dockerfile": """
FROM prom/prometheus:latest

# Copier le fichier de configuration Prometheus
COPY prometheus.yml /etc/prometheus/prometheus.yml
""",
        "grafana/Dockerfile": """
FROM grafana/grafana:latest

# Copier les fichiers de provisioning
COPY ./datasources /etc/grafana/provisioning/datasources
COPY ./dashboards /etc/grafana/provisioning/dashboards
""",
        "postgres/Dockerfile": """
FROM postgres:15

# Copier le script SQL d'initialisation
COPY ./init.sql /docker-entrypoint-initdb.d/
"""
    }

    for dockerfile_path, content in dockerfiles.items():
        full_path = os.path.join(airflow_home, dockerfile_path)
        with open(full_path, "w") as dockerfile:
            dockerfile.write(content.strip())
        print(f"Dockerfile créé : {full_path}")

    # Créer le fichier Docker Compose
    docker_compose_content = """
version: '3.7'

services:
  postgres:
    build:
      context: ./postgres
    ports:
      - "5432:5432"
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
    restart: always

  prometheus:
    build:
      context: ./prometheus
    ports:
      - "9090:9090"
    restart: always

  grafana:
    build:
      context: ./grafana
    ports:
      - "3000:3000"
    restart: always

  redis:
    image: redis:7.2-bookworm
    ports:
      - "6379:6379"
    restart: always

  airflow-webserver:
    build:
      context: ./airflow
    ports:
      - "8080:8080"
    depends_on:
      - postgres
      - redis

  airflow-scheduler:
    build:
      context: ./airflow
    command: scheduler
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  dags:
  logs:
  plugins:
"""

    docker_compose_path = os.path.join(airflow_home, "docker-compose.yml")
    with open(docker_compose_path, "w") as file:
        file.write(docker_compose_content.strip())
    print(f"Fichier docker-compose.yml créé à l'emplacement {docker_compose_path}")

    # Démarrer les services avec Docker Compose
    print("Démarrage des services Docker Compose...")
    subprocess.run(["docker-compose", "up", "-d"], cwd=airflow_home, check=True)

    print("=== Installation terminée ===")
    print("Accédez à Airflow sur http://localhost:8080")
    print("Accédez à Prometheus sur http://localhost:9090")
    print("Accédez à Grafana sur http://localhost:3000")

# Exécution
if __name__ == "__main__":
    install_airflow_with_docker()