"""Simple module to return the point value and guesses
from the difficulty of an objective"""

guessCal = {'SUPER_EASY':[2.0, 1], 'EASY':[1.0,2], 'MEDIUM':[.5,3], 'HARD':[.25,4], 'STUPID':[0,5]}

class gameLogic():
    def get_point_guesses(difficulty, objective):
        unique = len(set(objective))
        guesses = round(unique * guessCal[difficulty][0])
        points = unique * guessCal[difficulty][1]
        return guesses, points
