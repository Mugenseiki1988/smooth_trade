import os
import subprocess

# === Étape 2 : Installer Apache Airflow ===
def install_airflow():
    print("=== Installation d'Apache Airflow avec Docker ===")
    airflow_home = "D:/Airflow_tutorial"
    
    # Vérifier Docker
    try:
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.DEVNULL)
        print("Docker est installé.")
    except FileNotFoundError:
        print("Docker n'est pas installé. Veuillez installer Docker avant de continuer.")
        return

    # Créer le répertoire Airflow
    if not os.path.exists(airflow_home):
        os.makedirs(airflow_home)
        print(f"Répertoire créé : {airflow_home}")
    else:
        print(f"Répertoire déjà existant : {airflow_home}")
    
    # Télécharger docker-compose.yaml
    compose_file_url = "https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml"
    compose_file_path = os.path.join(airflow_home, "docker-compose.yaml")
    if not os.path.exists(compose_file_path):
        print("Téléchargement du fichier docker-compose.yaml...")
        subprocess.run(["curl", "-LfO", compose_file_url], cwd=airflow_home, check=True)
    else:
        print("Le fichier docker-compose.yaml existe déjà.")
    
    # Configurer les répertoires et le fichier .env
    dags_path = os.path.join(airflow_home, "dags")
    logs_path = os.path.join(airflow_home, "logs")
    plugins_path = os.path.join(airflow_home, "plugins")
    
    for path in [dags_path, logs_path, plugins_path]:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Répertoire créé : {path}")
    
    env_path = os.path.join(airflow_home, ".env")
    with open(env_path, "w") as env_file:
        env_file.write("AIRFLOW_UID=50000\n")
    print(f"Fichier .env configuré dans : {env_path}")
    
    # Initialiser et démarrer Docker Compose
    print("Initialisation de Docker Compose pour Airflow...")
    subprocess.run(["docker-compose", "up", "airflow-init"], cwd=airflow_home, check=True)
    subprocess.run(["docker-compose", "up", "-d"], cwd=airflow_home, check=True)
    
    print("=== Installation d'Apache Airflow terminée ===")
    print("Accédez à l'interface Web Airflow sur http://localhost:8080")

# Exécution
if __name__ == "__main__":
    install_airflow()