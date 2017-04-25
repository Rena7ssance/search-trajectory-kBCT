# -*- coding: utf-8 -*-

import os
import re
from rtree import index
from simlifier import *


class Processor(object):
    dir_path = ''

    def __init__(self, read_path, write_dir, city, city_range):
        self._rp = read_path
        self._wd = write_dir
        self._city = city
        self._range = city_range
        self.def_write_dir()

    def def_write_dir(self):
        self.dir_path = '%s/%s/%s' % (self._wd, self._city, self._rp[-11:-4])

    def create_write_dir(self):
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

    def pre_extract(self, time_threshold=1500):
        self.create_write_dir()

        obd = {'OBD_ID': 2, 'OBD_LNG': 3, 'OBD_LAT': 4, 'OBD_TIME': 8}
        lng_lb, lng_ub, lat_lb, lat_ub = \
            self._range['lng'][0], self._range['lng'][1], self._range['lat'][0], self._range['lat'][1],

        with open(self._rp, 'r') as fr:
            for line in fr:
                obd_info = line.strip('\n').split(',')
                obd_id, obd_lng, obd_lat, obd_time = \
                    obd_info[obd['OBD_ID']], obd_info[obd['OBD_LNG']], \
                    obd_info[obd['OBD_LAT']], obd_info[obd['OBD_TIME']],

                # wgs_2_gcj
                res = Helper.wgs_2_gcj(obd_lng, obd_lat)
                if res is None:
                    continue
                else:
                    obd_lng, obd_lat = res

                # Search for specified district or city
                if lng_lb < float(obd_lng) < lng_ub \
                        and lat_lb < float(obd_lat) < lat_ub:
                    with open(self.dir_path + '/%s.txt' % obd_id, 'a+') as fw:

                        # read the last timestamp
                        if fw.tell() != 0:
                            fw.seek(-20, 1)
                            timestamp = fw.read(19)

                            # break individual trajectory
                            if Helper.timestamp_delta(obd_time, timestamp) > time_threshold:
                                fw.write('\n')

                        # 'lng'\t'lat'\t'time'\n
                        fw.write('%.6f\t%.6f\t%s\n' % (
                            round(float(obd_lng), 6), round(float(obd_lat), 6), obd_time))
                    fw.close()
        fr.close()

        for f in os.listdir(self.dir_path):
            Helper.append_linebreak('%s/%s' % (self.dir_path, f))

    def trajectory_per_user(self):

        # NOTE: path = 'backend/data/trajectory/trajectory_per_user/<city>/<date>'
        path = re.compile('raw_trajectory').sub('trajectory_per_user', self.dir_path)
        if not os.path.exists(path):
            os.makedirs(path)

        for user in os.listdir(self.dir_path):
            # NOTE: user_path = 'backend/data/trajectory/trajectory_per_user/<city>/<date>/user_id'
            user_path = '%s/%s' % (path, user[:-4])
            if not os.path.exists(user_path):
                os.mkdir(user_path)

            count = 0
            trajectory = []
            with open('%s/%s' % (self.dir_path, user), 'r') as fr:
                obd_dict = {}
                day = '00'
                for line in fr:
                    if line == '\n':

                        # NOTE: open path = 'backend/data/trajectory/trajectory_per_user/<city>/<date>/user_id/r d'
                        with open('%s/r%d %s.txt' % (user_path, count, day), 'w') as fw:
                            for point in trajectory:
                                fw.write('%f\t%f\t%d\n'
                                         % (point[0], point[1], Helper.time2int(obd_dict.get(str(point)))))
                            trajectory = []
                        fw.close()
                        count += 1

                    else:
                        lng, lat, obd_time = line.strip('\n').split('\t')
                        if day != obd_time[8:10]:
                            day = obd_time[8:10]
                        point = [float(lng), float(lat)]
                        obd_dict.update({str(point): obd_time})
                        trajectory.append(point)

    def simplification_per_user(self):
        # NOTE: read_path = 'backend/data/trajectory/trajectory_per_user/<city>/<date>/'
        read_path = re.compile('raw_trajectory').sub('trajectory_per_user', self.dir_path)

        # NOTE: write_path = 'backend/data/sim_trajectory_per_user/trajectory_per_user/<city>/<date>/'
        write_path = re.compile('raw_trajectory').sub('sim_trajectory_per_user', self.dir_path)
        if not os.path.exists(write_path):
            os.makedirs(write_path)

        for user in os.listdir(read_path):
            user_read_path = '%s/%s' % (read_path, user)
            user_write_path = '%s/%s' % (write_path, user)
            if not os.path.exists(user_write_path):
                os.mkdir(user_write_path)

            for trajectory in os.listdir(user_read_path):

                points = []
                obd_time_dict = {}
                with open('%s/%s' % (user_read_path, trajectory), 'r') as fr:
                    for line in fr:
                        lng, lat, obd_time = line.strip('\n').split('\t')
                        point = [float(lng), float(lat)]
                        points.append(point)
                        obd_time_dict.update({str(point): obd_time})

                # TODO choose kind of simplification method
                simplified_points = Simplifier.ts_algorithm(points)
                # simplified_traj = Simplifier.dp_algorithm(trajectory, 0, len(trajectory)-1)

                with open('%s/%s' % (user_write_path, trajectory), 'w') as fw:
                    for point in simplified_points:
                        fw.write('%f\t%f\t%d\n'
                                 % (point[0], point[1], int(obd_time_dict.get(str(point)))))
                fw.close()

    # trajectory per user restored into trajectory per day
    def per_user2per_day(self):
        path_per_user = re.compile('raw_trajectory').sub('sim_trajectory_per_user', self.dir_path)
        path = re.compile('raw_trajectory').sub('sim_trajectory_per_day', self.dir_path)
        if not os.path.exists(path):
            os.makedirs(path)

        # preset the day of a month
        for day in range(1, 32):
            path_per_day = '%s/%.02d' % (path, day)
            if not os.path.exists(path_per_day):
                os.mkdir(path_per_day)

        for user in os.listdir(path_per_user):
            directory = '%s/%s' % (path_per_user, user)
            for per_trajectory in os.listdir(directory):
                day, r = per_trajectory[-6:-4], per_trajectory[:-7]
                trajectory_path = '%s/%s' % (directory, per_trajectory)
                target_path = '%s/%s/%s %s' % (path, day, user, r)
                with open(trajectory_path, 'r') as fr, open(target_path, 'w') as fw:
                    for line in fr:
                        fw.write(line)
                fr.close()
                fw.close()

    # construct the rtree: construct the rtree of each day here
    def construct_rtree(self):

        # data/trajectory/sim_trajectory_per_day/city/yyyy-mm
        path_per_day = re.compile('raw_trajectory').sub('sim_trajectory_per_day', self.dir_path)

        # data/rtree/city/yyyy-mm
        rtree_dir = re.compile('trajectory/sim_trajectory_per_day').sub('rtree', path_per_day)
        for day in os.listdir(path_per_day):
            if not os.path.exists(rtree_dir):
                os.makedirs(rtree_dir)

            rtree_path = '%s/%s' % (rtree_dir, day)
            rtree_properties = index.Property()
            rtree_properties.dat_extension = 'data'
            rtree_properties.idx_extension = 'index'
            rtree = index.Index(rtree_path, properties=rtree_properties)
            directory = '%s/%s' % (path_per_day, day)

            count = 0
            for trajectory in os.listdir(directory):
                trajectory_path = '%s/%s' % (directory, trajectory)
                with open(trajectory_path, 'r') as fr:
                    for line in fr:
                        lng, lat, obt_time = line.strip('\n').split('\t')
                        item_id = count * pow(10, 11) + int(obt_time)  # TODO a better way to generate id
                        rtree.insert(item_id, (float(lng), float(lat)))
                fr.close()
                count += 1
