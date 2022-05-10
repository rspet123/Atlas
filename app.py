import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from parser_tools import parse_log, generate_key, parse_hero_stats
from keygen import generate_access_key
from pymongo.errors import DuplicateKeyError
import configparser
from leaderboard import get_top_x_role, get_top_x_overall
from user import User, get_user_by_discord, get_all_users
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import requests
import json
from match import add_match
from playerqueue import get_players_in_queue, add_to_queue, matchmake_3, matchmake_3_ow2, can_start, can_start_ow2
from ow_info import MAPS, COLUMNS, STAT_COLUMNS

app = Flask(__name__)

# Get Config Data
config = configparser.ConfigParser()
config.read("config.ini")
CLIENT_ID = config.get("DISCORD", "CLIENT_ID")
CLIENT_SECRET = config.get("DISCORD", "CLIENT_SECRET")
CALLBACK = config.get("DISCORD", "CALLBACK")
# https://stackoverflow.com/questions/54892779/how-to-serve-a-local-app-using-waitress-and-nginx
# Generate Flask Secret key for auth
key = generate_key()
app.secret_key = key

# Setting up the config for the discord auth.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
app.config["DISCORD_CLIENT_ID"] = CLIENT_ID
app.config["DISCORD_CLIENT_SECRET"] = CLIENT_SECRET
app.config["DISCORD_REDIRECT_URI"] = CALLBACK

# Setting up the config for the file storage.
LOG_FOLDER = "log_folder"
app.config['UPLOAD_FOLDER'] = LOG_FOLDER
ALLOWED_EXTENSIONS = {'txt'}

# Set up OAuth session
discord = DiscordOAuth2Session(app)


