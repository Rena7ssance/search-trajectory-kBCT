# -*- coding: utf-8 -*-
from backend.helper import Helper
from backend.querier import Querier

from distance.edwp import EDwP
from distance.lcss import LCSS

if __name__ == '__main__':
    path1 = '/Users/Rena7ssance/Projects/Python/undergraduate/backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/02/P006000400001579 r4'
    query_points1 = Helper.file2points(path1)

    path2 = '/Users/Rena7ssance/Projects/Python/undergraduate/backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/02/P006000400001579 r7'
    query_points2 = Helper.file2points(path2)

    print query_points1
    print query_points2

    # 注意 similarity 前面是待查询的轨迹 后面是查询点集或查询轨迹
    print Querier.similarity(query_points2, query_points1)
    #print LCSS.get_distance(query_points2, query_points1)
    #print EDR.get_distance(query_points2, query_points1)
    print EDwP.get_distance(query_points2, query_points1)
