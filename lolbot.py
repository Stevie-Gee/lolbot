#!/usr/bin/env python

"""Discord bot"""

from __future__ import division, print_function

import json
import logging
import logging.config
import os
import sys
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
    """Loop forever, sending heartbeats. `interval` is in seconds."""
    while True:
        time.sleep(interval)
        socket_send({"op": 1, "d": SEQ_NO})

def load_plugins(directory):
    """
    Load all modules from the given directory, then return an array
    of all the modules with a `process_msg` function.
    """
    plugins = []
    files = os.listdir(directory)
    for fname in files:
        # Recursively load directories
        if os.path.isdir(os.path.join(directory, fname)):
            plugins += load_plugins(os.path.join(directory, fname))
            continue
        # Convert files to python module names
        elif fname.endswith('.py') and not fname.startswith('_'):
            modulename = "%s.%s" % (directory.replace('/', '.'),
                                    fname.rsplit('.py', 1)[0])
        # Find loadable packages too, ignore the root-level plugins dir
        elif fname == '__init__.py' and directory != "plugins":
            modulename = directory.replace('/', '.')
        # Ignore all other files
        else:
            logging.debug("Ignore %s", fname)
            continue
        
        # Import+reload the module
        logging.info("Found module '%s'", modulename)
        try:
            __import__(modulename)
            module = sys.modules[modulename]
            reload(module)
        except Exception as err:
            logging.warn("Failed to load module %s: %s %s", modulename, type(err), err)
            continue
        
        # Stash ones we care about
        if getattr(module, "process_msg", None):
            logging.debug("Loaded plugin %s", module)
            plugins.append(module)
    return plugins

_SOCK_LOCK = threading.RLock()
def socket_send(msg):
    """Thread-safe handling of socket sends.
    
    `msg` can be a string or a dictionary, but must represent a
    complete Discord API message.
    """
    logging.debug("websocket send: %s", msg)
    if not isinstance(msg, basestring):
        msg = json.dumps(msg)
    with _SOCK_LOCK:
        _WEBSOCKET.send(msg)

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
    
    # Login
    if not config.BOT_TOKEN:
        logging.error("You haven't provided a valid Discord bot token, please edit config.py")
        raise RuntimeError("You haven't provided a valid Discord bot token, please edit config.py")
    logging.info("Sending login...")
    socket_send({
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
    th = threading.Thread(target=heartbeater, args=[hbi])
    th.setDaemon(True)
    th.start()

def main():
    """Main function - connect to server, start plugins."""
    global SEQ_NO
    
    # Logging init
    logging.config.dictConfig(config.LOGGING_CONFIG)
    logging.debug("foo")
    
    # Connect to server, login
    websocket_connect()
    
    # Initialise plugins from the "plugins" directory
    plugins = load_plugins("plugins")
    
    # Main read loop
    _WEBSOCKET.timeout = None
    try:
        while True:
            # Wait for incoming message
            incoming = _WEBSOCKET.recv()
            logging.debug("websocket recv: %s", incoming)
            msg = json.loads(incoming)
            
            # Update heartbeat number
            if msg.get("s"):
                SEQ_NO = int(msg.get("s"))
            
            # Pass to plugins
            for plug in plugins:
                th = threading.Thread(target=plug.process_msg, args=[msg])
                th.setDaemon(True)
                th.start()
    
    except websocket.WebSocketException:
        logging.error("Websocket closed unexpectedly: %s %s", type(err), err)
    except Exception as err:
        logging.error("Unexpected error: %s %s", type(err), err)
    finally:
        # Explicitly disconnect when this process terminates
        _WEBSOCKET.close()

if __name__ == '__main__':
    main()