def allowed_file(filename):
    """
    If the file has an extension and the extension is in our list of allowed extensions, then return True

    :param filename: The name of the file that was uploaded
    :return: a boolean value.
    """
    """Checks if our file is of the correct type"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def landing():
    """
    It redirects the user to the post_upload page
    :return: A redirect to the post_upload page.
    """
    """Landing page"""
    return redirect(url_for("post_upload"))


@app.post('/upload')
@requires_authorization
def post_upload():
    """
    It takes the file that was uploaded, parses it, and adds it to the database
    :return: the string 'Error?!'
    """
    """Post our file to the server"""
    if 'file' not in request.files:
        return "", 400
    file = request.files['file']
    if file.filename == '':
        return "", 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        user = discord.fetch_user()
        winner = request.form["teams"]
        print(winner)
        data = parse_log(file.filename)
        scoreboard = data[2][data[0]]
        add_match(file.filename,
                  scoreboard,
                  winner,
                  str(user))
        return "", 201
    return "", 415


@app.route("/login")
def login():
    """
    > Redirect to discord auth
    :return: A redirect to the discord auth page.
    """
    """Redirect to discord auth"""
    return discord.create_session()


@app.route("/auth")
def callback():
    """
    It redirects the user to the login page.
    :return: The user object
    """
    discord.callback()
    user = discord.fetch_user()
    return user.to_json()


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    """
    If the user is not logged in, redirect them to the login page

    :param e: The exception that was raised
    :return: A redirect to the login page.
    """
    return redirect(url_for("login"))


@app.route("/user")
@requires_authorization
def curr_user():
    """
    If the user is in our database, we render the user page. If not, we redirect them to the signup page
    :return: The user object
    """
    user = discord.fetch_user()
    print(user)
    disc_user = get_user_by_discord(str(user))
    print(disc_user)
    if disc_user is None:
        # If the user isn't in our database, we make them signup
        return "", 403
    this_user = get_user_by_discord(str(disc_user))
    return this_user, 200


@app.route("/users")
@requires_authorization
def get_users():
    """
    `get_users` returns a list of all users and a status code of 200
    :return: A list of all users in the database.
    """
    return {"users":get_all_users()}, 200


@app.route("/users/<discord_name>")
@requires_authorization
def get_user(discord_name):
    try:
        return get_user_by_discord(discord_name).as_json(), 200
    except Exception as e:
        return "Can't find user", 500


@app.get("/signup")
@requires_authorization
def signup():
    """
    > This function renders the signup page, which links a user's discord account to their battle.net account
    :return: The user's discord name and id
    """
    """Signup page, links bnet to discord"""
    user = discord.fetch_user()
    return render_template("signup.html", discord_name=str(user), id=user.id)


@app.post("/signup/<id>/<name>")
@requires_authorization
def post_signup(id, name):
    """
    We get the user's information from the form, and then we get their ranks from the API.

    :param id: The discord user id
    :param name: The name of the player
    :return: A dictionary of the players ranks for each role
    """
    """post endpoint for signup data"""
    user = discord.fetch_user()
    # Through requests we get user information
    bnet = request.form["bnet"]
    try:
        key = request.form["key"]
    except Exception:
        # No key
        return "", 401
    if not key == generate_access_key(int(id)):
        # No key
        return "", 401
    discord_name = name
    avatar = user.avatar_url
    roles = []
    try:
        request.form["tank"]
        roles.append((
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Tank_icon.svg/228px-Tank_icon.svg.png?20190921150350",
            "TANK"))
    except Exception:
        # This is rly bad code lol
        pass
    try:
        request.form["dps"]
        roles.append((
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Damage_icon.svg/1200px-Damage_icon.svg.png",
            "DPS"))
    except Exception:
        # This is rly bad code lol
        pass
    try:
        request.form["support"]
        roles.append((
            "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Support_icon.svg/1200px-Support_icon.svg.png",
            "SUPPORT"))
    except Exception:
        # This is rly bad code lol
        pass

    # We now get the players ranks
    try:
        role_ranks = {}
        # Getting the player's rank for each role from the API.
        ratings = json.loads(requests.get(f"https://ovrstat.com/stats/pc/{str(bnet).replace('#', '-')}").text)[
            "ratings"]
        for rating in ratings:
            print(f"Role {rating['role']}: {rating['level']}")
            role_ranks[rating["role"]] = rating['level']
    except TypeError:
        # Handle the NoneType error from iterating an empty element, ie the player hasn't placed
        print(f"Type Error {str(bnet).replace('#', '-')}")
        role_ranks = {'tank': 0, 'damage': 0, 'support': 0}
    except Exception:
        # Handle any other error, this bnet is busted probably
        # We should do something else here, but not sure what yet
        print(f"Other Error {str(bnet).replace('#', '-')}")
        # TODO
        role_ranks = {'tank': 0, 'damage': 0, 'support': 0}
    print(roles)
    user = discord.fetch_user()
    # Placeholder new user object for now
    # As the user class automatically stores the user in the database
    try:
        new_user = User(discord_name, bnet, roles, avatar, id, user.name, role_ranks)
    except Exception as e:
        print(e)
        return "", 500
    return "", 201


@app.get('/upload')
def get_upload():
    """
    It returns the HTML template for the upload page
    :return: The upload_log.html file is being returned.
    """
    """Route for uploading logs to server"""
    return render_template("upload_log.html")


@app.get('/game_log/<log>')
@requires_authorization
def log(log):
    """
    It takes a log file, parses it, and returns a rendered template with the parsed data

    :param log: The name of the log file
    :return: The log.html template is being returned.
    """
    """Displays the stats from the selected log"""
    user = discord.fetch_user()
    data = parse_log(log)
    scoreboard = data[2][data[0]]
    out = {"scoreboard": scoreboard, "player_heroes": data[1], "log": log}
    return out


@app.get('/game_logs')
def logs():
    """
    It lists all the files in the LOG_FOLDER directory and passes them to the view_games.html template
    :return: The list of all the games that have been uploaded.
    """
    """Shows all games"""
    uploaded_matches = os.listdir(LOG_FOLDER)
    print(uploaded_matches)
    return {"matches": uploaded_matches}


@app.get('/game_log/<log>/<player>')
@requires_authorization
def match_player_hero_stats(log, player):
    """
    It takes a log file and a player name, and returns a rendered template with the player's hero stats

    :param log: the log file to be parsed
    :param player: The player's name
    :return: A dictionary of the hero stats for the given player in the given match.
    """
    """Displays Hero stats for given player in given match"""
    data = parse_log(log)
    hero_stats = parse_hero_stats(data[2])[player]
    out = {"hero_stats": hero_stats, "player_heroes": data[1], "player": player}
    return out


@app.get('/queue_ow1/<role>')
@requires_authorization
def queue_player_ow1(role: str):
    """
    It takes a discord user id, and a role, and adds them to the queue. If the queue is full, it starts a match

    :param role: str
    :type role: str
    :return: The return is a tuple of two values. The first value is the response body, and the second value is the status
    code.
    """
    try:
        user_to_queue = discord.fetch_user()
        queue_state = get_players_in_queue()
        user_bnet = get_user_by_discord(str(user_to_queue)).bnet_name
        add_to_queue(user_bnet, role)
        if can_start:
            # TODO websocket stuff
            # start queue
            team_1, team_2 = matchmake_3()
            return {"team_1": team_1, "team_2": team_2}, 200
        return {"players_in_queue": queue_state}

    except DuplicateKeyError as e:
        print(e)
        print(type(e))
        return "", 500


@app.get('/queue_ow2/<role>')
@requires_authorization
def queue_player_ow2(role: str):
    """
    It queues a player for a role in Overwatch 2.

    :param role: str
    :type role: str
    :return: The return is a tuple of two values. The first value is the response body, and the second value is the status
    code.
    """
    try:
        user_to_queue = discord.fetch_user()
        queue_state = get_players_in_queue()
        user_bnet = get_user_by_discord(str(user_to_queue)).bnet_name
        add_to_queue(user_bnet, role)
        if can_start_ow2:
            # TODO websocket stuff
            # start queue
            team_1, team_2 = matchmake_3_ow2()
            return {"team_1": team_1, "team_2": team_2}, 200
        return {"players_in_queue": queue_state}

    except DuplicateKeyError as e:
        print(e)
        print(type(e))
        return "", 500


@app.get("/leaderboard/<role>")
def get_top_x_by_role(role):
    """
    It returns the top x (default 10) players for a given role

    :param role: The role you want to get the top players for
    :return: A list of the top 10 (or whatever number is specified) players in the specified role.
    """
    top = request.args.get("top", 10)
    return get_top_x_role(top, role)


@app.get("/leaderboard")
def get_top_x(role):
    """
    It returns the top 10 (or whatever number is specified in the `top` query parameter) users for the given role

    :param role: The role you want to get the top players for
    :return: A list of the top 10 (or whatever number is specified) users by overall rating.
    """
    top = request.args.get("top", 10)
    return get_top_x_overall(top)


if __name__ == '__main__':
    app.run()
