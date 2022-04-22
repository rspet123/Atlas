class PlayerQueue:
    role_queue = {"tank": [], "dps": [], "support": []}

    def __init__(self):
        self.role_queue = {"tank": [], "dps": [], "support": []}

    def queue_up(self, role: str, player: str):
        """Adds a player to the queue in the chosen role"""
        self.role_queue[role].append(player)

    def get_players_in_queue(self):
        """Returns a list of players in the format Player, Role"""
        players_in_queue = []
        for role in self.role_queue:
            for player in self.role_queue[role]:
                players_in_queue.append((player, role))

        return players_in_queue
