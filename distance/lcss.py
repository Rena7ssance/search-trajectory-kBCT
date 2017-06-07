# -*- coding: utf-8 -*-
import math


class LCSS(object):

    threshold = 0.1

    @staticmethod
    def get_distance(r, s):
        return LCSS.get_lcss(r, s)

    @staticmethod
    def get_lcss(r, s):
        if len(r) == 1 or len(s) == 1:
            return 0

        lcss_matrix = [[0 for i in range(0, len(s) + 1)] for i in range(0, len(r) + 1)]
        for i in range(0, len(r) + 1):
            lcss_matrix[i][0] = 0
        for j in range(0, len(s) + 1):
            lcss_matrix[0][j] = 0

        lcss_matrix[0][0] = 0
        for i in range(1, len(r) + 1):
            for j in range(1, len(s) + 1):
                if LCSS.subcost(r[i - 1], s[j - 1]) == 0:
                    lcss_matrix[i][j] = lcss_matrix[i - 1][j - 1] + 1
                else:
                    lcss_matrix[i][j] = max(lcss_matrix[i][j - 1], lcss_matrix[i - 1][j])

        temp_r = lcss_matrix[len(r)][len(s)]
        result = 1 - (float(temp_r) / min(len(r), len(s)))
        return result

    @staticmethod
    def subcost(p1, p2):
        is_same = True
        for i in range(0, 2):
            # print abs(p1[i] - p2[i])
            if abs(p1[i] - p2[i]) > LCSS.threshold:
                is_same = False

        if is_same:
            return 0
        else:
            return 1
