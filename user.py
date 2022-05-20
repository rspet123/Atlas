import db
from openskill import Rating, rate, predict_win
import random


class User:
    discord_name = ""
    bnet_name = ""
    preferred_roles = []
    info = ""
    avatar = ""
    discord_id = ""
    name = ""
    user_id = ""
    role_ranks = {}
    role_ratings = {}

    def __init__(self, discord_name: str, bnet_name: str, preferred_roles: list, avatar: str, player_id: int, name: str,
                 role_ranks: dict, update_db=True, ratings=None):
        """
        creates our new player object, as well as turning SR into our rating system

        :param discord_name: The user's discord name
        :type discord_name: str
        :param bnet_name: The battletag of the user
        :type bnet_name: str
        :param preferred_roles: A list of roles that the user prefers to play
        :type preferred_roles: list
        :param avatar: The URL of the user's avatar
        :type avatar: str
        :param id: The discord id of the user
        :type id: str
        :param name: The name of the user
        :type name: str
        :param role_ranks: a dictionary of the user's role ranks
        :type role_ranks: dict
        :param update_db: Whether or not to update the database with the new user, defaults to True (optional)
        """
        self.discord_name = discord_name
        self.bnet_name = bnet_name
        self.preferred_roles = preferred_roles
        self.discord_id = player_id
        self.info = ""
        self.avatar = avatar
        self.name = name
        self.role_ranks = role_ranks
        if ratings is None:
            self.role_ratings = {"tank": {"sigma": 0, "mu": 0},
                                 "dps": {"sigma": 0, "mu": 0},
                                 "support": {"sigma": 0, "mu": 0}}
            for role in role_ranks.items():
                self.role_ratings[role[0]]["sigma"] = Rating((role[1] / 100), 8.33333).sigma
                self.role_ratings[role[0]]["mu"] = Rating((role[1] / 100), 8.33333).mu
                print(f"Setting {role[0]} to {(role[1] / 100)} for {self.name}")
        else:
            self.role_ratings = ratings

        if update_db:
            db.users.insert_one({"_id": discord_name,
                                 "bnet": bnet_name,
                                 "roles": preferred_roles,
                                 "info": self.info,
                                 "avatar": avatar,
                                 "id": self.discord_id,
                                 "name": name,
                                 "ranks": role_ranks,
                                 "ratings": self.role_ratings})

    def __repr__(self):
        """
        This function returns a string that contains the name, bnet name, and role ratings of the player
        :return: The name, bnet name, and role ratings for the player.
        """
        return f"Name: {self.name}, bnet: {self.bnet_name}" \
               f" DPS: {self.role_ratings['dps']}" \
               f" Support: {self.role_ratings['support']}" \
               f" Tank: {self.role_ratings['tank']}"

    def __hash__(self):
        """
        The hash function is used to return a unique integer for each unique object
        :return: The hash of the name attribute of the object.
        """
        return hash(self.name)

    def to_dict(self):
        """
        It returns a dictionary of the user's information for database use
        :return: A dictionary with the keys: _id, bnet, roles, info, avatar, id, name, ranks, ratings
        """
        return {"_id": self.discord_name,
                "bnet": self.bnet_name,
                "roles": self.preferred_roles,
                "info": self.info,
                "avatar": self.avatar,
                "id": self.discord_id,
                "name": self.name,
                "ranks": self.role_ranks,
                "ratings": self.role_ratings}

    def update(self):
        db.users.replace_one({"_id": self.discord_name}, {"_id": self.discord_name,
                                                          "bnet": self.bnet_name,
                                                          "roles": self.preferred_roles,
                                                          "info": self.info,
                                                          "avatar": self.avatar,
                                                          "id": self.user_id,
                                                          "name": self.name,
                                                          "ranks": self.role_ranks,
                                                          "ratings": self.role_ratings})

    def update_rating(self, role: str, new_rating: Rating):
        """
        It updates the user's rating for a given role, and then updates the database with the new rating

        :param role: the role you want to update
        :param new_rating: Rating = (mu, sigma)
        :type new_rating: Rating
        """
        self.role_ratings[role]["mu"] = float(new_rating.mu)
        self.role_ratings[role]["sigma"] = float(new_rating.sigma)
        this_user = self.to_dict()
        db.users.update_one({"bnet": self.bnet_name}, update={"$set": this_user})

    def get_rating(self, role):
        """
        It returns a player's openskill rating object

        :param role: The role you want to get the rating for
        :return: A Rating object with the mu and sigma values of the role.
        """
        return Rating(self.role_ratings[role]["mu"], self.role_ratings[role]["sigma"])


