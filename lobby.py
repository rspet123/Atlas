import random
from user import *
from playerqueue import matchmake_3
from db import lobbies, users


class Lobby:
    team_1 = []
    team_2 = []
    lobby_name = ""
    completed = False

    def __init__(self, team_1: list, team_2: list):
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
        # Randomly selecting a player from the lobby to be the host.
        host_idx = random.randint(0, 11)
        host = (team_1 + team_2)[host_idx]["bnet"]
        # Taking the hash of the two lists and taking the first 8 characters to make the lobby name
        self.lobby_name = str(hash(host_idx) + hash(str(team_1)) + hash(str(team_2)))[:8]
        self.completed = False
        lobbies.insert_one({"_id": self.lobby_name, "host": host, "team_1": team_1, "team_2": team_2})

    def complete(self):
        """
        sets "Complete" flag as true
        """
        # TODO delete the object and return a match object
        self.completed = True

    def get_lobby_name(self):
        """
        This function returns the lobby name
        :return: The lobby name.
        """
        return self.lobby_name


def display_lobby(lobby_id: str) -> dict:
    lobby = lobbies.find_one({"_id": lobby_id})
    team_1 = []
    team_2 = []
    for player in lobby["team_1"]:
        team_1.append(users.find_one({"bnet":player["bnet"]}))
    for player in lobby["team_2"]:
        team_2.append(users.find_one({"bnet":player["bnet"]}))
    return {"id":lobby["_id"],"host":lobby["host"],"team_1":team_1,"team_2":team_2}

if __name__ == '__main__':
    team1,team2 = matchmake_3()

    lobbyx = Lobby(team1,team2)
    print(lobbyx.get_lobby_name())
    print(display_lobby(lobbyx.get_lobby_name()))