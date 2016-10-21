# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
#from google.appengine.api import memcache
#from google.appengine.api import taskqueue

from models import User, StringMessage, Game, Score, GameForm, NewGameForm, MakeMoveForm, ScoreForm, ScoreForms

from utils import get_by_urlsafe

from gameLogic import gameLogic

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(MakeMoveForm, urlsafe_game_key=messages.StringField(1))
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1), email=messages.StringField(2))

from settings import WEB_CLIENT_ID

API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
EMAIL_SCOPE = endpoints.EMAIL_SCOPE

#MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='hangman', version='v1', allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
    scopes=[EMAIL_SCOPE])
class HangmanAPI(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='put')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        challenger = User.query(User.name == request.challenger).get()
        challenged = User.query(User.name == request.challenged).get()
        if not challenger or not challenged:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        print challenger.key
        print request.objective
        print request.difficulty
        print challenged.key
        print request.hint
        game = Game.new_game(challenger.key[1], request.objective, request.difficulty, challenged.key[1], request.hint)

        return game.to_form('Good luck playing Guess a Number!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')

#        game.attempts_remaining -= 1
        if request.guess in game.guesses:
            return game.to_form('Guess already made')


        game.cur_view, success = gameLogic.get_Cur_View(game.objective, game.cur_view, request.guess)
        game.guesses.append(guess)
        if success:
            if game.cur_view == game.objective:
                game.end_game(True)
                return game.to_form('You Win. {0} points awarded'.format(game.points))
            else:
                game.put()
                return game.to_form('Nice guess. Current results: {0}'.format(game.cur_view))
        else:
            game.attemps_remaining -= 1
            if game.attempts_remaining < 1:
                game.end_game(False)
                return game.to_form('Terrible guess and now Game Over')
            else:
                game.put()
                return game.to_form('Terrible guess')
api = endpoints.api_server([HangmanAPI])
