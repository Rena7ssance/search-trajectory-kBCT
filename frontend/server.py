# -*- coding: utf-8 -*-
import json
import os

from flask import Flask, render_template, request, url_for, session, flash
from werkzeug.utils import redirect

from backend.helper import Helper
from backend.querier import Querier
from backend.simlifier import Simplifier

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None

    # TODO log authentication
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        if True:
            session['username'] = username
            session['logged_in'] = True
            return redirect(url_for('index_page'))
        else:
            error = 'Invalid username/password'
    return render_template("login.html", error=error)


@app.route('/logout')
def logout():
    if session['logged_in']:
        session.pop('logged_in', None)
        session.pop('username', None)

        flash('You were logger out ')
        return redirect(url_for('index_page'))


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
        print trajectories
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
        query_points = Simplifier.dp_algorithm(query_points, 0, len(query_points) - 1, epsilon=5e-02)
        print query_points

    querier = Querier(prepath='../backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/%s' % query_date,
                      rtreepath='../backend/data/rtree/shanghai/2015-04/%s' % query_date)  # date
    query_results = querier.iknn_algorithm(query_points, 3)
    points_results = []
    for item in query_results:
        user, r = item[0].split(' ')
        path = '../backend/data/trajectory/trajectory_per_user/shanghai/2015-04/'
        trajectory = '%s/%s/%s %s.txt' % (path, user, r, query_date)
        points_results.append(Helper.file2points(trajectory))
    return json.dumps(points_results)



@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == '__main__':
    app.run()
