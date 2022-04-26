import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from parser_tools import parse_log, generate_key, parse_hero_stats
from keygen import generate_access_key
import configparser
from user import User
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import requests
import json
from match import add_match
from ow_info import MAPS,COLUMNS,STAT_COLUMNS
app = Flask(__name__)

# Get Config Data
config = configparser.ConfigParser()
config.read("config.ini")
CLIENT_ID = config.get("DISCORD", "CLIENT_ID")
CLIENT_SECRET = config.get("DISCORD", "CLIENT_SECRET")
CALLBACK = config.get("DISCORD", "CALLBACK")

#Generate Flask Secret key for auth
key = generate_key()
app.secret_key = key

# Set up discord auth config
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
app.config["DISCORD_CLIENT_ID"] = CLIENT_ID
app.config["DISCORD_CLIENT_SECRET"] = CLIENT_SECRET
app.config["DISCORD_REDIRECT_URI"] = CALLBACK

# set up file storage config
LOG_FOLDER = "log_folder"
app.config['UPLOAD_FOLDER'] = LOG_FOLDER
ALLOWED_EXTENSIONS = {'txt'}

# Set up OAuth session
discord = DiscordOAuth2Session(app)


def allowed_file(filename):
    """Checks if our file is of the correct type"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def landing():
    """Landing page"""
    return redirect(url_for("post_upload"))


@app.post('/upload')
@requires_authorization
def post_upload():
    """Post our file to the server"""
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
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
        return redirect(url_for('log', log=filename))
    return 'Error?!'


@app.route("/login")
def login():
    """Redirect to discord auth"""
    return discord.create_session()


@app.route("/auth")
def callback():
    """Callback for discord auth"""
    discord.callback()
    return (redirect(url_for("curr_user")))


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    """Errror handler for unauthed user, redirects to login"""
    return redirect(url_for("login"))


@app.route("/me")
@requires_authorization
def curr_user():
    """User landing page, after logging in"""
    user = discord.fetch_user()
    print(user)
    disc_user = User.get_user_by_discord(str(user))
    print(disc_user)
    if disc_user is None:
        # If the user isnt in our database, we make them signup
        return redirect(url_for("signup"))
    return render_template("user.html", user=disc_user)


@app.get("/signup")
@requires_authorization
def signup():
    """Signup page, links bnet to discord"""
    user = discord.fetch_user()
    return render_template("signup.html", discord_name=str(user), id=user.id)


@app.post("/signup/<id>/<name>")
@requires_authorization
def post_signup(id, name):
    """post endpoint for signup data"""
    user = discord.fetch_user()
    # Through requests we get user information
    bnet = request.form["bnet"]
    try:
        key = request.form["key"]
    except Exception:
        return render_template("nokey.html")
    if not key == generate_access_key(int(id)):
        return render_template("nokey.html")
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

    #We now get the players ranks
    try:
        role_ranks = {}
        ratings = json.loads(requests.get(f"https://ovrstat.com/stats/pc/{str(bnet).replace('#','-')}").text)["ratings"]
        for rating in ratings:
            print(f"Role {rating['role']}: {rating['level']}")
            role_ranks[rating["role"]] = rating['level']
    except TypeError:
        # Handle the NoneType error from iterating an empty element, ie the player hasn't placed
        print(f"Type Error {str(bnet).replace('#','-')}")
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
    new_user = User(discord_name, bnet, roles, avatar, id, user.name,role_ranks)
    return (redirect(url_for("curr_user")))


@app.get('/upload')
def get_upload():
    """Route for uploading logs to server"""
    return render_template("upload_log.html")


@app.get('/game_log/<log>')
@requires_authorization
def log(log):
    """Displays the stats from the selected log"""
    user = discord.fetch_user()
    data = parse_log(log)
    scoreboard = data[2][data[0]]
    return render_template("log.html",
                           COLUMNS=COLUMNS,
                           scoreboard=scoreboard,
                           player_heroes=data[1],
                           log=log)
@app.get('/game_logs')
def logs():
    """Shows all games"""
    uploaded_matches = os.listdir(LOG_FOLDER)
    print(uploaded_matches)
    return render_template("view_games.html",games = uploaded_matches)

@app.get('/game_log/<log>/<player>')
def match_player_hero_stats(log,player):
    """Displays Hero stats for given player in given match"""
    data = parse_log(log)
    hero_stats = parse_hero_stats(data[2])[player]
    return render_template("match_player_hero_stats.html",
                           hero_stats=hero_stats,
                           player_heroes=data[1],
                           player=player,
                           STATS_COLUMNS=STAT_COLUMNS)


if __name__ == '__main__':
    app.run()
