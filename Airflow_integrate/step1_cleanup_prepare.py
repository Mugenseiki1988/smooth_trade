import os
import shutil
import subprocess
import sys

# === Étape 1 : Désinstallation d'Apache Airflow ===
def uninstall_airflow():
    print("=== Désinstallation d'Apache Airflow ===")
    paths_to_remove = [
        "C:\\Users\\Nicolas JF Martin\\airflow",
        "D:\\Airflow"
    ]
    for path in paths_to_remove:
        if os.path.exists(path):
            print(f"Suppression du dossier : {path}")
            shutil.rmtree(path, ignore_errors=True)
        else:
            print(f"Dossier introuvable : {path}")
    
    # Désinstaller les paquets Python liés à Airflow
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
        "exports"
    ]
    for folder in folders_to_create:
        path = os.path.join(base_directory, folder)
        os.makedirs(path, exist_ok=True)
        print(f"Créé : {path}")
    print("=== Répertoires préparés avec succès ===")

# Exécution des étapes
if __name__ == "__main__":
    uninstall_airflow()
    prepare_directories()