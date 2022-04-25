import hashlib
from db import matches


def hash_match(filename, buffer=1024):
    """Hashes the log file"""
    h = hashlib.sha1()
    with open(f"log_folder/{filename}", 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(buffer)
            h.update(chunk)
    return h.hexdigest()


def add_match(match_log_file: str, scoreboard: dict, winning_team: str, uploading_user: str):
    match_hash = hash_match(match_log_file)
    if matches.find_one({"hash": match_hash}):
        print("Match has already been uploaded")
    else:
        matches.insert_one({"_id": match_log_file.replace(".txt", ""), "scoreboard": scoreboard, "winner": winning_team,
                            "hash": match_hash, "host":uploading_user})
