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
        requests.post(
            "{0}/channels/{1}/messages".format(config.BASE_URL, channel_id),
            headers = {"Authorization": "Bot "+config.BOT_TOKEN},
            json={"content": reply},
            )
