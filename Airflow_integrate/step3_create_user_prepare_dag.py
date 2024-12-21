import os
import subprocess

# === Étape 3.1 : Création d’un utilisateur Airflow ===
def create_airflow_user():
    print("=== Création d’un utilisateur Airflow ===")
    airflow_home = "D:/Airflow"
    create_user_command = (
        'docker-compose exec airflow-webserver airflow users create '
        '--username MugenAirflow '
        '--firstname Nicolas '
        '--lastname Martin '
        '--role Admin '
        '--email nicolas.j.f.martin@gmail.com'
    )
    try:
        subprocess.run(create_user_command, shell=True, cwd=airflow_home, check=True)
        print("=== Utilisateur Airflow créé avec succès ===")
    except subprocess.CalledProcessError:
        print("Erreur lors de la création de l'utilisateur.")

# === Étape 3.2 : Création d’un DAG d’exemple ===
def prepare_example_dag():
    print("=== Préparation d’un DAG d’exemple ===")
    dags_path = "D:/Airflow/dags"
    if not os.path.exists(dags_path):
        os.makedirs(dags_path)
    
    example_dag_path = os.path.join(dags_path, "example_dag.py")
    example_dag = """
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Exemple de DAG
with DAG(
    dag_id="example_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:
    task = BashOperator(
        task_id="print_hello",
        bash_command="echo \'Hello, Airflow!\'"
    )
    """
    try:
        with open(example_dag_path, "w") as f:
            f.write(example_dag)
        print(f"DAG d'exemple créé dans {example_dag_path}")
    except Exception as e:
        print(f"Erreur lors de la création du DAG : {e}")

# Exécution des étapes
if __name__ == "__main__":
    create_airflow_user()
    prepare_example_dag()