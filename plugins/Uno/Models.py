"""
 Self-contained Uno module. This is the 'model' part of MVC.
 
 Doesn't have any output (except for exceptions) - output is handled by the
 view.
"""

import random

def make_deck():
    """Return a list of cards representing a full Uno deck. Unshuffled.
    
    For reference, a full deck consists of one 0 in each colour, two of
    1-9 in each colour, two each of (draw2, skip, reverse) per colour,
    four wilds and four wild4s.
    """
    deck = []
    
    # Build the list of denominations
    # Numbers 1-9, reverse, skip and draw2 occur twice
    denoms = ['reverse', 'skip', 'draw2']
    denoms += range(1, 10)
    denoms *= 2
    
    # Zero only occurs once per colour
    denoms.append(0)
    
    # Add the normal cards for each colour
    for colour in Card.colours:
        for denom in denoms:
            deck.append(Card('{0} {1}'.format(colour, denom)))
    
    # There are four wilds and four wild4s.
    # They should be blue, so they appear after every other card.
    for dummy in range(4):
        deck.append(Card('blue wild'))
        deck.append(Card('blue wd4'))
    
    return deck


class Game(object):
    """
    Represents a game of Uno. Stores information about the deck, which players
    are in the game, whose turn it is etc.
    """
    def __init__(self):
        # players is the list of players in the game. Play ALWAYS moves from
        # low to high - reversing changes the order of the players list, not
        # which direction we move through it.
        self.players = []
        
        # Which player's turn is it?
        # We start with the player left of the dealer
        self.current_turn = 1
        
        # Card 0 is the top
        self.draw_pile = []
        self.discard_pile = []
        
        # Valid statuses are 'new', 'in progress' and 'finished'
        self.status = 'new'
        
        # The last action a player took
        self.last_action = None
        
        # Set to the winning player when someone wins. Last player alive
        # automatically wins.
        self.winner = None
        
        # Config settings. Configurable on a per-game basis?
        # How many cards should a player start with?
        self.starting_hand_size = 7
        # If True, you can't play a wild4 while you have other cards of the same colour
        self.strict_wild4_play = False
    
    def add_player(self, identifier):
        """
        Add a player to the game.
        
        `identifier` should be a way of uniquely identifying the player.
        A string is a good idea, maybe a username or something. Though you can
        use pretty much anything that has an equality test.
        """
        if self.status == 'finished':
            raise InvalidStatusError("you can't add players to a finished game.")
        
        # Make sure the player isn't already in this game
        if identifier in self.players:
            raise UnoError("player is already in this game.")
        
        player = Player(identifier, self)
        
        # If the game hasn't started, add the player to the end
        if self.status == 'new':
            self.players.append(player)
        #Otherwise add the player just before whoever's turn it is
        else:
            self.players.insert(self.current_turn, player)
            self.current_turn += 1
        
        # If the game is in progress, the player needs to draw a hand
        if self.status == 'in progress':
            player.draw(self.starting_hand_size)
    
    def draw(self, count = 1):
        """
        Draw the given number of cards from the deck and return them as a list.
        
        This will also shuffle the discard pile back into the deck if the deck
        is empty. If we somehow run out of available cards (say, we have 20
        players), make a new deck and add it to the pile.
        """
        # Make sure we have enough cards to draw
        if count > len(self.draw_pile):
            self._shuffle()
        
        # If we still don't have enough cards, we'd better add another deck
        while count > len(self.draw_pile):
            self.discard_pile += make_deck()
            self._shuffle()
        
        cards = []
        for dummy in range(count):
            cards.append(self.draw_pile.pop(0))
        
        return cards
    
    def get_current_player(self):
        """Return the player whose turn it is."""
        return self.players[self.current_turn]
    
    def get_last_action(self):
        """Return the last action taken by a player.
        
        Can be 'pass', 'draw' or 'play'
        """
        return self.last_action
    
    def get_next_player(self):
        """Return the next player."""
        next_player = self.current_turn + 1
        if next_player == len(self.players):
            next_player = 0
        return self.players[next_player]
    
    def get_player(self, identifier):
        """Return the player who matches `identifier`. Returns None if no
        players match."""
        for player in self.players:
            if player == identifier:
                return player
        
        return None
    
    def get_players(self):
        """Return a list of all players."""
        return list(self.players)
    
    def get_previous_player(self):
        """
        Return the previous player.
        
        Useful for finding out who was just skipped.
        """
        prev = self.current_turn - 1
        if prev == -1:
            prev = len(self.players) - 1
        return self.players[prev]
    
    def get_score(self):
        """Return the total score of all cards in players' hands."""
        score = 0
        for player in self.players:
            for card in player.get_cards():
                score += card.value()
        
        return score
    
    def get_top_card(self):
        """Return the top card on the discard pile."""
        return self.discard_pile[0]
    
    def has_player(self, player):
        """Checks whether the given player/identifier exists in this game."""
        return player in self.players
    
    def _next(self):
        """Advance to the next player."""
        self.current_turn += 1
        if self.current_turn == len(self.players):
            self.current_turn = 0
    
    def play(self, card):
        """
        Play a card. Raise an exception if this card cannot be played.
        """
        if self.status != 'in progress':
            raise InvalidStatusError("game is not in progress")
        
        top_card = self.get_top_card()
        
        # Is the card allowed to be played
        if(not card.is_wild() and card.colour != top_card.colour
                              and card.denomination != top_card.denomination):
            raise CannotPlayError("you must play a card of the same colour/denomination.")
        
        # Did it have any effects?
        if card.denomination == 'reverse':
            self._reverse()
            # For two-player Uno, reverse should do the same as skip
            if len(self.players) == 2:
                self._next()
        elif card.denomination == 'draw2':
            self._next()
            self.get_current_player().draw(2)
        elif card.denomination == 'wild4':
            self._next()
            self.get_current_player().draw(4)
        elif card.denomination == 'skip':
            self._next()
        
        # Put it on the discard pile
        self.discard_pile.insert(0, card)
        
        # Move to the next player
        self._next()
    
    def remove_player(self, player):
        """Remove a player from the game.
        
        Also dump their hand onto the discard pile, and check to make sure we
        still have at least two players."""
        if player not in self.players:
            raise UnoError("you are not in this game.")
        
        player = self.get_player(player)
        # Remove player from the game
        self.players.remove(player)
        
        # Extra things to do if the game is in progress
        if self.status == 'in progress':
            # If it was this player's turn, and they happened to be the last player
            # in the list, we need to change the current turn.
            if self.current_turn == len(self.players):
                self.current_turn = 0
            
            # Put their hand into the discard pile.
            # I don't even care if the game hasn't started yet.
            self.discard_pile += player.get_cards()
    
    def _reverse(self):
        """Reverse direction of play. Does NOT change whose turn it is."""
        current = self.get_current_player()
        self.players.reverse()
        self.current_turn = self.players.index(current)
    
    def set_last_action(self, action):
        """Set the last action performed by a player.
        
        Though it seems like bad design, this is set by the Player rather than
        the Game.
        """
        if action not in ('pass', 'draw', 'play'):
            raise UnoError("Unrecognised action: {0}".format(action))
        self.last_action = action
    
    def _set_status(self, status):
        """Sets the status of the game."""
        if status not in ('new', 'in progress', 'finished'):
            return ValueError("Unknown status: {0}".format(status))
        self.status = status
    
    def _shuffle(self):
        """
        Shuffles the discard pile onto the bottom of the draw pile, leaving the
        top card on the discard pile.
        
        Do not use Python's random.shuffle, because "for even rather small
        len(x)... most permutations of a long sequence can never be generated."
        """
        # Put the top card aside
        if self.status == 'in progress':
            top_card = self.get_top_card()
            self.discard_pile.remove(top_card)
        
        # Shuffle the rest of the discard pile back into the draw pile
        while self.discard_pile:
            card = random.choice(self.discard_pile)
            self.draw_pile.append(card)
            self.discard_pile.remove(card)
        
        # Put the top card back (assuming it's not None)
        if self.status == 'in progress':
            self.discard_pile.append(top_card)
    
    def start(self):
        """
        Start the game.
        
        First, shuffle the deck. Then draw hands for every player.
        
        Then drawsa random card onto the discard pile. If that card is a wild,
        redraw. If the card is some other special card we just treat it as a
        normal card. This isn't the standard Uno rules, but being skipped as the
        first player is kind of a dick design move.
        """
        if self.status is not 'new':
            raise InvalidStatusError("the game has already been started.")
        
        # Do we have at least two players?
        if len(self.players) < 2:
            raise TooFewPlayersError()
        # Shuffle the deck
        self.discard_pile += make_deck()
        self._shuffle()
        
        # Draw the players' hands
        for player in self.players:
            player.draw(self.starting_hand_size)
        
        # Then draw a starting card until we get a non-wild
        self.discard_pile.insert(0, self.draw()[0])
        while self.get_top_card().is_wild():
            self.discard_pile.insert(0, self.draw()[0])
        
        self._set_status('in progress')
    
    def win(self, player):
        """Sets player to the winner of this game."""
        if self.status != 'in progress':
            raise InvalidStatusError("Game is not in progress.")
        
        if player not in self.players:
            raise UnoError("Unknown Player cannot win the game.")
        
        self.winner = player
        self._set_status('finished')


