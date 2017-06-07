# -*- coding: utf-8 -*-
import os

import operator

from time import time
from backend.querier import Querier
from processor import Processor, Helper

if __name__ == '__main__':

    rp = 'data/trajectory/raw_data/vehicle_gps_log_2015-04.txt'
    wd = 'data/trajectory/raw_trajectory'
    c = 'shanghai'
    c_range = {'lng': [119.5, 123.5], 'lat': [30.5, 32.5]}

    path = '/Users/Rena7ssance/Projects/Python/undergraduate/backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/02/P006000400001579 r4'
    query_points = Helper.file2points(path)
    # print query_points
    query_date = '2015-04-02'
    query_item = {'query_points': query_points, 'query_date': query_date}

    year, month, day = query_date.split('-')
    prepath = 'data/trajectory/sim_trajectory_per_day/shanghai/%s-%s/%s' % (year, month, day)
    rtreepath = 'data/rtree/shanghai/%s-%s/%s' % (year, month, day)

    q = Querier(prepath=prepath,
                rtreepath=rtreepath)
    t0 = time()
    a = q.iknn_algorithm(query_item['query_points'], 3)
    t1 = time()
    for item in a:
        print item
        # print Helper.file2points(
        #    '/Users/Rena7ssance/Projects/Python/undergraduate/backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/02/%s' %
        #    item[0])

    print 'function takes %f' % (t1 - t0)
