"""Provides usage help for the other !commands. Help is the docstring for any function.

If you put {cc} in your docstring, it will be replaced by the command character.
"""

import bot_utils
import config

@bot_utils.command("help")
def call(msg):
    """For help with a particular command, type _{cc}help command_."""
    content = msg.get("d").get("content")
    if ' ' in content:
        command = content.split(None)[1].lower().strip(config.COMMAND_CHAR)
        if command in bot_utils._COMMANDS:
            reply = bot_utils._COMMANDS[command].__doc__ or "No help available"
        else:
            reply = "Unknown command"
    else:
        reply = "Available commands: {cc}%s.\nFor help with a particular command, type _{cc}help command_"
        helplist = bot_utils._COMMANDS.keys()
        helplist.sort()
        reply %= ', {cc}'.join(helplist)
    
    if not reply.endswith('.'):
        reply += '.'
    if '{cc}' in reply:
        reply = reply.format(cc=config.COMMAND_CHAR)
    bot_utils.reply(msg, reply)
