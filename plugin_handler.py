"""
Handle simple !command style plugins.
"""

import logging
import os
import sys
import threading

import config

# Dict mapping keyword-style chat commands to their callables
COMMANDS = {}

# List of callables to handle every received websocket message
PLUGINS = []

def load(directory):
    """Load plugins from the given directory."""
    files = os.listdir(directory)
    for fname in files:
        # Recursively load directories
        if os.path.isdir(os.path.join(directory, fname)):
            load(os.path.join(directory, fname))
            continue
        # Convert files to python module names
        elif fname.endswith('.py') and not fname.startswith('_'):
            modulename = "%s.%s" % (directory.replace('/', '.'),
                                    fname.rsplit('.py', 1)[0])
        # Find loadable packages too, ignore the root-level plugins dir
        elif fname == '__init__.py' and directory != "plugins":
            modulename = directory.replace('/', '.')
        # Ignore all other files
        else:
            logging.debug("Ignore %s", fname)
            continue
        
        # Import+reload the module
        logging.debug("Found module '%s'", modulename)
        try:
            __import__(modulename)
            module = sys.modules[modulename]
            reload(module)
        except Exception as err:
            logging.warn("Failed to load module %s: %s %s", modulename, type(err), err)
            continue
        
        # TODO: Handle errors gracefully
        # Note which modules have generic message handling
        if getattr(module, "handle", None):
            logging.info("Loaded plugin %s", module)
            PLUGINS.append(module.handle)
        # Note which modules provide commands
        if getattr(module, "COMMANDS", None):
            for keyword, function in  module.COMMANDS.iteritems():
                logging.info("Loaded command %s", keyword)
                COMMANDS[keyword] = function

def do_command(msg):
    """Possibly call a keyword-style command."""
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
# Add this to the plugins list
PLUGINS.append(do_command)

def handle(msg):
    """Distribute a received message to all relevant plugins."""
    # TODO: More graceful handling of errors
    for plug in PLUGINS:
        th = threading.Thread(target=plug, args=[msg])
        th.setDaemon(True)
        th.start()
