import os
import subprocess
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
# - Volumes : Un volume nommé mssql-data est utilisé pour stocker de manière persistante les données SQL Server,
#   même si le conteneur est redémarré ou recréé.

# Contenu du fichier docker-compose.yaml
DOCKER_COMPOSE_YAML_CONTENT = """
version: '3.7'
services:
  mssql:
    image: mcr.microsoft.com/mssql/server:2019-latest
    environment:
      ACCEPT_EULA: "Y"
      SA_PASSWORD: "Mugenseiki1988#"
      MSSQL_MEMORY_LIMIT_MB: 2048
      MSSQL_PID: "Express"
    ports:
      - "1433:1433"
    healthcheck:
      test: ["CMD-SHELL", "/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P Mugenseiki1988# -Q 'SELECT 1'"]
      interval: 10s
      retries: 5
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
sql_alchemy_conn = mssql+pyodbc://airflow_user:AirflowUserPassword#123@localhost/airflow_db?driver=ODBC+Driver+17+for+SQL+Server
load_examples = True

[celery]
broker_url = redis://:@redis:6379/0
result_backend = db+mssql+pyodbc://airflow_user:AirflowUserPassword#123@localhost/airflow_db?driver=ODBC+Driver+17+for+SQL+Server
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
            if container_id:
                print(f"Suppression du conteneur : {container_id}")
                subprocess.run(["docker", "rm", "-f", container_id], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la suppression des conteneurs inutiles : {e.stderr}")

# Configurer SQL Server et la base de données
def configure_sql_server_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=master;"
        "UID=sa;"
        "PWD=Mugenseiki1988#;"
    )
    try:
        print("Tentative de configuration initiale de SQL Server...")
        connection = pyodbc.connect(conn_str)
        print("Connexion au serveur réussie avec succès !")

        cursor = connection.cursor()

        database_name = "airflow_db"
        user_name = "airflow_user"
        user_password = "AirflowUserPassword#123"

        # Créer la base de données et l'utilisateur si nécessaire
        cursor.execute(f"""
        IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{database_name}') CREATE DATABASE {database_name};
        IF NOT EXISTS (SELECT name FROM sys.sql_logins WHERE name = '{user_name}')
        BEGIN
            CREATE LOGIN {user_name} WITH PASSWORD = '{user_password}';
        END;
        USE {database_name};
        IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = '{user_name}')
        BEGIN
            CREATE USER {user_name} FOR LOGIN {user_name};
        END;
        ALTER ROLE db_owner ADD MEMBER {user_name};
        """)

        print(f"Base de données '{database_name}' et utilisateur '{user_name}' configurés avec succès.")

        connection.commit()
        connection.close()
        print("Configuration de la connexion terminée.")

    except pyodbc.Error as e:
        print(f"Erreur lors de la configuration de SQL Server : {e}")

# Vérifier la connexion à SQL Server
def test_sql_server_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=airflow_db;"
        "UID=airflow_user;"
        "PWD=AirflowUserPassword#123;"
    )
    try:
        print("Tentative de connexion au serveur SQL Server...")
        connection = pyodbc.connect(conn_str)
        print("Connexion réussie !")

        cursor = connection.cursor()
        cursor.execute("SELECT @@VERSION;")

        for row in cursor.fetchall():
            print(f"Version SQL Server: {row[0]}")

        connection.close()
    except pyodbc.Error as e:
        print(f"Erreur lors de la connexion : {e}")

# Fonction principale
def diagnose_and_fix():
    airflow_home = "D:/Airflow_tutorial"
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
    configure_sql_server_connection()
    test_sql_server_connection()

if __name__ == "__main__":
    diagnose_and_fix()
