#!/usr/bin/env python

"""Discord bot"""

# TODO: Signal handling

from __future__ import division, print_function

import argparse
import json
import logging
import logging.config
import Queue
import threading
import time

import requests
import websocket

import config
import plugin_handler


def heartbeater(interval, msgqueue):
    """Loop forever, sending heartbeats. `interval` is in seconds."""
    while True:
        time.sleep(interval)
        msgqueue.put("HEARTBEAT")

def readloop(sock, msgqueue):
    """Loop over the websocket, waiting for input."""
    try:
        while True:
            # Wait for incoming message
            incoming = sock.recv()
            logging.debug("websocket recv: %s", incoming)
            msg = json.loads(incoming)
            msgqueue.put(("MSG", msg))
    except Exception as err:
        logging.error("readloop died: %s %s", type(err), err)
        msgqueue.put("WEBSOCKET_ERROR")

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
    # Get the websocket URL from discord
    ws_url = requests.get(config.BASE_URL + "/gateway").json()['url']
    
    # Connect to server
    logging.info("Connecting to websocket server at %s ...", ws_url + config.GATEWAY_VERSION)
    wsock = websocket.create_connection(
        ws_url + config.GATEWAY_VERSION,
        timeout=config.WS_TIMEOUT,
        origin="https://discordapp.com",
        )
    logging.debug("Connected")
    
    # Get welcome packet, stash heartbeat interval
    temp = wsock.recv()
    if not temp:
        logging.error("No welcome message received from websocket")
        raise RuntimeError("No welcome message received from websocket")
    logging.debug("websocket recv: %s", temp)
    hbi = int(json.loads(temp)["d"]["heartbeat_interval"]) // 1000  # Round to nearest second
    
    # Set timeout so the websocket won't hang indefinitely
    wsock.settimeout(2*hbi)
    
    # Login
    if not config.BOT_TOKEN:
        logging.error("You haven't provided a valid Discord bot token, please edit config.py")
        raise RuntimeError("You haven't provided a valid Discord bot token, please edit config.py")
    logging.info("Sending login...")
    socket_send(wsock, {
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
    return wsock, hbi

def main():
    """Replacement for main() """
    # Create queue
    msgqueue = Queue.Queue()
    
    # Initialise plugins from the "plugins" directory
    plugin_handler.load("plugins")
    
    # Connect to websocket. If this fails, give up.
    wsock, hb_int = websocket_connect()
    seq_no = 0
    
    # Start heartbeat loop
    hb_thread = threading.Thread(target=heartbeater, args=[hb_int, msgqueue])
    hb_thread.setDaemon(True)
    hb_thread.start()
    
    # Start thread for receiving from socket
    recv_thread = threading.Thread(target=readloop, args=[wsock, msgqueue])
    recv_thread.setDaemon(True)
    recv_thread.start()
    
    # Wait for messages in queue
    while True:
        msg = msgqueue.get(True)
        if msg[0] == "MSG":
            content = msg[1]
            # Fork off to process
            # Update heartbeat number
            # TODO: Get upset if we receive messages out of order
            if content.get("s"):
                seq_no = int(content.get("s"))
            
            # Pass to plugins
            # Don't pass messages we've generated as this could lead to
            # infinite looping
            if (content["d"] or {}).get("author", {}).get("id") != config.SELF:
                plugin_handler.handle(content)
        
        elif msg == "HEARTBEAT":
            # Send heartbeat
            # We don't care about dropping heartbeats if the socket is down
            try:
                socket_send(wsock, {"op": 1, "d": seq_no})
            except Exception as err:
                logging.info("Failed to send heartbeat: %s %s", type(err), err)
        
        elif msg == "QUIT":
            # Shutdown
            logging.info("Main loop stopping...")
            try:
                wsock.close()
            except:
                pass
        
        elif msg == "WEBSOCKET_ERROR":
            # Try to spawn new websocket
            # Except: put ERROR back to tail of queue, sleep a bit (linear sleep?)
            # An exponentially-growing sleep would delay our response to e.g. signals
            # TODO: This
            pass

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
