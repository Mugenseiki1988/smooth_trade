import pyodbc

def configure_sql_server_connection():
    # Chaîne de connexion pour configurer la base avec le compte administrateur SQL Server
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
        print("Configuration réussie avec succès !")

        # Créer un curseur pour exécuter des commandes SQL
        cursor = connection.cursor()

        # Créer une base de données (si nécessaire) et configurer un utilisateur SQL
        database_name = "airflow_db"
        user_name = "airflow_user"
        user_password = "AirflowUserPassword#123"
        
        # Créer la base de données si elle n'existe pas
        cursor.execute(f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{database_name}') CREATE DATABASE {database_name};")
        print(f"Base de données '{database_name}' vérifiée ou créée.")

        # Sélectionner la base de données
        cursor.execute(f"USE {database_name};")

        # Créer un utilisateur SQL si nécessaire
        cursor.execute(f"""
        IF NOT EXISTS (SELECT name FROM sys.sql_logins WHERE name = '{user_name}')
        BEGIN
            CREATE LOGIN {user_name} WITH PASSWORD = '{user_password}';
            CREATE USER {user_name} FOR LOGIN {user_name};
            EXEC sp_addrolemember 'db_owner', '{user_name}';
        END
        """)
        print(f"Utilisateur SQL '{user_name}' vérifié ou créé avec succès.")

        # Valider les modifications
        connection.commit()
        connection.close()
        print("Configuration de la connexion terminée.")
    except pyodbc.Error as e:
        print(f"Erreur lors de la configuration de SQL Server : {e}")

def test_sql_server_connection(server, database, username, password):
    # Chaîne de connexion pour tester l'authentification SQL Server
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

        # Créer un curseur pour exécuter des requêtes SQL
        cursor = connection.cursor()
        cursor.execute("SELECT @@VERSION;")
        
        # Afficher la version de SQL Server
        for row in cursor.fetchall():
            print(f"Version SQL Server: {row[0]}")
        
        # Fermer la connexion
        connection.close()
    except pyodbc.Error as e:
        print(f"Erreur lors de la connexion : {e}")

# Étape 1 : Configurer SQL Server
configure_sql_server_connection()

# Étape 2 : Tester la connexion avec les informations configurées
test_sql_server_connection(
    server="localhost",
    database="airflow_db",
    username="airflow_user",
    password="AirflowUserPassword#123"
)