import os
import sys
import math
import operator
import socket

from operator import add
from rtree import index
from helper import *

# Path for spark source folder
os.environ['SPARK_HOME'] = "/home/hadoop/Spark"

# Path for pyspark and py4j
sys.path.append("/home/hadoop/Spark/python")
sys.path.append("/home/hadoop/Spark/python/lib/py4j-0.10.1-src.zip")

try:
    from pyspark import SparkContext
    from pyspark import SparkConf
    from hdfs.client import Client

    print ("Successfully imported Spark Modules")
except ImportError as e:
    print ("Can not import Modules", e)
    sys.exit(1)


class QuerierParallel(object):
    name = "test"
    master = "spark://master:7077",
    # prepath = "user/hadoop/trajectory/sim_trajectory_per_day/shanghai/2015-04"
    prepath2 = "user/hadoop/trajectory/sim_trajectory_per_day/shanghai/%s-%s/%s/"
    master_hdfs_path = "http://10.211.55.5:50070"
    files = {}

    @staticmethod
    def generate_files(date,
                       path="user/hadoop/trajectory/sim_trajectory_per_day/shanghai/%s-%s/%s", ):
        year, month, day = date.split('-')
        if date in QuerierParallel.files:
            return
        else:
            client = Client(QuerierParallel.master_hdfs_path, root="/", timeout=100, session=False)
            QuerierParallel.files.update({date: client.list(path % (year, month, day))})

    @staticmethod
    def multiple_request_query(query_dict_lists):
        spark_conf = SparkConf() \
            .setAppName("test") \
            .setMaster("spark://master:7077")
        spark_context = SparkContext(conf=spark_conf)
        spark_context.addPyFile("/home/hadoop/PycharmProjects/undergraduate/backend/helper.py")

        query = spark_context.parallelize(query_dict_lists, 4)
        ret = query.map(QuerierParallel.iknn_algorithm)
        return ret.collect()

    @staticmethod
    def partition_query(query_item, num_of_node):

        query_points, query_date, k = query_item['query_points'], query_item['query_date'], query_item['k']
        l = []
        for i in range(0, num_of_node):
            l.append([])
        for i in range(0, len(query_points)):
            l[i % num_of_node].append(query_points[i])

        query_dict_lists = []
        for i in range(0, num_of_node):
            temp_item = {'query_points': l[i], 'query_date': query_date, 'k': k}
            query_dict_lists.append(temp_item)
        # print query_dict_lists

        spark_conf = SparkConf() \
            .setAppName("test") \
            .setMaster("spark://master:7077")
        spark_context = SparkContext(conf=spark_conf)
        spark_context.addPyFile("/home/hadoop/PycharmProjects/undergraduate/backend/helper.py")
        query = spark_context.parallelize(query_dict_lists, 4)
        ret = query.map(QuerierParallel.iknn_algorithm) \
            .flatMap(lambda x: x) \
            .reduceByKey(lambda x, y: x+y) \
            .sortBy(lambda x: x[1], ascending=False) \
            .collect()
        return ret

    #  TODO right now, I have to remove the rtree.data and rtree.index manually.
    @staticmethod
    def get_rtree(date,
                  hdfs_rtree_path="/user/hadoop/rtree/shanghai/%s-%s/%s.%s",
                  local_path="/home/hadoop/data/downloaded/rtree/%s-%s/"):

        year, month, day = date.split('-')
        # guarantee there exists local directory for the worker nodes
        path = local_path % (year, month)
        if not os.path.exists(path):
            os.makedirs(path)

        client = Client(QuerierParallel.master_hdfs_path, root="/", timeout=100, session=False)
        client.download(hdfs_rtree_path % (year, month, day, "data"), path, overwrite=True)
        client.download(hdfs_rtree_path % (year, month, day, "index"), path, overwrite=True)

        # contruct the rtree
        rtree_properties = index.Property()
        rtree_properties.dat_extension = 'data'
        rtree_properties.idx_extension = 'index'
        rtree = index.Index(path + day, properties=rtree_properties)

        return rtree

    @staticmethod
    def iknn_algorithm(query_item):  # query_item = {'query_points', 'query_date', 'k'}

        # check the info at master:8080 stderr
        print '%%%%%%'
        print socket.gethostname()
        print '%%%%%%'

        query_points, query_date, k = query_item['query_points'], query_item['query_date'], query_item['k']
        _lambda, m = k, len(query_points)
        lowerbound = {}

        rtree = QuerierParallel.get_rtree(query_date)
        QuerierParallel.generate_files(query_date)

        year, month, day = query_date.split('-')
        path = QuerierParallel.prepath2 % (year, month, day)

        lambda_delta, lambda_delta_prev = {}, {}
        for i in range(0, len(query_points)):
            lambda_delta.update({i: _lambda})
            lambda_delta_prev.update({i: 0})

        count = 0
        while True:

            # list_lambda is union of lambda_nn_i. list_candidate is union of trajectory_scanned_i
            list_lambda, list_candidate = [], []

            # Optimization: specified delta for each query point
            for i in range(0, len(query_points)):
                lambda_nn_i, trajectory_scanned_i = QuerierParallel.knn_algorithm(rtree, query_points[i], query_date,
                                                                                  lambda_delta[i])
                list_lambda.append(lambda_nn_i)
                list_candidate.append(trajectory_scanned_i)
            candidate = [trajectory for candicate_i in list_candidate for trajectory in candicate_i]

            # remove the duplicate elements in candidate
            candidate = list(set(candidate))
            if len(candidate) >= k:
                # t0 = time.clock()
                # compute lower bound for all the trajectory, LB = {'trajectory': lb}
                for trajectory in candidate:
                    lowerbound.update(
                        {trajectory: QuerierParallel.compute_lb(trajectory, list_candidate, query_points, path)})

                # t1 = time.clock()
                # print '%s %f first %d' % (socket.gethostname(), (t1 - t0), query_item['k'])

                # compute upper bound
                ub_n = QuerierParallel.compute_ub_n(query_points, list_lambda)
                # t2 = time.clock()
                # print '%s %f second %d' % (socket.gethostname(), (t2 - t1), query_item['k'])
                # find the k largest potential candidate
                lb_sorted = sorted(lowerbound.items(), key=operator.itemgetter(1), reverse=True)
                k_lb = lb_sorted[0:k]

                if k_lb[-1][1] >= ub_n:
                    return QuerierParallel.refine(candidate, list_candidate, query_points, path, list_lambda, k)

            # Optimization
            count += 1
            assert len(query_points) == len(list_lambda)
            dec_rate, ret_rate = 0, 0
            dec_rate_list, ret_rate_list = [], []
            for i in range(0, len(query_points)):
                current_lambda, prev_lambda = lambda_delta[i], lambda_delta_prev[i]
                r = Helper.lnglat_eucildean_distance(query_points[i], list_lambda[i][-1])
                dec_rate_i = float(r) / (2 * current_lambda) * math.pow(math.e, -r)
                ret_rate_i = float(len(list_lambda[i])) / (current_lambda - prev_lambda)
                dec_rate_list.append(dec_rate_i)
                ret_rate_list.append(ret_rate_i)
                dec_rate += dec_rate_i
                ret_rate += ret_rate_i

            delta, mu, nu = m * k * pow(2, count), 0.5, 0.5
            for i in range(0, m):
                current_lambda = lambda_delta[i]
                lambda_delta_prev.update({i: current_lambda})
                delta_i = delta * (mu * (dec_rate_list[i] / dec_rate) + nu * (ret_rate_list[i] / ret_rate))
                lambda_delta.update({i: int(current_lambda + delta_i)})

    @staticmethod
    def knn_algorithm(query_rtree, query_point, query_date, _lambda):
        query_lng, query_lat = float(query_point[0]), float(query_point[1])
        lambda_nn, trajectory_scanned = [], []
        query_res = query_rtree.nearest((query_lng, query_lat), _lambda, objects=True)

        for item in query_res:
            lambda_nn.append([item.bbox[0], item.bbox[1]])
            idx = item.id / pow(10, 11)  # TODO optimise rtree id
            trajectory_scanned.append(QuerierParallel.files[query_date][idx])
        return lambda_nn, trajectory_scanned

    @staticmethod
    def compute_lb(trajectory, list_candidate, query_points, path):
        assert len(list_candidate) == len(query_points)

        trajectory_path = path + trajectory
        trajectory_points = QuerierParallel.hdfs_file2points(trajectory_path)

        lower_bound = 0
        for i in range(0, len(list_candidate)):
            if trajectory in list_candidate[i]:
                lower_bound += math.pow(math.e,
                                        -(QuerierParallel.compute_distance_q(query_points[i], trajectory_points)))
        return lower_bound

    @staticmethod
    def compute_ub(trajectory, list_candidate, query_points, path, list_lambda):
        assert len(list_candidate) == len(query_points)

        # trajectory_path = '%s/%s/%s' % (QuerierParallel.prepath, query_date, trajectory)
        trajectory_path = path + trajectory
        trajectory_points = QuerierParallel.hdfs_file2points(trajectory_path)
        upper_bound = 0

        for i in range(0, len(list_candidate)):
            if trajectory in list_candidate[i]:
                upper_bound += math.pow(math.e,
                                        -(QuerierParallel.compute_distance_q(query_points[i], trajectory_points)))
            else:
                upper_bound += math.pow(math.e,
                                        -(Helper.lnglat_eucildean_distance(query_points[i], list_lambda[i][-1])))
        return upper_bound

    @staticmethod
    def refine(candidate, list_candidate, query_points, path, list_lambda, k):
        upperbound, k_BCT = {}, {}

        for trajectory in candidate:
            upperbound.update({trajectory: QuerierParallel.compute_ub(trajectory, list_candidate, query_points,
                                                                       path, list_lambda)})

        # sort candidates in C by UB in a descending order
        upperbound_sorted = sorted(upperbound.items(), key=operator.itemgetter(1), reverse=True)

        for i in range(0, len(upperbound_sorted)):
            trajectory = upperbound_sorted[i][0]

            # trajectory_path = '%s/%s/%s' % (QuerierParallel.prepath, query_date, trajectory)
            trajectory_path = path + trajectory
            trajectory_points = QuerierParallel.hdfs_file2points(trajectory_path)

            # TODO
            similarity = QuerierParallel.similarity(trajectory_points, query_points)  # Without order
            # similarity = Querier.similarity_order(trajectory_points, query_points)  # With order

            if i < k:
                k_BCT.update({upperbound_sorted[i][0]: similarity})
            else:
                min_trajectory, min_ub = min(k_BCT.items(), key=lambda t: t[1])
                if similarity > min_ub:
                    del k_BCT[min_trajectory]
                    k_BCT.update({trajectory: similarity})
                if i == len(upperbound_sorted) - 1 or min_ub > upperbound_sorted[i + 1][1]:
                    return sorted(k_BCT.items(), key=operator.itemgetter(1), reverse=True)

    @staticmethod
    def compute_ub_n(query_points, list_lambda):
        assert len(query_points) == len(list_lambda)
        ub_n = 0
        for i in range(0, len(query_points)):
            ub_n += math.pow(math.e, (-1) * Helper.lnglat_eucildean_distance(query_points[i], list_lambda[i][-1]))
        return ub_n

    @staticmethod
    def compute_distance_q(point, trajectory_points):
        min_dist = sys.maxint

        for trajectory_point in trajectory_points:
            dist = Helper.lnglat_eucildean_distance(trajectory_point, point)
            if dist < min_dist:
                min_dist = dist
        return min_dist

    @staticmethod
    def similarity(trajectory_points, query_points):
        ret = 0
        for query_point in query_points:
            ret += math.pow(math.e, -QuerierParallel.compute_distance_q(query_point, trajectory_points))
        return ret

    @staticmethod
    def similarity_order(trajectory_points, query_points):
        if len(trajectory_points) == 0 or len(query_points) == 0:
            return 0
        return math.pow(math.e, -(Helper.lnglat_eucildean_distance(trajectory_points[0], query_points[0]))) + max(
            QuerierParallel.similarity_order(trajectory_points[1:], query_points),
            QuerierParallel.similarity_order(trajectory_points, query_points[1:]))

    @staticmethod
    def hdfs_file2points(path):
        client = Client(QuerierParallel.master_hdfs_path, root="/", timeout=100, session=False)
        points = []
        with client.read(path) as f:
            for line in f:
                info = line.strip('\n').split('\t')
                points.append([float(info[0]), float(info[1])])
        f.close()
        return points


