import subprocess
import os

DOCKER_COMPOSE_YAML_CONTENT = """
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data
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
      - D:/Airflow_tutorial/config/airflow.cfg:/opt/airflow/airflow.cfg

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

def check_docker_containers():
    print("=== Vérification des conteneurs Docker ===")
    run_command(["docker", "ps"])

def check_logs(container_name):
    print(f"=== Vérification des logs du conteneur {container_name} ===")
    run_command(["docker", "logs", container_name])

def check_airflow_cfg_in_container():
    print("=== Vérification de la présence du fichier airflow.cfg dans le conteneur airflow-webserver ===")
    try:
        result = subprocess.run(
            ["docker", "exec", "airflow_tutorial-airflow-webserver-1", "ls", "/opt/airflow/airflow.cfg"],
            check=True, text=True, capture_output=True
        )
        print("Fichier airflow.cfg trouvé dans le conteneur.")
    except subprocess.CalledProcessError:
        print("Fichier airflow.cfg introuvable dans le conteneur airflow-webserver.")
        print("Redémarrage des services avec le bon montage des volumes...")
        restart_services()

def restart_services():
    print("=== Redémarrage des services ===")
    airflow_home = "D:/Airflow_tutorial"
    run_command(["docker-compose", "down"], cwd=airflow_home)
    run_command(["docker-compose", "up", "-d"], cwd=airflow_home)

def reset_postgres_data():
    print("=== Réinitialisation des données PostgreSQL ===")
    airflow_home = "D:/Airflow_tutorial"
    postgres_data_path = os.path.join(airflow_home, "postgres-data")

    # Arrêter les conteneurs Docker
    run_command(["docker-compose", "down"], cwd=airflow_home)

    # Supprimer les données PostgreSQL si elles existent
    if os.path.exists(postgres_data_path):
        print(f"Suppression du répertoire PostgreSQL : {postgres_data_path}")
        subprocess.run(["rm", "-rf", postgres_data_path], check=True)

    # Réinitialiser les migrations de base de données
    run_command(["docker-compose", "run", "airflow-webserver", "airflow", "db", "init"], cwd=airflow_home)
    run_command(["docker-compose", "up", "-d"], cwd=airflow_home)

def reset_airflow_database():
    print("=== Réinitialisation et mise à jour de la base de données Airflow ===")
    run_command(["docker-compose", "exec", "airflow-webserver", "airflow", "db", "reset", "--yes"])
    run_command(["docker-compose", "exec", "airflow-webserver", "airflow", "db", "upgrade"])

def test_localhost_connection():
    print("=== Test de connexion à l'interface Web Airflow ===")
    try:
        result = subprocess.run(["curl", "http://localhost:8080"], check=True, text=True, capture_output=True)
        print("Connexion réussie :")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("La connexion à l'interface Web Airflow a échoué :")
        print(e.stderr)

def diagnose_and_fix():
    airflow_home = "D:/Airflow_tutorial"
    docker_compose_path = os.path.join(airflow_home, "docker-compose.yaml")

    if not os.path.exists(airflow_home):
        print(f"Le répertoire {airflow_home} n'existe pas. Assurez-vous que le chemin est correct.")
        return

    print("=== Étape 25 : Diagnostic et correction des erreurs d'Airflow ===")

    # Mettre à jour le fichier docker-compose.yaml
    write_docker_compose_yaml(docker_compose_path)

    # Créer le fichier airflow.cfg
    create_airflow_cfg(airflow_home)

    # Vérification des conteneurs
    check_docker_containers()

    # Vérification des logs des principaux conteneurs
    check_logs("airflow_tutorial-airflow-webserver-1")
    check_logs("airflow_tutorial-airflow-scheduler-1")
    check_logs("airflow_tutorial-postgres-1")
    check_logs("airflow_tutorial-redis-1")

    # Vérification de airflow.cfg dans le conteneur
    check_airflow_cfg_in_container()

    # Réinitialisation des données PostgreSQL
    reset_postgres_data()

    # Réinitialisation de la base de données Airflow
    reset_airflow_database()

    # Test de la connexion à l'interface Web
    test_localhost_connection()

if __name__ == "__main__":
    diagnose_and_fix()
