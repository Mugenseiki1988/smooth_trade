import pandas as pd
import requests
from datetime import datetime
from helpers import connect_mysql, load_config
from setup_logging import log_info
from error_logging import log_error
from arbitrage_instance_metrics import update_metrics

# Configuration du fichier pour Prometheus Pushgateway
PROMETHEUS_PUSHGATEWAY_URL = 'http://localhost:9091/metrics/job/metrics_generation'

# Extraction des données de la base MySQL pour les métriques
def fetch_trading_data(conn):
    try:
        query = """
        SELECT 
            symbol,
            price,
            quantity,
            trade_time 
        FROM trades
        """
        log_info("Récupération des données de trading depuis MySQL.")
        df = pd.read_sql(query, conn)
        log_info(f"{len(df)} lignes récupérées pour le calcul des métriques.")
        return df
    except Exception as e:
        log_error(f"Erreur lors de la récupération des données MySQL : {e}")
        return pd.DataFrame()

# Calcul des métriques sur les données
def calculate_metrics(df):
    try:
        log_info("Calcul des métriques en cours...")
        metrics = {
            'total_trades': len(df),
            'average_trade_price': df['price'].mean(),
            'total_quantity': df['quantity'].sum(),
            'max_trade_price': df['price'].max(),
            'min_trade_price': df['price'].min(),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        log_info("Métriques calculées avec succès.")
        update_metrics("metrics_calculated", 1)
        return metrics
    except Exception as e:
        log_error(f"Erreur lors du calcul des métriques : {e}")
        update_metrics("metrics_calculation_errors", 1)
        return {}

# Générer un rapport CSV pour Power BI
def generate_csv_report(metrics, filename='metrics_report.csv'):
    try:
        df = pd.DataFrame([metrics])
        df.to_csv(filename, index=False)
        log_info(f"Rapport CSV généré : {filename}")
        update_metrics("csv_reports_generated", 1)
    except Exception as e:
        log_error(f"Erreur lors de la génération du rapport CSV : {e}")
        update_metrics("csv_report_errors", 1)

# Envoyer les métriques à Grafana/Prometheus
def send_metrics_to_grafana(metrics):
    try:
        log_info("Envoi des métriques à Grafana/Prometheus...")
        metric_lines = [
            f"# HELP total_trades Nombre total de trades.",
            f"# TYPE total_trades gauge",
            f"total_trades {metrics['total_trades']}",
            f"# HELP average_trade_price Prix moyen des trades.",
            f"# TYPE average_trade_price gauge",
            f"average_trade_price {metrics['average_trade_price']}",
            f"# HELP total_quantity Quantité totale échangée.",
            f"# TYPE total_quantity gauge",
            f"total_quantity {metrics['total_quantity']}",
            f"# HELP max_trade_price Prix maximum d'un trade.",
            f"# TYPE max_trade_price gauge",
            f"max_trade_price {metrics['max_trade_price']}",
            f"# HELP min_trade_price Prix minimum d'un trade.",
            f"# TYPE min_trade_price gauge",
            f"min_trade_price {metrics['min_trade_price']}"
        ]
        payload = "\n".join(metric_lines)
        response = requests.post(PROMETHEUS_PUSHGATEWAY_URL, data=payload)
        if response.status_code == 200:
            log_info("Métriques envoyées à Grafana/Prometheus avec succès.")
            update_metrics("prometheus_metrics_sent", 1)
        else:
            log_error(f"Erreur lors de l'envoi des métriques à Grafana/Prometheus : {response.status_code}")
            update_metrics("prometheus_metrics_errors", 1)
    except requests.RequestException as e:
        log_error(f"Erreur de connexion à Prometheus : {e}")
        update_metrics("prometheus_connection_errors", 1)

# Fonction principale
def main():
    try:
        # Charger la configuration
        config = load_config()
        mysql_config = config['mysql']

        # Connexion à MySQL
        conn = connect_mysql(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database']
        )
        if not conn:
            log_error("Connexion à MySQL échouée.")
            return

        # Récupérer et traiter les données
        df = fetch_trading_data(conn)
        if df.empty:
            log_error("Aucune donnée récupérée pour le calcul des métriques.")
            return

        metrics = calculate_metrics(df)

        # Générer un rapport pour Power BI
        generate_csv_report(metrics)

        # Envoyer les métriques à Grafana/Prometheus
        send_metrics_to_grafana(metrics)

        conn.close()
        log_info("Rapport de métriques généré et envoyé avec succès.")
    except Exception as e:
        log_error(f"Erreur inattendue dans metrics_report.py : {e}")

if __name__ == "__main__":
    main()