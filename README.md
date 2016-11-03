# FSND-Project 4

##Description:
Udacity Full Stack Nanodegree Project 4. Creating a Google Appengine web application api for playing a game of hangman. Users are able to challenger each other and receive points from wins.

##Game Description:
Hangman is a phrase guessing game. Each game is initiated with a challenger and 
a challenged. The challenger sets the objective, the difficulty (must 
be the followingg: UPER_EASY, EASY, MEDIUM, HARD, STUPID, the challenged, 
the challenger(themselves) and a hint. The game logic then sets the attempts remaining,
points, and the current view. The challenged receives an email notification 
about the game. Then the challenged can reveiw the game or make move. A move is a
single character. If they are right then they don't loose an attempt, if they are wrong
then they loose a remaining attemp. If they are out of attempts, the challenged looses
the game and the points are awarded to the challenger. If they get the objective correct
before the attempts run out, they receive the points. A user can cancel an active game.

##Notes on Attempts
When setting the difficulty this also relates to the attempts allowed. The attempts are
calculated in the following way.
- 'SUPER_EASY': 2 per unique character
- 'EASY': 1 per unique character
- 'MEDIUM': .5 per unique character 
- 'HARD': .25 per unique character
- 'STUPID': one attempt only

##Scoring
Difficulty also sets the points and scoring. Points are calculated in the following way.
- 'SUPER_EASY': 1 per unique character
- 'EASY': 2 per unique character
- 'MEDIUM': 3 per unique character 
- 'HARD': 4 per unique character
- 'STUPID': 5 per unique character

Points are awarded to the challenger when the challenged does not guess the objective in the 
allowed attempts. If the challenged does guess the objective in the allowed attempts then they
receive the points.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.
 - gameLogic.py: Helper function to create current view and set the points
  and the attempts for a new game.
  


##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email, total_points
    - Returns: NewUserForm
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists. Also
    requires email and total_points. Total points are used for ranking.
    
 - **get_user**
    - Path: 'user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: UserForm
    - Description: Returns a user based on username query. Gives current user information.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: challenger, challenged, difficulty, hint, objective
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. Challenger and challenged provided must 
    correspond to an existing user - will raise a NotFoundException if not. Challenger
    and challenged cannot be the same user. Also adds a task to a task queue to
    to send an email to the challenged.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **get_game_history**
    - Path: 'game/{urlsafe_game_key}/history'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game and its history.
    Almost a duplication of get_game but here for further expansion if needed.    

 - **get_user_game**
    - Path: 'game/user/{user_name}'
    - Method: GET
    - Parameters: username
    - Returns: Gameforms with current game state.
    - Description: Returns all currently active games for a single user. Includes
    challenges and challenged.

 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Accepts a 'guess' and returns the updated state of the game.
    If this causes a game to end, a corresponding Score entity will be created
    for both users. It also enques a task to send an email to the challenger 
    about the end of the game. This will also update a user's total points as
    necessary for ranking.

 - **cancel_game**
    - Path: 'game/cancel/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Allows a user to cancel a game as long as it is active.

 - **get_ranks**
    - Path: 'ranks'
    - Method: GET
    - Parameters: None
    - Returns: UserForms.
    - Description: Returns all users ordered by total_points desc. This is
    the current ranking of the users.
    
    
##Models Included:
 - **User**
    - Stores unique user_name, email address, and total points.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
##Forms Included:
 - **NewUserForm**
    - Representation of a new user(name, email, total_points).
 - **UserForm**
    - Representation of a user(name, email, total_points).
 - **UserForms**
    - Multiple UserForm container.
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, challenger,
    cur_view, challenged, hint, difficulty, attempts_remaining,
    game_over, cancel, guesses, message).
 - **GameForms**
    - Multiple GameForm container.
 - **NewGameForm**
    - Used to create a new game (challenger, objective, difficulty,
    challenged, hint)
 - **MakeMoveForm**
    - Inbound make move form (guess).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, won, date,
    points).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.