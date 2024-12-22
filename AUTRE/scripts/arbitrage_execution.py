import requests
import hmac
import hashlib
import yaml
import time
import json
import random
import websocket
import sqlite3
import os
from datetime import datetime
from threading import Thread
from helpers import initialize_database, save_to_database, generate_signature
from helpers import log_info, log_error, update_metrics  # Centralisé dans helpers.py

DB_PATH = "/data/tradeV3.sqlite"

# Charger la configuration
with open("/config/config.yml", "r") as config_file:
    config = yaml.safe_load(config_file)["settings"]

API_KEYS = config["api_keys"]
SECRET_KEYS = config["secret_keys"]
BASE_URL = "https://api.binance.com"
WEB_SOCKET_URLS = [config[f"ws{i}_url"] for i in range(1, 21)]

order_book_cache = {}

# Gestion des messages WebSocket
def on_message(ws, message):
    data = json.loads(message)
    symbol = data.get("s")
    if symbol:
        order_book_cache[symbol] = data

def on_error(ws, error):
    log_error(f"Erreur WebSocket : {error}")

def on_close(ws):
    log_info("Connexion WebSocket fermée")

# Connexion WebSocket pour chaque paire active
def open_websocket_connections(symbols):
    def start_ws(symbol):
        url = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@depth5"
        ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.run_forever()

    threads = [Thread(target=start_ws, args=(symbol,)) for symbol in symbols]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

# Placer un ordre sur Binance
def place_order(symbol, side, quantity, api_key, secret_key, order_type="MARKET", price=None):
    url = f"{BASE_URL}/api/v3/order"
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
        "timestamp": timestamp,
    }

    if order_type == "LIMIT" and price:
        params["price"] = price
        params["timeInForce"] = "GTC"

    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    signature = generate_signature(query_string, secret_key)
    params["signature"] = signature

    headers = {"X-MBX-APIKEY": api_key}
    response = requests.post(url, headers=headers, params=params)
    if response.status_code == 200:
        log_info(f"Ordre {side} exécuté pour {symbol} à {quantity}")
        return response.json()
    else:
        log_error(f"Erreur lors du placement de l'ordre pour {symbol}")
        return None

# Charger les boucles d’arbitrage identifiées
def load_arbitrage_loops():
    with open("/config/config.yml", "r") as config_file:
        config_data = yaml.safe_load(config_file)
        return config_data.get("arbitrage_loops", [])

# Exécuter des transactions pour chaque étape de la boucle
def execute_trade(loop, api_key, secret_key):
    total_profit = 0
    usdt_balance = config["initial_usdt_balance"]
    for trade in loop:
        symbol = trade["symbol"]
        side = trade["side"]
        quantity = trade["quantity"]

        order_book = order_book_cache.get(symbol)
        if order_book:
            price = float(order_book["bids"][0][0]) if side == "BUY" else float(order_book["asks"][0][0])
            profit = (price * quantity * (1 - config["trading_fee"])) - (price * quantity)
            total_profit += profit
            usdt_balance += profit
            log_info(f"Trade exécuté : {symbol} | Profit : {profit} USDT | Balance actuelle : {usdt_balance}")

            # Préparer les données pour la base
            trade_data = {
                "execution_id": f"exec_{random.randint(1, 1000)}",
                "loop_id": f"loop_{random.randint(1, 10)}",
                "pair_sequence": ["BTCUSDT", "ETHBTC", "ETHUSDT"],
                "execution_prices": [random.uniform(40000, 41000), random.uniform(0.065, 0.070), random.uniform(2500, 2600)],
                "quantities": [quantity, random.uniform(0.6, 0.7), random.uniform(25, 26)],
                "initial_investment": 100.0,
                "final_return": total_profit + usdt_balance,
                "net_profit": total_profit,
                "instance_id": f"instance_{random.randint(1, 10)}",
                "side": side,
                "exchange": "binance",
                "pair": symbol,
                "base_currency": "BTC",
                "stake_currency": "USDT",
                "is_open": 0,
                "fee_open": 0.001,
                "fee_open_cost": 0.098,
                "fee_open_currency": "USDT",
                "fee_close": 0.001,
                "fee_close_cost": 0.099,
                "fee_close_currency": "USDT",
                "open_rate": price,
                "open_trade_value": 100,
                "close_rate": price + 0.1,
                "realized_profit": profit,
                "close_profit": profit,
                "close_profit_abs": profit,
                "stake_amount": usdt_balance,
                "amount": quantity,
                "open_date": datetime.utcnow().isoformat() + 'Z',
                "close_date": datetime.utcnow().isoformat() + 'Z',
                "stop_loss": config.get("stop_loss", 0),
                "exit_reason": "roi",
                "strategy": "Triangular_arbitrage",
                "timeframe": config.get("timeframe", 5),
                "trading_mode": "SPOT",
                "amount_precision": 0.01,
                "price_precision": 0.01,
                "final_balance": usdt_balance
            }

            save_to_database(trade_data)  # Enregistrer dans la base
        else:
            log_error(f"Aucun carnet d'ordres pour {symbol} dans le cache")
            continue

    update_metrics(loop, total_profit)  # Mettre à jour les métriques pour Prometheus/Grafana
    return total_profit, usdt_balance

# Fonction principale
if __name__ == "__main__":
    log_info("Démarrage de l'exécution des transactions d'arbitrage...")

    # Initialiser la base de données
    initialize_database()

    # Charger les boucles d'arbitrage
    arbitrage_loops = load_arbitrage_loops()

    # Choisir aléatoirement une clé API parmi les 29 disponibles pour chaque instance
    api_key = random.choice(API_KEYS)
    secret_key = SECRET_KEYS[API_KEYS.index(api_key)]

    # Lancer les WebSockets pour les paires actives
    pairs = [trade["symbol"] for loop in arbitrage_loops for trade in loop]
    unique_pairs = list(set(pairs))
    open_websocket_connections(unique_pairs)

    # Exécution des boucles
    for loop in arbitrage_loops:
        log_info(f"Exécution de la boucle : {loop}")
        profit, balance = execute_trade(loop, api_key, secret_key)
        log_info(f"Profit total de la boucle : {profit} USDT")
        time.sleep(1)