if __name__ == '__main__':

    '''
    query_points = [[121.359331, 31.184999], [121.360705, 31.287742], [121.50284, 31.294784]]
    query_item = {'query_points': query_points, 'query_date': '2015-04-01', 'k': 2}
    query_points2 = [[121.449803, 31.225391], [121.446351, 31.231352]]
    query_item2 = {'query_points': query_points2, 'query_date': '2015-04-02', 'k': 3}
    query_points3 = [[121.420210, 30.940452], [120.889590, 30.911189], [120.268870, 30.562625]]
    query_item3 = {'query_points': query_points3, 'query_date': '2015-04-02', 'k': 4}
    query_points4 = [[121.449803, 31.225391], [121.446351, 31.231352]]
    query_item4 = {'query_points': query_points4, 'query_date': '2015-04-02', 'k': 5}
    query_dict_lists = [query_item, query_item2, query_item3, query_item4]
    for res in QuerierParallel.multiple_request_query(query_dict_lists):
        print res
    '''

    query_item = {'query_points': [[120.666481, 31.291738], [120.642091, 31.331085], [120.551929, 31.367378], [120.485923, 31.470893],
                    [120.337090, 31.627510], [120.252312, 31.692899], [120.129056, 31.738499], [120.046136, 31.754994]],
                  'query_date': '2015-04-02',
                  'k': 3}
    for res in QuerierParallel.partition_query(query_item, 2):
        print res