def create_user_from_json(data: dict):
    """
    It takes a dictionary of data and returns a new user object

    :param data: The JSON data that is being passed in
    :type data: dict
    :return: A new user object
    """
    new_user = User(data["_id"], data["bnet"], data["roles"], data["avatar"], data["id"], data["name"], data["ranks"],
                    False, data["ratings"])
    return new_user


def get_user_by_bnet(bnet: str):
    """
    > This function takes a bnet and returns a user

    :param bnet: The battlenet ID of the user
    :type bnet: str
    :return: A user object
    """
    this_user = db.users.find_one({"bnet": bnet})
    return create_user_from_json(this_user)


def get_user_by_id(id: int):
    """
    > This function takes a bnet and returns a user

    :param bnet: The discord ID of the user
    :type bnet: str
    :return: A user object
    """
    this_user = db.users.find_one({"id": id})
    if this_user is None:
        return None
    return create_user_from_json(this_user)


def get_user_by_discord(discord: str):
    """
    `get_user_by_discord` takes a discord name and returns the user object from the database

    :param discord: The discord name of the user
    :type discord: str
    :return: A user object
    """
    this_user = db.users.find_one({"_id": discord})
    if this_user is None:
        return None
    return create_user_from_json(this_user)


def get_all_users():
    """
    > This function returns a list of all the users in the database
    :return: A list of all the users in the database.
    """
    users = list(db.users.find())
    return users


def update_player_hero_stats(bnet: str, hero_stats: dict):
    """
    This function takes a battletag and a dictionary of hero stats, and adds the hero stats to the user's hero stats

    :param bnet: str = The user's battletag
    :type bnet: str
    :param hero_stats: dict
    :type hero_stats: dict
    :return: Nothing, Updates database (or sometime None)
    """
    this_user = db.users.find_one({"bnet": bnet})
    if "hero_stats" not in this_user:
        print(f"No Hero Stats for {this_user['_id']}")
        this_user["hero_stats"] = hero_stats
        db.users.update_one({"_id": this_user["_id"]}, update={"$set": this_user})
        return None
    for k, v in hero_stats.items():
        # k = Hero name
        # v = hero stats
        if k not in this_user["hero_stats"]:
            # if the hero isn't found, we just add the hero data straight from the dict, no need to add prev data
            print(f"No {k} Stats for {this_user['_id']}")
            this_user["hero_stats"][k] = v
        else:
            for stat, val in v.items():
                this_user["hero_stats"][k][stat] += val
    db.users.update_one({"_id": this_user["_id"]}, update={"$set": this_user})


