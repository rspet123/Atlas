import random

COLUMNS = ["Player", "Hero Damage Dealt", "Barrier Damage Dealt",
           "Damage Blocked", "Damage Taken", "Deaths", "Eliminations", "Defensive Assists",
           "Final Blows", "Environmental Deaths", "Environmental Kills", "Healing Dealt",
           "Multikill Best", "Multikills", "Objective Kills", "Objective Assists", "Solo Kills",
           "Ultimates Earned", "Ultimates Used", "Weapon Accuracy", "All Damage Dealt", "Hero", "Team"]


def parse_log(log, log_folder ="log_folder", columns=None):
    """Returns a tuple containing the final player scoreboard [0] and player hero time [1]"""
    if columns is None:
        columns = COLUMNS
    player_heroes = {}
    log_stats = {}
    with open(f"{log_folder}/{log}", encoding='utf-8') as log_file:
        lines = log_file.readlines()
        for line in lines:

            split_line = line.split(" ", 1)
            time_stamp = split_line[0]
            time_stats = split_line[1].split("/")
            if time_stamp not in log_stats:
                log_stats[time_stamp] = []
            curr_stats = list(zip(columns, time_stats))
            stat_dict = {}
            for stat in curr_stats:
                try:
                    stat_dict[stat[0]] = float(stat[1])
                except:
                    stat_dict[stat[0]] = stat[1]
            log_stats[time_stamp].append(stat_dict.copy())
    prev = time_stamp
    for time in log_stats:
        for player in log_stats[time]:
            if player["Player"] not in player_heroes:
                player_heroes[player["Player"]] = {}
            if not player["Hero"] == "":
                player_heroes[player["Player"]][player["Hero"]] = player_heroes[player["Player"]].get(player["Hero"],
                                                                                                      0) + 3
        if len(log_stats[time]) < 12:
            time_stamp = prev
            break
        prev = time
    return(log_stats[time_stamp],player_heroes)

def generate_key(size = 24):
    #48 - 122
    key = ""
    for _ in range(size):
        key+=chr(random.randint(65,122))
    return bytes(key,"ascii")