class Player(object):
    """
    Represents a player. Stores what cards the player has, but not things like
    which game they're in. Could store the player's total points??
    """
    def __init__(self, identifier, game):
        """
        Represents a player.
        
        `identifier` is any unique way of identifying the player. It could be
        a nickname, for example.
        
        `game` is the game this player is a part of.
        """
        self.cards = []
        self.game = game
        self.identifier = identifier
        
        # Used to find out what the player got last time they drew
        self.last_draw = []
    
    def __eq__(self, other):
        """Equality test.
        
        If we're given a player object, check that our identifiers match.
        
        If we're not given a player object, assume we've been given an
        identifier instead and check whether that identifier matches.
        """
        if not isinstance(other, self.__class__):
            return self.identifier == other
        else:
            return self.identifier == other.identifier
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        return "<Player: {0}>".format(self)
    
    def __str__(self):
        """This lets us use the Player directly in string formatting."""
        return str(self.identifier)
    
    def draw(self, count = 1):
        """Draw the specified number of cards from the deck.
        
        This is an internally used command, rather than a deliberate player
        action.
        """
        self.last_draw = self.game.draw(count)
        self.cards += self.last_draw
        self.cards.sort()
    
    def get_cards(self):
        """Return the player's current hand."""
        return self.cards
    
    def get_identifier(self):
        """Return the player's identifier."""
        return self.identifier
    
    def has_card(self, card):
        """Return True if the player has this card in their hand.
        
        You can pass a string representation of a card, rather than a Card
        instance."""
        return card in self.cards
    
    def manual_draw(self):
        """Draw a card from the deck if you can't play.
        
        This is an action a player performs, rather than an internal
        command.
        """
        # Make sure it's our turn
        if self.game.get_current_player() != self:
            raise CannotPlayError("it's not your turn.")
        
        # Make sure the player hasn't already drawn
        if self.game.get_last_action() == 'draw':
            raise CannotPlayError("you cannot draw twice in the same turn.")
        else:
            self.draw(1)
            self.game.set_last_action('draw')
    
    def pass_turn(self):
        """Pass your turn."""
        # Make sure it's our turn
        if self.game.get_current_player() != self:
            raise CannotPlayError("it's not your turn.")
        
        if self.game.get_last_action() != 'draw':
            raise CannotPlayError("you have to draw before you can pass.")
        else:
            self.game.set_last_action('pass')
            self.game._next()
    
    def play(self, card):
        """
        Attempt to play the specified card.
        
        Raise an exception if the requested card cannot be played.
        """
        if self.game.get_current_player() != self:
            raise CannotPlayError("it's not your turn.")
        
        # Make sure they named a valid card
        try:
            card = Card(card)
        except InvalidCardError:
            raise
        
        if not self.has_card(card):
            raise CannotPlayError("you do not have that card.")
        
        if self.game.status != 'in progress':
            raise CannotPlayError("the game is not in progress.")
        
        # Enforce the check on playing a wild4 when you have a card in that colour
        if card.denomination == 'wild4' and self.game.strict_wild4_play:
            for owned_card in self.cards:
                if not owned_card.is_wild() and owned_card.colour == self.game.get_top_card.colour:
                    raise CannotPlayError("you cannot play a wd4 when you have another card to play.")
        
        try:
            self.game.play(card)
        except CannotPlayError:
            # This card can't be played right now
            raise
        
        self.cards.remove(card)
        self.game.set_last_action('play')
        
        if len(self.cards) == 0:
            self.game.win(self)
    
    def set_identifier(self, identifier):
        """
        Set the player's identifier.
        
        First check whether that player already exists in this game. If they do,
        raise an exception.
        
        This is probably unnecessary in the IRC package, as we're identifying
        by server-managed User objects rather than nicknames.
        """
        if self.game.has_player(identifier):
            raise UnoError("another player already exists with that identifier.")
        self.identifier = identifier


