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

import os
import sys
import time

import cv2
import numpy as np

sys.path.append('../../webapp')

from candysorter.models.images.calibrate import ImageCalibrator
from candysorter.models.images.detect import CandyDetector
from candysorter.config import get_config

calibrator = ImageCalibrator(area=(1625, 1100), scale=550)
config = get_config(os.getenv('FLASK_ENV', 'dev'))

# Convert config from class object to dictionary for compatability with flask
config_dict = {}
for key in dir(config):
    if key.isupper():
        config_dict[key] = getattr(config, key)

detector = CandyDetector().from_config(config_dict)

should_exit = False


def mouse_event(event, x, y, flags, param):
    global should_exit
    if event == cv2.EVENT_LBUTTONUP:
        print("mouse_event:L-click")
        should_exit = True


def write_message(image, msg, size=3, thickness=3):
    cv2.putText(image, msg, (10, 130), font, size, (250, 30, 30), thickness)


def write_ok(image):
    cv2.putText(image, 'OK', (900, 500), font, 7, (30, 250, 30), 5)


def detect_corners(image):
    try:
        corners = calibrator.detect_corners(image)
    except Exception as e:
        print(e)
        return None
    if len(corners) < 4:
        return None
    return corners


def draw_detection(image, candies):
    for candy in candies:
        cv2.polylines(image, np.int32([np.array(candy.box_coords)]), isClosed=True, color=(0, 0, 255),
                      lineType=cv2.LINE_AA, thickness=3)

font = cv2.FONT_HERSHEY_PLAIN

def main():

    capture = cv2.VideoCapture(0)
    capture.set(3, 1920)
    capture.set(4, 1080)

    # Attempt to display using cv2
    cv2.namedWindow('Tuning Camera', cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Tuning Camera', 960, 540)
    cv2.setMouseCallback('Tuning Camera', mouse_event)

    w2_size = (960, 540)
    cv2.namedWindow('Detection', cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Detection', *w2_size)
    cv2.setMouseCallback('Detection', mouse_event)

    candies = None
    counter = 0

    while True:
        time.sleep(0.01)
        if capture.isOpened:
            ret, frame = capture.read()
            if not ret:
                break
            corners = detect_corners(frame)
            corners = detect_corners(frame)
            if corners is not None:
                cropped = calibrator.calibrate(frame)
                if (counter % 5 == 0):
                    candies = detector.detect(cropped)
                draw_detection(cropped, candies)
                cv2.imshow('Detection', cropped)
                write_ok(frame)
                counter += 1
            else:
                blank = np.zeros((w2_size[1], w2_size[0], 3), np.uint8)
                write_message(blank, 'Marker detection failed', size=1, thickness=1)
                cv2.imshow('Detection', blank)

            write_message(frame, 'Click L-button of mouse to exit')
            cv2.imshow('Tuning Camera', frame)
            cv2.waitKey(1)
        if should_exit:
            break

    print("Exit.")
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
