"""
 Controller object for the Uno package.
 
 Also contains a heap of Command objects for passing stuff to the Uno_Controller.
"""

from functools import wraps

import bot_utils
import config
import Views
import Models

# Global dictionary of Uno_Controller objects.
# Games are accessed by concatenating server hostname and channel.
GAMES = {}

def get_game(msg):
    """Gets the appropriate game for a given server and message."""
    # Key is comprised of <server hostname><channel>
    try:
        key = msg["d"]["channel_id"]
        return GAMES[key]
    except KeyError:
        return None

def needs_game(func):
    """Decorator to fetch the Uno game relating to the given message.
    If no game is currently active, tell the user and exit."""
    @wraps(func)
    def decorated_f(msg):
        game = get_game(msg)
        if not game:
            bot_utils.reply(msg, "Error, no game is currently active.")
            return
        return func(msg, game)
    return decorated_f

class Uno_Controller(object):
    """Handles all the commands in a single object."""
    def __init__(self, msg):
        # Key that we'll be stored under in GAMES
        self.key = msg["d"]["channel_id"]
        
        # Game and View objects (Model and View)
        self.game = Models.Game()
        self.view = Views.Uno_View(self.game, msg["d"]["channel_id"])
        
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
        if user != self.owner and user not in config.ADMINS:
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
        try:
            return msg["d"]["author"]["id"]
        except KeyError:
            return None
    
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
        if ' ' in msg["d"]["content"]:
            card = msg["d"]["content"].split(None, 1)[1]
        else:
            card = ''
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
        if user != self.owner and user not in config.ADMINS:
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
@bot_utils.command('uno')
def uno_start(msg):
    """Creates a game of uno. Other commands are:
    {cc}draw, {cc}hand, {cc}join, {cc}leave, {cc}pass, {cc}play, {cc}players, {cc}start, {cc}stop, {cc}top, {cc}turn"""
    game = get_game(msg)
    if game:
        bot_utils.reply(msg,
            "There is already a game in progress (owned by {0})".format(game.owner))
        return
    
    game = Uno_Controller(msg)
    GAMES[game.key] = game
    reply = "{0} started a game of uno! Type {1}join to join."
    server.replyto(msg, reply.format(game.owner, config.COMMAND_CHAR))

@bot_utils.command('draw')
@needs_game
def draw(msg, game):
    """Uno: Draw a card from the deck."""
    game.method(msg)

@bot_utils.command('stop')
@needs_game
def stop(msg, game):
    """Uno: Stop an existing game."""
    game.end_game(msg)

@bot_utils.command('play')
@needs_game
def play(msg, game):
    """Uno: Play a card. E.g. 'play r4' to play a red four."""
    game.play(msg)

@bot_utils.command('hand')
@needs_game
def hand(msg, game):
    """Uno: Find out what cards are in your hand."""
    game.get_hand(msg)

@bot_utils.command('pass')
@needs_game
def pass_turn(msg, game):
    """Uno: Pass your turn. You must draw before you can pass."""
    game.pass_turn(msg)

@bot_utils.command('turn')
@needs_game
def turn(msg, game):
    """Uno: Show whose turn it is"""
    game.get_turn(msg)

@bot_utils.command('join')
@needs_game
def join(msg, game):
    """Uno: Join a new or in-progress game."""
    game.join(msg)

@bot_utils.command('start')
@needs_game
def start(msg, game):
    """Uno: Start the game. You must have created a game with the uno command first."""
    game.start(msg)

@bot_utils.command('top')
@needs_game
def top(msg, game):
    """Uno: Show the top card of the discard pile."""
    game.top_card(msg)

@bot_utils.command('leave')
@needs_game
def leave(msg, game):
    """Uno: Leave a game."""
    game.leave(msg)

@bot_utils.command('players')
@needs_game
def players(msg, game):
    """Uno: List all current players, and (if applicable) how many cards they have."""
    game.players(msg)

'''
class Uno_Kicker(Plugin):
    """Removes a player from the game if they leave/are kicked."""
    def __init__(self):
        self.commands = ['KICK', 'PART', 'QUIT']
    
    def call(self, msg, server):
        """Call method."""
        if msg.command == 'KICK':
            game = get_game(msg)
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
            game = get_game(msg)
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
'''
