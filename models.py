"""models.py - This file contains the class definitions for the Datastore
entities used by the Hangman game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

from protorpc import messages
from google.appengine.ext import ndb
from gameLogic import get_point_guesses, get_Cur_View

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()
    
class Game(ndb.Model):
    """Game object"""
    objective = ndb.StringProperty(required=True) #Word or Phrase
    cur_view = ndb.StringProperty(required=True)
    hint = ndb.StringProperty(required=False) #Hint for the objective if offered
    difficulty = ndb.StringProperty(required=True) #Sets the amount of guesses allowed, relates to points too
    attempts_remaining = ndb.IntegerProperty(required=True)
    points = ndb.IntegerProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    challengee = ndb.KeyProperty(required=True, kind='User')
    guesses = ndb.StringProperty(required=True, repeated=True)
    
    @classmethod
    def new_game(user, objective, hint='', difficulty, challengee):
        """Creates and returns a new game"""
        values = getDiff(difficulty)
        game = Game( user=user,
                    chanllengee = challengee,
                    objective = objective,
                    cur_view = get_Cur_View(objective, '')[0],
                    hint = hint,
                    difficulty = difficulty,
                    attempts_remaining = values[0],
                    points = values[1],
                    game_over=False,
                    guesses=[]
                   )
        game.put()
        return game
    
    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.cur_view = self.cur_view
        form.challengee = self.challengee
        form.hint = self.hint
        form.difficulty = self.difficulty
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.guesses = self.guesses
        form.message = message
        return form
    
    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      points=points)
        score.put()

    
class Score(ndb.Model):
    won = ndb.BooleanProperty(required=True),
    date = ndb.DateProperty(required=True),
    points = ndb.IntegerProperty(required=True),
    user = ndb.KeyProperty(required=True, kind='User')

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), points=self.points)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    user_name = messages.StringField(2, required=True)
    cur_view = messages.StringField(3, required=True)
    challengee = messages.StringField(4, required=True)
    hint = messages.StringField(5, required=False)
    difficulty = messages.StringField(6, required=True)
    attempts_remaining = messages.IntegerField(7, required=True)
    game_over = messages.BooleanField(8, required=True)
    guesses = messages.StringField(9, required=True, repeated=True)
    message = messages.StringField(10, required=True)
##########################################################################

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    guess = messages.StringField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    won = messages.BooleanField(2, required=True)
    date = messages.DateField(3, required=True)
    points = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
