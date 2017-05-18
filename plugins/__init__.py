"""
Any modules in this directory may provide either:

A callable named `handle`,
AND/OR
A `COMMANDS` dictionary, mapping command keywords to callables.

All of these callables must take a single positional argument - a dict
representing a JSON message received from the Discord websocket API.
"""
