import time
from datetime import datetime
from utils.helpers import connect_db, read_yaml, write_yaml, calculate_duration
from setup_logging import log_info
from error_logging import log_error
from arbitrage_instance_metrics import update_metrics

CONFIG_PATH = "/config/"  # Chemin vers les fichiers de configuration des WebSockets
EXPIRATION_THRESHOLD = 60 * 60  # Durée en secondes pour considérer une boucle comme inactive

# Identifie les boucles d'arbitrage inactives
def identify_inactive_loops():
    inactive_loops = []
    current_time = time.time()

    log_info("Début de la recherche des boucles inactives...")
    for i in range(1, 21):  # Boucles pour chaque WebSocket configuré
        config_file_path = f"{CONFIG_PATH}/ws_{i}_config.yml"
        try:
            config_data = read_yaml(config_file_path)

            loops = config_data.get("settings", {}).get("profitable_arbitrage_loops", [])
            for loop in loops:
                if "timestamp" in loop and (current_time - loop["timestamp"]) > EXPIRATION_THRESHOLD:
                    inactive_loops.append({"ws_id": i, "loop": loop})
        except Exception as e:
            log_error(f"Erreur lors de la lecture du fichier {config_file_path} : {e}")

    log_info(f"{len(inactive_loops)} boucles inactives identifiées.")
    update_metrics("inactive_loops_count", len(inactive_loops))
    return inactive_loops

# Retire les boucles inactives des fichiers de configuration
def remove_inactive_loops_from_config(inactive_loops):
    for loop_info in inactive_loops:
        ws_id = loop_info["ws_id"]
        loop = loop_info["loop"]
        config_file_path = f"{CONFIG_PATH}/ws_{ws_id}_config.yml"
        try:
            config_data = read_yaml(config_file_path)

            # Mise à jour pour exclure les boucles inactives
            loops = config_data["settings"]["profitable_arbitrage_loops"]
            config_data["settings"]["profitable_arbitrage_loops"] = [l for l in loops if l != loop]

            write_yaml(config_file_path, config_data)
            log_info(f"Boucle inactive retirée de la configuration pour WebSocket {ws_id}.")
        except Exception as e:
            log_error(f"Erreur lors de la mise à jour du fichier {config_file_path} : {e}")

# Enregistre la durée d'exécution des boucles dans la base de données pour analyse
def log_execution_duration(loop):
    try:
        conn = connect_db("/data/tradeV3.sqlite")

        start_time = datetime.fromtimestamp(loop["timestamp"])
        end_time = datetime.now()
        duration = calculate_duration(start_time, end_time)

        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO execution_durations (loop_id, start_time, end_time, duration)
            VALUES (?, ?, ?, ?)
            """,
            (str(loop), start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S"), duration),
        )
        conn.commit()
        conn.close()
        log_info(f"Durée d'exécution enregistrée pour la boucle : {loop}")
        update_metrics("execution_duration", duration)
    except Exception as e:
        log_error(f"Erreur lors de l'enregistrement de la durée d'exécution : {e}")

# Fonction principale
def main():
    log_info("Gestion des boucles non actives...")
    inactive_loops = identify_inactive_loops()

    if inactive_loops:
        for loop_info in inactive_loops:
            log_execution_duration(loop_info["loop"])
        remove_inactive_loops_from_config(inactive_loops)
    else:
        log_info("Aucune boucle inactive trouvée.")

if __name__ == "__main__":
    main()