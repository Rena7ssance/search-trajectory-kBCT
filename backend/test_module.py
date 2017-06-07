import os
import random

from time import time
from backend.querier import Querier
from processor import Processor, Helper

if __name__ == '__main__':

    all_paths = os.listdir(
        '/Users/Rena7ssance/Projects/Python/undergraduate/backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/01')
    paths_dict = {}
    for path in all_paths:
        trajectory = '/Users/Rena7ssance/Projects/Python/undergraduate/backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/01/' + path
        points = Helper.file2points(trajectory)
        if not len(points) in paths_dict:
            paths_dict.update({len(points): [path]})
        else:
            paths_dict[len(points)].append(path)

    # Initialize the query module
    year, month, day = '2015', '04', '01'
    prepath = 'data/trajectory/sim_trajectory_per_day/shanghai/%s-%s/%s' % (year, month, day)
    rtreepath = 'data/rtree/shanghai/%s-%s/%s' % (year, month, day)
    q = Querier(prepath=prepath,
                rtreepath=rtreepath)

    # test k
    '''
    number_of_query_point = 9
    paths = paths_dict.get(number_of_query_point)
    if len(paths) > 20:
        paths = random.sample(paths, 20)
        
    for k in range(1, 16):
        t = 0
        for path in paths:
            trajectory = '/Users/Rena7ssance/Projects/Python/undergraduate/backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/01/' + path
            query_points = Helper.file2points(trajectory)

            s = time()
            a = q.iknn_algorithm(query_points, k)
            e = time()
            t += (e - s)
        print t / len(paths)
    '''

    # test query_number
    '''
    number_of_k = 8
    for number in range(2, 11):
        paths = random.sample(paths_dict.get(number), 20)
        t = 0
        count = len(paths)
        for path in paths:
            trajectory = '/Users/Rena7ssance/Projects/Python/undergraduate/backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/01/' + path
            query_points = Helper.file2points(trajectory)
            s = time()
            a = q.iknn_algorithm(query_points, number_of_k)
            e = time()
            t += (e-s)
        print t / count
    '''

    # test accuracy k
    '''
    number_of_query_point = 11
    paths = paths_dict.get(number_of_query_point)
    if len(paths) > 20:
        paths = random.sample(paths, 10)

    for k in range(3, 16):
        average_sum = 0
        for path in paths:
            trajectory = '/Users/Rena7ssance/Projects/Python/undergraduate/backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/01/' + path
            query_points = Helper.file2points(trajectory)

            res = q.iknn_algorithm(query_points, k)
            if res is None:
                #print 'none'
                continue

            sim_sum = 0
            for item in res:
                sim_sum += item[1]
            average = float(sim_sum) / (number_of_query_point * len(res))
            average_sum += average
        print float(average_sum) / len(paths)
    '''

    # test accurary number of query point
    for number_of_k in range(3, 9):
        for number in range(2, 11):
            paths = random.sample(paths_dict.get(number), 10)

            average_sum = 0
            for path in paths:
                trajectory = '/Users/Rena7ssance/Projects/Python/undergraduate/backend/data/trajectory/sim_trajectory_per_day/shanghai/2015-04/01/' + path
                query_points = Helper.file2points(trajectory)
                res = q.iknn_algorithm(query_points, number_of_k)
                if res is None:
                    continue
                sim_sum = 0
                for item in res:
                    sim_sum += item[1]
                average = float(sim_sum) / len(res)
                average_sum += average
            print float(average_sum) / len(paths)

        print