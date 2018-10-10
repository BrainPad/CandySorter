from capture import ImageCapture
import argparse
import cv2
import os
import datetime
import tensorflow as tf
import numpy as np
import time
import config as config_img

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


should_exit = False

class Trainingdata():
    candies = []
    path_to_label_dir = None
    font = cv2.FONT_HERSHEY_PLAIN
    num_images = 0

    def mouse_event(self, event, x, y, flags, param):
        global should_exit
        if event == cv2.EVENT_LBUTTONUP:
            print("mouse_event:L-click")
            should_exit = True
        elif event == cv2.EVENT_RBUTTONUP:
            print("mouse_event:R-click")
            self.take_pictures_and_save()


    def write_message(self, image, msg, size=3, thickness=3):
        cv2.putText(image, msg, (10, 130), self.font, size, (250, 30, 30), thickness)


    def write_ok(self, image):
        cv2.putText(image, 'OK', (900, 500), self.font, 7, (30, 250, 30), 5)


    def detect_corners(self, image):
        try:
            corners = calibrator.detect_corners(image)
        except Exception as e:
            print(e)
            return None
        if len(corners) < 4:
            return None
        return corners


    def draw_detection(self, image, candies):
        for candy in candies:
            cv2.polylines(image, np.int32([np.array(candy.box_coords)]), isClosed=True, color=(0, 0, 255),
                          lineType=cv2.LINE_AA, thickness=3)

    def set_variables(self, images, path):
        self.candies = images
        self.path_to_label_dir = path


    def take_pictures_and_save(self):
        self.num_images += len(self.candies)
        for i in range(len(self.candies)):
            if (self.candies == None or self.path_to_label_dir == None):
                print("Images or path to label directory is not set")
                return
            tmp_file = os.path.join((self.path_to_label_dir),
                                    ('{}{}.jpg'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), i)))
            cv2.imwrite(tmp_file, self.candies[i].cropped_img)
        print(len(self.candies), 'saved to path', self.path_to_label_dir, 'which makes a total of', self.num_images)


def main():
    parser = argparse.ArgumentParser(description='Gather images for training.')
    parser.add_argument('--image_dir', type=str, default="training_dir", help="location for new training images + /label_name")

    detector = CandyDetector.from_config(config_dict)
    td = Trainingdata()
    args = parser.parse_args()
    image_dir = args.image_dir
    candy_list = config_img.BOX_CANDIES
    if config.CANDY_TYPE == 0:
        candy_list = config_img.TWIST_CANDIES

    print('The following labels are available in directory: ')
    for i in range(len(candy_list)):
        print(i, ':', candy_list[i])

    lid = int(input("input label number: "))
    label = ""

    if lid < 0 or lid >= len(candy_list):
        raise ValueError("{} is not a valid input".format(lid))
    else :
        label = candy_list[lid]

    path_to_label_dir = os.path.join(image_dir, label)
    if not tf.gfile.Exists(path_to_label_dir):
        tf.gfile.MakeDirs(path_to_label_dir)

    capture = cv2.VideoCapture(0)
    capture.set(3, 1920)
    capture.set(4, 1080)

    w2_size = (960, 540)
    cv2.namedWindow('Detection', cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Detection', *w2_size)
    cv2.setMouseCallback('Detection', td.mouse_event)
    candies = None
    counter = 0

    while True:
        time.sleep(0.01)
        if capture.isOpened:
            ret, frame = capture.read()
            if not ret:
                break
            corners = td.detect_corners(frame)
            if corners is not None:
                cropped = calibrator.calibrate(frame)
                #write_message(cropped, label)
                #td.write_message(cropped, 'click right mouse button to take image')
                if (counter % 5 == 0):
                    candies = detector.detect(cropped)
                    td.set_variables(candies, os.path.join(os.path.join(image_dir, label)))
                td.draw_detection(cropped, candies)
                cv2.imshow('Detection', cropped)
                td.write_ok(frame)
                counter += 1
            else:
                blank = np.zeros((w2_size[1], w2_size[0], 3), np.uint8)
                td.write_message(blank, 'Marker detection failed', size=1, thickness=1)
                cv2.imshow('Detection', blank)

            key = cv2.waitKey(1)
            if (key == ord(' ')):
                td.take_pictures_and_save()
            if (key == 27):
                break

        if should_exit:
            break

    print("Exit.")
    cv2.destroyAllWindows()
if __name__ == '__main__':
    main()
