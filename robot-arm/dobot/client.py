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


from dobot import command
from dobot import alarms
from dobot.errors import TimeoutError
from dobot.serial import SerialCommunicator

logger = logging.getLogger(__name__)
DOBOT_QUEUE_SIZE = 32


class Dobot(object):
    def __init__(self, port, baudrate, read_timeout_sec=10, serial_timeout_sec=5):
        self.serial = SerialCommunicator(
            port, baudrate, read_timeout_sec=read_timeout_sec, serial_timeout_sec=serial_timeout_sec
        )


    def get_pose(self):
        return self.serial.call(command.GetPose())

    def wait(self, timeout_sec=120):
        logger.debug("waiting for dobot to complete commands")
        start_time = time.time()
        while self.count_queued_command() > 0:
            time.sleep(1)
            if time.time() - start_time > timeout_sec:
                raise TimeoutError("timeout when waiting for dobot to complete commands")

    def current_command_id(self):
        # todo
        pass

    def count_queued_command(self):
        result = self.serial.call(command.GetQueuedCmdLeftSpace())
        return DOBOT_QUEUE_SIZE - result['leftSpace']

    def get_alarms_state(self, discard_reset_alarm=True):
        # Get the alarms from the Dobot
        result = self.serial.call(command.GetAlarmsState())
        # Process alarm data into a string with bit flags
        alarm_string = "".join(["{0:0>8b}".format(x)[::-1] for x in list(result)[4:-1]])  # Get only the alarm values
        # Traverse the bit flags and extract the alarm IDs
        alarm_ids = ["0x" + "{0:0>2X}".format(index) for index, value in
                     enumerate(alarm_string[int(discard_reset_alarm):]) if value == "1"]
        # Lookup alarm ids to get the information about the alarms
        dobot_alarms = [alarms.alarms.get(alarm_id) if alarms.alarms.get(alarm_id) else alarm_id
                        for alarm_id in alarm_ids]
        return dobot_alarms

    def clear_alarms_state(self):
        return self.serial.call(command.ClearAllAlarmsState())

    def initialize(self):
        self.serial.call(command.ClearAllAlarmsState())
        self.serial.call(command.SetQueuedCmdClear())
        self.adjust_z(0)
        self.serial.call(command.SetHomeCmd())

    def move(self, x, y, z, r=0, velocity=200, accel=200, jump=True):
        self.serial.call(command.SetPTPJointParams(velocity, velocity, velocity, velocity, accel, accel, accel, accel))

        mode = 0
        if not jump:
            mode = 1

        self.serial.call(command.SetPTPCmd(mode, x, y, z, r))

    def linear_move(self, x, y, z, r=0, velocity=200, accel=200):
        self.serial.call(command.SetPTPCoordinateParams(velocity, velocity, accel, accel))
        self.serial.call(command.SetPTPCmd(2, x, y, z, r))

    def pickup(self, x, y, z_low=0, z_high=100, sleep_sec=1, velocity=200, accel=100, num_trials=1):
        self.move(x, y, z_high, 0,  velocity, accel)
        self.pump(1)
        for i in range(num_trials):
            self.linear_move(x, y, z_low, 0, velocity, accel)
            time.sleep(sleep_sec)
            self.linear_move(x, y, z_high, 0, velocity, accel)

    def pickup_gripper(self, x, y, r, z_low=0, z_high=100, sleep_sec=0.5, velocity=200, accel=100, num_trials=1):
        self.grip(0)
        self.move(x, y, z_high, r,  velocity, accel)
        for i in range(num_trials):
            self.linear_move(x, y, z_low, r, velocity, accel)
            time.sleep(1)
            self.grip(1)
            self.wait(120)
            time.sleep(sleep_sec)
            self.linear_move(x, y, z_high, r, velocity, accel)

    def adjust_z(self, z):
        self.wait()
        pose = self.serial.call(command.GetPose())
        self.linear_move(pose['x'], pose['y'], z, pose['r'])

    def adjust_r(self, r):
        self.wait()
        pose = self.serial.call(command.GetPose())
        self.linear_move(pose['x'], pose['y'], pose['z'], r)

    def pump(self, on):
        self.serial.call(command.SetEndEffectorSuctionCup(1, on))

    def grip(self, grip):
        self.serial.call(command.SetEndEffectorGripper(1, grip))

    def stepper_motor(self, index, enabled, reverse=False):
        self.serial.call(command.SetEMotor(index, enabled, -10000 if reverse else 10000))

    def close(self):
        self.serial.close()
