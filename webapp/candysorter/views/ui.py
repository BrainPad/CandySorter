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

from datetime import datetime
import os

import cv2
from flask import Blueprint, current_app, send_file, send_from_directory

from candysorter.config import Config
from candysorter.decorators import after_this_request
from candysorter.utils import load_class

ui = Blueprint('ui', __name__)


@ui.route('/predict')
def predict():
    return current_app.send_static_file('predict.html')


@ui.route('/learn')
def learn():
    return current_app.send_static_file('learn.html')


@ui.route('/image/<path:filename>')
def image(filename):
    return send_from_directory(Config.DOWNLOAD_IMAGE_DIR, filename)


@ui.route('/_capture')
def capture():
    tmp_dir = os.path.join(Config.DOWNLOAD_IMAGE_DIR, 'tmp')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    tmp_file = os.path.join(tmp_dir, '{}.jpg'.format(datetime.now().strftime('%Y%m%d_%H%M%S')))

    @after_this_request
    def remove_tmp_file(response):
        os.remove(tmp_file)

    image_capture = load_class(Config.CLASS_IMAGE_CAPTURE).from_config(Config)
    img = image_capture.capture()

    cv2.imwrite(tmp_file, img)
    return send_file(tmp_file)
