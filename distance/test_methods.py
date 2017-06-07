# -*- coding: utf-8 -*-
import os

import operator
from time import time

from backend.helper import Helper
from backend.querier import Querier
from distance.edwp import EDwP
from distance.lcss import LCSS

if __name__ == '__main__':
    path = '/Users/Rena7ssance/Projects/Python/undergraduate/backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/02/P006000400001579 r4'
    query_points = Helper.file2points(path)

    k_BCT = {}
    path = '/Users/Rena7ssance/Projects/Python/undergraduate/backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/02'
    candicate = os.listdir(path)

    t0 = time()
    for i in range(0, len(candicate)):
        trajectory = Helper.file2points(path + '/' + candicate[i])
        similarity = EDwP.get_distance(trajectory, query_points)

        k_BCT.update({candicate[i]: similarity})
    res = sorted(k_BCT.items(), key=operator.itemgetter(1), reverse=True)
    t1 = time()
    print res
    print 'function takes %f' % (t1 - t0)

    print Helper.file2points('/Users/Rena7ssance/Projects/Python/undergraduate/backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/02/' + 'P006000400001579 r7')
