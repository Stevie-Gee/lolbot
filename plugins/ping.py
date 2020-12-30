"""
Example plugin, demonstrating how to implement a generic message handler
and a keyword-response type command.
"""

import logging
import bot_utils
import config

@bot_utils.handler
def handle(msg):
    if msg.get("t") == "MESSAGE_CREATE":
        content = msg.get("d").get("content")
        # Respond to !ping with !pong
        if content == "!foo":
            reply = u"!bar"
        # If the !ping has content attached, match this content in the output
        elif content.startswith("!foo "):
            reply = u"!bar " + msg.get("d").get("content").split(' ', 1)[1]
        else:
            return
        bot_utils.reply(msg, reply)

@bot_utils.command("ping")
def command(msg):
    """Reply with {cc}pong, and any args passed to the original {cc}ping."""
    content = msg.get("d").get("content")
    if ' ' in content:
        reply = u"{0}pong {1}".format(config.COMMAND_CHAR, content.split(' ', 1)[1])
    else:
        reply = u"{0}pong".format(config.COMMAND_CHAR)
    
    bot_utils.reply(msg, reply)

@bot_utils.command("foo")
def dofoo(msg):
    """Reply with {cc}bar, and any args passed to the original {cc}foo"""
    # This is just a placeholder so !foo isn't treated as an unrecognised command
    pass
