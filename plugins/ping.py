"""
Example plugin, demonstrating how to implement a generic message handler
and a keyword-response type command.
"""

import logging
import bot_utils
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
        
        bot_utils.reply(msg, reply)

def command(msg):
    """Reply with {cc}pong, and any args passed to the original {cc}ping."""
    content = msg.get("d").get("content")
    if ' ' in content:
        reply = "{0}pong {1}".format(config.COMMAND_CHAR, content.split(' ', 1)[1])
    else:
        reply = "{0}pong".format(config.COMMAND_CHAR)
    
    bot_utils.reply(msg, reply)

# Commands as a dict
COMMANDS = {
    "ping": command,
    # Add this so that !foo isn't an 'unrecognised command'
    "foo": lambda msg: None,
}
