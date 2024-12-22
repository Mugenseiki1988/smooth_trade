import yaml
import itertools
from helpers import log_info, log_error, update_metrics  # Répartition vers helpers.py

CONFIG_PATH = "/config/"  # Répertoire où sont stockés les fichiers config.yml individuels pour chaque WebSocket

# Charge les paires depuis le fichier de configuration associé à ce WebSocket
def load_pairs_from_config(ws_id):
    config_path = f"{CONFIG_PATH}/{ws_id}_config.yml"
    try:
        with open(config_path, "r") as config_file:
            config_data = yaml.safe_load(config_file)
            pairs = config_data["settings"]["assigned_pairs"]
            log_info(f"Paires chargées pour {ws_id}: {len(pairs)}")
            return pairs
    except Exception as e:
        log_error(f"Erreur lors du chargement des paires pour {ws_id}: {e}")
        return []

# Identifie les boucles triangulaires d'arbitrage à partir des paires assignées
def find_arbitrage_loops(pairs):
    arbitrage_loops = []
    try:
        for (pair_a, pair_b, pair_c) in itertools.permutations(pairs, 3):
            if pair_a["quote"] == pair_b["base"] and pair_b["quote"] == pair_c["base"] and pair_c["quote"] == pair_a["base"]:
                arbitrage_loops.append((pair_a, pair_b, pair_c))
        log_info(f"Nombre de boucles identifiées : {len(arbitrage_loops)}")
        update_metrics("arbitrage_loops_found", len(arbitrage_loops))  # Mise à jour des métriques
        return arbitrage_loops
    except Exception as e:
        log_error(f"Erreur lors de l'identification des boucles : {e}")
        return []

# Calcule le profit potentiel pour une boucle d'arbitrage
def calculate_profit(loop):
    try:
        pair_a, pair_b, pair_c = loop
        amount = 1  # Montant de base
        amount /= pair_a["price"]
        amount *= pair_b["price"]
        amount *= pair_c["price"]
        profit = amount - 1
        return profit
    except Exception as e:
        log_error(f"Erreur lors du calcul du profit pour la boucle {loop}: {e}")
        return 0

# Enregistre les boucles d’arbitrage rentables dans le fichier de configuration associé au WebSocket
def update_loop_configuration(ws_id, profitable_loops):
    config_path = f"{CONFIG_PATH}/{ws_id}_config.yml"
    try:
        with open(config_path, "r") as config_file:
            config_data = yaml.safe_load(config_file)

        # Mise à jour avec les boucles rentables
        config_data["settings"]["profitable_arbitrage_loops"] = [
            {"pairs": loop, "profit": calculate_profit(loop)} for loop in profitable_loops
        ]

        with open(config_path, "w") as config_file:
            yaml.dump(config_data, config_file, default_flow_style=False)
        log_info(f"Configuration mise à jour pour {ws_id} avec {len(profitable_loops)} boucles rentables.")
        update_metrics("profitable_arbitrage_loops", len(profitable_loops))  # Mise à jour des métriques
    except Exception as e:
        log_error(f"Erreur lors de la mise à jour de la configuration pour {ws_id}: {e}")

# Fonction principale pour charger les paires, identifier les boucles, et enregistrer les boucles rentables
def main(ws_id):
    log_info(f"Traitement des boucles d'arbitrage pour {ws_id}...")
    pairs = load_pairs_from_config(ws_id)
    if not pairs:
        log_info(f"Aucune paire assignée pour {ws_id}.")
        update_metrics("assigned_pairs_count", 0)  # Mise à jour des métriques pour indiquer l'absence de paires
        return

    # Identifier les boucles potentielles et calculer leur profit
    arbitrage_loops = find_arbitrage_loops(pairs)
    profitable_loops = [loop for loop in arbitrage_loops if calculate_profit(loop) > 0]

    # Mettre à jour la configuration avec les boucles rentables
    update_loop_configuration(ws_id, profitable_loops)

if __name__ == "__main__":
    ws_id = "ws_1"  # Exemple d'ID WebSocket, à modifier pour chaque instance
    main(ws_id)