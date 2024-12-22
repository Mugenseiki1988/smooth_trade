import time
import sqlite3
import pyodbc
from helpers import log_info, log_error, connect_db, connect_sql_server  # Fonctions centralisées dans helpers.py

DB_PATH = "/data/tradeV3.sqlite"
EXPORT_INTERVAL = 1800  # Intervalle d'exportation en secondes (30 minutes)

# Fonction pour exporter les données de SQLite vers SQL Server
def export_to_sql_server():
    try:
        # Connexion à la base SQLite
        sqlite_conn = connect_db(DB_PATH)
        sqlite_cursor = sqlite_conn.cursor()

        # Connexion à SQL Server
        conn = connect_sql_server()
        cursor = conn.cursor()

        # Supprimer la table existante avant de recréer
        drop_table_query = """
        IF OBJECT_ID('export_vers_MySQL_trades_Binance', 'U') IS NOT NULL
        DROP TABLE export_vers_MySQL_trades_Binance
        """
        cursor.execute(drop_table_query)
        conn.commit()
        log_info("Table SQL Server 'export_vers_MySQL_trades_Binance' supprimée si elle existait.")

        # Création de la table SQL Server
        create_table_query = """
        CREATE TABLE export_vers_MySQL_trades_Binance (
            id INT IDENTITY(1,1) PRIMARY KEY,
            execution_id VARCHAR(50),
            loop_id VARCHAR(50),
            pair_sequence TEXT,
            execution_prices TEXT,
            quantities TEXT,
            initial_investment FLOAT,
            final_return FLOAT,
            net_profit FLOAT,
            instance_id VARCHAR(50),
            side VARCHAR(10),
            exchange VARCHAR(50),
            pair VARCHAR(50),
            base_currency VARCHAR(50),
            stake_currency VARCHAR(50),
            is_open TINYINT,
            fee_open FLOAT,
            fee_open_cost FLOAT,
            fee_open_currency VARCHAR(10),
            fee_close FLOAT,
            fee_close_cost FLOAT,
            fee_close_currency VARCHAR(10),
            open_rate FLOAT,
            open_trade_value FLOAT,
            close_rate FLOAT,
            realized_profit FLOAT,
            close_profit FLOAT,
            close_profit_abs FLOAT,
            stake_amount FLOAT,
            amount FLOAT,
            open_date DATETIME,
            close_date DATETIME,
            stop_loss FLOAT,
            exit_reason VARCHAR(50),
            strategy VARCHAR(50),
            timeframe INT,
            trading_mode VARCHAR(10),
            amount_precision FLOAT,
            price_precision FLOAT,
            final_balance FLOAT,
            timestamp DATETIME DEFAULT GETDATE()
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        log_info("Table SQL Server 'export_vers_MySQL_trades_Binance' créée avec succès.")

        # Récupérer les données de SQLite
        sqlite_cursor.execute("SELECT * FROM trades")
        rows = sqlite_cursor.fetchall()
        columns = [desc[0] for desc in sqlite_cursor.description]

        # Préparation de l'insertion dans SQL Server
        insert_query = f"""
        INSERT INTO export_vers_MySQL_trades_Binance ({', '.join(columns)})
        VALUES ({', '.join(['?'] * len(columns))})
        """

        # Insertion des données dans SQL Server
        for row in rows:
            cursor.execute(insert_query, row)
        conn.commit()
        log_info(f"{len(rows)} lignes exportées de SQLite vers SQL Server avec succès.")

        # Fermer les connexions
        sqlite_cursor.close()
        sqlite_conn.close()
        cursor.close()
        conn.close()
        log_info("Connexions SQLite et SQL Server fermées.")
    except Exception as e:
        log_error(f"Erreur lors de l'exportation des données vers SQL Server : {e}")

# Fonction principale pour exécuter l'export toutes les 30 minutes
def main():
    log_info("Démarrage de l'export périodique des données vers SQL Server.")
    while True:
        try:
            export_to_sql_server()
            log_info(f"Prochain export programmé dans {EXPORT_INTERVAL / 60} minutes.")
        except Exception as e:
            log_error(f"Erreur inattendue dans le processus d'exportation : {e}")
        time.sleep(EXPORT_INTERVAL)

if __name__ == "__main__":
    main()