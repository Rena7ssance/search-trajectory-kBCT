# -*- coding: utf-8 -*-
import os
import time
from math import radians, cos, sin, asin, sqrt

import math


class Helper(object):
    def __init__(self):
        pass

    '''
    File Read/Write
    '''

    @staticmethod
    def file2points(path):
        assert os.path.exists(path)
        points = []
        with open(path, 'r') as f:
            for line in f:
                info = line.strip('\n').split('\t')
                points.append([float(info[0]), float(info[1])])
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
    def lnglat2distance(lng_a, lat_a, lng_b, lat_b):
        lng_a, lat_a, lng_b, lat_b = map(radians, [lng_a, lat_a, lng_b, lat_b])
        delta_lng = lng_b - lng_a
        delta_lat = lat_b - lat_a
        a = sin(delta_lat / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(delta_lng / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # radius of the earth
        return c * r * 1000  # unit:meter

    @staticmethod
    def lnglat_eucildean_distance(p, q):
        return math.sqrt(pow(p[0] - q[0], 2) + pow(p[1] - q[1], 2))

    '''
    WGS84(GPS device) => GCJ02(Map)
    '''

    @staticmethod
    def wgs_2_gcj(longitude, latitude):
        longitude, latitude = float(longitude), float(latitude)
        if Helper.out_of_china(longitude, latitude):
            return None

        a = 6378245.0
        ee = 0.00669342162296594323

        d_lon = Helper.transform_lon(float(longitude - 105.0), float(latitude - 35.0))
        d_lat = Helper.transform_lat(float(longitude - 105.0), float(latitude - 35.0))
        rad_lat = float(latitude) / 180.0 * math.pi
        magic = sin(rad_lat)
        magic = 1 - ee * magic * magic
        sqrt_magic = sqrt(magic)
        d_lon = (d_lon * 180.0) / (a / sqrt_magic * cos(rad_lat) * math.pi)
        d_lat = (d_lat * 180.0) / ((a * (1 - ee)) / (magic * sqrt_magic) * math.pi)
        mg_lon = longitude + d_lon
        mg_lat = latitude + d_lat
        return round(mg_lon, 6), round(mg_lat, 6)

    @staticmethod
    def out_of_china(longitude, latitude):
        if longitude < 72.004 or longitude > 137.8347:
            return True
        if latitude < 0.8293 or latitude > 55.8281:
            return True
        else:
            return False

    @staticmethod
    def transform_lon(x, y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
        ret += (20.0 * sin(6.0 * x * math.pi) + 20.0 * sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * sin(x * math.pi) + 40.0 * sin(x / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (150.0 * sin(x / 12.0 * math.pi) + 300.0 * sin(x / 30.0 * math.pi)) * 2.0 / 3.0
        return ret

    @staticmethod
    def transform_lat(x, y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
        ret += (20.0 * sin(6.0 * x * math.pi) + 20.0 * sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * sin(y * math.pi) + 40.0 * sin(y / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (160.0 * sin(y / 12.0 * math.pi) + 320 * sin(y * math.pi / 30.0)) * 2.0 / 3.0
        return ret
