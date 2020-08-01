#!/usr/bin/env python

"""Discord bot"""

from __future__ import division, print_function

import argparse
from collections import namedtuple
import json
import logging
import logging.config
import Queue
import signal
import threading
import time

import requests
import websocket

import config
import plugin_handler

# Global event queue, handled by main() loop
MSGQUEUE = Queue.Queue()

# Handle signals gracefully
def sig_handler(signum, frame):
    MSGQUEUE.put("QUIT")
signal.signal(signal.SIGINT, sig_handler)

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

def heartbeater(myqueue):
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
        MSGQUEUE.put("HEARTBEAT")

def readloop(sock):
    """Loop over the websocket, waiting for input."""
    try:
        while True:
            # Wait for incoming message
            incoming = sock.recv()
            logging.debug("websocket recv: %s", incoming)
            msg = json.loads(incoming)
            MSGQUEUE.put(("MSG", msg))
    except Exception as err:
        logging.error("readloop died: %s %s", type(err), err)
        MSGQUEUE.put("WEBSOCKET_ERROR")

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

def websocket_connect(session):
    """Connect to the websocket, login."""
    # Get the websocket URL from discord
    ws_url = requests.get(config.BASE_URL + "/gateway").json()['url']
    
    # Connect to server
    logging.info("Connecting to websocket server at %s ...", ws_url + config.GATEWAY_VERSION)
    wsock = websocket.create_connection(
        ws_url + config.GATEWAY_VERSION,
        timeout=config.WS_TIMEOUT,
        origin="https://discord.com",
        sslopt={'ca_certs':requests.utils.DEFAULT_CA_BUNDLE_PATH},
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
    if session.get("session_id"):
        logging.info("Resuming session...")
        socket_send(wsock, {
            "op": 6,
            "d": {
                "token": config.BOT_TOKEN,
                "session_id": session["session_id"],
                "seq": session["seq"],
            }})
    else:
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
    MSGQUEUE.put("WEBSOCKET_CONNECT")
    
    # Initialise plugins from the "plugins" directory
    plugin_handler.load("plugins")
    
    # Initialise sequence number to zero.
    session = {"seq": 0, "session_id": ""}
    
    # Add a placeholder websocket object with a close() method, so
    # WEBSOCKET_ERROR doesn't crash if our first connection fails
    wsock = namedtuple("WebSocket", "close")(close=lambda: None)
    
    # Start heartbeat loop
    hb_queue = Queue.Queue()
    hb_thread = threading.Thread(target=heartbeater, args=[hb_queue])
    hb_thread.setDaemon(True)
    hb_thread.start()
    
    # Wait for messages in queue
    while True:
        try:
            # We need a timeout on this queue so that signals can
            # interrupt the get() call. The read thread will timeout
            # after 2*hb_int of inactivity, so we don't expect to
            # reach this
            msg = MSGQUEUE.get(True, 9999)
        except Queue.Empty:
            # Expect to never reach here
            msg = "QUEUE_EMPTY"
        
        if msg[0] == "MSG":
            content = msg[1]
            # Fork off to process
            # If this is first message, set session_id
            if content.get("t") == "READY":
                session["session_id"] = content["d"].get("session_id")
            # Update heartbeat number
            # TODO: Get upset if we receive messages out of order
            if content.get("s"):
                session["seq"] = int(content.get("s"))
            
            # Rejected login or rejected heartbeat - disconnect and try again
            if content["op"] == 9:
                # Session resumption failed
                session = {"seq": 0, "session_id": ""}
                MSGQUEUE.put("WEBSOCKET_ERROR")
            
            # Pass to plugins
            # Don't pass messages we've generated as this could lead to
            # infinite looping
            if content["op"] == 0 and (content["d"] or {}).get("author", {}).get("id") != config.SELF:
                plugin_handler.handle(content)
        
        elif msg == "HEARTBEAT":
            # Send heartbeat
            # We don't care about dropping heartbeats if the socket is down
            try:
                socket_send(wsock, {"op": 1, "d": session["seq"]})
            except Exception as err:
                logging.info("Failed to send heartbeat: %s %s", type(err), err)
                MSGQUEUE.put("WEBSOCKET_ERROR")
        
        elif msg == "QUIT":
            # Shutdown
            logging.info("Main loop stopping...")
            break
        
        elif msg == "WEBSOCKET_ERROR":
            # Kill the existing websocket
            delay = 6
            logging.warn("Websocket appears to have died. Reconnecting in %ss...", delay)
            # Make sure the old socket is closed first
            try:
                wsock.close()
            except:
                pass
            # Wait a little, then reconnect
            time.sleep(delay)
            clean_queue(MSGQUEUE)
            MSGQUEUE.put("WEBSOCKET_CONNECT")
        
        elif msg == "WEBSOCKET_CONNECT":
            # Purge any heartbeats, connects, or error messages from the
            # queue so we don't double-process
            clean_queue(MSGQUEUE)
            
            # Reconnect to websocket
            try:
                wsock, hb_int = websocket_connect(session)
            except:
                # Failure!
                MSGQUEUE.put("WEBSOCKET_ERROR")
                logging.warn("Reconnection failed!")
                continue
            # Update heartbeat interval
            hb_queue.put(hb_int)
            # Start new thread for receiving from socket
            recv_thread = threading.Thread(target=readloop, args=[wsock])
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
    
    try:
        main()
    except Exception as err:
        logging.error("Main thread crashed: %s %s", repr(err), err)
        raise
