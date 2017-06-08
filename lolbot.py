#!/usr/bin/env python

"""Discord bot"""

from __future__ import division, print_function

import argparse
import json
import logging
import logging.config
import threading
import time

import requests
import websocket

import config
import plugin_handler

# Global variable for storing the current sequence number received from discord
SEQ_NO = 0

# Global variable for storing the websocket
# Don't access this directly - use socket_send() instead
_WEBSOCKET = None

# Send and recv threads
_RECV_THREAD = None
_SEND_THREAD = None


def heartbeater(sock, interval):
    """Loop forever, sending heartbeats. `interval` is in seconds."""
    while True:
        time.sleep(interval)
        socket_send(sock, {"op": 1, "d": SEQ_NO})

def readloop(sock):
    """Loop over the websocket, waiting for input."""
    global SEQ_NO
    
    try:
        while True:
            # Wait for incoming message
            incoming = sock.recv()
            logging.debug("websocket recv: %s", incoming)
            msg = json.loads(incoming)
            
            # Update heartbeat number
            # TODO: Get upset if we receive messages out of order
            if msg.get("s"):
                SEQ_NO = int(msg.get("s"))
            
            # Pass to plugins
            # Don't pass messages we've generated as this could lead to
            # infinite looping
            if (msg["d"] or {}).get("author", {}).get("id") != config.SELF:
                plugin_handler.handle(msg)
    
    except websocket.WebSocketException as err:
        logging.error("Websocket closed unexpectedly: %s %s", type(err), err)
    finally:
        # Explicitly disconnect when this process terminates
        sock.close()

_SOCK_LOCK = threading.RLock()
def socket_send(sock, msg):
    """Thread-safe handling of socket sends.
    
    `msg` can be a string or a dictionary, but must represent a
    complete Discord API message.
    """
    logging.debug("websocket send: %s", msg)
    if not isinstance(msg, basestring):
        msg = json.dumps(msg)
    with _SOCK_LOCK:
        sock.send(msg)

def websocket_connect():
    """Connect to the websocket, login."""
    global _WEBSOCKET
    # Get the websocket URL from discord
    ws_url = requests.get(config.BASE_URL + "/gateway").json()['url']
    
    # Connect to server
    logging.info("Connecting to websocket server at %s ...", ws_url + config.GATEWAY_VERSION)
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
    logging.debug("websocket recv: %s", temp)
    hbi = int(json.loads(temp)["d"]["heartbeat_interval"]) // 1000  # Round to nearest second
    
    # Set timeout so the websocket won't hang indefinitely
    _WEBSOCKET.settimeout(2*hbi)
    
    # Login
    if not config.BOT_TOKEN:
        logging.error("You haven't provided a valid Discord bot token, please edit config.py")
        raise RuntimeError("You haven't provided a valid Discord bot token, please edit config.py")
    logging.info("Sending login...")
    socket_send(_WEBSOCKET, {
        "op": 2,
        "d": {
            "token": config.BOT_TOKEN,
            "properties": {
                "$os": "linux",
                "$browser": "Disgordian",
                "$device": "Disgordian",
                "$referrer": "",
                "$referring_domain": ""
            },
            "compress": False,
            "large_threshold": 250,
            "shard": [0, 1]
        }})
    
    # Start heartbeater thread
    global _RECV_THREAD, _SEND_THREAD
    _SEND_THREAD = threading.Thread(target=heartbeater, args=[_WEBSOCKET, hbi])
    _SEND_THREAD.setDaemon(True)
    _SEND_THREAD.start()
    
    # Start input thread
    _RECV_THREAD = threading.Thread(target=readloop, args=[_WEBSOCKET])
    _RECV_THREAD.setDaemon(True)
    _RECV_THREAD.start()

def main():
    """Main function - connect to server, start plugins."""
    # Connect to server, login
    websocket_connect()
    
    # Initialise plugins from the "plugins" directory
    plugin_handler.load("plugins")
    
    while True:
        if not _RECV_THREAD.is_alive() or not _SEND_THREAD.is_alive():
            # Threads have died, assume our websocket has died and restart it
            # The old threads were tied to the old socket so will time themselves out
            try:
                _WEBSOCKET.close()
            except:
                pass
            logging.info("Websocket appears to have died, restarting...")
            websocket_connect()
        # Wait a while, since I don't have an input queue yet
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            logging.info("Main loop stopped by SIGINT")
            _WEBSOCKET.close()
            break

def parse_args():
    """Create and run argparse"""
    parser = argparse.ArgumentParser(description="Discord bot")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args()

if __name__ == '__main__':
    ARGS = parse_args()
    
    # Logging init
    logging.config.dictConfig(config.LOGGING_CONFIG)
    if ARGS.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    main()
