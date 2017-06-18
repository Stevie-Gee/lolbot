"""
 Controller object for the Uno package.
 
 Also contains a heap of Command objects for passing stuff to the Uno_Controller.
"""

# Disable warnings about __init__ from parent class not being called,
# because of all the Command classes
#pylint: disable=W0231

from plugins import Command, Plugin
from . import Views
from . import Models

# Global dictionary of Uno_Controller objects.
# Games are accessed by concatenating server hostname and channel.
GAMES = {}

def get_game(msg, server):
    """Gets the appropriate game for a given server and message."""
    # Key is comprised of <server hostname><channel>
    key = "{0}{1}".format(server.getconfig().host, msg.channel)
    
    # No game exists for this channel
    if key not in GAMES:
        return None
    else:
        return GAMES[key]

class Uno_Controller(object):
    """Handles all the commands in a single object."""
    def __init__(self, msg, server):
        # Server we're sitting on
        self.server = server
        
        # Key that we'll be stored under in GAMES
        self.key = "{0}{1}".format(server.getconfig().host, msg.channel)
        
        # Game and View objects (Model and View)
        self.game = Models.Game()
        self.view = Views.Uno_View(self.game, server, msg.channel)
        
        # Player who owns the game
        self.owner = self.get_user(msg)
        
        # The creator of the game obviously wants to play
        self.join(msg)
    
    def draw_card(self, msg):
        """Called when a Player tries to draw a card."""
        player = self.get_player(msg)
        if not player:
            self.view.error_report("you're not in this game.")
        
        try:
            player.manual_draw()
            self.view.action_summary(player)
            self.view.drawn(player)
        except Models.UnoError as err:
            self.view.error_report(err, player)
    
    def end_game(self, msg):
        """Called when someone tries to kill the game early."""
        user = self.get_user(msg)
        if user != self.owner and not self.server.isowner(msg):
            self.view.error_report("only the game owner can end the game.")
        else:
            del GAMES[self.key]
            self.view.end()
    
    def get_hand(self, msg):
        """Called when a Player requests to see their hand."""
        player = self.get_player(msg)
        if not player:
            self.view.error_report("you're not in this game.")
        
        self.view.show_hand(player)
    
    def get_player(self, msg):
        """Attempts to get the Player who sent this message.
        
        Return None if the user isn't in this game.
        """
        return self.game.get_player(self.get_user(msg))
    
    def get_turn(self, msg):
        """Called when someone wants to know whose turn it is."""
        self.view.next_player()
    
    def get_user(self, msg):
        """Get the IRC User object representing the person who sent this message.
        """
        return self.server.getuserlist().getuser(msg.nick)
    
    def join(self, msg):
        """Called when a Player tries to join the game."""
        user = self.get_user(msg)
        try:
            self.game.add_player(user)
            self.view.joined(user)
        except Models.UnoError as err:
            self.view.error_report(err)
    
    def leave(self, msg, user = None):
        """Called when a Player wants to leave the game.
        
        By default, will use the user who sent the message. If `user` is
        specified, that user will be kicked instead of the user who sent
        `msg` (and so `msg` can be null.)
        """
        if not user:
            user = self.get_user(msg)
        
        try:
            # Remove the player from the game
            self.game.remove_player(user)
            self.view.left(user)
            
            # If there are no people left, end the game
            if len(self.game.get_players()) == 0:
                del GAMES[self.key]
                return
            
            # If there's one person left and the game was in progress, they win
            if len(self.game.get_players()) == 1 and self.game.status == 'in progress':
                final_player = self.game.get_players()[0]
                self.game.win(final_player)
                self.view.win()
                del GAMES[self.key]
                return
            
            # If the person who left was the owner, we need a new owner
            if user == self.owner:
                self.owner = self.game.get_players()[0].get_identifier()
            
        except Models.UnoError as err:
            self.view.error_report(err)
    
    def pass_turn(self, msg):
        """Called when a Player tries to pass."""
        player = self.get_player(msg)
        if not player:
            self.view.error_report("you're not in this game.")
        
        try:
            player.pass_turn()
            self.view.action_summary(player)
        except Models.UnoError as err:
            self.view.error_report(err)
    
    def play(self, msg):
        """Called when a Player tries to play a card."""
        # Initialise some variables
        card = msg.commargs
        player = self.get_player(msg)
        
        # Make sure the player is in the game
        if not player:
            self.view.error_report("you're not in this game.")
        
        # Attempt to play the card
        try:
            player.play(card)
            self.view.action_summary(player)
        except Models.UnoError as err:
            # Tell the player what they did wrong
            self.view.error_report(err, player)
        
        # Delete the game if it ended
        if self.game.status == 'finished':
            del GAMES[self.key]
    
    def players(self, msg):
        """List players currently in the game."""
        self.view.player_summary()
    
    def start(self, msg):
        """Called when someone tries to start the game."""
        user = self.get_user(msg)
        
        # Make sure the user owns the game (or the bot)
        if user != self.owner and not self.server.isowner(msg):
            self.view.error_report("only the game owner can start the game.")
        else:
            try:
                self.game.start()
                self.view.start()
            except Models.UnoError as err:
                self.view.error_report(err)
    
    def top_card(self, msg):
        """Announce what the top card is."""
        self.view.top_card()


