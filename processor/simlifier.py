# -*- coding: utf-8 -*-
from helper import *


class Simplifier(object):
    def __init__(self):
        pass

    # Other parameters can passed:
    # 1) segmentation number
    def ts_algorithm(self, trajectory):

        # Decide the simplification rate, personalized
        if len(trajectory) <= 15:
            return trajectory
        elif 15 < len(trajectory) <= 50:
            m = len(trajectory) / 2
        else:
            m = len(trajectory) / 5

        # update heading_direction, neighbor_heading_change
        dict_list = []
        prev_hd = self.heading_direction(trajectory[0], trajectory[1])
        for i in range(0, len(trajectory) - 1):
            hd = self.heading_direction(trajectory[i], trajectory[i + 1])  # 0 -> 1
            nhc, prev_hd = hd - prev_hd, hd  # Neighbor Heading Change
            dict_list.append({'point': trajectory[i], 'hd': hd, 'nhc': nhc})
        dict_list.append({'point': trajectory[-1], 'hd': 0, 'nhc': 0})

        # update accumulated_heading_change, heading_change
        for i in range(0, len(dict_list)):
            ahc = self.accumulated_heading_change(i, dict_list)
            dict_list[i].update({'ahc': ahc})
            dict_list[i].update({'hc': abs(dict_list[i]['nhc']) + abs(ahc)})

        # update neighbor_distance
        prev_point, curr_point, next_point = '', dict_list[0]['point'], dict_list[1]['point']
        dict_list[0].update({'nd': Helper.lnglat2distance(curr_point[0], curr_point[1], next_point[0], next_point[1])})
        prev_point, curr_point = curr_point, next_point
        for i in range(1, len(dict_list) - 1):
            next_point = dict_list[i + 1]['point']
            nd = Helper.lnglat2distance(prev_point[0], prev_point[1], curr_point[0], curr_point[1]) + \
                 Helper.lnglat2distance(curr_point[0], curr_point[1], next_point[0], next_point[1])
            dict_list[i].update({'nd': nd})
            prev_point, curr_point = curr_point, next_point
        dict_list[-1].update({'nd': Helper.lnglat2distance(prev_point[0], prev_point[1], curr_point[0], curr_point[1])})

        print dict_list

    def segmentation(self, trajectory, seg_length=7):
        return [trajectory[x:x + seg_length] for x in range(0, len(trajectory), seg_length)]

    def get_distance(self, seg):
        distance = 0
        for i in range(0, len(seg) - 1):
            distance += Helper.lnglat2distance(seg[i][0], seg[i][1], seg[i + 1][0], seg[i + 1][1])
        return distance

    def get_heading_change(self, seg):
        total = 0
        for i in range(0, len(seg) - 1):
            total += seg[i][2]
        return float(total) / len(seg) - 1

    def distribute_points(self, segs, m):
        total_weight = 0
        weight_list = []
        for seg in segs:
            distance = self.get_distance(seg)  # distance of segment
            alpha = self.get_heading_change(seg)  # average heading change
            weight = distance * alpha
            weight_list.append(weight)
            total_weight += weight

        dict_list = []
        for i in range(0, len(segs)):
            for item in segs[i]:
                del item[-1]
            normalized_weight = float(weight_list[i]) / total_weight
            dict_list.append({'point': segs[i], 'w': normalized_weight, 'hc': normalized_weight * m})

        return dict_list

    # longitude-x 经度 latitude-y 纬度
    def heading_direction(self, cur, nxt):
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

    def accumulated_heading_change(self, index, dict_list, tau=3):
        l, r = max(index - tau, 0), min(index + tau + 1, len(dict_list))
        accum = 0
        for i in range(l, r):
            accum += dict_list[i]['nhc']
        return accum

    def heading_change(self, l):
        return abs(l['nhc']) + abs(l['ahc'])
