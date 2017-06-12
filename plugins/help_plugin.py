"""Provides usage help for the other !commands. Help is the docstring for any function.

If you put {cc} in your docstring, it will be replaced by the command character.
"""

import bot_utils
import config

# Dictionary mapping commands to their help strings
HELPS = {}

def init(commdict):
    """Given the 'COMMANDS' dictionary from plugin_handler,
    assemble our own HELPS dictionary.
    """
    global HELPS
    HELPS = {}
    for key, func in commdict.iteritems():
        HELPS[key.lower()] = func.__doc__

def call(msg):
    """For help with a particular command, type _{cc}help command_."""
    content = msg.get("d").get("content")
    if ' ' in content:
        command = content.split(None)[1].lower()
        if command in HELPS:
            reply = HELPS[command] or "No help available"
        else:
            reply = "Unknown command"
    else:
        reply = "Available commands: {cc}%s. For help with a particular command, type {cc}help command"
        reply %= ', {cc}'.join(HELPS)
    
    if not reply.endswith('.'):
        reply += '.'
    if '{cc}' in reply:
        reply = reply.format(cc=config.COMMAND_CHAR)
    bot_utils.reply(msg, reply)

COMMANDS = {
    "help": call,
}
