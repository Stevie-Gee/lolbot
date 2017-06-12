"""Provides usage help for the other !commands. Help is the docstring for any function."""

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
    content = msg.get("d").get("content")
    if ' ' in content:
        command = content.split(None)[1].lower()
        if command in HELPS:
            reply = HELPS[command] or "No help available"
        else:
            reply = "Unknown command"
    else:
        reply = "Available commands: !{0}. For help with a particular command, type {1}help command"
        reply = reply.format(', !'.join(HELPS), config.COMMAND_CHAR)
    if not reply.endswith('.'):
        reply += '.'
    bot_utils.reply(msg, reply)

call.__doc__ = """Provides help for a given command. For help with a particular command, type _{0}help command_.""".format(config.COMMAND_CHAR)

COMMANDS = {
    "help": call,
}
