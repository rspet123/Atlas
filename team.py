from user import User


class Team:
    players = []
    team_name = ""
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
        self.team_rating = 0
        self.captain = captain

    def add_player(self, player: User, role: str):
        """
        This function adds a player to the team and updates the team rating

        :param player: The player to be added to the team
        :type player: User
        :param role: The role of the player in the team
        :type role: str
        """
        self.players[player] = role
        self.team_rating += player.get_rating(role)[0]

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