class Card(object):
    """
    Represents a card.
    """
    # The colours. Note that this order determines sorting.
    colours = ('red', 'green', 'yellow', 'blue')
    
    # The denominations. Wild should come before wild4, otherwise 'w g' would be
    # interpreted as 'wild4 green' instead of 'wild green'.
    # Note that this order determines sorting.
    denominations = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                     'draw2', 'reverse', 'skip', 'wild', 'wild4')
    
    def __init__(self, name):
        """Parse a string into a card. Raise an exception if we can't understand
        the string.
        
        We try to be generous with interpreting the name, ignoring whitespace
        and case. Arguments can be either <colour denomination> or
        <denomination colour>. However it will not parse text numbers into
        digits, so "red four" is not recognised.
        E.g.
            red 4
            r4
            red4
            4red
            rdr2
            r dr2
            r draw2
            red draw2
            wildg
            gwild
            gwd4
        """
        self.denomination = ''
        self.colour = ''
        
        # First remove any spaces and casing
        name = name.lower().replace(' ', '')
        
        # Fix up alterntive spellings of wild4 and draw2
        if 'dr2' in name:
            name = name.replace('dr2', 'draw2')
        if 'wd4' in name:
            name = name.replace('wd4', 'wild4')
        
        # Is the first letter a colour? Only check the first letter.
        for colour in Card.colours:
            # Try to match the colour to the start of the string
            if name.startswith(colour):
                rest = name.replace(colour, '', 1)
            elif name.startswith(colour[0]):
                rest = name[1:]
            else:
                continue
            
            # Then test whether the remaining string represents a denomination
            # Handle wild4 first since it contains 'wild'
            if 'wild4' in rest:
                self.denomination = 'wild4'
                self.colour = colour
                return
            
            for denomination in Card.denominations:
                if rest.startswith(denomination[0]):
                    # We have a valid card!
                    self.denomination = denomination
                    self.colour = colour
                    return
    
        # It didn't start with a colour.
        # Maybe they put the denomination first instead?
        for denomination in Card.denominations:
            if name.startswith(denomination):
                rest = name.replace(denomination, '', 1)
            elif name.startswith(denomination[0]):
                rest = name[1:]
            else:
                continue
            
            # Then test whether the remaining string is a colour
            for colour in Card.colours:
                if rest.startswith(colour[0]):
                    # We have a valid card!
                    self.denomination = denomination
                    self.colour = colour
                    return
        
        # We can't parse this mess
        raise InvalidCardError("I didn't recognise that card.")
    
    def __cmp__(self, other):
        """
        Compare to other. Return -1 if self < other, 0 if self == other, 1 if
        self > other.
        
        Because wilds are always coloured blue in the deck, they appear at the
        end of every list.
        """
        if not isinstance(other, self.__class__):
            raise ValueError("You can't compare these!")
        
        # If they're equal, return zero
        if self == other:
            return 0
        
        # If their colours differ, compare by those
        if self.colour != other.colour:
            return Card.colours.index(self.colour) - Card.colours.index(other.colour)
        
        # Otherwise, compare by denomination
        return Card.denominations.index(self.denomination)  \
             - Card.denominations.index(other.denomination)
    
    def __eq__(self, other):
        """Test whether we're equal to another card. Wild cards ignore colour,
        so that a player trying to play a green wild will match the red wild in
        his hand.
        
        If we're not given a Card, attempt to make a Card instance out of
        whatever we've been given (presumably a string).
        """
        # If we're not given a card object, try to make one.
        # Maybe we were passed a string naming a card?
        if not isinstance(other, self.__class__):
            try:
                other = Card(other)
            except InvalidCardError:
                return False
        
        # Make sure we're the same denomination
        if self.denomination != other.denomination:
            return False
        
        # Make sure the colours match (or wild)
        return self.colour == other.colour or self.is_wild()
    
    def __ne__(self, other):
        """Not-equal operator."""
        return not self.__eq__(other)
    
    def __repr__(self):
        """Prints a representation of the card. Uses the __str__ method."""
        return '<Card: {0}>'.format(self)
    
    def __str__(self):
        """Return a string suitable for passing to the Card constructor."""
        return '{0} {1}'.format(self.colour, self.denomination)
    
    def is_wild(self):
        """Return True if wild or wild4."""
        return self.denomination in ('wild', 'wild4')
    
    def value(self):
        """Return the points value of the card."""
        # Numbers are worth face value
        try:
            return int(self.denomination)
        except ValueError:
            # Wilds are worth 50
            if self.is_wild():
                return 50
            # Other special cards are worth 20
            else:
                return 20   


# Custom exception classes
class UnoError(Exception):
    """Base Uno Error class."""
    
class CannotPlayError(UnoError):
    """Raised when you try to make an invalid move."""
    
class InvalidCardError(UnoError):
    """Raised when you try to parse an invalid card name."""
    
class TooFewPlayersError(UnoError):
    """Raised when you try to start a game with too few players."""
    
class InvalidStatusError(UnoError):
    """Raised when the game hasn't started, or has finished."""
