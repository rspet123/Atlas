import configparser
from pymongo import MongoClient
#Get Config Data
config = configparser.ConfigParser()
config.read("config.ini")

USERNAME = config.get("DATABASE","USERNAME")
PASSWORD = config.get("DATABASE","PASSWORD")


client = MongoClient(f"mongodb+srv://{USERNAME}:{PASSWORD}@gauntletdb.glcqr.mongodb.net")

db = client["DB"]
matches = db["Matches"]
players = db["Players"]
users = db["Users"]
tank_queue = db["Tank_Queue"]
dps_queue = db["DPS_Queue"]
support_queue = db["Support_Queue"]