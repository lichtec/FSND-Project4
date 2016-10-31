"""models.py - This file contains the class definitions for the Datastore
entities used by the Hangman game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

from protorpc import messages, message_types
from google.appengine.ext import ndb
from gameLogic import *
from datetime import date

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
    cancel = ndb.BooleanProperty(required=True, default=False)
    challenger = ndb.KeyProperty(required=True, kind='User')
    challenged = ndb.KeyProperty(required=True, kind='User')
    guesses = ndb.StringProperty(required=False, repeated=True)
    
    @classmethod
    def new_game(cls, challenger, objective, difficulty, challenged, hint):
        """Creates and returns a new game"""
        values = get_point_guesses(difficulty, objective)
        game = Game( challenger=challenger,
                    challenged = challenged,
                    objective = objective,
                    cur_view = get_Cur_View(objective, '', ''),
                    hint = hint,
                    difficulty = difficulty,
                    attempts_remaining = int(values[0]),
                    points = values[1],
                    game_over=False,
                    cancel=False,
                    guesses=[]
                   )
        game.put()
        return game
    
    def to_form(self, message=''):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.challenger = self.challenger.get().name
        form.cur_view = self.cur_view
        form.challenged = self.challenged.get().name
        form.hint = self.hint
        form.difficulty = self.difficulty
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.cancel = self.cancel
        form.guesses = self.guesses
        form.message = message
        return form
    
    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        game = self.key
        # Add the game to the score 'board'
        if(won==True):
            scoreWin = Score(user=self.challenged, date=date.today(), won=won,
                      points=self.points, game=game)
            scoreLost = Score(user=self.challenger, date=date.today(), won=False,
                      points=0, game=game)
        else:
            scoreWin = Score(user=self.challenger, date=date.today(), won=True,
                      points=self.points, game=game)
            scoreLost = Score(user=self.challenged, date=date.today(), won=won,
                      points=0, game=game)
        scoreWin.put()
        scoreLost.put()

    
class Score(ndb.Model):
    won = ndb.BooleanProperty(required=True)
    date = ndb.DateProperty(required=True)
    points = ndb.IntegerProperty(required=True)
    user = ndb.KeyProperty(required=True, kind='User')
    game = ndb.KeyProperty(required=True, kind='Game')


    @classmethod
    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=self.date, points=self.points)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    challenger = messages.StringField(2, required=True)
    cur_view = messages.StringField(3, required=True)
    challenged = messages.StringField(4, required=True)
    hint = messages.StringField(5, required=False)
    difficulty = messages.StringField(6, required=True)
    attempts_remaining = messages.IntegerField(7, required=True)
    game_over = messages.BooleanField(8, required=True)
    cancel = messages.BooleanField(9, required=True)
    guesses = messages.StringField(10, required=False, repeated=True)
    message = messages.StringField(11, required=True)

class NewGameForm(messages.Message):
    challenger = messages.StringField(1, required=True)
    objective = messages.StringField(2, required=True)
    difficulty = messages.StringField(3, required=True)
    challenged = messages.StringField(4, required=False)
    hint = messages.StringField(5, required=True)

class GameForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    guess = messages.StringField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    won = messages.BooleanField(2, required=True)
    date = message_types.DateTimeField(3, required=True)
    points = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
