# -*- coding: utf-8 -*-
import os

import operator

from backend.helper import Helper
from backend.querier import Querier
from processor import Processor

if __name__ == '__main__':
    rp = 'data/trajectory/raw_data/vehicle_gps_log_2015-04.txt'
    wd = 'data/trajectory/raw_trajectory'
    c = 'shanghai'
    c_range = {'lng': [119.5, 123.5], 'lat': [30.5, 32.5]}

    p = Processor(rp, wd, c, c_range)
    # p.pre_extract()

    # TODO the simplified rate could be better set for project
    # p.simplification_per_user()
    # p.per_user2per_day()
    # p.construct_rtree()

    from time import time
    q = Querier(prepath='data/trajectory/sim_trajectory_per_day/shanghai/2015-04/01')
    t0 = time()
    a = q.iknn_algorithm([[121.65047, 31.271888], [121.551866,31.213136], [121.435922, 31.196443]], 5)
    t1 = time()
    print 'function takes %f' % (t1 - t0)
    for item in a:
        print Helper.file2points('data/trajectory/sim_trajectory_per_day/shanghai/2015-04/01/%s' % item[0])
        print