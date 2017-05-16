"""
Basic ping/pong responder
"""

import logging
import requests
import config

def process_msg(msg):
    if msg.get("t") == "MESSAGE_CREATE":
        content = msg.get("d").get("content")
        # Respond to !ping with !pong
        if content == "!ping":
            reply = "!pong"
        # If the !ping has content attached, match this content in the output
        elif content.startswith("!ping "):
            reply = "!pong " + msg.get("d").get("content")[6:]
        else:
            return
        
        channel_id = msg.get("d").get("channel_id")
        logging.debug("Send %s", reply)
        config.HTTP_SESSION.post(
            "/channels/{0}/messages".format(channel_id),
            json={"content": reply},
            )
