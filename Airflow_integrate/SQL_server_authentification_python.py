import pyodbc
import subprocess

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

        # Vérifier et créer la base de données si elle n'existe pas
        cursor.execute(f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{database_name}') CREATE DATABASE {database_name};")
        print(f"Base de données '{database_name}' vérifiée ou créée.")

        # Vérifier et configurer l'utilisateur SQL
        cursor.execute(f"""
        IF NOT EXISTS (SELECT name FROM sys.sql_logins WHERE name = '{user_name}')
        BEGIN
            CREATE LOGIN {user_name} WITH PASSWORD = '{user_password}';
            CREATE USER {user_name} FOR LOGIN {user_name};
        END
        """)
        print(f"Utilisateur SQL '{user_name}' vérifié ou créé.")

        # Assigner les autorisations nécessaires
        cursor.execute(f"USE {database_name};")
        cursor.execute(f"ALTER ROLE db_owner ADD MEMBER {user_name};")
        print(f"Autorisations configurées pour l'utilisateur '{user_name}'.")

        connection.commit()
        connection.close()
        print("Configuration de la connexion terminée.")

    except pyodbc.Error as e:
        print(f"Erreur lors de la configuration de SQL Server : {e}")


def test_sql_server_connection(server, database, username, password):
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
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
        if "18456" in str(e):
            print("Erreur : Échec de l'authentification. Vérifiez les identifiants.")
        elif "4060" in str(e):
            print("Erreur : Base de données introuvable ou accès refusé.")
        else:
            print(f"Erreur lors de la connexion : {e}")


def launch_ssms(server, username, password):
    try:
        print("Tentative de lancement de SQL Server Management Studio...")
        ssms_path = r"C:\\Program Files (x86)\\Microsoft SQL Server Management Studio 20\\Common7\\IDE\\Ssms.exe"

        command = f'{ssms_path} -S {server} -U {username} -P {password}'

        subprocess.Popen(command, shell=True)
        print("SQL Server Management Studio lancé avec succès.")

    except FileNotFoundError:
        print("Erreur : SSMS n'est pas installé ou le chemin est incorrect.")
    except Exception as e:
        print(f"Erreur lors du lancement de SSMS : {e}")


# Étape 1 : Configurer SQL Server
configure_sql_server_connection()

# Étape 2 : Tester la connexion avec les informations configurées
test_sql_server_connection(
    server="localhost",
    database="airflow_db",
    username="airflow_user",
    password="AirflowUserPassword#123"
)

# Étape 3 : Lancer SQL Server Management Studio
launch_ssms(
    server="localhost",
    username="sa",
    password="Mugenseiki1988#"
)