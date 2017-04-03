# -*- coding: utf-8 -*-
import json

from flask import Flask, render_template, request

from backend.helper import Helper
from backend.querier import Querier
from backend.simlifier import Simplifier

app = Flask(__name__)


@app.route('/index')
def index_page():
    return render_template("index.html")


@app.route('/display', methods=['POST'])
def display_post_request():
    filepath = request.form['filepath']
    absolution_path = '../backend/data/trajectory/trajectory_per_user/shanghai/2015-04/%s' % filepath
    trajectory_points = Helper.file2points(absolution_path)
    return json.dumps(trajectory_points)


@app.route('/search', methods=['POST'])
def search_post_request():
    query_type = request.form['queryType']
    query_points = None
    if query_type == 'p':  # Search similar trajectory by location(point)
        query_points = json.loads(request.form['queryPoints']).values()
    elif query_type == 't':
        query_points = json.loads(request.form['queryPoints'])  # Search similar trajectory by a specified trajectory
        query_points = Simplifier.dp_algorithm(query_points, 0, len(query_points) - 1)

    querier = Querier(prepath='../backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/01',
                      rtreepath='../backend/data/rtree/shanghai/2015-04/01')
    query_results = querier.iknn_algorithm(query_points, 3)
    points_results = []
    for item in query_results:
        user, r = item[0].split(' ')
        path = '../backend/data/trajectory/trajectory_per_user/shanghai/2015-04/'
        trajectory = '%s/%s/%s %s.txt' % (path, user, r, '01')
        points_results.append(Helper.file2points(trajectory))
    return json.dumps(points_results)


if __name__ == '__main__':
    app.run()
