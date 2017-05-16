#!/usr/bin/env python

"""Discord bot"""

import json
import logging
import logging.config
import threading
import time

import requests
import websocket

import config

# Global variable for storing the current sequence number received from discord
SEQ_NO = 0

# Global variable for storing the websocket
# Don't access this directly - use socket_send() instead
_WEBSOCKET = None

def heartbeater(interval):
    """Loop forever, sending heartbeats."""
    while True:
        time.sleep(interval)
        socket_send({"op": 1, "d": SEQ_NO})

_SOCK_LOCK = threading.RLock()
def socket_send(msg):
    """Thread-safe handling of socket sends.
    
    `msg` can be a string or a dictionary, but must represent a
    complete Discord API message.
    """
    logging.debug("websocket send: %s", msg)
    if isinstance(msg, dict):
        msg = str(msg)
    with _SOCK_LOCK:
        _WEBSOCKET.send(msg)

def websocket_connect():
    """Connect to the websocket, login."""
    global _WEBSOCKET
    # Get the websocket URL from discord
    ws_url = requests.get(config.BASE_URL + "/gateway").json()['url']
    
    # Connect to server
    logging.debug("Connecting to websocket server at %s...", ws_url)
    _WEBSOCKET = websocket.create_connection(
        ws_url + config.GATEWAY_VERSION,
        timeout=config.WS_TIMEOUT,
        origin="https://discordapp.com",
        )
    logging.debug("Connected")
    
    # Get welcome packet, stash heartbeat interval
    temp = _WEBSOCKET.recv()
    if not temp:
        logging.error("No welcome message received from websocket")
        raise RuntimeError("No welcome message received from websocket")
    hbi = int(json.loads(temp)["d"]["heartbeat_interval"]) // 10000   # Round to nearest second
    
    # TOOD: Login
    
    # Start heatbeater thread
    th = threading.Thread(target=heartbeater, args=[hbi])
    th.setDaemon(True)
    th.start()

def main():
    """Main function - connect to server, start plugins."""
    # Logging init
    logging.config.dictConfig(config.LOGGING_CONFIG)
    logging.debug("foo")
    
    # Connect to server
    websocket_connect()
    
    while True:
        try:
            logging.debug("Recv %s", _WEBSOCKET.recv())
        except websocket.WebSocketException:
            logging.debug("No read")
            time.sleep(1)

if __name__ == '__main__':
    main()
