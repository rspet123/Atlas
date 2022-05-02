import random
import time
from db import tank_queue, support_queue, dps_queue, users
import statistics
from itertools import combinations, product


def add_to_queue(bnet: str, role: str):
    player = users.find_one({"bnet": bnet})
    if role.lower() == "dps":
        try:
            dps_queue.insert_one({"_id": player["_id"], "bnet": bnet, "rank": player["ratings"]["damage"]["mu"], "role": "dps"})
        except Exception as e:
            # Player probably already in queue
            print(f"{type(e)}:{e}")
    if role.lower() == "tank":
        try:
            tank_queue.insert_one({"_id": player["_id"], "bnet": bnet, "rank": player["ratings"]["tank"]["mu"], "role": "tank"})
        except Exception as e:
            # Player probably already in queue
            print(f"{type(e)}:{e}")
    if role.lower() == "support":
        try:
            support_queue.insert_one(
                {"_id": player["_id"], "bnet": bnet, "rank": player["ratings"]["support"]["mu"], "role": "support"})
        except Exception as e:
            # Player probably already in queue
            print(f"{type(e)}:{e}")


def get_players_in_queue():
    """Returns a list of players in the format Player, Role"""
    queue_state = {}
    dps_in_queue = dps_queue.find()
    support_in_queue = support_queue.find()
    tank_in_queue = tank_queue.find()
    for dps in dps_queue.find():
        queue_state[dps["bnet"]] = ({"bnet": dps["bnet"], "role": "dps", "rank": dps["rank"]})
    for support in support_queue.find():
        queue_state[support["bnet"]] = ({"bnet": support["bnet"], "role": "support", "rank": support["rank"]})
    for tank in tank_queue.find():
        queue_state[tank["bnet"]] = ({"bnet": tank["bnet"], "role": "tank", "rank": tank["rank"]})
    return queue_state


def matchmake():
    reverse = False
    if not reverse:
        print("Finding Highest SR Game")
    team_1 = []
    team_2 = []
    dps_in_queue = list(dps_queue.find())
    support_in_queue = list(support_queue.find())
    tank_in_queue = list(tank_queue.find())
    if len(dps_in_queue) < 4 or len(support_in_queue) < 4 or len(tank_in_queue) < 4:
        print("Not enough players in queue")
        return -1
    dps_in_queue = sorted(dps_in_queue, key=lambda d: d['rank'], reverse=reverse)
    support_in_queue = sorted(support_in_queue, key=lambda d: d['rank'], reverse=reverse)
    tank_in_queue = sorted(tank_in_queue, key=lambda d: d['rank'], reverse=reverse)
    tank_in_queue = tank_in_queue[-4:]
    support_in_queue = support_in_queue[-4:]
    dps_in_queue = dps_in_queue[-4:]
    for i, dps in enumerate(dps_in_queue):
        if i % 2 == 1:
            dps["role"] = "dps"
            team_1.append(dps)
        if i % 2 == 0:
            dps["role"] = "dps"
            team_2.append(dps)
    for i, supp in enumerate(support_in_queue):
        if i % 2 == 1:
            supp["role"] = "support"
            team_1.append(supp)
        if i % 2 == 0:
            supp["role"] = "support"
            team_2.append(supp)
    for i, tank in enumerate(tank_in_queue):
        if i % 2 == 1:
            tank["role"] = "tank"
            team_1.append(tank)
        if i % 2 == 0:
            tank["role"] = "tank"
            team_2.append(tank)
    return team_1, team_2


def matchmake_2():
    reverse = False
    if not reverse:
        print("Finding Highest SR Game")
    team_1 = []
    team_2 = []
    dps_in_queue = list(dps_queue.find())
    support_in_queue = list(support_queue.find())
    tank_in_queue = list(tank_queue.find())
    if len(dps_in_queue) < 4 or len(support_in_queue) < 4 or len(tank_in_queue) < 4:
        print("Not enough players in queue")
        return -1

    dps_in_queue = sorted(dps_in_queue, key=lambda d: d['rank'], reverse=reverse)
    support_in_queue = sorted(support_in_queue, key=lambda d: d['rank'], reverse=reverse)
    tank_in_queue = sorted(tank_in_queue, key=lambda d: d['rank'], reverse=reverse)

    tank_in_queue = tank_in_queue[-4:]
    support_in_queue = support_in_queue[-4:]
    dps_in_queue = dps_in_queue[-4:]
    for tank in tank_in_queue:
        tank["role"] = "tank"
    for dps in dps_in_queue:
        dps["role"] = "dps"
    for support in support_in_queue:
        support["role"] = "support"

    team_1.extend([dps_in_queue[0],
                   dps_in_queue[3],
                   support_in_queue[0],
                   support_in_queue[3],
                   tank_in_queue[0],
                   tank_in_queue[3]])
    team_2.extend([dps_in_queue[1],
                   dps_in_queue[2],
                   support_in_queue[1],
                   support_in_queue[2],
                   tank_in_queue[1],
                   tank_in_queue[2]])
    return team_1, team_2


