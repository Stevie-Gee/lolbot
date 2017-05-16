#!/usr/bin/env python

"""Discord bot"""

import logging, logging.config
import requests
import websocket
import config

# Base URL for the REST api
BASE_URL = "https://discordapp.com/api"

# What version of the gateway protocol do we speak?
GATEWAY_VERSION = "?v=5&encoding=json"

# Template for generating heartbeats
HEARTBEAT_MSG = {"op": 1, "d": 0}

def websocket_connect():
    """Connect to the websocket, login."""
    # Get the websocket URL from discord
    ws_url = requests.get(BASE_URL + "/gateway").json()['url']
    logging.debug("Websocket url is %s", ws_url)

def main():
    """Main function - connect to server, start plugins."""
    # Logging init
    logging.config.dictConfig(config.logging_config)
    logging.debug("foo")
    
    # Connect to server
    websocket_connect()

if __name__ == '__main__':
    main()
