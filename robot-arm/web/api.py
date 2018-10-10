# Copyright 2017 BrainPad Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import time

from flask import Blueprint, jsonify, request, current_app

from dobot.client import Dobot
from calibration.converter import CoordinateConverter

DEFAULT_BAUDRATE = 115200

logger = logging.getLogger(__name__)
api = Blueprint('dobot', __name__)


def get_dobot(port):
    logging.info('Opening serial port {} to communicate with dobot.'.format(port))
    return Dobot(port, DEFAULT_BAUDRATE)


@api.route("/init", methods=['POST'])
def initialize():
    dobot = get_dobot(current_app.config['DOBOT_SERIAL_PORT'])
    logging.info('Starting dobot initialization protocol')
    dobot.initialize()
    dobot.wait()
    dobot.close()

    return jsonify()


@api.route("/pickup", methods=['POST'])
def pickup():
    body = request.get_json(silent=True)
    x = float(body["x"])
    y = float(body["y"])
    logging.info('Starting pickup from ({}, {})'.format(x, y))

    cfg = current_app.config

    cv = cfg['DOBOT_COORDINATE_CONVERTER']

    dest = cfg['DOBOT_SERVE_XY']
    z_high = cfg['DOBOT_Z_HIGH']
    z_low = cv.z_low
    v = cfg['DOBOT_MAX_VELOCITY']
    a = cfg['DOBOT_MAX_ACCERALATION']
    logging.info('Pickup parameters: z_low={}, z_high={}, velocity={}, accel={}'.format(z_low, z_high, v, a))

    xy_conv = cv.convert(x, y)
    logging.info('Logical coordinate ({}, {}) converted to dobot coordinate {}'.format(x, y, xy_conv))

    dobot = get_dobot(current_app.config['DOBOT_SERIAL_PORT'])
    logging.info('Adjusting arm height to {}'.format(z_high))
    dobot.adjust_z(z_high)
    logging.info('Starting pickup.')
    dobot.pickup(xy_conv[0], xy_conv[1], z_low=z_low, z_high=z_high, velocity=v, accel=a)
    logging.info('Serving to {}.'.format(dest))
    dobot.move(dest[0], dest[1], dest[2],  velocity=v, accel=a)
    logging.info('Turning pump off.')
    dobot.pump(0)
    dobot.close()

    return jsonify()


@api.route('/pickup/gripper', methods=['POST'])
def pickup_grip():
    body = request.get_json(silent=True)
    x = float(body["x"])
    y = float(body["y"])
    r = float(body['r'])
    logging.info('Starting pickup from ({}, {}, {})'.format(x, y, r))

    cfg = current_app.config

    cv = cfg['DOBOT_COORDINATE_CONVERTER']

    dest = cfg['DOBOT_SERVE_XY']
    z_high = cfg['DOBOT_Z_HIGH']
    z_low = cv.z_low
    v = cfg['DOBOT_MAX_VELOCITY']
    a = cfg['DOBOT_MAX_ACCERALATION']
    logging.info('Pickup parameters: z_low={}, z_high={}, velocity={}, accel={}'.format(z_low, z_high, v, a))

    xy_conv = cv.convert(x, y, r)
    logging.info('Logical coordinate ({}, {}, {}) converted to dobot coordinate {}'.format(x, y, r, xy_conv))

    dobot = get_dobot(current_app.config['DOBOT_SERIAL_PORT'])
    current_pose = dobot.get_pose()

    logging.info('Move robot arm onto the sheet to avoid occasional crash into base and adjusting arm height to {}'
                 .format(z_high))

    dobot.move(x=160, y=140 if current_pose['y'] > 0 else -140, z=z_high, r=xy_conv[2], jump=False)

    logging.info('Starting pickup.')
    dobot.pickup_gripper(xy_conv[0], xy_conv[1], xy_conv[2], z_low=z_low, z_high=z_high, velocity=v, accel=a)
    logging.info('Serving to {}.'.format(dest))
    dobot.move(dest[0], dest[1], dest[2], 0, velocity=v, accel=a)
    dobot.wait()
    logging.info('Releasing the candy')
    dobot.grip(0)
    dobot.wait()
    logging.info('Turning pump off.')
    dobot.pump(0)
    dobot.close()

    return jsonify()


@api.route("/status", methods=['GET'])
def get_state():
    dobot = get_dobot(current_app.config['DOBOT_SERIAL_PORT'])
    status = {}

    logging.info('Getting pose of dobot.')
    pose = dobot.get_pose()
    status["queue_count"] = dobot.count_queued_command()
    status["alarms"] = dobot.get_alarms_state()
    dobot.close()

    logging.info('Dobot pose: (x, y, z, r)=({}, {}, {}, {}) (base, fore, rear, end)=({}, {}, {}, {})'.format(
        pose['x'], pose['y'], pose['z'], pose['r'], pose['basement'], pose['fore'], pose['rear'], pose['end']
    ))

    for key in ['x', 'y', 'z', 'r', 'basement', 'fore', 'rear', 'end']:
        status[key] = pose[key]

    return jsonify(status)



@api.route("/test")
def test():
    dobot = get_dobot(current_app.config['DOBOT_SERIAL_PORT'])
    pose = dobot.get_pose()
    dobot.close()
    return jsonify({})
