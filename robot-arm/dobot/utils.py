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

import serial

from dobot import command
from dobot.serial import logger, SerialCommunicator


def detect_dobot_port(baudrate):
    found_port = detect_ports(baudrate)
    dobot_port = None
    for port in found_port:
        if dobot_is_on_port(port, baudrate):
            dobot_port = port

    return dobot_port


def detect_ports(baudrate):
    port_prefix = '/dev/ttyUSB'
    all_ports = [port_prefix + str(i) for i in range(5)]
    all_ports.extend(["COM" + str(i) for i in range(5)])
    found_ports = []
    for port in all_ports:
        logger.debug('scanning port: {}'.format(port))
        try:
            s = serial.Serial(port, baudrate, timeout=1)
            s.close()
        except serial.SerialException:
            continue
        found_ports.append(port)
    return found_ports


def dobot_is_on_port(port, baudrate):
    try:
        ser = SerialCommunicator(port, baudrate)
        ser.call(command.GetPose())
    except Exception as e:
        print(e)
        return False
    return True
