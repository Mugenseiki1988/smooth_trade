import os
import subprocess
from datetime import datetime, timedelta
import pyodbc

# Description des conteneurs Docker utilisés dans ce projet :
# - mssql : Conteneur pour la base de données SQL Server utilisée par Airflow. 
#   Il stocke les métadonnées d'Airflow et permet le suivi des DAGs, tâches et leurs états. 
#   La configuration inclut l'acceptation de la licence Microsoft et l'utilisation d'un mot de passe sécurisé.
# - redis : Conteneur pour Redis, utilisé comme broker par Airflow pour gérer la distribution des tâches
#   entre le scheduler et les workers dans un environnement CeleryExecutor.
# - airflow-webserver : Conteneur pour le serveur web Airflow. Il fournit l'interface utilisateur accessible 
#   via http://localhost:8080, permettant de visualiser et de gérer les DAGs, les tâches, les journaux et l'état des exécutions.
# - airflow-scheduler : Conteneur pour le scheduler Airflow, responsable de l'orchestration des DAGs 
#   en fonction de leurs horaires planifiés, dépendances et conditions de réussite/échec.
# - Volumes : Un volume nommé `mssql-data` est utilisé pour stocker de manière persistante les données SQL Server,
#   même si le conteneur est redémarré ou recréé.

# Configuration du fichier docker-compose.yaml
DOCKER_COMPOSE_YAML_CONTENT = """
version: '3.7'
services:
  mssql:
    image: mcr.microsoft.com/mssql/server:2019-latest
    environment:
      ACCEPT_EULA: "Y"
      SA_PASSWORD: "StrongP@ssw0rd"
    ports:
      - "1433:1433"
    healthcheck:
      test: ["CMD-SHELL", "sqlcmd -S localhost -U SA -P StrongP@ssw0rd -Q 'SELECT 1'"]
      interval: 10s
      retries: 3
    volumes:
      - ./mssql-data:/var/opt/mssql
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
    depends_on:
      redis:
        condition: service_healthy
      mssql:
        condition: service_healthy
    volumes:
      - ./config/airflow.cfg:/opt/airflow/airflow.cfg
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always

  airflow-scheduler:
    image: apache/airflow:2.10.4
    command: scheduler
    depends_on:
      redis:
        condition: service_healthy
      mssql:
        condition: service_healthy
    restart: always

volumes:
  mssql-data:
"""

# Créer le fichier docker-compose.yaml
def write_docker_compose_yaml(file_path):
    with open(file_path, 'w') as file:
        file.write(DOCKER_COMPOSE_YAML_CONTENT)
    print(f"docker-compose.yaml mis à jour à l'emplacement {file_path}")

# Générer le fichier airflow.cfg
def create_airflow_cfg(airflow_home):
    config_path = os.path.join(airflow_home, "config/airflow.cfg")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    airflow_cfg_content = """
[core]
executor = CeleryExecutor
sql_alchemy_conn = mssql+pyodbc://@localhost/airflow_db?driver=ODBC+Driver+17+for+SQL+Server
load_examples = True

[celery]
broker_url = redis://:@redis:6379/0
result_backend = db+mssql+pyodbc://@localhost/airflow_db?driver=ODBC+Driver+17+for+SQL+Server
"""
    with open(config_path, 'w') as file:
        file.write(airflow_cfg_content)
    print(f"airflow.cfg créé à l'emplacement {config_path}")

# Exécuter une commande shell
def run_command(command, cwd=None):
    try:
        print(f"\nExécution : {' '.join(command)}")
        result = subprocess.run(command, cwd=cwd, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Erreur : {e.stderr}")

# Suppression des conteneurs inutiles
def remove_unused_containers():
    print("=== Suppression des conteneurs inutiles ===")
    try:
        result = subprocess.run(["docker", "ps", "-a", "--filter", "name=airflow", "--format", "{{.ID}}"],
                                check=True, text=True, capture_output=True)
        container_ids = result.stdout.strip().split("\n")
        for container_id in container_ids:
            if container_id:  # Éviter les entrées vides
                print(f"Suppression du conteneur : {container_id}")
                subprocess.run(["docker", "rm", "-f", container_id], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la suppression des conteneurs inutiles : {e.stderr}")

# Connexion à SQL Server
def test_sql_server_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=airflow_db;"
        "Trusted_Connection=yes;"
    )
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Vérification ou création d'une table
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'airflow_test')
        CREATE TABLE airflow_test (
            id INT PRIMARY KEY IDENTITY(1,1),
            task_name NVARCHAR(50),
            executed_at DATETIME
        )
        """)
        conn.commit()

        print("Connexion réussie et table vérifiée.")
    except Exception as e:
        print(f"Erreur lors de la connexion : {e}")
    finally:
        conn.close()

# Fonction principale
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

    # Démarrer les services Docker
    run_command(["docker-compose", "up", "-d"], cwd=airflow_home)

    # Vérifier les conteneurs en cours d'exécution
    run_command(["docker", "ps"])

    # Tester la connexion à SQL Server
    test_sql_server_connection()

if __name__ == "__main__":
    diagnose_and_fix()