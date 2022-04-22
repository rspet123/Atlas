import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from parser_tools import parse_log, generate_key
import configparser
from user import User
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized

app = Flask(__name__)

# Get Config Data
config = configparser.ConfigParser()
config.read("config.ini")
CLIENT_ID = config.get("DISCORD", "CLIENT_ID")
CLIENT_SECRET = config.get("DISCORD", "CLIENT_SECRET")
CALLBACK = config.get("DISCORD", "CALLBACK")

key = generate_key()
app.secret_key = key
print(key)
COLUMNS = ["Player", "Hero Damage Dealt", "Barrier Damage Dealt",
           "Damage Blocked", "Damage Taken", "Deaths", "Eliminations", "Defensive Assists",
           "Final Blows", "Environmental Deaths", "Environmental Kills", "Healing Dealt",
           "Multikill Best", "Multikills", "Objective Kills", "Objective Assists", "Solo Kills",
           "Ultimates Earned", "Ultimates Used", "Weapon Accuracy", "All Damage Dealt", "Hero", "Team"]

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
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def hello_world():
    return redirect(url_for("post_upload"))


@app.post('/upload')
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
        return redirect(url_for('log', log=filename))
    return 'Error?!'


@app.route("/login/")
def login():
    return discord.create_session()


@app.route("/auth")
def callback():
    discord.callback()
    return (redirect(url_for("curr_user")))


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
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
    print(roles)
    user = discord.fetch_user()
    # Placeholder new user object for now
    # As the user class automatically stores the user in the database
    new_user = User(discord_name, bnet, roles, avatar, id, user.name)
    return (redirect(url_for("curr_user")))


@app.get('/upload')
def get_upload():  # put application's code here
    return render_template("upload_log.html")


@app.get('/game_log/<log>')
def log(log):  # put application's code here
    data = parse_log(log)

    return render_template("log.html", COLUMNS=COLUMNS, scoreboard=data[0], player_heroes=data[1])


if __name__ == '__main__':
    app.run()