def matchmake_3(sr_break=100, stdv_break=600, stdv_filtering=True, reverse=True, range=200):
    if not reverse:
        print("Finding Highest SR Game")

    if range < 4:
        print("Can't make a queue with this, try a range > 4")

    # Ok, so now to prevent low rank players in high rank games, we only take the highest(or lowest, if reverse) X
    dps_in_queue = sorted(list(dps_queue.find()), key=lambda d: d['rank'], reverse=reverse)[-range:]
    support_in_queue = sorted(list(support_queue.find()), key=lambda d: d['rank'], reverse=reverse)[-range:]
    tank_in_queue = sorted(list(tank_queue.find()), key=lambda d: d['rank'], reverse=reverse)[-range:]

    if len(dps_in_queue) < 4 or len(support_in_queue) < 4 or len(tank_in_queue) < 4:
        print("Not enough players in queue")
        return -1

    all_dps = list(combinations(dps_in_queue, 2))
    all_supp = list(combinations(support_in_queue, 2))
    all_tank = list(combinations(tank_in_queue, 2))
    team_roles = [all_dps, all_supp, all_tank]
    all_teams = list(product(*team_roles))
    team_list = []
    queue_state = get_players_in_queue()
    for team in all_teams:
        team_avg = 0
        players = []
        player_stats = []
        for role in team:
            team_avg += sum(player['rank'] for player in role)
            for i, player in enumerate(role):
                players.append(player["bnet"])
                player_stats.append(
                    {"bnet": player["bnet"], "role": player["role"], "rank": player['rank']})
        if len(set(players)) == 6:
            # Check if players aren't on the same team twice, for multi-role queue
            team_list.append({"team": team,
                              "avg": (team_avg / 6),
                              "players": set(players),
                              "player_stats": player_stats})

    sorted_teams = sorted(team_list, key=lambda d: d['avg'], reverse=reverse)

    # TODO WIP optimization
    candidates = []
    for team_1 in sorted_teams:
        for team_2 in sorted_teams:
            if team_1["players"].intersection(team_2["players"]) == set():
                if abs(team_1["avg"] - team_2["avg"]) < sr_break:
                    candidates.append({"team_1": team_1["player_stats"], "team_2": team_2["player_stats"],
                                       "diff": abs(team_1["avg"] - team_2["avg"])})
                    break
                break
    filtered_teams = []
    if stdv_filtering:
        for candidate in candidates:
            stdv_1 = statistics.pstdev(player["rank"] for player in candidate["team_1"])
            stdv_2 = statistics.pstdev(player["rank"] for player in candidate["team_2"])
            if stdv_2 < stdv_break and stdv_1 < stdv_break:
                filtered_teams.append(candidate)
    else:
        filtered_teams = candidates
    try:
        min_diff = min(filtered_teams, key=lambda x: x['diff'])
    except ValueError:
        print("No teams found for selected parameters")
        min_diff = min(candidates, key=lambda x: x['diff'])
    return min_diff["team_1"], min_diff["team_2"]

def matchmake_3_ow2(sr_break=100, stdv_break=600, stdv_filtering=True, reverse=True, range=200):
    if not reverse:
        print("Finding Highest SR Game")

    if range < 4:
        print("Can't make a queue with this, try a range > 4")

    # Ok, so now to prevent low rank players in high rank games, we only take the highest(or lowest, if reverse) X
    dps_in_queue = sorted(list(dps_queue.find()), key=lambda d: d['rank'], reverse=reverse)[-range:]
    support_in_queue = sorted(list(support_queue.find()), key=lambda d: d['rank'], reverse=reverse)[-range:]
    tank_in_queue = sorted(list(tank_queue.find()), key=lambda d: d['rank'], reverse=reverse)[-range:]

    if len(dps_in_queue) < 4 or len(support_in_queue) < 4 or len(tank_in_queue) < 2:
        print("Not enough players in queue")
        return -1

    all_dps = list(combinations(dps_in_queue, 2))
    all_supp = list(combinations(support_in_queue, 2))
    all_tank = list(combinations(tank_in_queue, 1))
    team_roles = [all_dps, all_supp, all_tank]
    all_teams = list(product(*team_roles))
    team_list = []
    queue_state = get_players_in_queue()
    for team in all_teams:
        team_avg = 0
        players = []
        player_stats = []
        for role in team:
            team_avg += sum(player['rank'] for player in role)
            for i, player in enumerate(role):
                players.append(player["bnet"])
                player_stats.append(
                    {"bnet": player["bnet"], "role": player["role"], "rank": player['rank']})
        if len(set(players)) == 5:
            # Check if players aren't on the same team twice, for multi-role queue
            team_list.append({"team": team,
                              "avg": (team_avg / 5),
                              "players": set(players),
                              "player_stats": player_stats})

    sorted_teams = sorted(team_list, key=lambda d: d['avg'], reverse=reverse)

    # TODO WIP optimization
    candidates = []
    for team_1 in sorted_teams:
        for team_2 in sorted_teams:
            if team_1["players"].intersection(team_2["players"]) == set():
                if abs(team_1["avg"] - team_2["avg"]) < sr_break:
                    candidates.append({"team_1": team_1["player_stats"], "team_2": team_2["player_stats"],
                                       "diff": abs(team_1["avg"] - team_2["avg"])})
                    break
                break
    filtered_teams = []
    if stdv_filtering:
        for candidate in candidates:
            stdv_1 = statistics.pstdev(player["rank"] for player in candidate["team_1"])
            stdv_2 = statistics.pstdev(player["rank"] for player in candidate["team_2"])
            if stdv_2 < stdv_break and stdv_1 < stdv_break:
                filtered_teams.append(candidate)
    else:
        filtered_teams = candidates
    try:
        min_diff = min(filtered_teams, key=lambda x: x['diff'])
    except ValueError:
        print("No teams found for selected parameters")
        min_diff = min(candidates, key=lambda x: x['diff'])
    return min_diff["team_1"], min_diff["team_2"]


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


