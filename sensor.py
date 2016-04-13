# imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
from datetime import datetime
import pygal

# configuration
DATABASE = '/tmp/sensors.db'
DEBUG = True
SECRET_KEY = 'development key'

# app creation
app = Flask(__name__)
app.config.from_object(__name__)
# To read from settings file, set SENSOR_SETTINGS in envvar
#app.config.from_envvar('SENSOR_SETTINGS', slient=True)

# initialize database
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# connect to database
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# handle requests
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'bd', None)
    if db is not None:
        db.close()

# viewing database
@app.route('/')
def show_entries():
    cur = g.db.execute('SELECT date, temperature, humidity, pressure FROM weather ORDER BY id desc')
    entries = [dict(date=row[0], temperature=row[1], humidity=row[2], pressure=row[3]) for row in cur.fetchall()]

    # datetimeline = pygal.DateTimeLine(
    #         x_label_rotation=30, truncate_label=-1,
    #         x_value_formatter=lambda dt: dt.strftime('%d, %b %Y %I:%M %p')
    #         )
    # datetimeline.add("Temp F", [(row[0], row[1]) for row in cur.fetchall()])
    # datetimeline.render_response()

    # return render_template('show_entries.html', wgraph=datetimeline, weather=entries)
    return render_template('show_entries.html', weather=entries)

@app.route('/wgraph.svg')
def weather_route():
    cur = g.db.execute('SELECT date, temperature, humidity, pressure FROM weather ORDER BY id desc')

    datetimeline = pygal.DateTimeLine(
            x_label_rotation=30, truncate_label=-1,
            x_value_formatter=lambda dt: dt.strftime('%d, %b %Y %I:%M %p')
            )
    datetimeline.add("Temp F", [(row[0], row[1]) for row in cur.fetchall()])

    return datetimeline.render_response()


# adding entries to database
@app.route('/data', methods=['POST'])
def add_data():
    mkey = request.args.get('key')
    if mkey != SECRET_KEY:
        abort(401)
    temp = request.args.get('temp')
    humidity = request.args.get('humidity')
    pressure = request.args.get('pressure')
    now = datetime.now()
    g.db.execute('INSERT INTO weather (date, temperature, humidity, pressure) VALUES (?, ?, ?, ?)', \
            [now, temp, humidity, pressure])
    g.db.commit()
    return 200


if __name__ == '__main__':
    app.run()
