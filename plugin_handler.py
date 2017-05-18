"""
Handle simple !command style plugins.
"""

import config

# Dict mapping every known command word to its module
# Or should it map a command to a callable? But then how do we do aliases?
COMMANDS = {}

def process_msg(msg):
    # If this isn't a spoken chat message, ignore it
    if msg.get("t") != "MESSAGE_CREATE":
        return
    
    # If the message doesn't begin with our command char, ignore it
    content = msg.get("d").get("content")
    if not content.startswith(config.COMMAND_CHAR):
        return
    
    # Remove the command prefix from the message
    content = content[len(config.COMMAND_CHAR):]
    
    # Do we have args for this command?
    if ' ' in content:
        content = content.split(' ', 1)[0]
    
    # Normalise case
    content = content.lower()
    
    # Is the command recognised? If so, call it
    if content in COMMANDS:
        COMMANDS[content](msg)
