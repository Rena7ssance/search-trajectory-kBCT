# -*- coding: utf-8 -*-
import os
import sys
import math

import operator
from rtree import index
from backend.helper import Helper


class Querier(object):
    def __init__(self, prepath, rtreepath):
        self._prepath = prepath
        self._rtreepath = rtreepath
        self._files = os.listdir(prepath)

    def get_rtree(self):
        rtree_properties = index.Property()
        rtree_properties.dat_extension = 'data'
        rtree_properties.idx_extension = 'index'
        rtree = index.Index(self._rtreepath, properties=rtree_properties)
        return rtree

    """
    class function: Incremental K-Nearest Neighbor based Algorithm
    retrieve the candidate trajectories in a filter-and-refine fashion
    Return format: list(["obd_id rx", similarity])
    """

    def iknn_algorithm(self, query_points, k):
        _lambda, m = k, len(query_points)
        lowerbound = {}
        rtree = self.get_rtree()

        lambda_delta, lambda_delta_prev = {}, {}
        for i in range(0, len(query_points)):
            lambda_delta.update({i: _lambda})
            lambda_delta_prev.update({i: 0})

        count = 0
        while True:
            # list_lambda is union of lambda_nn_i. list_candidate is union of trajectory_scanned_i
            list_lambda, list_candidate = [], []

            #
            # for query_point in query_points:
            #     lambda_nn_i, trajectory_scanned_i = self.knn_algorithm(query_point, _lambda)
            #     list_lambda.append(lambda_nn_i)
            #     list_candidate.append(trajectory_scanned_i)
            # candidate = [trajectory for sub_list in list_candidate for trajectory in sub_list]
            #

            # Optimization: specified delta for each query point

            for i in range(0, len(query_points)):
                lambda_nn_i, trajectory_scanned_i = self.knn_algorithm(rtree, query_points[i], lambda_delta[i])
                list_lambda.append(lambda_nn_i)
                list_candidate.append(trajectory_scanned_i)
            candidate = [trajectory for candicate_i in list_candidate for trajectory in candicate_i]

            # remove the duplicate elements in candidate
            candidate = list(set(candidate))
            if len(candidate) >= k:

                # compute lower bound for all the trajectory, LB = {'trajectory': lb}
                for trajectory in candidate:
                    lowerbound.update({trajectory: self.compute_lb(trajectory, list_candidate, query_points)})

                # compute upper bound
                ub_n = Querier.compute_ub_n(query_points, list_lambda)

                # find the k largest potential candidate
                lb_sorted = sorted(lowerbound.items(), key=operator.itemgetter(1), reverse=True)
                k_lb = lb_sorted[0:k]
                if k_lb[-1][1] >= ub_n:
                    return self.refine(candidate, list_candidate, query_points, list_lambda, k)


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

    """
    class function: nearest-neighbor algorithm
    retrieve the λ-NN(q_i) of q_i and then generate the child candidate set
    """

    # TODO date parameter, now is preset 2015-04/01
    def knn_algorithm(self, rtree, query_point, _lambda):
        query_lng, query_lat = float(query_point[0]), float(query_point[1])
        lambda_nn, trajectory_scanned = [], []
        query_res = rtree.nearest((query_lng, query_lat), _lambda, objects=True)

        for item in query_res:
            lambda_nn.append([item.bbox[0], item.bbox[1]])
            idx = item.id / pow(10, 11)  # TODO optimise rtree id
            trajectory_scanned.append(self._files[idx])
        return lambda_nn, trajectory_scanned

    """
    class function: computer the lower bound of similarity for each trajectory
    """

    def compute_lb(self, trajectory, list_candidate, query_points):
        assert len(list_candidate) == len(query_points)

        trajectory_path = '%s/%s' % (self._prepath, trajectory)
        trajectory_points = Helper.file2points(trajectory_path)
        lower_bound = 0
        for i in range(0, len(list_candidate)):
            if trajectory in list_candidate[i]:
                lower_bound += math.pow(math.e, -(Querier.compute_distance_q(query_points[i], trajectory_points)))
        return lower_bound

    """
    class function: computer the upper bound of similarity for each trajectory
    """

    def computer_ub(self, trajectory, list_candidate, query_points, list_lambda):
        assert len(list_candidate) == len(query_points)

        trajectory_path = '%s/%s' % (self._prepath, trajectory)
        trajectory_points = Helper.file2points(trajectory_path)
        upper_bound = 0
        for i in range(0, len(list_candidate)):
            if trajectory in list_candidate[i]:
                upper_bound += math.pow(math.e,
                                        -(Querier.compute_distance_q(query_points[i], trajectory_points)))
            else:
                upper_bound += math.pow(math.e,
                                        -(Helper.lnglat_eucildean_distance(query_points[i], list_lambda[i][-1])))
        return upper_bound

    """
    class function: refinement procedure is to examine the exact similarity
    """

    # TODO choose similarity function without order restriction
    def refine(self, candidate, list_candidate, query_points, list_lambda, k):
        upperbound, k_BCT = {}, {}

        for trajectory in candidate:
            upperbound.update({trajectory: self.computer_ub(trajectory, list_candidate, query_points, list_lambda)})

        # sort candidates in C by UB in a descending order
        upperbound_sorted = sorted(upperbound.items(), key=operator.itemgetter(1), reverse=True)

        for i in range(0, len(upperbound_sorted)):
            trajectory = upperbound_sorted[i][0]
            trajectory_path = '%s/%s' % (self._prepath, trajectory)
            trajectory_points = Helper.file2points(trajectory_path)

            similarity = Querier.similarity(trajectory_points, query_points) # Without order
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

    """
    class function: determine an upper bound ub_n of similarity for all the non-scanned trajectoies
    """

    @staticmethod
    def compute_ub_n(query_points, list_lambda):
        assert len(query_points) == len(list_lambda)
        ub_n = 0
        for i in range(0, len(query_points)):
            ub_n += math.pow(math.e, (-1) * Helper.lnglat_eucildean_distance(query_points[i], list_lambda[i][-1]))
        return ub_n

    """
    compute the min distance between a trajectory and a point = min(distance_e(trajectory,point))
    """

    @staticmethod
    def compute_distance_q(point, trajectory_points):
        min_dist = sys.maxint

        for trajectory_point in trajectory_points:
            dist = Helper.lnglat_eucildean_distance(trajectory_point, point)
            if dist < min_dist:
                min_dist = dist
        return min_dist

    """
    function: similarity without order restriction
    """

    @staticmethod
    def similarity(trajectory_points, query_points):
        ret = 0
        for query_point in query_points:
            ret += math.pow(math.e, -Querier.compute_distance_q(query_point, trajectory_points))
        return ret

    """
    function: similarity with order restriction
    """

    @staticmethod
    def similarity_order(trajectory_points, query_points):
        if len(trajectory_points) == 0 or len(query_points) == 0:
            return 0
        return math.pow(math.e, -(Helper.lnglat_eucildean_distance(trajectory_points[0], query_points[0]))) + max(
            Querier.similarity_order(trajectory_points[1:], query_points),
            Querier.similarity_order(trajectory_points, query_points[1:]))