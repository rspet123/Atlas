import db
from openskill import Rating, rate
import random


class User:
    discord_name = ""
    bnet_name = ""
    preferred_roles = []
    info = ""
    avatar = ""
    discord_id = ""
    name = ""
    role_ranks = {}
    role_ratings = {}

    def __init__(self, discord_name: str, bnet_name: str, preferred_roles: list, avatar: str, id: str, name: str,
                 role_ranks: dict, update_db=True):
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
                                 "id": id,
                                 "name": name,
                                 "ranks": role_ranks,
                                 "ratings": self.role_ratings})

    def __repr__(self):
        return f"Name: {self.name}, bnet: {self.bnet_name}" \
               f" DPS: {self.role_ratings['damage']}" \
               f" Support: {self.role_ratings['support']}" \
               f" Tank: {self.role_ratings['tank']}"
    def as_json(self):
        return {"_id": self.discord_name,
         "bnet": self.bnet_name,
         "roles": self.preferred_roles,
         "info": self.info,
         "avatar": self.avatar,
         "id": self.discord_id,
         "name": self.name,
         "ranks": self.role_ranks,
         "ratings": self.role_ratings}

    def update_rating(self, role, new_rating: Rating):
        """If updating ratings from the rate keywird"""
        self.role_ratings[role]["mu"] = new_rating[0]
        self.role_ratings[role]["sigma"] = new_rating[1]
        db.users.update_one({"bnet": self.bnet_name},update={"$set":self.as_json()})

    def get_rating(self, role):
        return Rating(self.role_ratings[role]["mu"],self.role_ratings[role]["sigma"])

    @staticmethod
    def get_user_by_bnet(bnet: str):
        user = db.users.find_one({"bnet": bnet})
        return user

    @staticmethod
    def get_user_by_discord(discord: str):
        user = db.users.find_one({"_id": discord})
        return user

# Testing
if __name__ == '__main__':
    db.users.delete_many({})
    team_1 = []
    team_2 = []

    for i in range(120, 130):
        if i % 2 == 0:
            team_1.append(User(f"player{i}", f"player{i}",
                               ["tank"], f"player{i}",
                               696969696, f"player{i}",
                               {"tank": random.randint(1500, 5000),
                                "support": random.randint(1500, 5000),
                                "damage": random.randint(1500, 5000)}, True))
        else:
            team_2.append(User(f"player{i}", f"player{i}",
                               ["tank"], f"player{i}",
                               696969696, f"player{i}",
                               {"tank": random.randint(1500, 5000),
                                "support": random.randint(1500, 5000),
                                "damage": random.randint(1500, 5000)}, True))
print("Team 1")
for player in team_1:
    print(f"{player.name} - {player.role_ratings['damage']}")
print("Team 2")
for player in team_2:
    print(f"{player.name} - {player.role_ratings['damage']}")
print(team_2)
team_2_rank = [player.get_rating("damage") for player in team_2]
team_1_rank = [player.get_rating("tank") for player in team_1]
print(rate([team_2_rank, team_1_rank]))
team_2_new_rank, team_1_new_rank = rate([team_2_rank, team_1_rank])

for tuple in zip(team_2_new_rank,team_2):
    tuple[1].update_rating("damage",tuple[0])
    print(tuple[1])

for tuple in zip(team_1_new_rank,team_1):
    tuple[1].update_rating("damage",tuple[0])
    print(tuple[1])

