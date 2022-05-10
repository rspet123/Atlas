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
    id = ""
    role_ranks = {}
    role_ratings = {}

    def __init__(self, discord_name: str, bnet_name: str, preferred_roles: list, avatar: str, id: str, name: str,
                 role_ranks: dict, update_db=True):
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
        self.discord_id = id
        self.info = ""
        self.avatar = avatar
        self.name = name
        self.role_ranks = role_ranks
        self.role_ratings = {"tank": {"sigma": 0, "mu": 0},
                             "damage": {"sigma": 0, "mu": 0},
                             "support": {"sigma": 0, "mu": 0}}
        for role in role_ranks.items():
            self.role_ratings[role[0]]["sigma"] = Rating((role[1] / 100), 8.33333).sigma
            self.role_ratings[role[0]]["mu"] = Rating((role[1] / 100), 8.33333).mu
            print(f"Setting {role[0]} to {(role[1] / 100)} for {self.name}")

        if update_db:
            db.users.insert_one({"_id": discord_name,
                                 "bnet": bnet_name,
                                 "roles": preferred_roles,
                                 "info": self.info,
                                 "avatar": avatar,
                                 "id": self.id,
                                 "name": name,
                                 "ranks": role_ranks,
                                 "ratings": self.role_ratings})

    def __repr__(self):
        """
        This function returns a string that contains the name, bnet name, and role ratings of the player
        :return: The name, bnet name, and role ratings for the player.
        """
        return f"Name: {self.name}, bnet: {self.bnet_name}" \
               f" DPS: {self.role_ratings['damage']}" \
               f" Support: {self.role_ratings['support']}" \
               f" Tank: {self.role_ratings['tank']}"

    def __hash__(self):
        """
        The hash function is used to return a unique integer for each unique object
        :return: The hash of the name attribute of the object.
        """
        return hash(self.name)

    def as_json(self):
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
                                                          "id": self.id,
                                                          "name": self.name,
                                                          "ranks": self.role_ranks,
                                                          "ratings": self.role_ratings})

    def update_rating(self, role, new_rating: Rating):
        """
        It updates the user's rating for a given role, and then updates the database with the new rating

        :param role: the role you want to update
        :param new_rating: Rating = (mu, sigma)
        :type new_rating: Rating
        """
        self.role_ratings[role]["mu"] = new_rating[0]
        self.role_ratings[role]["sigma"] = new_rating[1]
        db.users.update_one({"bnet": self.bnet_name}, update={"$set": self.as_json()})

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
                    False)
    return new_user


def get_user_by_bnet(bnet: str):
    """
    > This function takes a bnet and returns a user

    :param bnet: The battlenet ID of the user
    :type bnet: str
    :return: A user object
    """
    user = db.users.find_one({"bnet": bnet})
    return create_user_from_json(user)


def get_user_by_discord(discord: str):
    """
    `get_user_by_discord` takes a discord ID and returns the user object from the database

    :param discord: The discord ID of the user
    :type discord: str
    :return: A user object
    """
    user = db.users.find_one({"_id": discord})
    return create_user_from_json(user)


def get_all_users():
    """
    > This function returns a list of all the users in the database
    :return: A list of all the users in the database.
    """
    users = list(db.users.find())
    return users


# Testing
if __name__ == '__main__':
    pass
    # db.users.delete_many({})
    # team_1 = []
    # team_2 = []
#
# for i in range(0, 30):
#    if i % 2 == 0:
#        team_1.append(User(f"player{i}", f"player{i}",
#                           ["tank"], f"player{i}",
#                           696969696, f"player{i}",
#                           {"tank": random.randint(1500, 5000),
#                            "support": random.randint(1500, 5000),
#                            "damage": random.randint(1500, 5000)}, True))
#    else:
#        team_2.append(User(f"player{i}", f"player{i}",
#                           ["tank"], f"player{i}",
#                           696969696, f"player{i}",
#                           {"tank": random.randint(1500, 5000),
#                            "support": random.randint(1500, 5000),
#                            "damage": random.randint(1500, 5000)}, True))
# print("Team 1")
# for player in team_1:
#    print(f"{player.name} - {player.role_ratings['damage']}")
# print("Team 2")
# for player in team_2:
#    print(f"{player.name} - {player.role_ratings['damage']}")
# print(team_2)
# team_2_rank = [player.get_rating("damage") for player in team_2]
# team_1_rank = [player.get_rating("tank") for player in team_1]
# print(rate([team_2_rank, team_1_rank]))
# print(predict_win([team_1_rank,team_2_rank]))
# team_2_new_rank, team_1_new_rank = rate([team_2_rank, team_1_rank])
#
# for tuple in zip(team_2_new_rank,team_2):
#    tuple[1].update_rating("damage",tuple[0])
#    print(tuple[1])
#
# for tuple in zip(team_1_new_rank,team_1):
#    tuple[1].update_rating("damage",tuple[0])
#    print(tuple[1])
