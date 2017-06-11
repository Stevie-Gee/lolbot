#!/usr/bin/env python

"""Discord bot"""

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

def clean_queue(msgqueue):
    """Perform an in-place modification of the given queue, removing
    any message types we don't want in there.
    
    Used to remove heartbeat and reconnection requests if we're already
    in a failure mode.
    """
    badtypes = ("WEBSOCKET_ERROR", "WEBSOCKET_CONNECT", "HEARTBEAT")
    msgs = []
    while True:
        try:
            msgs.append(msgqueue.get(False))
        except Queue.Empty:
            break
    for msg in msgs:
        if msg not in badtypes:
            msgqueue.put(msg)

def heartbeater(msgqueue, myqueue):
    """Loop forever, sending heartbeats. `interval` is in seconds.
    
    If the heartbeat interval needs to be updated (i.e. for a websocket
    reconnect), a message will be pushed to myqueue.
    """
    # Initially, we need to block until someone sends us a heartbeat interval
    # Once we have a heartbeat interval, we don't block on `myqueue` anymore
    startup = True
    
    # Now we can start the main loop
    while True:
        try:
            interval = myqueue.get(startup)
            logging.debug("Updating heartbeat interval to %ss", interval)
            startup = False
        except Queue.Empty:
            pass
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
    # Create queue and prepare to connect
    msgqueue = Queue.Queue()
    msgqueue.put("WEBSOCKET_CONNECT")
    
    # Initialise plugins from the "plugins" directory
    plugin_handler.load("plugins")
    
    # Initialise sequence number to zero.
    # Initialise websocket and heartbeat intervals
    seq_no = 0
    wsock = None
    
    # Start heartbeat loop
    hb_queue = Queue.Queue()
    hb_thread = threading.Thread(target=heartbeater, args=[msgqueue, hb_queue])
    hb_thread.setDaemon(True)
    hb_thread.start()
    
    # Wait for messages in queue
    while True:
        try:
            # We need a timeout on this queue so that signals can
            # interrupt the get() call. The read thread will timeout
            # after 2*hb_int of inactivity, so we don't expect to
            # reach this
            msg = msgqueue.get(True, 9999)
        except Queue.Empty:
            # Expect to never reach here
            msg = "QUEUE_EMPTY"
        except KeyboardInterrupt:
            msg = "QUIT"
        
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
                msgqueue.put("WEBSOCKET_ERROR")
        
        elif msg == "QUIT":
            # Shutdown
            logging.info("Main loop stopping...")
            break
        
        elif msg == "WEBSOCKET_ERROR":
            # Kill the existing websocket
            delay = 10
            logging.warn("Websocket appears to have died. Reconnecting in %ss...", delay)
            # Make sure the old socket is closed first
            wsock.close()
            # Wait a little, then reconnect
            time.sleep(delay)
            clean_queue(msgqueue)
            msgqueue.put("WEBSOCKET_CONNECT")
        
        elif msg == "WEBSOCKET_CONNECT":
            # Purge any heartbeats, connects, or error messages from the
            # queue so we don't double-process
            clean_queue(msgqueue)
            
            # Reconnect to websocket
            try:
                wsock, hb_int = websocket_connect()
                hb_queue.put(hb_int)
            except:
                # Failure!
                msgqueue.put("WEBSOCKET_ERROR")
                logging.warn("Reconnection failed!")
                continue
            # Start new thread for receiving from socket
            recv_thread = threading.Thread(target=readloop, args=[wsock, msgqueue])
            recv_thread.setDaemon(True)
            recv_thread.start()
        
        else:
            logging.error("Unknown message type: %s", msg)
            break
    
    # Explicitly close socket when this function stops
    wsock.close()

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
    
    # Validate config
    if not config.BOT_TOKEN:
        logging.error("You haven't provided a valid Discord bot token, please edit config.py")
        raise RuntimeError("You haven't provided a valid Discord bot token, please edit config.py")
    
    main()
