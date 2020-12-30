"""
 View object for the Uno package. Handles all output to the IRC server.
"""
from collections import defaultdict
import re
import sys

import bot_utils

if sys.version_info[0] == 2:
    import Models
else:
    from . import Models


def card_format(hand, discard_pile=False):
    """Given one (or more) cards, format them into a pretty coloured string.
    
    If `discard_pile` is True, this will also display the current colour for
    wild cards. This is because when a wild is on the discard pile it has a
    colour set, but when it's in someone's hand it does not.
    """
    # Make sure the hand is sorted
    if isinstance(hand, Models.Card):
        hand = [hand]
    hand = list(hand)
    hand.sort()
    
    # Produce output
    output = []
    for card in hand:
        if card.denomination in ('wild', 'wild4') and not discard_pile:
            output.append(card.denomination)
        else:
            output.append(card.colour[0] + card.denomination)
    return ' '.join(output)

class Uno_View(object):
    """The sole view object."""
    
    def __init__(self, game, channel):
        """We need to keep a record of both what game we're viewing, and where
        to send messages (channel id)."""
        self.game = game
        self.channel = channel
    
    def action_summary(self, player):
        """Send a summary of the last action a player performed.
        
        Player is the player who just played.
        
        Gives a description of which card was played, any effects that card had,
        whose turn it is, who plays next, and how many cards each player has.
        """
        top_card = self.game.get_top_card()
        msg = None
        
        # Make sure player is a class instance, not just the indentifier
        player = self.game.get_player(player)
        
        # Person drew a card. We exit early here because we don't want a full
        # turn summary.
        if self.game.get_last_action() == 'draw':
            self._privmsg("{0} draws a card.".format(player))
            return
        
        # Person passed
        if self.game.get_last_action() == 'pass':
            self._privmsg("{0} passed their turn.".format(player))
        # They played a card
        else:
            msg = "{0} plays a {1}.".format(player, card_format(self.game.get_top_card(), True))
            self._privmsg(msg)
            
            # Check for a special effects card
            if top_card.denomination == 'draw2':
                msg = "{0} draws two cards and is skipped.".format(self.game.get_previous_player())
                self._privmsg(msg)
                self.drawn(self.game.get_previous_player())
            
            elif top_card.denomination == 'wild4':
                msg = "{0} draws four cards and is skipped.".format(self.game.get_previous_player())
                self._privmsg(msg)
                self.drawn(self.game.get_previous_player())
            
            elif top_card.denomination == 'reverse':
                msg = "Direction is reversed!"
                self._privmsg(msg)
            
            elif top_card.denomination == 'skip':
                msg = "{0} is skipped.".format(self.game.get_previous_player())
                self._privmsg(msg)
        
        # Did anyone win?
        if self.game.winner:
            self.win()
        
        else:
            # Uno check?
            if len(player.get_cards()) == 1:
                self._privmsg("{0} has uno!".format(player))
            
            # Provide a list of who comes next, and how many cards each player has
            self.next_player()
            #self.player_summary()
            
            # Tell the current player what cards they have
            self.show_hand(self.game.get_current_player())
    
    def drawn(self, player):
        """Tell a player what card(s) they most recently drew.
        
        Should be called after a Player draws a card.
        
        `player` can either be a Player object, or a player identifier.
        """
        # Convert an identifier to a Player
        player = self.game.get_player(player)
        
        # Build an IRC-format string for each card
        card_strings = card_format(player.last_draw)
        self._privmsg("You drew: {0}".format(card_strings), player)
    
    def end(self):
        """Declares that the game was ended early."""
        self._privmsg("The game has been ended.")
    
    def error_report(self, error, player = None):
        """Send an error message to a player when they attempt to do something
        illegal.
        
        If `player` is not specified, the error will go to the entire channel.
        """
        # Make sure player is a class instance, not just the indentifier
        player = self.game.get_player(player)
        self._privmsg("Sorry, {0}".format(error), player)
    
    def joined(self, player):
        """Report that someone joined the game."""
        # Make sure player is a class instance, not just the indentifier
        player = self.game.get_player(player)
        self._privmsg("{0} joined the game.".format(player))
    
    def left(self, player):
        """Report that someone left the game."""
        # Make sure player is a class instance, not just the indentifier
        player = self.game.get_player(player)
        self._privmsg("{0} left the game.".format(player))
    
    def next_player(self):
        """Report whose turn it is, and who plays next."""
        # Get the current player, and number of cards he has
        cur = self.game.get_current_player()
        nex = self.game.get_next_player()
        msg = "Current player: {0}. Next player: {1}."
        
        self._privmsg(msg.format(self.player_string(cur),
                                 self.player_string(nex)))
    
    def player_string(self, player):
        """Return a string giving the player's name, and how many cards
        they have.
        
        If the game is not in progress, only return their name
        """
        # Make sure player is a class instance, not just the indentifier
        player = self.game.get_player(player)
        
        if not self.game.status == 'in progress':
            return "{0}".format(player)
        
        # Game is in progress
        string = "{0} ({1} card".format(player, len(player.get_cards()))
        if len(player.get_cards()) > 1:
            string += 's'
        string += ')'
        return string
    
    def player_summary(self):
        """Report who is in the game, and how many cards each player has.
        
        Ordered based on player order, starting with the current player.
        """
        # Get all the players in the game, and the index of the current player
        players = self.game.get_players()
        if len(players) > 1:
            cur = players.index(self.game.get_current_player())
        else:
            cur = 0
        
        # If the game isn't in progress this method should still work,
        # but shouldn't try to list how many cards each player has
        
        # Rearrange the players list so the current player is first
        players = players[cur:] + players[:cur]
        
        # Make a list of "player: # cards" strings
        player_strings = []
        for player in players:
            player_strings.append(self.player_string(player))
        
        # Join the strings and send
        self._privmsg("Current players: " + ', '.join(player_strings))
    
    def _privmsg(self, msg, player=None):
        """Send a PRIVMSG to the specified Player.
        
        If no user is specified, send it to the channel intead.
        """
        # Get our destination ID
        # Make sure player is a class instance, not just the indentifier
        player = self.game.get_player(player)
        
        if player:
            destination = bot_utils.get_dm(player.identifier)
        else:
            destination = self.channel
        
        # Sanitise in case we have <> wrapper around the ID
        matches = re.match(r'\<.(\d+)\>', destination)
        if matches:
            destination = matches.group(1)
        
        # Hijack the bot_utils.reply function
        fake = {"d": {"channel_id": destination}}
        bot_utils.reply(fake, msg)
    
    def show_hand(self, player):
        """Tell a player what cards they have. This message is private.
        
        Assume that `player` is the IRC nickname of the player.
        """
        cards = self.game.get_player(player).get_cards()
        card_strings = card_format(cards)
        self._privmsg("Your cards are {0}".format(card_strings), player)
    
    def start(self):
        """Declares that the game has started."""
        self._privmsg("The game has started.")
        self.top_card()
        self.next_player()
        self.show_hand(self.game.get_current_player())
    
    def top_card(self):
        """Tell everyone what the top card of the discard pile is."""
        card = card_format(self.game.get_top_card(), True)
        self._privmsg("The top card is {0}".format(card))
    
    def win(self):
        """Declare that someone has won the game."""
        self._privmsg("{0} has won the game!".format(self.game.winner))
