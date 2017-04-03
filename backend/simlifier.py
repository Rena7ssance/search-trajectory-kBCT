# -*- coding: utf-8 -*-
import operator

from math import atan, pi

from helper import *


class Simplifier(object):
    def __init__(self):
        pass

    # Other parameters can passed:
    @staticmethod
    def ts_algorithm(trajectory, length=75):

        # No need to simplify the trajectory
        if len(trajectory) <= 5:
            return trajectory

        trajectory_segs = [trajectory[x:x + length] for x in range(0, len(trajectory), length)]
        ts_res = []
        for trajectory_seg in trajectory_segs:
            ts_res.extend(Simplifier.ts_algorithm_per(trajectory_seg))
        return ts_res

    @staticmethod
    def ts_algorithm_per(trajectory):
        if len(trajectory) < 5:
            return trajectory

        # Decide the simplification rate, personalized
        len_traj = len(trajectory)
        if len_traj <= 25:
            m = len_traj / 8
        elif 25 <= trajectory < 45:
            m = len_traj / 15
        else:
            m = len_traj / 25

        # update heading_direction, neighbor_heading_change
        traj_list = []

        prev_hd = Simplifier.heading_direction(trajectory[0], trajectory[1])
        for i in range(0, len(trajectory) - 1):
            hd = Simplifier.heading_direction(trajectory[i], trajectory[i + 1])  # 0 -> 1
            nhc, prev_hd = hd - prev_hd, hd  # Neighbor Heading Change
            traj_list.append({'point': trajectory[i], 'hd': hd, 'nhc': nhc})
        traj_list.append({'point': trajectory[-1], 'hd': 0, 'nhc': 0})

        # update accumulated_heading_change, heading_change
        for i in range(0, len(traj_list)):
            ahc = Simplifier.accumulated_heading_change(i, traj_list)
            traj_list[i].update({'ahc': ahc})
            traj_list[i].update({'hc': abs(traj_list[i]['nhc']) + abs(ahc)})

        # update neighbor_distance
        prev_point, curr_point, next_point = '', traj_list[0]['point'], traj_list[1]['point']
        traj_list[0].update({'nd': Helper.lnglat2distance(curr_point[0], curr_point[1], next_point[0], next_point[1])})
        prev_point, curr_point = curr_point, next_point
        for i in range(1, len(traj_list) - 1):
            next_point = traj_list[i + 1]['point']
            nd = Helper.lnglat2distance(prev_point[0], prev_point[1], curr_point[0], curr_point[1]) + \
                 Helper.lnglat2distance(curr_point[0], curr_point[1], next_point[0], next_point[1])
            traj_list[i].update({'nd': nd})
            prev_point, curr_point = curr_point, next_point
        traj_list[-1].update({'nd': Helper.lnglat2distance(prev_point[0], prev_point[1], curr_point[0], curr_point[1])})

        # flowchart of ts_algorithm
        segs = Simplifier.segmentation(traj_list)
        seg_list = Simplifier.distribute_points(segs, m)
        selected_point = []
        for seg in seg_list:
            for point in Simplifier.select_points(seg):
                selected_point.append(point)

        # the head point may not be count because the initial heading direction
        if len(selected_point) == 0 or selected_point[0] != trajectory[0]:
            selected_point.insert(0, trajectory[0])
        return selected_point

    @staticmethod
    def segmentation(traj_list, seg_length=6):
        return [traj_list[x:x + seg_length] for x in range(0, len(traj_list), seg_length)]

    @staticmethod
    def get_distance(seg):
        distance = 0
        for i in range(0, len(seg) - 1):
            distance += Helper.lnglat2distance(seg[i][0], seg[i][1], seg[i + 1][0], seg[i + 1][1])
        return distance

    @staticmethod
    def distribute_points(segs, m):
        seg_list = []
        total_weight = 0
        for seg in segs:
            points = []
            seg_dis, seg_ahc = 0, seg[0]['nhc']
            prev_point = seg[0]['point']
            for point_dict in seg:
                # preset
                point = point_dict['point']
                points.append({'point': point, 'w': point_dict['nd'] * point_dict['hc']})
                # points.append({'point': point, 'w': point_dict['hc']})

                # distance
                seg_dis += Helper.lnglat2distance(prev_point[0], prev_point[1], point[0], point[1])
                prev_point = point

                # average Heading change
                seg_ahc += abs(point_dict['nhc'])
            seg_ahc /= len(seg)
            seg_weight = seg_dis * seg_ahc
            seg_list.append({'points': points, 'seg_d': seg_dis, 'seg_ahc': seg_ahc, 'seg_w': seg_weight})
            total_weight += seg_weight

        for seg in seg_list:
            if total_weight != 0:
                seg['seg_w'] /= total_weight  # normalize weight
            seg.update({'seg_hc': seg['seg_w'] * m})  # assign headcount

        return seg_list

    @staticmethod
    def select_points(seg):  # return a simplified segment S'
        simplified_points = []
        headcount, points = seg['seg_hc'], seg['points']

        for i in range(0, len(points)):
            points[i].update({'index': i})

        points = sorted(points, key=operator.itemgetter('w'), reverse=True)[0: min(int(headcount), len(points))]
        points = sorted(points, key=operator.itemgetter('index'))
        for point in points:
            simplified_points.append(point['point'])
        return simplified_points

    # longitude-x 经度 latitude-y 纬度
    @staticmethod
    def heading_direction(cur, nxt):
        lng_cur, lat_cur = cur[0], cur[1]
        lng_nxt, lat_nxt = nxt[0], nxt[1]
        delta_lng = lng_nxt - lng_cur
        delta_lat = lat_nxt - lat_cur
        if delta_lng == 0:
            if lat_nxt > lat_cur:
                return 0
            elif lat_nxt < lat_cur:
                return 180

        if delta_lat == 0:
            if lng_nxt > lng_cur:
                return 90
            elif lng_nxt < lng_cur:
                return 270
            elif lng_nxt == lng_cur:
                return 0

        angle = atan(delta_lng / delta_lat) * 180 / pi  # |x|/|y|
        if angle < 0:
            if lng_nxt < lng_cur:
                angle = 360 - abs(angle)  # Delta Quadrant
            else:
                angle = 180 - abs(angle)  # Beta Quadrant
        elif angle > 0:
            if lng_nxt < lng_cur:
                angle += 180
        return angle

    @staticmethod
    def accumulated_heading_change(index, dict_list, tau=3):
        l, r = max(index - tau, 0), min(index + tau + 1, len(dict_list))
        accum = 0
        for i in range(l, r):
            accum += dict_list[i]['nhc']
        return accum

    @staticmethod
    def heading_change(l):
        return abs(l['nhc']) + abs(l['ahc'])

    '''
    Recursion,
    '''

    # DouglasPeucker
    @staticmethod
    def dp_algorithm(points, start_index, end_index, epsilon=1e-02):
        index = start_index
        max_dist = 0

        for i in range(start_index + 1, end_index):
            temp_dist = Simplifier.point_line_distance(points[i], points[start_index], points[end_index])
            if temp_dist > max_dist:
                index = i
                max_dist = temp_dist

        if max_dist > epsilon:
            res1 = Simplifier.dp_algorithm(points, start_index, index, epsilon)
            res2 = Simplifier.dp_algorithm(points, index, end_index, epsilon)
            final_res = []
            for point_in_res1 in res1[:-1]:
                final_res.append(point_in_res1)
            for point_in_res2 in res2:
                final_res.append(point_in_res2)
            return final_res
        else:
            return [points[start_index], points[end_index]]

    @staticmethod
    def point_line_distance(p, start, end):
        # If the start point is the same as the end point
        if start[0] == end[0] and start[1] == end[1]:
            return sqrt(pow(p[0] - start[0], 2) + pow(p[1] - start[1], 2))

        n = float(abs((end[0] - start[0]) * (start[1] - p[1]) - (start[0] - p[0]) * (end[1] - start[1])))
        d = float(sqrt((end[0] - start[0]) * (end[0] - start[0]) + (end[1] - start[1]) * (end[1] - start[1])))
        return n / d
