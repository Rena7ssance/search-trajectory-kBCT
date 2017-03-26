# -*- coding: utf-8 -*-
import time
from math import radians, cos, sin, asin, sqrt


class Helper(object):
    def __init__(self):
        pass

    '''
    File Read/Write
    '''

    @staticmethod
    def file2points(path):
        points = []
        with open(path, 'r') as f:
            for line in f:
                info = line.strip('\n').split('\t')
                points.append([info[0], info[1]])
        f.close()
        return points

    '''
    File Process
    '''

    @staticmethod
    def append_linebreak(file_path):
        with open(file_path, 'a') as f:
            f.write('\n')
        f.close()

    '''
    Time Process
    '''

    @staticmethod
    def time2int(timestamp, f='%Y-%m-%d %H:%M:%S'):
        return int(time.mktime(time.strptime(timestamp, f)))

    @staticmethod
    def timestamp_delta(latter, former):
        return Helper.time2int(latter) - Helper.time2int(former)

    '''
    Distance Process
    '''

    @staticmethod
    def lnglat2distance(a, b):
        lng_a, lat_a, lng_b, lat_b = map(radians, [a[0], a[1], b[0], b[1]])
        delta_lng = lng_b - lng_a
        delta_lat = lat_b - lat_a
        a = sin(delta_lat / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(delta_lng / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # radius of the earth
        return c * r * 1000  # unit:meter
