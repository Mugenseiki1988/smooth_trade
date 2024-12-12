import os
import shutil
import subprocess

# Répertoires source et destination
source_directory = "D:/smooth_trade/"
destination_directory = "C:/utilisateur/smooth_trade/"
github_url = "https://github.com/Mugenseiki1988/smooth_trade.git"

# Fonction pour confirmer avant de passer à l'étape suivante
def confirm_step(step_name):
    while True:
        user_input = input(f"Confirmez la réussite de l'étape '{step_name}' (y/n/A) : ").strip().lower()
        if user_input == 'y':
            return True
        elif user_input == 'n':
            return False
        elif user_input == 'a':
            print("Annulation de l'exécution.")
            exit(0)

# Étape 1 : Création de la structure des répertoires GitHub
folders_to_create = [
    "dags",
    "scripts",
    "config",
    "data/logs",
    "data/trades",
    "exports"
]

for folder in folders_to_create:
    os.makedirs(os.path.join(destination_directory, folder), exist_ok=True)
print("Structure des répertoires créée avec succès.")
if not confirm_step("Création de la structure des répertoires"):
    exit(0)

# Fonction pour copier un fichier en vérifiant son existence
def safe_copy(src, dst):
    if os.path.exists(src):
        shutil.copy(src, dst)
        print(f"Copié : {src}")
    else:
        print(f"Fichier manquant : {src}")

# Étape 2.1 : Copie des scripts
scripts_to_copy = [
    "config_setup.py",
    "config_setup_2.py",
    "helpers.py",
    "setup_logging.py",
    "error_logging.py",
    "arbitrage_instance_metrics.py",
    "data_fetching.py",
    "dynamic_distribution.py",
    "arbitrage_loops.py",
    "arbitrage_execution.py",
    "inactive_loops_management.py",
    "export_vers_MySQL.py",
    "gpu_monitor.py",
    "digital_ocean_monitor.py",
    "metrics_report.py",
    "performance_metrics.py",
    "tax_report_generation.py"
]

for script in scripts_to_copy:
    safe_copy(
        os.path.join(source_directory, script), 
        os.path.join(destination_directory, "scripts", script)
    )
print("Scripts copiés avec succès.")
if not confirm_step("Copie des scripts"):
    exit(0)

# Étape 2.2 : Copie des fichiers de configuration
config_files_to_copy = [
    "config.yaml",
    "prometheus.yml",
    "grafana_dashboard.json"
]

for config_file in config_files_to_copy:
    safe_copy(
        os.path.join(source_directory, config_file), 
        os.path.join(destination_directory, "config", config_file)
    )
print("Fichiers de configuration copiés avec succès.")
if not confirm_step("Copie des fichiers de configuration"):
    exit(0)

# Étape 2.3 : Copie des fichiers JSON
json_files_to_copy = [
    "execution_results.json",
    "metrics.json",
    "pairs_data.json",
    "trade_data.json"
]

for json_file in json_files_to_copy:
    safe_copy(
        os.path.join(source_directory, json_file), 
        os.path.join(destination_directory, "data", json_file)
    )
print("Fichiers JSON copiés avec succès.")
if not confirm_step("Copie des fichiers JSON"):
    exit(0)

# Étape 2.4 : Copie des documents
documents_to_copy = [
    "LICENSE.txt",
    "README.md",
    "ligne powershell docker compose.txt",
    "liens deploiement et pipeline workflows.xlsx",
    "Projet deploiement smooth_trade.docx"
]

for document in documents_to_copy:
    safe_copy(
        os.path.join(source_directory, document), 
        os.path.join(destination_directory, document)
    )
print("Documents copiés avec succès.")
if not confirm_step("Copie des documents"):
    exit(0)

# Étape 3 : Initialisation du dépôt Git
os.chdir(destination_directory)
subprocess.run(["git", "init"])
subprocess.run(["git", "config", "user.email", "nicolas.j.f.martin@gmail.com"])
subprocess.run(["git", "config", "user.name", "Nicolas Martin"])
subprocess.run(["git", "remote", "add", "origin", github_url])
print("Dépôt Git initialisé avec succès.")
if not confirm_step("Initialisation du dépôt Git"):
    exit(0)

# Étape 4 : Ajout, commit et push des fichiers
subprocess.run(["git", "add", "."])
try:
    subprocess.run(["git", "commit", "-m", "Initial import of smooth_trade project"], check=True)
    subprocess.run(["git", "branch", "-M", "main"])
    subprocess.run(["git", "push", "-u", "origin", "main"])
    print("Fichiers importés et poussés sur le dépôt GitHub avec succès.")
except subprocess.CalledProcessError as e:
    print("Erreur lors du commit ou du push :", e)
if not confirm_step("Push des fichiers sur GitHub"):
    exit(0)
