# -*- coding: utf-8 -*-
from helper import *


class Simplifier(object):
    def __init__(self):
        pass

    # Other parameters can passed:
    # 1) segmentation number
    def ts_algorithm(self, trajectory):

        if len(trajectory) <= 15:
            return trajectory
        elif 15 < len(trajectory) <= 50:
            m = len(trajectory) / 2
        else:
            m = len(trajectory) / 4

        simplified_traj = []
        segs = self.segmentation(trajectory)
        """
        self.distribute_points(segs, m)
        for seg in segs:
            self.weight_points(seg)
            selected_p = self.select_points(seg)
            for p in selected_p:
                simplified_t.append(p)
        return simplified_t
        """

    def segmentation(self, trajectory, seg_length=5):
        return [trajectory[x:x + seg_length] for x in range(0, len(trajectory), seg_length)]

    def get_distance(self, seg):
        distance = 0
        for i in range(1, len(seg)):
            distance += Helper.lnglat2distance(seg[i - 1], seg[i])
        return distance

    # def get_heading_change(self, seg):

    def distributed_points(self, segs, m):
        total_weight = 0
        weight_l = []
        for seg in segs:
            distance = self.get_distance(seg)
            alpha = self.get_heading_change(seg)
            weight = distance * alpha
            weight_l.append(weight)
            total_weight += weight
        map(lambda x: x / total_weight, weight_l)
