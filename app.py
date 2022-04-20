import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import pymongo
app = Flask(__name__)
COLUMNS = ["Player", "Hero Damage Dealt", "Barrier Damage Dealt",
           "Damage Blocked", "Damage Taken", "Deaths", "Eliminations", "Defensive Assists",
           "Final Blows", "Environmental Deaths", "Environmental Kills", "Healing Dealt",
           "Multikill Best", "Multikills", "Objective Kills", "Objective Assists", "Solo Kills",
           "Ultimates Earned", "Ultimates Used", "Weapon Accuracy", "All Damage Dealt", "Hero", "Team"]
LOG_FOLDER = "log_folder"
app.config['UPLOAD_FOLDER'] = LOG_FOLDERdf
ALLOWED_EXTENSIONS = {'txt'}


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
        return redirect(url_for('log',log=filename))
    return 'Hello World!'


@app.get('/upload')
def get_upload():  # put application's code here
    return render_template("upload_log.html")


@app.get('/game_log/<log>')
def log(log):  # put application's code here
    player_heroes = {}
    log_stats = {}
    with open(f"{LOG_FOLDER}/{log}",encoding='utf-8') as log_file:
        lines = log_file.readlines()
        for line in lines:

            split_line = line.split(" ",1)
            time_stamp = split_line[0]
            time_stats = split_line[1].split("/")
            if time_stamp not in log_stats:
                log_stats[time_stamp] = []
            curr_stats = list(zip(COLUMNS, time_stats))
            stat_dict = {}
            for stat in curr_stats:
                try:
                    stat_dict[stat[0]] = float(stat[1])
                except:
                    stat_dict[stat[0]] = stat[1]
            log_stats[time_stamp].append(stat_dict.copy())
    prev = time_stamp
    for time in log_stats:
        for player in log_stats[time]:
            if player["Player"] not in player_heroes:
                player_heroes[player["Player"]] = {}
            if not player["Hero"] == "":
                player_heroes[player["Player"]][player["Hero"]]=player_heroes[player["Player"]].get(player["Hero"],0)+3
        if len(log_stats[time]) < 12:
            time_stamp = prev
            break
        prev = time
    print(player_heroes)


    return render_template("log.html",COLUMNS=COLUMNS,scoreboard = log_stats[time_stamp],player_heroes = player_heroes)


if __name__ == '__main__':
    app.run()
