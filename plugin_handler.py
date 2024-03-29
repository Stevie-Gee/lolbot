"""
Check all modules in the plugins/ directory. Any modules may present:
A callable named `handle`,
AND/OR
A `COMMANDS` dictionary, mapping command keywords to callables.

All of these callables must take a single positional argument - a dict
representing a JSON message received from the Discord websocket API.

The COMMANDS dictionary will create simple !command-style handlers.
The handle() function will be called for every event received from Discord.
"""

import imp
import logging
import os
import re
import threading

import bot_utils
import config


@bot_utils.handler
def do_command(msg):
    """Check if we need to call a keyword-style command."""
    # If this isn't a spoken chat message, ignore it
    if msg.get("t") != "MESSAGE_CREATE":
        return
    
    # If the message doesn't begin with our command char, ignore it
    content = msg.get("d").get("content")
    if not content.startswith(config.COMMAND_CHAR):
        return
    
    # If the command came from a bot, do not respond
    if msg["d"]["author"].get("bot") and not config.BOT_COMMANDS:
        return
    
    # Remove the command prefix from the message
    content = content[len(config.COMMAND_CHAR):]
    
    # Do we have args for this command?
    if ' ' in content:
        content = content.split(' ', 1)[0]
    
    # Normalise case
    content = content.lower()
    
    # Check whether a dynamic content handler will take this
    handled = False
    for regex in bot_utils.RECOMMANDS:
        if (re.match(regex, content)):
            handled = True
    
    # Ignore a lone command character
    if not content:
        pass
    # Is the command recognised? If so, call it
    elif content in bot_utils.COMMANDS:
        bot_utils.COMMANDS[content](msg)
    elif not handled:
        bot_utils.reply(msg, "Unknown command: _{0}{1}_.".format(config.COMMAND_CHAR, content))

def handle(msg):
    """Distribute a received message to all relevant plugins."""
    # TODO: More graceful handling of errors
    for plug in bot_utils.HANDLERS:
        th = threading.Thread(target=plug, args=[msg])
        th.setDaemon(True)
        th.start()

def load(directory, package=None):
    """Load plugins from the given directory."""
    files = os.listdir(directory)
    for fname in files:
        fname = os.path.abspath(os.path.join(directory, fname))
        
        # If we find a directory, attempt to import it as a package
        if os.path.isdir(fname):
            logging.debug("Attempting package %s", fname)
            try:
                triple = imp.find_module(os.path.basename(fname), [os.path.dirname(fname)])
                imp.load_module(os.path.basename(fname), *triple)
            except ImportError:
                # If it isn't a package, just load any modules within
                load(fname)
            else:
                # If we loaded it as a package, import modules as a package
                load(fname, package=os.path.basename(fname))
            continue
        # Only load .py files
        elif os.path.basename(fname).startswith("_") or not fname.endswith(".py"):
            continue
        
        # Import the module
        mname = os.path.basename(fname[:-3])
        if package:
            mname = package + '.' + mname
        logging.debug("Found module '%s'", mname)
        try:
            triple = imp.find_module(os.path.basename(fname[:-3]), [os.path.dirname(fname)])
            module = imp.load_module(mname, *triple)
        except Exception as err:
            logging.warn("Failed to import module %s: %s %s", fname, type(err), err)
            continue
