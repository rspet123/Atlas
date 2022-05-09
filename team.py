from user import User

class Team:
    players = []
    team_name = ""
    team_rating = 0
    captain = ""

    def __init__(self,team_name:str,captain:User):
        self.team_name=team_name
        self.players = []
        self.team_rating = 0
        self.captain = captain

    def add_player(self,player:User,role:str):
        self.players.append((player,role))
        self.team_rating += player.get_rating(role)[0]

    def __repr__(self):
        return(f"Team:{self.team_name} Average Rating:{self.team_rating/len(self.players)}")