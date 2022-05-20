import hashlib
from db import matches


def hash_match(filename, buffer=1024):
    """
    It takes a file name and a buffer size, reads the file in chunks of the buffer size, and returns the
    SHA1 hash of the file

    :param filename: The name of the file to be hashed
    :param buffer: The size of the chunk of data to read from the file, defaults to 1024 (optional)
    :return: The hash of the file
    """
    h = hashlib.sha1()
    with open(f"log_folder/{filename}", 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(buffer)
            h.update(chunk)
    return h.hexdigest()


def add_match(match_log_file: str, scoreboard: dict, winning_team: str, uploading_user: str, lobby_id: str,
              team_1: list, team_2: list):
    """
    `add_match` takes a match log file, a scoreboard, the winning team, the user who uploaded the match, and the lobby ID,
    and adds the match to the database.

    :param match_log_file: The name of the file that contains the match log
    :type match_log_file: str
    :param scoreboard: a dictionary of the form {team_name: score}
    :type scoreboard: dict
    :param winning_team: The team that won the match
    :type winning_team: str
    :param uploading_user: The user who uploaded the match
    :type uploading_user: str
    :param lobby_id: The lobby id of the match. This is used to identify the lobby that created the match object
    :type lobby_id: str
    """
    match_hash = hash_match(match_log_file)
    if matches.find_one({"hash": match_hash}):
        print("Match has already been uploaded")
    else:
        matches.insert_one({"_id": lobby_id,
                            "filename": match_log_file.replace(".txt", ""),
                            "scoreboard": scoreboard,
                            "winner": winning_team,
                            "hash": match_hash,
                            "host": uploading_user,
                            "team_1": team_1,
                            "team_2": team_2})


def display_match(id):
    return matches.find_one({"_id": id})
