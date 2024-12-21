import os
import subprocess

# === Étape 5.1 : Synchroniser le dépôt GitHub ===
def sync_github_repo():
    print("=== Synchronisation avec GitHub ===")
    source_directory = "D:/smooth_trade"
    github_url = "https://github.com/Mugenseiki1988/smooth_trade.git"

    # Configurer Git
    subprocess.run(["git", "config", "--global", "user.name", "Nicolas Martin"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "nicolas.j.f.martin@gmail.com"], check=True)

    os.chdir(source_directory)
    if not os.path.exists(os.path.join(source_directory, ".git")):
        print("Initialisation du dépôt Git local...")
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "remote", "add", "origin", github_url], check=True)
    else:
        print("Dépôt Git déjà initialisé. Mise à jour du remote...")
        subprocess.run(["git", "remote", "set-url", "origin", github_url], check=True)

    # Ajouter et pousser les modifications
    print("Ajout et synchronisation des fichiers...")
    subprocess.run(["git", "add", "."], check=True)
    try:
        subprocess.run(["git", "commit", "-m", "Mise à jour des DAGs et des scripts"], check=True)
    except subprocess.CalledProcessError:
        print("Aucun changement détecté, pas de commit effectué.")
    subprocess.run(["git", "branch", "-M", "main"], check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
    print("=== Synchronisation avec GitHub terminée ===")

# === Étape 5.2 : Ouvrir le projet dans Visual Studio Code ===
def open_in_vscode():
    print("=== Ouverture du projet dans Visual Studio Code ===")
    source_directory = "D:/smooth_trade"
    if os.path.exists(source_directory):
        subprocess.run(["code", source_directory], check=True)
        print(f"Projet ouvert dans VSCode : {source_directory}")
    else:
        print(f"Répertoire introuvable : {source_directory}")

# Exécution des étapes
if __name__ == "__main__":
    sync_github_repo()
    open_in_vscode()