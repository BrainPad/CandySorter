# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import numpy as np

from calibration.adjust import AdjustForPictureToRobot

class CoordinateConverter(object):

    def __init__(self, from_points, to_points):
        """
        find T that meets x_robot = T x_logical
        """

        self.mat_x_from = np.array([[from_points[0][0], from_points[0][1], 1],
                                    [from_points[1][0], from_points[1][1], 1],
                                    [from_points[2][0], from_points[2][1], 1]])

        self.mat_x_to = np.array([[to_points[0][0], to_points[0][1], 1],
                                  [to_points[1][0], to_points[1][1], 1],
                                  [to_points[2][0], to_points[2][1], 1]])

        inv_x = np.linalg.inv(self.mat_x_from.T)

        self.mat_transform = np.dot(self.mat_x_to.T, inv_x)
        print(self.mat_transform)

    def convert(self, x, y):

        xy_trans = AdjustForPictureToRobot()
        x, y = xy_trans.adjust(x, y)
        xy_trans = None

        from_vector = np.array([x, y, 1])
        transformed = np.dot(from_vector, self.mat_transform.T)

        return transformed[0], transformed[1]

    @classmethod
    def from_tuning_file(cls, to_points, file_='/tmp/robot_tuner.dat'):
        tuner_data = []
        with open(file_, 'r') as readfile:
            for line in readfile:
                if not line:
                    break
                data = json.loads(line)
                tuner_data.append(data)
        return cls(
            [(-0.3, 1.5), (-0.3, -1.5), (0.3, 0)],
            [(tuner_data[0]['x'], tuner_data[0]['y']),
            (tuner_data[1]['x'], tuner_data[1]['y']),
            (tuner_data[2]['x'], tuner_data[2]['y'])]
        )


if __name__ == "__main__":
    c = CoordinateConverter([(-1.105, 1.631), (-1.105, -1.631), (0, 0)],
                            [(78.83, 132.45), (74.41, -145.70), (175.01, -7.77)])
    print(c.convert(0, 0))
