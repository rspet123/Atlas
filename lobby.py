import random
from user import *
from playerqueue import matchmake_3

class Lobby:
    team_1 = []
    team_2 = []
    lobby_name = ""
    completed = False

    def __init__(self, team_1:list,team_2:list):
        """
        The function takes two lists of players and creates a lobby name by adding the hashes of the two lists and taking
        the first 8 characters

        :param team_1: list of players in team 1
        :type team_1: list
        :param team_2: list
        :type team_2: list
        """
        self.team_1 = team_1
        self.team_2 = team_2
        self.lobby_name = (hash(str(team_1)) + hash(str(team_2)))[:8]
        self.completed = False

    def complete(self):
        """
        sets "Complete" flag as true
        """
        # TODO delete the object and return a match object
        self.completed = True




