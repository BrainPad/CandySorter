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

import argparse
import os
import logging
import json
import sys
import tensorflow as tf
import threading
import multiprocessing
import time
import random
import math
import numpy as np
from itertools import islice


INPUT_DATA_TENSOR_NAME = 'DecodeJpeg:0'
FEATURE_TENSOR_NAME = 'pool_3/_reshape:0'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-7s %(levelname)-7s %(message)s'
)
logger = logging.getLogger(__name__)

# Mute logging of warnings to avoid spam with deprecated use of .op_scope
tf.logging.set_verbosity(tf.logging.ERROR)


class FeatureExtractor(object):
    """
    FeatureExtractor extracts 2048-dimension feature vectors from image files
    using inception-v3.
    """

    def __init__(self, model_file):
        # load inception-v3 model
        self.graph = tf.Graph()
        with tf.gfile.FastGFile(model_file, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            with self.graph.as_default():
                _ = tf.import_graph_def(graph_def, name='')

            feature = tf.reshape(self.graph.get_tensor_by_name(FEATURE_TENSOR_NAME), [-1])
        self.feature_op = feature

        self.saver = None

    @classmethod
    def from_model_dir(cls, model_dir):
        return cls(os.path.join(model_dir, 'classify_image_graph_def.pb'))

    def get_feature_vector(self, img_bgr):
        with tf.Session(graph=self.graph) as sess:
            feature_data = sess.run(
                self.feature_op,
                {INPUT_DATA_TENSOR_NAME: img_bgr}
            )
        return feature_data.reshape(-1, feature_data.shape[0])

    def get_feature_vectors_from_files(self, image_paths, turn=0, gamma_min=1, gamma_max=1):

        # Decode image
        with self.graph.as_default():
            image = tf.image.decode_jpeg(tf.read_file(image_paths[0]))

        # Extract features
        features = []
        with tf.Session(graph=self.graph) as sess:
            if turn > 0:
                rotate = tf.image.rot90(image, k=turn)
                image = sess.run(rotate)
                image = tf.convert_to_tensor(image)


            if gamma_min != 1 or gamma_max != 1:
                image = tf.image.convert_image_dtype(image, tf.float32)
                gamma = tf.image.adjust_gamma(image, gamma=random.uniform(gamma_min, gamma_min))
                image = sess.run(gamma)

                image = tf.convert_to_tensor(image)



            for path in image_paths:
                image_data = sess.run(
                    image
                )
                feature_data = sess.run(
                    self.feature_op,
                    {INPUT_DATA_TENSOR_NAME: image_data}
                )
                features.append(feature_data)
        return features

class ImagePathGeneratorForTraining(object):
    def __init__(self, image_dir, extension='jpg'):
        self.image_dir = image_dir
        self.extension = extension

    def get_labels(self):
        return sorted(
            [sub_dir for sub_dir in tf.gfile.ListDirectory(self.image_dir)
             if tf.gfile.IsDirectory('/'.join((self.image_dir, sub_dir)))
             ]
        )

    def __iter__(self):
        for label_id, label in enumerate(self.get_labels()):
            dir_path = os.path.join(self.image_dir, label)
            paths = tf.gfile.Glob('{}/*.{}'.format(dir_path, self.extension))
            for path in paths:
                yield path, label_id
        raise StopIteration()


class ImagePathGeneratorForPrediction(object):
    def __init__(self, image_dir, extension='jpg'):
        self.image_dir = image_dir
        self.extension = extension

    def __iter__(self):
        paths = tf.gfile.Glob('{}/*.{}'.format(self.image_dir, self.extension))
        for path in paths:
            yield path, None
        raise StopIteration()


def write_labels(labels, labels_data_path):
    with tf.gfile.FastGFile(labels_data_path, 'w') as f:
        f.write(json.dumps(labels))


def main():
    args = _parse_arguments()

    labels_file = os.path.join(args.output_dir, 'labels.json')
    features_file_train = os.path.join(args.output_dir, 'features.json')
    features_file_test = os.path.join(args.output_dir, 'testfeatures.json')

    _ensure_dir_exists(args.output_dir)

    path_gen_train, path_gen_test = _get_path_generators(args)

    logger.info("Writing label file: {}".format(labels_file))
    write_labels(path_gen_train.get_labels(), labels_file)

    _run_multiprocess_extraction(args, path_gen_train, "train-output-", features_file_train)

    if args.active_test_mode:
        _run_multiprocess_extraction(args, path_gen_test, "test-output-", features_file_test)

    logger.info("Process completed successfully")


def _ensure_dir_exists(directory):
    if not tf.gfile.Exists(directory):
        tf.gfile.MakeDirs(directory)


def _get_path_generators(args):
    path_gen_train, path_gen_test = None, None

    if args.for_prediction:
        path_gen_train = ImagePathGeneratorForPrediction(args.image_dir_train)
        if args.active_test_mode:
            path_gen_test = ImagePathGeneratorForPrediction(args.image_dir_test)

    else:
        path_gen_train = ImagePathGeneratorForTraining(args.image_dir_train)
        if args.active_test_mode:
            path_gen_test = ImagePathGeneratorForTraining(args.image_dir_test)

    return path_gen_train, path_gen_test


def _run_multiprocess_extraction(args, path_generator, temp_files_prefix, output_feature_file):
    num_of_files = len(list(path_generator))

    progress_queue = multiprocessing.Queue()
    progress_printer = threading.Thread(target=ProgressPrinter, args=(progress_queue, num_of_files))
    progress_printer.start()

    image_chunks = generate_image_chunks(path_generator, args.processes)

    test_processes = [multiprocessing.Process(target=ExtractionProcess,
                                              args=(args, image_chunks[i], temp_files_prefix, i, progress_queue))
                      for i in range(args.processes)]

    _start_and_join_processes(test_processes)

    progress_queue.put(("CLOSE", 0))
    progress_printer.join()

    _merge_files(output_feature_file, args.output_dir, temp_files_prefix)


def _merge_files(output_file, output_dir, prefix):
    logger.info("Merging files prefixed with {} into file {}".format(prefix, output_file))
    with tf.gfile.FastGFile(output_file, 'w') as f:
        for _, _, filenames in os.walk(output_dir):
            for filename in filenames:
                if filename.startswith(prefix):
                    path = os.path.join(output_dir, filename)
                    with tf.gfile.FastGFile(path, 'r') as g:
                        f.write(g.read())
                    os.remove(path)


def _start_and_join_processes(processes):
    logger.info("Starting {} processes and waiting for completion".format(len(processes)))
    for t in processes:
        t.start()

    for t in processes:
        t.join()


# -------------------------------------------------
#
#
#               PROCESS
#
#
# -------------------------------------------------
def generate_image_chunks(generator, split_into):
    all_files = list(generator)
    number_of_files = len(all_files)
    chunk_size = math.ceil(number_of_files / float(split_into))

    chunks = []
    for start_index in range(0, number_of_files, chunk_size):
            chunks.append(all_files[start_index: start_index + chunk_size])

    return chunks


class FeaturesDataWriterProcess(object):
    """
    FeatureDataWriter extracts feature data from images and write to json lines
    """

    def __init__(self, image_list, feature_extractor, progress_queue):
        self.image_list = image_list
        self.extractor = feature_extractor
        self.progress_queue = progress_queue

    def write_features(self, features_data_path, rotations):
        with tf.gfile.FastGFile(features_data_path, 'w') as f:
            for index, (path, label_id) in enumerate(self.image_list):
                for i in range(rotations + 1):
                    for gamma_min, gamma_max in [(0.9, 1), (0.5, 0.9), (1, 1.3)]:
                        line = self.extract_data_for_path(path, label_id, i, gamma_min, gamma_max)
                        f.write(json.dumps(line) + '\n')

                if (index + 1) % 20 == 0:
                    self.progress_queue.put(("PROGRESS", 20))

    def extract_data_for_path(self, image_path, label_id, turn, gamma_min, gamma_max):
        vector = self.extractor.get_feature_vectors_from_files([image_path], turn, gamma_min, gamma_max)
        line = {
            'image_uri': image_path,
            'feature_vector': vector[0].tolist()
        }
        if label_id is not None:
            line['label_id'] = label_id
        return line


def ExtractionProcess(args, image_list, output_prefix, index, progress_queue):
    print("Extraction process " + str(index) + " started")

    extractor = FeatureExtractor(args.model_file)
    writer_train = FeaturesDataWriterProcess(image_list, extractor, progress_queue)

    output_file = os.path.join(args.output_dir, output_prefix + str(index) + '.json')

    writer_train.write_features(output_file, args.rotations)


def ProgressPrinter(progress_queue, total):
    start_time = time.time()
    completed = 0

    while True:
        message_type, data = progress_queue.get()
        if message_type == "CLOSE":
            return
        elif message_type == "PROGRESS":
            completed += data

        time_per_image = (time.time() - start_time) / completed
        time_left = (time_per_image * (total - completed)) / 60
        percent_complete = (completed / total) * 100
        sys.stdout.write("\rProcessing image {}/{} (Not counting rotations) - {:.1f}% "
                         "- Estimated time left: {:.0f} minutes"
                         .format(completed, total, percent_complete, math.ceil(time_left)))
        sys.stdout.flush()


def _parse_arguments():
    parser = argparse.ArgumentParser(description='Run feature extraction')
    parser.add_argument(
        '--output_dir',
        default='output',
        nargs=1,
        type=str
    )
    parser.add_argument(
        '--image_dir_train',
        default='../image/train',
        type=str
    )
    parser.add_argument(
        '--active_test_mode',
        default=False,
        action='store_true',
        help='Use this flag to enable generating test features'
    )
    parser.add_argument(
        '--image_dir_test',
        default='../image/test',
        type=str
    )
    parser.add_argument(
        '--model_file',
        type=str,
        default='classify_image_graph_def.pb'
    )
    parser.add_argument(
        '--for_prediction',
        action='store_true'
    )
    parser.add_argument(
        '--processes',
        default=1,
        type=int,
        help="The number of processes to use for the extraction. More processes might help speeding up the "
             "extraction process. Rule of thumb might be to use approx one process per 4 logical cores"
    )
    parser.add_argument(
        '--rotations',
        default=0,
        type=int,
        help="Number of 90deg rotations of the training image to use. 0 will only use the image as is, "
             "while 1 will use the image as is as well as rotating the image 1 time, doubling the number"
             "of extracted features")

    return parser.parse_args()


if __name__ == "__main__":
    main()
