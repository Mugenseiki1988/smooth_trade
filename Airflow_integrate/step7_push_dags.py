import os
import shutil
import subprocess

# Répertoires source et destination
dags_directory = "D:/Airflow/dags"
github_directory = "D:/smooth_trade/dags"

# Fonction pour copier les DAGs dans le dépôt GitHub
def copy_dags_to_github():
    print("=== Copie des DAGs dans le dépôt GitHub ===")
    if not os.path.exists(github_directory):
        os.makedirs(github_directory)
        print(f"Création du répertoire GitHub pour les DAGs : {github_directory}")

    for dag_file in os.listdir(dags_directory):
        src = os.path.join(dags_directory, dag_file)
        dst = os.path.join(github_directory, dag_file)
        if os.path.isfile(src):
            shutil.copy(src, dst)
            print(f"Copié : {src} -> {dst}")
        else:
            print(f"Fichier introuvable : {src}")
    print("=== Copie des DAGs terminée ===")

# Fonction pour pousser les modifications dans GitHub
def push_dags_to_github():
    print("=== Poussée des DAGs dans le dépôt GitHub ===")
    os.chdir("D:/smooth_trade")
    try:
        subprocess.run(["git", "add", "dags"], check=True)
        subprocess.run(["git", "commit", "-m", "Ajout des DAGs pour le pipeline"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("=== Poussée des DAGs terminée ===")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la poussée des DAGs : {e}")

# Exécution
if __name__ == "__main__":
    copy_dags_to_github()
    push_dags_to_github()