############################################################################
# Here we handle interfacing between irc messages and the controller class #
############################################################################
# This dict lists all the uno commands and their help messages
uno_commands = {
    'draw': 'Draw a card from the deck.',
    'cards': 'Find out what cards are in your hand.',
    'hand': 'Alias for cards.',
    'join': 'Join a new or in-progress game.',
    'leave': 'Leave a game.',
    'pass': 'Pass your turn. You must draw before you can pass.',
    'play': "Play a card. E.g. 'play r4' to play a red four.",
    'players': 'List all current players, and (if applicable) how many cards they have.',
    'start': 'Start the game. You must have created a game with the uno command first.',
    'stop': 'Stop an existing game.',
    'top': 'Show the top card of the discard pile.',
    'turn': 'Show whose turn it is',
}

class Uno_Command(Command):
    """Handles translating irc !commands into Uno_Controller methods."""
    def __init__(self):
        global uno_commands
        self.command = 'uno'
        self.aliases = uno_commands.keys()
    
    def call(self, msg, server):
        """Handle a command call."""
        # Extract the !command from the message
        # Yes, this should probably be part of the msg class
        if msg.trailing.startswith('\x03'):
            # Remove leading colour codes
            command = re.sub(r'^\x03\d\d?(\,\d\d?)?', '', msg.trailing)
        else:
            command = msg.trailing
        if not command.startswith(server.getcchar()):
            return
        command = command.replace(server.getcchar(), '', 1).lower()
        if ' ' in command:
            command = command.split(' ', 1)[0]
        
        # See if there's an uno game active on this channel
        game = get_game(msg, server)
        
        # Handle the !uno command separately
        if command == 'uno':
            if game:
                reply = "There is already a game in progress (owned by {0})"
                server.replyto(msg, reply.format(game.owner))
                return
            
            game = Uno_Controller(msg, server)
            GAMES[game.key] = game
            reply = "{0} started a game of uno! Type {1}join to join."
            server.replyto(msg, reply.format(game.owner, server.getcchar()))
            return
        
        # For all other commands, there must be a game existing
        if not game:
            server.replyto(msg, "Error, no game is currently active.")
            return
        
        # Any other logic is handled by the Uno_Controller
        if command == 'draw':
            game.draw_card(msg)
        elif command in ('cards', 'hand'):
            game.get_hand(msg)
        elif command == 'join':
            game.join(msg)
        elif command == 'leave':
            game.leave(msg)
        elif command == 'pass':
            game.pass_turn(msg)
        elif command == 'play':
            game.play(msg)
        elif command == 'players':
            game.players(msg)
        elif command == 'start':
            game.start(msg)
        elif command == 'stop':
            game.end_game(msg)
        elif command == 'top':
            game.top_card(msg)
        elif command == 'turn':
            game.get_turn(msg)
        else:
            # This shouldn't happen
            server.replyto("Error, no action configured for this uno command.")
    
    def help(self, msg, server):
        """Handle the help commands.
        
        You can call this with '!help uno' or '!help uno <command>"""
        global uno_commands
        # Was there a command after the 'uno'?
        arg_parts = msg.commargs.split(' ')
        if len(arg_parts) == 1:
            # No, there wasn't. Return help for the !uno command.
            answer =  "Creates a game of uno. For help with a particular "
            # The newline on the end is a really nasty hack to break the !help commmand,
            # so it doesn't list "aliases" of the !uno command
            answer += "command, type {0}help uno command. Current commands are: {1}\n"
            return answer.format(server.getcchar(), ', '.join(self.aliases))
        
        # Yes, figure out what it was.
        command = arg_parts[1]
        if command not in uno_commands:
            return "Unrecognised command."
        else:
            return uno_commands[command] + "\n"

class Uno_Kicker(Plugin):
    """Removes a player from the game if they leave/are kicked."""
    def __init__(self):
        self.commands = ['KICK', 'PART', 'QUIT']
    
    def call(self, msg, server):
        """Call method."""
        if msg.command == 'KICK':
            game = get_game(msg, server)
            if not game:
                # Make sure there's actually game in this channel
                return
            # Get the user who was kicked
            nick = msg.middle.split(' ')[-1]
            user = game.server.getuserlist().getuser(nick)
            
            if game.game.has_player(user):
                # Note that for a KICK message, the 'user' is the person who
                # delivered the kick, not the one who received it.
                game.leave(msg, user = user)
        
        elif msg.command == 'PART':
            game = get_game(msg, server)
            if not game:
                # Make sure there's actually game in this channel
                print "NOGAME"
                return
            if game.get_player(msg):
                print "PARTING"
                game.leave(msg)
        
        elif msg.command == 'QUIT':
            # QUITs need to be handled for every game on the server
            global GAMES
            for game in GAMES.values():
                user = game.server.getuserlist().getuser(msg.nick)
                if game.server == server and game.game.has_player(user):
                    game.leave(msg)
