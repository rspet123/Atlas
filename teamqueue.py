from db import team_queue
from team import Team
from user import User, get_user_by_bnet


def dequeue_team(player_queuing: str, team: Team):
    """
    This function removes a team from the queue
    :param player_queuing: The player who is unqueuing the team
    :type player_queuing: str
    :param team: The team object that is being dequeued
    :type team: Team
    """
    team_queue.delete_one({"_id": team.team_name, "rating": team.get_rating().mu})

def empty_queue():
    """
    It deletes all documents in the team_queue collection
    """
    team_queue.delete_many({})


def queue_team(player_queuing: str, team: Team):
    """
    > This function inserts a team into the team queue

    :param player_queuing: The name of the player who is queuing the team
    :type player_queuing: str
    :param team: Team object
    :type team: Team
    """
    # Probably should check if the team captain is queueing the team
    team_queue.insert_one({"_id": team.team_name, "rating": team.get_rating().mu})

def team_matchmake():
    """
    It takes the two teams with the highest rating from the team queue, removes them from the queue, and returns them
    :return: A tuple of two dictionaries.
    """
    teams_in_queue = list(team_queue.find())
    teams_in_queue = sorted(teams_in_queue, key=lambda i: i['rating'], reverse=True)
    team_1 = teams_in_queue[0]
    team_2 = teams_in_queue[1]
    team_queue.delete_one({"_id": team_1["_id"], "rating": team_1["rating"]})
    team_queue.delete_one({"_id": team_2["_id"], "rating": team_2["rating"]})
    return team_1, team_2


if __name__ == '__main__':
    empty_queue()
    team_a = Team("Team Poggers Mountain", "player0")
    team_b = Team("Team Poggers Peak", "player21")
    for i in range(3, 10):
        team_a.add_player(get_user_by_bnet(f"player{i}"), "support")
    for i in range(12, 20):
        team_b.add_player(get_user_by_bnet(f"player{i}"), "support")
    print(team_a)
    print(team_b)
    queue_team("player0",team_a)
    queue_team("player21",team_b)

    a = team_matchmake()


    print(a)


