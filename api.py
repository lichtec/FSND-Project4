# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from utils import get_by_urlsafe
from settings import WEB_CLIENT_ID
from gameLogic import *
from models import (
    User,
    StringMessage,
    Game,
    Score,
    GameForm,
    GameForms,
    NewGameForm,
    MakeMoveForm,
    ScoreForm,
    ScoreForms,
    NewUserForm,
    UserForm,
    UserForms )

DIFF = ['SUPER_EASY', 'EASY', 'MEDIUM', 'HARD', 'STUPID']

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1))
CANCEL_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm, urlsafe_game_key=messages.StringField(1))
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1))
NEW_USER_REQUEST = endpoints.ResourceContainer(NewUserForm)
GET_USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1))

API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
EMAIL_SCOPE = endpoints.EMAIL_SCOPE


@endpoints.api(name='hangman', version='v1',
               allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
               scopes=[EMAIL_SCOPE])
class HangmanAPI(remote.Service):
    """Game API"""
    # USER Endpoints
    @endpoints.method(request_message=NEW_USER_REQUEST,
                      response_message=UserForm,
                      path='user',
                      name='create_user',
                      http_method='PUT')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User.new_user(name=request.name, email=request.email,
                             total_points=request.total_points)
        return user.to_form('Welcome {} to hangman!'.format(user.name))

    @endpoints.method(request_message=GET_USER_REQUEST,
                      response_message=UserForm,
                      path='user/{user_name}',
                      name='get_user',
                      http_method='get')
    def get_user(self, request):
        """Get a User."""
        user = User.query(User.name == request.user_name).get()
        return user.to_form('Welcome {} to hangman!'.format(user.name))

    # GAME Endpoints
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
        if challenger == challenged:
            raise endpoints.ForbiddenException('Challenger and Challenged\
                                               cannot be the same user.')
        if request.difficulty.upper() not in DIFF:
            raise endpoints.ForbiddenException(
                'Difficulty must be one of the following: SUPER_EASY, EASY,\
                MEDIUM, HARD, STUPID')
        if len(request.objective) < 1:
            raise endpoints.ForbiddenException('Objective must be at least 1 character')
        game = Game.new_game(challenger.key, request.objective,
                             request.difficulty, challenged.key, request.hint)
        taskqueue.add(params={'email': challenged.email,
                              'challenger': challenger.name,
                              'gameInfo': repr(game)},
                      url='/tasks/send_confirmation_email')
        return game.to_form('Good luck playing Hangman!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return the history of a game."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='game/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Returns all of an individual User's Games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        games = Game.query(ndb.AND(
            Game.game_over == False,
            ndb.AND(
                Game.cancel == False,
                ndb.OR(
                    Game.challenger == user.key,
                    Game.challenged == user.key))))
        return GameForms(items=[game.to_form() for game in games])

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        challenged = game.challenged.get()
        challenger = game.challenger.get()
        if game.game_over:
            raise endpoints.ForbiddenException('Game already over!')

        if request.guess in game.guesses:
            return game.to_form('Guess already made')

        if len(request.guess) > 1 or not request.guess.isalpha():
            raise endpoints.ForbiddenException('Guess must be only 1 character')

        game.cur_view, success = get_Cur_View(game.objective,
                                              game.cur_view, request.guess)
        game.guessLog.append('Guess: {0}, Result {1}, Current View: {2}'.format(
            request.guess, success, game.cur_view))
        game.guesses.append(request.guess)
        if success:
            if game.cur_view == game.objective:
                game.end_game(True)
                taskqueue.add(
                    params={'email': challenger.email,
                            'challenged': challenged.name,
                            'gameInfo': repr(game)},
                    url='/tasks/send_end_game_email')
                return game.to_form('You Win. {0} points awarded'.format(
                    game.points))
            else:
                game.put()
                return game.to_form('Nice guess. Current results: {0}'.format(
                    game.cur_view))
        else:
            game.attempts_remaining -= 1
            if game.attempts_remaining < 1:
                game.end_game(False)
                taskqueue.add(
                    params={'email': challenger.email,
                            'challenged': challenged.name,
                            'gameInfo': repr(game)},
                    url='/tasks/send_end_game_email')
                return game.to_form('Terrible guess and now Game Over')
            else:
                game.put()
                return game.to_form('Terrible guess')

    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Cancel a game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.game_over or game.cancel:
                raise endpoints.ForbiddenException('Game cannot be cancelled, game over')
            else:
                game.cancel = True
                game.put()
                return game.to_form('Game cancelled.')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(
        response_message=UserForms,
        path='ranks',
        name='get_ranks',
        http_method='GET')
    def get_ranks(self, request):
        """Get all user rankings."""
        users = User.query().order(-User.total_points)
        return UserForms(items=[user.to_form('') for user in users])

api = endpoints.api_server([HangmanAPI])
