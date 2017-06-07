# -*- coding: utf-8 -*-
import json
import os

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

from backend.helper import Helper
from backend.querier import Querier
from backend.simlifier import Simplifier

app = Flask(__name__)  # create the application instance :)
app.secret_key = os.urandom(24)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE='flaskr.db',
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/register', methods=['POST', 'GET'])
def resgiter():
    if request.method == 'GET':
        db = get_db()
        result = db.execute('select admin_name, password from admins')
        print result.fetchall()
        return render_template("register.html")
    elif request.method == 'POST':
        db = get_db()
        db.execute('INSERT INTO admins (admin_name, password) VALUES (?, ?)',
                   [request.form['admin_name'], request.form['password']])
        db.commit()
        return render_template("register.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None

    # TODO log authentication
    if request.method == 'POST':  # send the request
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        is_admin = request.form.get('check-admin', None)

        if is_admin is None:  # login as a user

            if not os.path.exists('../backend/data/trajectory/trajectory_per_user/shanghai/2015-04/%s' % username):
                error = 'Invalid username'
                return render_template("login.html", error=error)

            session['username'] = username
            session['logged_in'] = True
            return redirect(url_for('index_page'))

        elif is_admin == 'admin':  # login as an admin
            session['admin'] = username
            session['logged_in'] = True
            return redirect(url_for('admin_page'))

        else:  # into the login page
            error = 'Invalid username/password'
    return render_template("login.html", error=error)


@app.route('/logout')
def logout():
    if session['logged_in']:
        session.pop('logged_in', None)
        session.pop('username', None)
        flash('You were logger out ')
        return redirect(url_for('index_page'))


@app.route('/admin')
def admin_page():
    return render_template("admin.html", username=session['admin'])


@app.route('/index')
def index_page():
    if 'username' in session:
        # TODO -> the path of all the trajectory of user
        dirs = os.listdir(
            "../backend/data/trajectory/trajectory_per_user/shanghai/2015-04/%s" % session['username'])
        files = [str(f).split(' ') for f in dirs]
        trajectories = []
        for f in files:
            trajectories.append({"r": f[0], "date": f[1][:-4]})
        return render_template("index.html", username=session['username'], Month='April', trajectories=trajectories)
    else:
        return render_template("index.html", username=None, Month=None, trajectories=None)


@app.route('/display', methods=['POST'])
def display_post_request():
    filepath = request.form['filepath']
    absolution_path = '../backend/data/trajectory/trajectory_per_user/shanghai/2015-04/%s' % filepath
    trajectory_points = Helper.file2points(absolution_path)
    return json.dumps(trajectory_points)


@app.route('/search', methods=['POST'])
def search_post_request():
    query_type = request.form['queryType']
    query_date = request.form['queryDate']
    query_points = None

    if query_type == 'p':
        # Search similar trajectory by location(point)
        query_points = json.loads(request.form['queryPoints']).values()

    elif query_type == 't':
        # Search similar trajectory by a specified trajectory
        query_points = json.loads(request.form['queryPoints'])
        query_points = Simplifier.dp_algorithm(query_points, 0, len(query_points) - 1, epsilon=1e-04)

    year, month, day = query_date.split('-')
    prepath = '../backend/data/trajectory/sim_trajectory_per_day/shanghai/%s-%s/%s' % (year, month, day)
    rtreepath = '../backend/data/rtree/shanghai/%s-%s/%s' % (year, month, day)
    querier = Querier(prepath=prepath,
                      rtreepath=rtreepath)
    query_results = querier.iknn_algorithm(query_points, 3)

    trajectory_results, points_results = [], []
    for item in query_results:
        user, r = item[0].split(' ')
        path = '../backend/data/trajectory/trajectory_per_user/shanghai/%s-%s/' % (year, month)
        trajectory = '%s/%s/%s %s.txt' % (path, user, r, day)
        trajectory_results.append('%s' % user)
        points_results.append(Helper.file2points(trajectory))

    # return json.dumps(points_results)

    ret = [trajectory_results, points_results]
    return json.dumps(ret)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == '__main__':
    init_db()
    app.run()
