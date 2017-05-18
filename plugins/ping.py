"""
Basic ping/pong responder
"""

import logging
import config

def handle(msg):
    if msg.get("t") == "MESSAGE_CREATE":
        content = msg.get("d").get("content")
        # Respond to !ping with !pong
        if content == "!foo":
            reply = "!bar"
        # If the !ping has content attached, match this content in the output
        elif content.startswith("!foo "):
            reply = "!bar " + msg.get("d").get("content").split(' ')[1]
        else:
            return
        
        channel_id = msg.get("d").get("channel_id")
        logging.debug("Send %s", reply)
        config.HTTP_SESSION.post(
            "/channels/{0}/messages".format(channel_id),
            json={"content": reply},
            )

# Commands as a dict
def command(msg):
    """Reply with !pong, and any args passed to the original !ping."""
    content = msg.get("d").get("content")
    if ' ' in content:
        reply = "{0}pong {1}".format(config.COMMAND_CHAR, content.split(' ', 1)[1])
    else:
        reply = "{0}pong".format(config.COMMAND_CHAR)
    
    channel_id = msg.get("d").get("channel_id")
    logging.debug("Send %s", reply)
    config.HTTP_SESSION.post(
        "/channels/{0}/messages".format(channel_id),
        json={"content": reply},
        )

COMMANDS = {
    "ping": command,
    "ping2": command,
}
# Help is a separate dictionary
HELPS = {
    "ping": "Replies with a pong",
}
# Or maybe the keys could be tuples instead, so we have a primary and aliases?
HELPS = {
    ("ping", "ping2"): "replies with a pong",
}
