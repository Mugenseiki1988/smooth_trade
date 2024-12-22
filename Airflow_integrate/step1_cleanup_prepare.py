import os
import shutil
import subprocess
import sys

# === Étape 1 : Désinstallation et nettoyage ===
def uninstall_airflow():
    print("=== Désinstallation d'Apache Airflow, nettoyage des répertoires et des conteneurs Docker ===")
    
    # Répertoires à conserver
    excluded_directories = ["Airflow_integrate", "AUTRE"]

    # Supprimer tous les sous-dossiers sauf exclusions
    base_directory = "D:\\smooth_trade"
    for item in os.listdir(base_directory):
        item_path = os.path.join(base_directory, item)
        if os.path.isdir(item_path) and item not in excluded_directories:
            print(f"Suppression du dossier : {item_path}")
            shutil.rmtree(item_path, ignore_errors=True)
        elif os.path.isfile(item_path):
            print(f"Suppression du fichier : {item_path}")
            os.remove(item_path)
        else:
            print(f"Conservé : {item_path}")

    # Supprimer les conteneurs, volumes et réseaux Docker
    print("Suppression des conteneurs, volumes et réseaux Docker...")
    subprocess.run(["docker-compose", "down", "--volumes", "--remove-orphans"], cwd=base_directory, check=False)
    subprocess.run(["docker", "system", "prune", "-f", "--volumes"], check=False)

    # Supprimer les images Docker associées
    print("Suppression des images Docker associées...")
    images = ["apache/airflow", "postgres", "prom/prometheus", "grafana/grafana", "redis"]
    for image in images:
        subprocess.run(["docker", "rmi", "-f", image], check=False)

    # Désinstaller Airflow de Python si nécessaire
    print("Suppression des paquets Python liés à Apache Airflow...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "apache-airflow"], check=False)

    print("=== Nettoyage complet terminé ===")

# === Étape 2 : Préparer les répertoires ===
def prepare_directories():
    print("=== Préparation des répertoires pour le projet ===")
    base_directory = "D:/smooth_trade"
    folders_to_create = [
        "dags", "scripts", "config", "data/logs", "data/trades",
        "exports", "prometheus", "grafana/datasources", "grafana/dashboards", "postgres_data"
    ]
    for folder in folders_to_create:
        path = os.path.join(base_directory, folder)
        os.makedirs(path, exist_ok=True)
        print(f"Créé : {path}")
    print("=== Répertoires préparés avec succès ===")

# === Étape 3 : Nettoyage et préparation des ports ===
def clean_ports():
    print("=== Nettoyage des ports en cours ===")
    ports = [8080, 5432, 6379, 9090, 3000]
    for port in ports:
        try:
            # Tuer les processus sur les ports (Windows spécifique)
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if f":{port} " in line:
                    pid = line.split()[-1]
                    subprocess.run(["taskkill", "/PID", pid, "/F"], check=False)
                    print(f"Processus sur le port {port} arrêté (PID {pid}).")
        except Exception as e:
            print(f"Erreur lors du nettoyage du port {port} : {e}")
    print("=== Ports nettoyés ===")

if __name__ == "__main__":
    uninstall_airflow()
    prepare_directories()
    clean_ports()