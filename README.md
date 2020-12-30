# Getting started

## First, authorise your bot on discord

* Create an app on discord
* Create an "app bot user" for your user
* Navigate here to add your bot to your server (make sure to replace [bot client ID] with the ID provided by discord): https://discord.com/oauth2/authorize?client_id=[bot client ID]&scope=bot

## Then install the bot

* Pull a copy of the source code to your local server. The recommended location is /opt/lolbot/
* Create a lolbot user+group to run the service as.
* Create a config.py file based on the config.py.EXAMPLE provided. 

  At minimum, you need to set BOT_TOKEN. You should probably add ADMINS too.

* Install any required package dependencies with `python setup.py develop`
* Compatible with python 2.7 and 3.x
* Rename `install/lolbot.systemd` to `/usr/lib/systemd/system/lolbot.service`, then run `systemctl enable lolbot` to start on boot

## To run the bot

Service scripts are provided for both upstart and systemd in the install/ directory. Install one of these scripts as is appropriate for your OS, then start the service.

# Writing your own plugins

There are some simple examples in the plugins/ directory, take a look at ping.py for a demonstration of basic responding to commands.
