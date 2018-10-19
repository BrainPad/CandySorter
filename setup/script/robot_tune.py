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

import argparse
import json
import sys
import time

import requests

sys.path.append('../../robot-arm')
from dobot.client import Dobot
from dobot.utils import detect_dobot_port, dobot_is_on_port


DEFAULT_BAUDRATE = 115200


class SerialDobotCalibrator(object):
    def __init__(self, port):
        self.dobot = Dobot(port, DEFAULT_BAUDRATE)

    def get_position(self):
        pose = self.dobot.get_pose()
        return {'x': pose['x'], 'y': pose['y'], 'z': pose['z']}

    def get_rotation(self):
        pose = self.dobot.get_pose()
        return {'r': pose['r']}

    def initialize(self):
        self.dobot.initialize()

    def wait(self):
        self.dobot.wait()

    def move(self, x, y, z=0, r=0):
        self.dobot.move(x, y, z, r)

    def grip(self, on):
        self.dobot.grip(on)

    def pump(self, on):
        self.dobot.pump(on)

    def rotate_gripper(self, delta):
        pose = self.dobot.get_pose()
        self.dobot.adjust_r(pose['r'] + delta)


class HTTPDobotCalibrator(object):
    base_url = ""

    def __init__(self, ipaddress):
        self.base_url = "http://{}".format(ipaddress)
        print(self.base_url)

    def get_position(self):
        r = requests.get(self.base_url + '/api/status')

        if 200 != r.status_code:
            print("Error: unable to connect to server.")
            msg = "Error: Please check network or the 'robot api' is working on host machine."
            raise Exception(msg)

        value_ = r.content
        decode_data = json.loads(value_)
        x = decode_data['x']
        y = decode_data['y']
        z = decode_data['z']
        return {'x': x, 'y': y, 'z': z}

    def initialize(self):
        requests.post(self.base_url + '/api/init')

    def grip(self, on):
        raise NotImplementedError

    def rotate_gripper(self, cw=True):
        raise NotImplementedError


def _request(url):
    r = requests.get(url)
    if 200 != r.status_code:
        print("Error: unable to connect to server.")
        msg = "Error: Please check network or the 'robot api' is working on host machine."
        raise Exception(msg)
    return r.content


def wait_for_keystroke(mark_id):
    input("Push the button (marked as 'unlock') which is located in middle of  arm) to release the arm and then slowly move the arm edge to slightly touch \n'{}' on marker sheet.\nAfter you finished, press Enter.".format(mark_id))

if '__main__' == __name__:
    parser = argparse.ArgumentParser(description='Run Dobot WebAPI.')
    parser.add_argument('--http', dest='http', action='store_true', default=False)
    parser.add_argument('--api-uri', type=str, default="127.0.0.1:8000")
    parser.add_argument('--dobot-port', type=str, default=None)
    parser.add_argument('--tuner-file', type=str, default='/var/tmp/robot_tuner.dat')
    parser.add_argument('--use-gripper', action='store_true', default=False)
    parser.add_argument('--mark-drop', action='store_true', default=False)

    args = parser.parse_args()

    if args.http:
        tuner = HTTPDobotCalibrator(args.api_uri)
        print('via http')
    else:
        if args.dobot_port is None:
            dobot_port = detect_dobot_port(DEFAULT_BAUDRATE)
            if dobot_port is None:
                print('dobot offline')
                exit(1)
        else:
            dobot_port = args.dobot_port
            if not dobot_is_on_port(dobot_port, DEFAULT_BAUDRATE):
                print('dobot is not detected on port {}'.format(dobot_port))
                exit(1)
        print('via {}'.format(dobot_port))
        tuner = SerialDobotCalibrator(dobot_port)

    val_arr = []

    print("---Calibrate robot arm---")
    print("When asked to place the robot on the marker, place it on the CROSS NEXT TO THE MARKER, not the letter.")
    print()
    print("Before you begin, please use the arm-release button located at the top of the robot arm and move the arm to \
3'o clock. \nEnsure that the arm can move freely and that there are no obstacles to the right of the robot")

    print()
    input("PRESS Enter to start dobot arm initialization protocol.")
    tuner.initialize()


    if args.use_gripper:
        tuner.grip(True)
        tuner.wait()
        time.sleep(1)
        tuner.pump(False)

    print("")
    wait_for_keystroke("Marker A")
    value = tuner.get_position()
    print(">> Marker A(x,y,z)={}".format(value))
    val_arr.append(value)

    print("")
    wait_for_keystroke("Marker D")
    value = tuner.get_position()
    print(">> Marker D(x,y,z)={}".format(value))
    val_arr.append(value)

    print("")
    wait_for_keystroke("Marker E")
    value = tuner.get_position()
    print(">> Marker E(x,y,z)={}".format(value))
    val_arr.append(value)

    if args.use_gripper:
        print("")
        # average_z = sum([v['z'] for v in val_arr]) / 3 + 4
        tuner.move(value['x'], value['y'], value['z'] + 3, 0)
        tuner.grip(0)
        tuner.wait()
        time.sleep(1)
        tuner.pump(0)


        print("Positive values turns the gripper counter clockwise, negative clockwise.")
        while True:
            angle = input("Enter rotation delta in degrees or 0 to finish: ")
            if angle == '0':
                break

            tuner.rotate_gripper(float(angle))

        value = tuner.get_rotation()
        print(">> Rotation={}".format(value))
        val_arr.append(value)
    else:
        value = {'r': 0}
        val_arr.append(value)

    if args.mark_drop:
        print('')
        print('Move the arm to the drop-off location (including height)')
        input('After you finished, press Enter')

        value = tuner.get_position()
        val_arr.append(value)


    print("")
    with open(args.tuner_file, 'w') as writefile:
        for entry in val_arr:
            json.dump(entry, writefile)
            writefile.write('\n')
