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

    querys = [[[121.359331, 31.184999], [121.360705, 31.287742], [121.50284, 31.294784]],
              [[121.449803, 31.225391], [121.446351, 31.231352]],
              [[121.420210, 30.940452], [120.889590, 30.911189], [120.268870, 30.562625]],
              [[121.449803, 31.225391], [121.446351, 31.231352]]]

    query_points = [[120.666481, 31.291738], [120.642091, 31.331085], [120.551929, 31.367378], [120.485923, 31.470893],
                    [120.337090, 31.627510], [120.252312, 31.692899], [120.129056, 31.738499], [120.046136, 31.754994]]
    query_date = '2015-04-02'
    query_item = {'query_points': query_points, 'query_date': query_date}

    year, month, day = query_date.split('-')
    prepath = 'data/trajectory/sim_trajectory_per_day/shanghai/%s-%s/%s' % (year, month, day)
    rtreepath = 'data/rtree/shanghai/%s-%s/%s' % (year, month, day)

    q = Querier(prepath=prepath,
                rtreepath=rtreepath)
    t0 = time()
    a = q.iknn_algorithm(query_item['query_points'], 5)
    print a
    t1 = time()
    print 'function takes %f' % (t1 - t0)
    print Helper.file2points(
        "/Users/Rena7ssance/Projects/Python/undergraduate/backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/02/P006000300003481 r7")
