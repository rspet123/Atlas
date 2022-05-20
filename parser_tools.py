import random

COLUMNS = ["Player", "Hero Damage Dealt", "Barrier Damage Dealt",
           "Damage Blocked", "Damage Taken", "Deaths", "Eliminations", "Defensive Assists",
           "Final Blows", "Environmental Deaths", "Environmental Kills", "Healing Dealt",
           "Multikill Best", "Multikills", "Objective Kills", "Objective Assists", "Solo Kills",
           "Ultimates Earned", "Ultimates Used", "Weapon Accuracy", "All Damage Dealt", "Hero", "Team"]
STAT_COLUMNS = ["Hero Damage Dealt", "Barrier Damage Dealt",
           "Damage Blocked", "Damage Taken", "Deaths", "Eliminations", "Defensive Assists",
           "Final Blows", "Environmental Deaths", "Environmental Kills", "Healing Dealt",
           "Multikill Best", "Multikills", "Objective Kills", "Objective Assists", "Solo Kills",
           "Ultimates Earned", "Ultimates Used", "Weapon Accuracy", "All Damage Dealt"]


def parse_log(log, log_folder ="log_folder", columns=None):
    """
    It takes a log file and returns a tuple containing the final player scoreboard [0] and player hero time [1]

    The function takes in a log file, and a list of columns. The columns are the stats that are recorded in the log file.
    The function then reads the log file line by line, and splits the line into a timestamp and a list of stats. The stats
    are then zipped with the columns, and put into a dictionary. The dictionary is then appended to a list of stats for that
    timestamp. The list of stats for each timestamp is then put into a dictionary, with the timestamp as the key

    :param log: the name of the log file
    :param log_folder: The folder where the logs are stored, defaults to log_folder (optional)
    :param columns: The columns of the log file
    :return: A tuple containing the final player scoreboard [0] and player hero time [1]
    """
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
    return time_stamp, player_heroes, log_stats

def generate_key(size = 24):
    """
    It generates a random string of characters between 65 and 122, and returns it as a byte string

    :param size: The size of the key to generate. Defaults to 24, defaults to 24 (optional)
    :return: A string of random characters
    """
    #48 - 122
    key = ""
    for _ in range(size):
        key+=chr(random.randint(65,122))
    return bytes(key,"ascii")

def diff_stats(players:dict,player:dict,last_tick:dict,stat:str):
    """
    If the player exists in the players dictionary, and the hero exists in the player's dictionary, and the stat exists in
    the hero's dictionary, then add the stat to the hero's dictionary
    Nice helper function for diffing stats between frames

    :param players: dict
    :type players: dict
    :param player: the player object
    :type player: dict
    :param last_tick: the last tick of data we've seen
    :type last_tick: dict
    :param stat: the stat we're looking at
    :type stat: str
    """
    try:
        players[player["Player"]][player["Hero"]][stat] = \
            players[player["Player"]][player["Hero"]].get(stat, 0) + player[stat] - \
            last_tick[player["Player"]].get(stat, 0)
    except TypeError:
        print(f"incorrect type for {player['Player']} {stat}, cannot cast {player[stat]} as float")



data_template = {"Hero":"", 'Hero Damage Dealt': 0,
            'Barrier Damage Dealt': 0, 'Damage Blocked': 0.0,
            'Damage Taken': 0, 'Deaths': 0, 'Eliminations': 0,
            'Defensive Assists': 0, 'Final Blows': 0,
            'Environmental Deaths': 0.0, 'Environmental Kills': 0.0,
            'Healing Dealt': 0.0, 'Multikill Best': 0.0, 'Multikills': 0.0,
            'Objective Kills': 0, 'Objective Assists': 0.0, 'Solo Kills': 0,
            'Ultimates Earned': 0, 'Ultimates Used': 0, 'Weapon Accuracy': 0,
            'All Damage Dealt': 0}

def parse_hero_stats(stats_log):
    """
    For each player, for each hero, for each stat, calculate the difference between the current stat and the last stat

    :param stats_log: The log of stats for each player at each tick
    :return: A dictionary of dictionaries of dictionaries.
    """
    players = {}
    last_tick = {}
    for log in stats_log:
        for player in stats_log[log]:
            if player["Player"] not in players:
                players[player["Player"]] = {}
            if player["Player"] not in last_tick:
                last_tick[player["Player"]] = {}
            if player["Hero"] is not "":
                if player["Hero"] not in players[player["Player"]]:
                    players[player["Player"]][player["Hero"]] = {}
                for stat in STAT_COLUMNS:
                    # Calculate and update stats for each player and each hero
                    diff_stats(players, player, last_tick, stat)
            last_tick[player["Player"]] = player
    return players

