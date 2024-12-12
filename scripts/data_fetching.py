import requests
import websocket
import yaml
import json
import time
import hmac
import hashlib
from helpers import log_info, log_error, generate_signature, process_websocket_message

# Charger la configuration depuis config.yml
with open("/config/config.yml", "r") as config_file:
    config = yaml.safe_load(config_file)["settings"]

API_KEYS = config["api_keys"]  # Liste des 29 clés API
SECRET_KEYS = config["secret_keys"]  # Liste des 29 clés secrètes correspondantes
VOLUME_THRESHOLD = config["pair_validation_criteria"]["min_volume"]
MIN_DAYS_LISTED = config["pair_validation_criteria"]["min_days_active"]
WEB_SOCKET_URLS = [config[f"ws{i}_url"] for i in range(1, 21)]  # Charger les 20 WebSocket URLs

# Connexion à l'API Binance pour récupérer les paires actives
def get_active_pairs(api_key, secret_key):
    url = "https://api.binance.com/api/v3/exchangeInfo"
    headers = {"X-MBX-APIKEY": api_key}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        pairs = [symbol["symbol"] for symbol in data["symbols"] if symbol["status"] == "TRADING"]
        log_info(f"Paires actives récupérées : {len(pairs)}")
        return pairs
    else:
        log_error("Erreur lors de la récupération des paires actives")
        return []

# Récupérer le carnet d'ordres d'une paire spécifique
def get_order_book(symbol, api_key, secret_key, limit=5):
    url = f"https://api.binance.com/api/v3/depth"
    params = {"symbol": symbol, "limit": limit}
    headers = {"X-MBX-APIKEY": api_key}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        log_error(f"Erreur lors de la récupération du carnet d'ordres pour {symbol}")
        return None

# Filtrer les paires actives selon les critères de volume et de durée
def filter_active_pairs(pairs, api_key, secret_key):
    filtered_pairs = []
    for pair in pairs:
        if pair_meets_criteria(pair, api_key, secret_key):
            filtered_pairs.append(pair)
    log_info(f"Paires filtrées : {len(filtered_pairs)} sur {len(pairs)}")
    return filtered_pairs

# Vérifier si une paire répond aux critères de volume et de durée
def pair_meets_criteria(pair, api_key, secret_key):
    order_book = get_order_book(pair, api_key, secret_key)
    if order_book:
        volume = float(order_book.get("volume", 0))
        days_listed = int(order_book.get("days_listed", 0))  # Ajuster si ce champ est disponible
        return volume >= VOLUME_THRESHOLD and days_listed >= MIN_DAYS_LISTED
    return False

# Ouverture de connexions WebSocket pour les mises à jour en temps réel
def open_websocket_connections():
    websockets = []
    for url in WEB_SOCKET_URLS:
        ws = websocket.WebSocketApp(
            url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        websockets.append(ws)
    for ws in websockets:
        ws.run_forever()

# Gestion des messages WebSocket
def on_message(ws, message):
    data = json.loads(message)
    process_websocket_message(data)  # Délégation de la logique au helpers.py

def on_error(ws, error):
    log_error(f"Erreur WebSocket : {error}")

def on_close(ws):
    log_info("Connexion WebSocket fermée")

# Exécution principale du script
if __name__ == "__main__":
    try:
        log_info("Démarrage du script de récupération des données")
        
        # Utilisation d'une des clés API pour récupérer les paires actives
        pairs = get_active_pairs(API_KEYS[0], SECRET_KEYS[0])
        
        # Filtrage des paires
        filtered_pairs = filter_active_pairs(pairs, API_KEYS[0], SECRET_KEYS[0])
        
        # Ouverture des connexions WebSocket pour les paires filtrées
        open_websocket_connections()
    except Exception as e:
        log_error(f"Erreur inattendue : {e}")