# Testing, making fake users
if __name__ == '__main__':
    num_users = 30

    #for i in range(num_users):
    #    try:
    #        users.insert_one({"_id": f"player{i}", "bnet": f"player{i}", "ranks": {"tank": random.randint(1500, 5000),
    #                                                                               "damage": random.randint(1500, 5000),
    #                                                                               "support": random.randint(1500, 5000)}})
    #    except Exception as e:
    #        print(type(e))
    empty_queue()
    for i in range(num_users):
        userbnet = users.find_one({"_id": f"player{i}"})["bnet"]
        if i % 3 == 0:
            add_to_queue(userbnet, "tank")
        if i % 3 == 1:
            add_to_queue(userbnet, "dps")
        if i % 3 == 2:
            add_to_queue(userbnet, "support")

    teams = matchmake()
    team_1 = teams[0]
    team_2 = teams[1]
    print("Matchmaker 1")
    print(f"Team 1 SR AVG:{sum(player['rank'] for player in team_1) / len(team_1)}")
    print(f"Team 1 SR STDV:{statistics.pstdev(player['rank'] for player in team_1)}")
    for player in team_1:
        print(f"{player['bnet']}, \tRank:{player['rank']}, \tRole:{player['role']}")
    print(f"Team 2 SR AVG:{sum(player['rank'] for player in team_2) / len(team_1)}")
    print(f"Team 2 SR STDV:{statistics.pstdev(player['rank'] for player in team_2)}")
    for player in team_2:
        print(f"{player['bnet']}, \tRank:{player['rank']}, \tRole:{player['role']}")
    print("-------------------------------")
    teams = matchmake_2()
    team_1 = teams[0]
    team_2 = teams[1]
    print("Matchmaker 2")
    print(f"Team 1 SR AVG:{sum(player['rank'] for player in team_1) / len(team_1)}")
    print(f"Team 1 SR STDV:{statistics.pstdev(player['rank'] for player in team_1)}")
    for player in team_1:
        print(f"{player['bnet']}, \tRank:{player['rank']}, \tRole:{player['role']}")
    print(f"Team 2 SR AVG:{sum(player['rank'] for player in team_2) / len(team_1)}")
    print(f"Team 2 SR STDV:{statistics.pstdev(player['rank'] for player in team_2)}")
    for player in team_2:
        print(f"{player['bnet']}, \tRank:{player['rank']}, \tRole:{player['role']}")
    print("-------------------------------")
    start = time.time()
    teams = matchmake_3()
    end = time.time()
    print(f"Time:{end - start}")
    team_1 = teams[0]
    team_2 = teams[1]
    print("Matchmaker 3")
    print(f"Team 1 SR AVG:{sum(player['rank'] for player in team_1) / len(team_1)}")
    print(f"Team 1 SR STDV:{statistics.pstdev(player['rank'] for player in team_1)}")
    for player in team_1:
        print(f"{player['bnet']}, \tRank:{player['rank']}, \tRole:{player['role']}")
    print(f"Team 2 SR AVG:{sum(player['rank'] for player in team_2) / len(team_1)}")
    print(f"Team 2 SR STDV:{statistics.pstdev(player['rank'] for player in team_2)}")
    for player in team_2:
        print(f"{player['bnet']}, \tRank:{player['rank']}, \tRole:{player['role']}")
