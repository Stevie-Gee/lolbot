"""
Functions that might be useful for plugins.
"""

import config

# This will be populated with a custom requests.Session instance
# which handles Discord's HTTP auth and URL prefix for you
# Make requests to the root-relative API paths, e.g. "/channels/"
HTTP_SESSION = None

def reply(msg, reply):
    """Given a MESSAGE_CREATE event from discord, and a reply string,
    send the reply string to whichever channel/PM the original event
    came from.
    """
    channel_id = msg.get("d").get("channel_id")
    HTTP_SESSION.post(
        "/channels/{0}/messages".format(channel_id),
        json={"content": reply},
        )
