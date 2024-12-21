import os
import shutil

# Répertoires source et destination
source_directory = "D:/smooth_trade/"
destination_directory = "D:/Airflow/pipeline/"
github_url = "https://github.com/Mugenseiki1988/smooth_trade.git"

# Fonction pour créer les répertoires
def create_pipeline_structure():
    print("=== Création de la structure des workflows ===")
    folders_to_create = [
        "workflows/workflow_1",
        "workflows/workflow_2",
        "workflows/workflow_3",
        "workflows/workflow_4",
        "workflows/workflow_5",
        "workflows/workflow_6",
        "workflows/workflow_7",
        "config",
        "logs",
        "exports",
        "data"
    ]

    for folder in folders_to_create:
        folder_path = os.path.join(destination_directory, folder)
        os.makedirs(folder_path, exist_ok=True)
        print(f"Créé : {folder_path}")
    print("=== Structure des workflows créée avec succès ===")

# Fonction pour copier les fichiers dans les workflows
def copy_pipeline_files():
    print("=== Copie des fichiers dans les workflows ===")

    # Fichiers des scripts pour chaque workflow
    workflows_scripts = {
        "workflows/workflow_1": ["arbitrage_loops.py", "arbitrage_execution.py"],
        "workflows/workflow_2": ["inactive_loops_management.py"],
        "workflows/workflow_3": ["export_vers_MySQL.py"],
        "workflows/workflow_4": ["gpu_monitor.py", "digital_ocean_monitor.py"],
        "workflows/workflow_5": ["metrics_report.py"],
        "workflows/workflow_6": ["performance_metrics.py"],
        "workflows/workflow_7": ["tax_report_generation.py"]
    }

    for workflow, scripts in workflows_scripts.items():
        for script in scripts:
            src = os.path.join(source_directory, "scripts", script)
            dst = os.path.join(destination_directory, workflow, script)
            if os.path.exists(src):
                shutil.copy(src, dst)
                print(f"Copié : {src} -> {dst}")
            else:
                print(f"Fichier manquant : {src}")

    # Copier les fichiers de configuration
    config_files = ["config.yaml", "grafana_dashboard.json", "prometheus.yaml"]
    for config_file in config_files:
        src = os.path.join(source_directory, "config", config_file)
        dst = os.path.join(destination_directory, "config", config_file)
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f"Copié : {src} -> {dst}")
        else:
            print(f"Fichier manquant : {src}")

    # Copier les fichiers JSON
    json_files = ["execution_results.json", "metrics.json", "pairs_data.json", "trade_data.json"]
    for json_file in json_files:
        src = os.path.join(source_directory, "AUTRE", json_file)
        dst = os.path.join(destination_directory, "data", json_file)
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f"Copié : {src} -> {dst}")
        else:
            print(f"Fichier manquant : {src}")

    print("=== Copie des fichiers terminée ===")

# Exécution
if __name__ == "__main__":
    create_pipeline_structure()
    copy_pipeline_files()