from db import team_queue
from team import Team


def dequeue_team(player_queuing: str, team: Team):
    """
    This function removes a team from the queue
    :param player_queuing: The player who is unqueuing the team
    :type player_queuing: str
    :param team: The team object that is being dequeued
    :type team: Team
    """
    team_queue.delete_one({"_id": team.team_name})


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
