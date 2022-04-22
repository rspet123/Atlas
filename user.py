import db


class User:
    discord_name = ""
    bnet_name = ""
    preferred_roles = []
    info = ""
    avatar = ""
    discord_id = ""
    name = ""
    role_ranks = {}

    def __init__(self, discord_name: str, bnet_name: str, preferred_roles: list, avatar: str, id:str, name: str,role_ranks:dict):
        self.discord_name = discord_name
        self.bnet_name = bnet_name
        self.preferred_roles = preferred_roles
        self.discord_id = id
        self.info = ""
        self.avatar = avatar
        self.name = name
        self.role_ranks = role_ranks


        db.users.insert_one({"_id": discord_name,
                             "bnet": bnet_name,
                             "roles": preferred_roles,
                             "info": self.info,
                             "avatar":avatar,
                             "id":id,
                             "name":name,
                             "ranks":role_ranks})


    @staticmethod
    def get_user_by_bnet(bnet: str):
        user = db.users.find_one({"bnet": bnet})
        return user

    @staticmethod
    def get_user_by_discord(discord: str):
        user = db.users.find_one({"_id": discord})
        return user

