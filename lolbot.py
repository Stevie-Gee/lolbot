#!/usr/bin/env python

"""Discord bot"""

import logging, logging.config
import requests
import config

# Base URL for the REST api
BASE_URL = "https://discordapp.com/api"

# What version of the gateway protocol do we speak?
GATEWAY_VERSION = "?v=5&encoding=json"

# Template for generating heartbeats
HEARTBEAT_MSG = {"op": 1, "d": 0}

def main():
    """Main function - connect to server, start plugins."""
    logging.config.dictConfig(config.logging_config)
    logging.debug("foo")

if __name__ == '__main__':
    main()
