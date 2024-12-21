import subprocess
import os

# Description des conteneurs Docker utilisés dans ce projet :
# - postgres : Conteneur pour la base de données PostgreSQL utilisée par Airflow.
# - redis : Conteneur pour Redis, utilisé comme broker par Airflow pour la gestion des tâches.
# - airflow-webserver : Conteneur pour le serveur web Airflow (interface utilisateur accessible via http://localhost:8080).
# - airflow-scheduler : Conteneur pour le scheduler Airflow, responsable de l'exécution des DAGs programmés.
# - airflow-triggerer (si présent) : Composant gérant les événements dans les DAGs, utilisé dans certaines configurations.
# - airflow-worker (si présent) : Optionnel, pour exécuter les tâches dans une configuration CeleryExecutor.

DOCKER_COMPOSE_YAML_CONTENT = """
version: '3.7'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - ./postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 10s
      retries: 5
      start_period: 5s
    restart: always

  redis:
    image: redis:7.2-bookworm
    expose:
      - 6379
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 30s
      retries: 50
      start_period: 30s
    restart: always

  airflow-webserver:
    image: apache/airflow:2.10.4
    command: webserver
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    volumes:
      - ./config/airflow.cfg:/opt/airflow/airflow.cfg

  airflow-scheduler:
    image: apache/airflow:2.10.4
    command: scheduler
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8974/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy

volumes:
  postgres-db-volume:
"""

def write_docker_compose_yaml(file_path):
    with open(file_path, 'w') as file:
        file.write(DOCKER_COMPOSE_YAML_CONTENT)
    print(f"docker-compose.yaml mis à jour à l'emplacement {file_path}")

def create_airflow_cfg(airflow_home):
    config_path = os.path.join(airflow_home, "config/airflow.cfg")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    airflow_cfg_content = """
[core]
executor = CeleryExecutor
sql_alchemy_conn = postgresql+psycopg2://airflow:airflow@postgres/airflow
load_examples = True

[celery]
broker_url = redis://:@redis:6379/0
result_backend = db+postgresql://airflow:airflow@postgres/airflow
"""
    with open(config_path, 'w') as file:
        file.write(airflow_cfg_content)
    print(f"airflow.cfg créé à l'emplacement {config_path}")

def run_command(command, cwd=None):
    try:
        print(f"\nExécution : {' '.join(command)}")
        result = subprocess.run(command, cwd=cwd, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Erreur : {e.stderr}")

# Détection et suppression des conteneurs inutiles
def remove_unused_containers():
    print("=== Suppression des conteneurs inutiles ===")
    try:
        result = subprocess.run(["docker", "ps", "-a", "--filter", "name=airflow", "--format", "{{.ID}}"],
                                check=True, text=True, capture_output=True)
        container_ids = result.stdout.strip().split("\n")
        for container_id in container_ids:
            print(f"Suppression du conteneur : {container_id}")
            subprocess.run(["docker", "rm", "-f", container_id], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la suppression des conteneurs inutiles : {e.stderr}")

# Analyse des logs avec OpenAI
# (hypothèse : les logs sont collectés dans un fichier ou via une commande)
def analyze_logs_with_openai(log_file):
    try:
        import openai
        print("=== Analyse des logs avec OpenAI ===")
        with open(log_file, 'r') as file:
            logs = file.read()
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Analyse ces logs et identifie les erreurs et solutions potentielles :\n{logs}",
            max_tokens=500
        )
        print(response["choices"][0]["text"].strip())
    except ImportError:
        print("Le module OpenAI n'est pas installé. Installez-le avec 'pip install openai'.")
    except Exception as e:
        print(f"Erreur lors de l'analyse des logs : {e}")

def diagnose_and_fix():
    airflow_home = os.getcwd()
    docker_compose_path = os.path.join(airflow_home, "docker-compose.yaml")

    print("=== Étape 25 : Diagnostic et correction des erreurs d'Airflow ===")

    # Mettre à jour le fichier docker-compose.yaml
    write_docker_compose_yaml(docker_compose_path)

    # Créer le fichier airflow.cfg
    create_airflow_cfg(airflow_home)

    # Suppression des conteneurs inutiles
    remove_unused_containers()

    # Vérification des conteneurs Docker
    run_command(["docker-compose", "up", "-d"], cwd=airflow_home)
    run_command(["docker", "ps"])

    # Vérification des logs et analyse avec OpenAI
    logs_path = os.path.join(airflow_home, "airflow_logs.txt")
    run_command(["docker", "logs", "airflow_tutorial-airflow-webserver-1", "&>", logs_path])
    analyze_logs_with_openai(logs_path)

if __name__ == "__main__":
    diagnose_and_fix()
