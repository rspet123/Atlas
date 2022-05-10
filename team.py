from user import User
from db import teams


class Team:
    players = []
    team_name = ""
    avg_player_rating = 0
    team_rating = 0
    captain = ""

    def __init__(self, team_name: str, captain: User):
        """
        This function initializes a team object with a team name, a list of players, a team rating, and a captain.

        :param team_name: The name of the team
        :type team_name: str
        :param captain: The captain of the team
        :type captain: User
        """
        self.team_name = team_name
        self.players = {}
        self.avg_player_rating = 0
        self.team_rating = 0
        self.captain = captain
        try:
            teams.insert_one({"_id": self.team_name,
                              "players": self.players,
                              "avg_player_rating": self.avg_player_rating,
                              "team_rating": self.team_rating,
                              "captain": self.captain.bnet_name})
        except Exception as e:
            print(f"There is already a team named {self.team_name}")

    def add_player(self, player: User, role: str):
        """
        This function adds a player to the team and updates the team rating

        :param player: The player to be added to the team
        :type player: User
        :param role: The role of the player in the team
        :type role: str
        """
        # TODO add db
        self.players[player.bnet_name] = role
        self.avg_player_rating += player.get_rating(role)[0]

    def remove_player(self, player: User):
        """
        This function removes a player from the team

        :param player: The player to remove from the team
        :type player: User
        """
        del (self.players[player])

    def __repr__(self):
        """
        The __repr__ function returns a string that represents the object
        :return: The team name and the average rating of the team.
        """
        return f"Team:{self.team_name} " \
               f"Average Rating:{self.team_rating / len(self.players)} " \
               f"Captain: {self.captain.name} "

    def as_json(self):
        return {"_id": self.team_name,
                "players": self.players,
                "avg_player_rating": self.avg_player_rating,
                "team_rating": self.team_rating,
                "captain": self.captain.bnet_name}