def adjust_team_rating(team_1: list, team_2: list, winner: str):
    """
    It takes in two lists of players, and a winner, and updates the ratings of the players in the database

    :param team_1: list of players in team 1
    :type team_1: list
    :param team_2: list of players in team 2
    :type team_2: list
    :param winner: 1 or 2, depending on which team won
    :type winner: str
    :return: 0 if we aren't given a winner, else void
    """
    team_1_players = [[get_user_by_bnet(player["bnet"]), player["queued_role"]] for player in team_1]
    team_2_players = [[get_user_by_bnet(player["bnet"]), player["queued_role"]] for player in team_2]
    team_1_ratings = [player[0].get_rating(player[1]) for player in team_1_players]
    team_2_ratings = [player[0].get_rating(player[1]) for player in team_2_players]

    if winner == "1":
        new_1, new_2 = rate([team_1_ratings, team_2_ratings])
    elif winner == "2":
        new_2, new_1 = rate([team_2_ratings, team_1_ratings])
    else:
        return 0
    # Printing out the amount of points that each player gained or lost.
    for i, player in enumerate(team_1_players):
        adj_amt = (player[0].get_rating(player[1]).mu - new_1[i][0])
        adjustment = "lost" if adj_amt >= 0 else "gained"
        print(f"{player[0].bnet_name} {adjustment} {abs(adj_amt)} points")

    for i, player in enumerate(team_2_players):
        adj_amt = (player[0].get_rating(player[1]).mu - new_2[i][0])
        adjustment = "lost" if adj_amt >= 0 else "gained"
        print(f"{player[0].bnet_name} {adjustment} {abs(adj_amt)} points")

    for i, pair in enumerate(zip(new_1, new_2)):
        team_1_players[i][0].update_rating(team_1_players[i][1], Rating(pair[0][0], pair[0][1]))
        team_2_players[i][0].update_rating(team_2_players[i][1], Rating(pair[1][0], pair[1][1]))
    # Will do smth with these later
    # print(f"Team 1 Old Ratings {team_1_ratings}")
    # print(f"Team 1 New Ratings {new_1}")
    # print(f"Team 2 Old Ratings {team_2_ratings}")
    # print(f"Team 2 New Ratings {new_2}")


# Testing
if __name__ == '__main__':
    # adjust_team_rating([{"bnet": "player7", "queued_role": "tank"},{"bnet": "player3", "queued_role": "tank"}], [{"bnet": "player5", "queued_role": "tank"},{"bnet": "player11", "queued_role": "tank"}], "2")
    # db.users.delete_many({})
    team_1 = []
    team_2 = []
    for i in range(0, 30):
        if i % 2 == 0:
            team_1.append(User(f"player{i}", f"player{i}",
                               ["tank"],
                               f"https://static.wikia.nocookie.net/starcraft/images/b/be/SC2_Portrait_Overwatch_Tracer.jpg/revision/latest?cb=20151113020737",
                               696969696, f"player{i}",
                               {"tank": random.randint(1500, 5000),
                                "support": random.randint(1500, 5000),
                                "dps": random.randint(1500, 5000)}, True))
        else:
            team_2.append(User(f"player{i}", f"player{i}",
                               ["tank"],
                               f"https://static.wikia.nocookie.net/starcraft/images/b/be/SC2_Portrait_Overwatch_Tracer.jpg/revision/latest?cb=20151113020737",
                               696969696, f"player{i}",
                               {"tank": random.randint(1500, 5000),
                                "support": random.randint(1500, 5000),
                                "dps": random.randint(1500, 5000)}, True))
# print("Team 1")
# for player in team_1:
#    print(f"{player.name} - {player.role_ratings['dps']}")
# print("Team 2")
# for player in team_2:
#    print(f"{player.name} - {player.role_ratings['dps']}")
# print(team_2)
# team_2_rank = [player.get_rating("dps") for player in team_2]
# team_1_rank = [player.get_rating("tank") for player in team_1]
# print(rate([team_2_rank, team_1_rank]))
# print(predict_win([team_1_rank,team_2_rank]))
# team_2_new_rank, team_1_new_rank = rate([team_2_rank, team_1_rank])
#
# for tuple in zip(team_2_new_rank,team_2):
#    tuple[1].update_rating("dps",tuple[0])
#    print(tuple[1])
#
# for tuple in zip(team_1_new_rank,team_1):
#    tuple[1].update_rating("dps",tuple[0])
#    print(tuple[1])
