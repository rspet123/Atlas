from user import User, get_user_by_bnet
from db import teams
from openskill import Rating


class Team:
    players = []
    team_name = ""
    avg_player_rating = 0
    team_rating = {"mu": 0, "sigma": 0}  # We want to store this as a dict so we can easily retrieve it from our db
    captain = ""
    new_team = True
    eligible = False

    def __init__(self, team_name: str, captain: str, players=None, avg_player_rating=0, team_rating=None,
                 eligible=False):
        """
        This function creates a new team object and inserts it into the database

        :param team_name: The name of the team
        :type team_name: str
        :param captain: The captain of the team
        :type captain: captain's Bnet name
        :param players: a dictionary of players in the team, with their bnet_name as the key and their rating as the value
        :param avg_player_rating: The average rating of all the players on the team, defaults to 0 (optional)
        :param team_rating: The rating of the team. This is a dictionary with two keys: mu and sigma
        :param eligible: whether the team is eligible to queue, defaults to False (optional)
        """
        if team_rating is None:
            team_rating = {"mu": 0, "sigma": 0}
        if players is None:
            players = {}
        self.team_name = team_name
        self.players = players
        self.avg_player_rating = avg_player_rating
        self.team_rating = team_rating
        self.captain = captain
        self.new_team = (not len(players) >= 6)
        self.eligible = eligible

        try:
            teams.insert_one({"_id": self.team_name,
                              "players": self.players,
                              "avg_player_rating": self.avg_player_rating,
                              "captain": self.captain,
                              "team_rating": self.team_rating,
                              "eligible": self.eligible})
        except Exception as e:
            # Probably this lol
            print(f"There is already a team named {self.team_name}")

    def add_player(self, player: User, role: str):
        """
        This function adds a player to the team and updates the team's rating

        :param player: User
        :type player: User
        :param role: str
        :type role: str
        """
        self.players[player.bnet_name] = role
        self.avg_player_rating += player.get_rating(role).mu  # Get Mu
        if len(self.players) >= 6 & self.new_team:
            self.team_rating = {"mu": self.avg_player_rating / len(self.players), "sigma": 3}
            self.new_team = False
            self.eligible = True
        teams.replace_one({"_id": self.team_name}, self.as_json())

    def remove_player(self, player: User):
        """
        This function removes a player from the team

        :param player: The player to remove from the team
        :type player: User
        """
        del (self.players[player])

    def get_rating(self):
        """
        It returns a Rating object with the mu and sigma values of the team rating
        :return: The rating of the team.
        """
        return Rating(self.team_rating["mu"], self.team_rating["sigma"])

    def set_eligible(self):
        self.eligible = True

    def set_ineligible(self):
        """
        This function sets the eligibility of a team to False.
        """
        self.eligible = False

    def __repr__(self):
        """
        The __repr__ function returns a string that represents the object
        :return: The team name and the average rating of the team.
        """
        return f"Team:{self.team_name} " \
               f"Average Rating:{self.team_rating['mu'] / len(self.players)} " \
               f"Captain: {self.captain} "

    def as_json(self):
        """
        It returns a dictionary of the team's attributes
        :return: A dictionary with the team name, players, avg_player_rating, team_rating, and captain.
        """
        return {"_id": self.team_name,
                "players": self.players,
                "avg_player_rating": self.avg_player_rating,
                "team_rating": self.team_rating,
                "captain": self.captain,
                "eligible": self.eligible}

    def get_roster(self) -> list[User]:
        """
        `get_roster` returns a list of `User` objects for each player in the `Team` object
        :return: A list of User objects
        """
        out = []
        for player in self.players:
            out.append(get_user_by_bnet(player))
        return out


def team_from_json(data: dict) -> Team:
    """
    It takes a dictionary and returns a Team object
    :param data: dict
    :type data: dict
    :return: A Team object
    """
    return Team(data["team_name"],
                data["captain"],
                data["players"],
                data["avg_player_rating"],
                data["team_rating"],
                data["eligible"])


def get_team_by_name(team_name: str) -> Team:
    """
    It takes a team name as a string and returns a Team object from the db

    :param team_name: The name of the team you want to get
    :type team_name: str
    :return: A Team object
    """
    return team_from_json(teams.find_one({"_id": team_name}))


if __name__ == '__main__':
    team_a = Team("Team Poggers Mountain", "player0")
    for i in range(3, 10):
        team_a.add_player(get_user_by_bnet(f"player{i}"), "support")
    print(team_a)
    print(team_a.get_roster())
