"""models.py - This file contains the class definitions for the Datastore
entities used by the Hangman game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

from protorpc import messages
from google.appengine.ext import ndb

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()
    
class Game(ndb.Model):
    """Game object"""
    objective = ndb.StringProperty(required=True)
    hint = ndb.StringProperty(required=False)
    difficulty = ndb.StringProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True, default=5)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    challengee = ndb.KeyProperty(required=True, kind='User')
    
    @classmethod
    def new_game(user, objective, hint='', difficulty, challengee):
        """Creates and returns a new game"""
        game = Game( user=user,
                    chanllengee = challengee
                    objective = objective,
                    hint = hint,
                    difficulty = difficulty,
                    attempts_remaining = getDiff(difficulty)
                    game_over=False)
        game.put()
        return game
    
    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.challengee = self.challengee
        form.hint = self.hint
        form.difficulty = self.difficulty
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.message = message
        return form
    
    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      guesses=self.attempts_allowed - self.attempts_remaining)
        score.put()

    
class Score
    challenges_won = ndb.IntegerProperty(required=True),
    challenges_lost = ndb.IntegerProperty(required=True),
    points = ndb.IntegerProperty(required=True),
    user = ndb.KeyProperty(required=True, kind='User')