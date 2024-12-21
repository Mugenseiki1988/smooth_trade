import os

# === Étape 4 : Génération des DAGs associés au pipeline ===
def generate_dags():
    print("=== Génération des DAGs pour le pipeline ===")
    dags_path = "D:/Airflow/dags"
    if not os.path.exists(dags_path):
        os.makedirs(dags_path)

    # Définition des DAGs et leur contenu
    dags = {
        "dag_arbitrage.py": """
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def workflow_1():
    print("Workflow 1 : Gestion des arbitrages")

with DAG(
    dag_id="dag_arbitrage",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:
    task = PythonOperator(
        task_id="workflow_1_task",
        python_callable=workflow_1
    )
        """,
        "dag_boucles_inactives.py": """
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def workflow_2():
    print("Workflow 2 : Nettoyage des boucles inactives")

with DAG(
    dag_id="dag_boucles_inactives",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:
    task = PythonOperator(
        task_id="workflow_2_task",
        python_callable=workflow_2
    )
        """,
        "dag_export_sql.py": """
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def workflow_3():
    print("Workflow 3 : Export des données vers SQL Server")

with DAG(
    dag_id="dag_export_sql",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:
    task = PythonOperator(
        task_id="workflow_3_task",
        python_callable=workflow_3
    )
        """,
        "dag_surveillance.py": """
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def workflow_4():
    print("Workflow 4 : Surveillance des ressources")

with DAG(
    dag_id="dag_surveillance",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@hourly",
    catchup=False
) as dag:
    task = PythonOperator(
        task_id="workflow_4_task",
        python_callable=workflow_4
    )
        """,
        "dag_metrics_report.py": """
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def workflow_5():
    print("Workflow 5 : Génération des rapports")

with DAG(
    dag_id="dag_metrics_report",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:
    task = PythonOperator(
        task_id="workflow_5_task",
        python_callable=workflow_5
    )
        """,
        "dag_performance_analysis.py": """
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def workflow_6():
    print("Workflow 6 : Analyse des performances")

with DAG(
    dag_id="dag_performance_analysis",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@weekly",
    catchup=False
) as dag:
    task = PythonOperator(
        task_id="workflow_6_task",
        python_callable=workflow_6
    )
        """,
        "dag_tax_report.py": """
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def workflow_7():
    print("Workflow 7 : Génération du rapport fiscal")

with DAG(
    dag_id="dag_tax_report",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@yearly",
    catchup=False
) as dag:
    task = PythonOperator(
        task_id="workflow_7_task",
        python_callable=workflow_7
    )
        """
    }

    # Générer les fichiers de DAGs
    for dag_name, content in dags.items():
        dag_path = os.path.join(dags_path, dag_name)
        with open(dag_path, "w") as dag_file:
            dag_file.write(content)
        print(f"DAG créé : {dag_path}")

    print("=== Génération des DAGs terminée ===")

# Exécution
if __name__ == "__main__":
    generate_dags()