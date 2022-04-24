from db import tank_queue,support_queue,dps_queue,users


def add_to_queue(bnet:str,role:str):
    player = users.find_one({"bnet":bnet})
    if role.lower() == "dps":
        try:
            dps_queue.insert_one({"_id":player["name"],"bnet":bnet,"rank":player["ranks"]["damage"]})
        except Exception as e:
            # Player probably already in queue
            print(f"{type(e)}:{e}")
    if role.lower() == "tank":
        try:
            tank_queue.insert_one({"_id": player["name"], "bnet": bnet, "rank": player["ranks"]["tank"]})
        except Exception as e:
            # Player probably already in queue
            print(f"{type(e)}:{e}")
    if role.lower() == "support":
        try:
            tank_queue.insert_one({"_id":player["name"],"bnet":bnet,"rank":player["ranks"]["support"]})
        except Exception as e:
            # Player probably already in queue
            print(f"{type(e)}:{e}")

def get_players_in_queue():
    """Returns a list of players in the format Player, Role"""
    queue_state = []
    dps_in_queue = dps_queue.find()
    support_in_queue = support_queue.find()
    tank_in_queue = tank_queue.find()
    for dps in dps_queue.find():
        queue_state.append({"bnet":dps["bnet"],"role":"dps","rank":dps["rank"]})
    for support in support_queue.find():
        queue_state.append({"bnet":support["bnet"],"role":"support","rank":support["rank"]})
    for tank in tank_queue.find():
        queue_state.append({"bnet":tank["bnet"],"role":"tank","rank":tank["rank"]})

def empty_queue():
    tank_queue.delete_many({})
    dps_queue.delete_many({})
    support_queue.delete_many({})


class PlayerQueue:
    role_queue = {"tank": [], "dps": [], "support": []}

    def __init__(self):
        self.role_queue = {"tank": [], "dps": [], "support": []}

    def queue_up(self, role: str, player: str):
        """Adds a player to the queue in the chosen role"""
        self.role_queue[role].append(player)
