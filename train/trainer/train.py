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
import json
import logging
import os
import random

import numpy as np
import tensorflow as tf
import trainer.model as model
from trainer.utils import TrainingFeaturesDataReader

JPEG_EXT = 'jpg'

logger = logging.getLogger(__name__)


class DataSet(object):
    def __init__(self, features_data, label_ids_data, image_uris, labels):
        self.features_data = features_data
        self.label_ids_data = label_ids_data
        self.image_uris = image_uris
        self.labels = labels

    @classmethod
    def from_reader(cls, reader):
        data = reader.read_features()
        uris = reader.read_feature_metadata('image_uri')
        labels = reader.read_labels()
        # print(data[0],  data[1], uris, labels)

        return cls(data[0], data[1], uris, labels)

    def n_samples(self):
        return len(self.features_data)

    def feature_size(self):
        return self.features_data[0].shape[0]

    def get(self, idx):
        return self.features_data[idx], self.label_ids_data[idx]

    def get_meta(self, idx):
        lid = self.label_ids_data[idx]
        return {'url': self.image_uris[idx], 'label': self.labels[lid], 'lid': lid}

    def all(self):
        return self.features_data, self.label_ids_data


class TrainingConfig(object):
    def __init__(self, epochs, batch_size, optimizer_class, optimizer_args, keep_prob=1.0):
        self.epochs = epochs
        self.batch_size = batch_size
        self.optimizer = optimizer_class(**optimizer_args)
        self.optimizer_args = optimizer_args
        self.keep_prob = keep_prob

    def to_json(self):
        optimizer_str = type(self.optimizer).__name__
        return json.dumps({
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "keep_prob": self.keep_prob,
            "optimizer": {
                "name": optimizer_str,
                "args": self.optimizer_args,
            }
        })


class Trainer(object):
    def __init__(self, train_config, model_params, train_dir, log_dir, plot_dir, test_dir=None):
        self.train_config = train_config
        self.model_params = model_params
        self.test_dir = test_dir
        self.train_dir = train_dir
        self.log_dir = log_dir
        self.plot_dir = plot_dir

        self.model = model.TransferModel.from_model_params(self.model_params)
        self.train_op = self.model.train_op(self.train_config.optimizer)

        self._sleep_sec = 0.1

        self._last_logged_loss = None

        self._force_logging_interval = 200
        self._check_interval = 10
        self._threshold = 0.20

    def _epoch_log_path(self, num_epoch):
        return os.path.join(self.log_dir, 'epochs', '{}.json'.format(str(num_epoch).zfill(6)))

    def train(self, trainingset, testingset=None):

        n_samples = trainingset.n_samples()
        logger.info('Build transfer network.')

        logger.info('Start training.')
        checkpoint_path = os.path.join(self.train_dir, 'model.ckpt')

        epoch_log_dir = os.path.dirname(self._epoch_log_path(0))
        if not tf.gfile.Exists(epoch_log_dir):
            tf.gfile.MakeDirs(epoch_log_dir)

        loss_log = []
        with tf.Session() as sess:
            summary_writer = tf.summary.FileWriter(self.log_dir, graph=sess.graph)
            sess.run(tf.initialize_all_variables())

            losses = []
            accuracies_test = []
            accuracies_train = []
            label_accuracy = []

            if (testingset):
                for i in range(len(testingset.labels)):
                    label_accuracy.append([])

            for epoch in range(self.train_config.epochs):

                num_img_per_label = [0] * len(label_accuracy)
                num_errors_per_label = [0] * len(label_accuracy)

                # Shuffle data for batching
                shuffled_idx = list(range(n_samples))
                random.shuffle(shuffled_idx)
                for begin_idx in range(0, n_samples, self.train_config.batch_size):
                    batch_idx = shuffled_idx[begin_idx: begin_idx + self.train_config.batch_size]
                    sess.run(self.train_op, self.model.feed_for_training(*trainingset.get(batch_idx)))

                # Print and write summaries.
                in_sample_loss, summary = sess.run(
                    [self.model.loss_op, self.model.summary_op],
                    self.model.feed_for_training(*trainingset.all())
                )

                loss_log.append(in_sample_loss)
                losses.append(in_sample_loss)

                summary_writer.add_summary(summary, epoch)

                if epoch % 100 == 0 or epoch == self.train_config.epochs - 1:
                    logger.info('{}th epoch end with loss {}.'.format(epoch, in_sample_loss))

                # -------- Accuracy for training set:

                if trainingset:
                    features = sess.run(
                        [self.model.softmax_op],
                        self.model.feed_for_training(*trainingset.all())  # feed training data
                    )

                    # write loss and predicted probabilities
                    probs = list(map(lambda a: a.tolist(), features[0]))
                    averageAccuracy = 0
                    max_l = max(loss_log)
                    loss_norm = [float(l) / max_l for l in loss_log]
                    with tf.gfile.FastGFile(self._epoch_log_path(epoch + 1000), 'w') as f:
                        data = {
                            'epoch': epoch + 1000,
                            'loss': loss_norm,
                        }
                        probs_with_uri = []
                        correctCount = 0

                        for i, p in enumerate(probs):
                            meta = trainingset.get_meta(i)  # metadata for training
                            predicted = np.argmax(p)
                            if predicted == int(meta['lid']):
                                correctCount += 1
                            item = {
                                'probs': p,
                                'url': meta['url'],
                                'property': {
                                    'label': meta['label'],
                                    'lid': int(meta['lid'])
                                }
                            }
                            probs_with_uri.append(item)

                        averageAccuracy += correctCount / len(probs)
                        accuracies_train.append(averageAccuracy)
                        data['probs'] = probs_with_uri
                        f.write(json.dumps(data))

                # -------- Accuracy for test set:

                if (testingset):
                    features = sess.run(
                        [self.model.softmax_op],
                        self.model.feed_for_training(*testingset.all())  # feed testing data ---------not training
                    )

                    # write loss and predicted probabilities Test
                    probs = list(map(lambda a: a.tolist(), features[0]))
                    averageAccuracy = 0
                    max_l = max(loss_log)
                    loss_norm = [float(l) / max_l for l in loss_log]

                    with tf.gfile.FastGFile(self._epoch_log_path(epoch), 'w') as f:
                        data = {
                            'epoch': epoch,
                            'loss': loss_norm,
                        }
                        probs_with_uri = []
                        correctCount = 0

                        for i, p in enumerate(probs):
                            meta = testingset.get_meta(i)  # metadata for testing
                            num_img_per_label[(meta['lid'])] += 1
                            predicted = np.argmax(p)
                            if predicted == int(meta['lid']):
                                correctCount += 1
                            else:
                                num_errors_per_label[meta['lid']] += 1
                                # print('error on ', meta['url'], ' with label ', meta['label'], 'thought it was ', testingset.labels[predicted])

                            item = {
                                'probs': p,
                                'url': meta['url'],
                                'property': {
                                    'label': meta['label'],
                                    'lid': int(meta['lid'])
                                }
                            }
                            probs_with_uri.append(item)

                        averageAccuracy += correctCount / len(probs)
                        accuracies_test.append(averageAccuracy)
                        data['probs'] = probs_with_uri
                        f.write(json.dumps(data))

                for i in range(len(label_accuracy)):
                    print('fails on', num_errors_per_label[i], 'out of ', num_img_per_label[i], 'images of ',
                          testingset.labels[i])

                    if (num_errors_per_label[i] != 0):
                        label_accuracy[i].append(100 - (num_errors_per_label[i] / num_img_per_label[i]) * 100)
                        print('gives accuracy ', 100 - (num_errors_per_label[i] / num_img_per_label[i]) * 100)
                    elif ((num_errors_per_label[i] == 0) and (num_img_per_label != 0)):
                        label_accuracy[i].append(100)
                        print('gives accuracy ', 100)
                    else:
                        label_accuracy[i].append(0)
                        print('gives accuracy ', 0)

            # FIXME: sleep to show convergence slowly on UI
            # if epoch < 200 and loss_log[-1] > max(loss_log) * 0.01:
            #     time.sleep(self._sleep_sec)

            if testingset:
                self.export_plot_data(losses, accuracies_train, accuracies_test, label_accuracy, testingset.labels)

            self.model.saver.save(sess, checkpoint_path, global_step=self.model.global_step)
            summary_writer.close()

    def _needs_logging(self, loss_log):
        if len(loss_log) < self._check_interval or len(loss_log) % self._check_interval != 0:
            return False
        if len(loss_log) % self._force_logging_interval == 0:
            return True

        loss = loss_log[-1]
        if self._last_logged_loss is None:
            self._last_logged_loss = loss
            return True

        loss_change_rate = loss / self._last_logged_loss
        if 1 - loss_change_rate > self._threshold:
            self._last_logged_loss = loss
            return True

        return False

    def export_plot_data(self, losses, accuracy_train, accuracy_test, accuracy_per_label, labels):
        with tf.gfile.FastGFile(os.path.join(self.plot_dir, "plot_data.json"), 'w') as f:
            f.write(json.dumps({
                'losses': losses,
                'accuracy_train': accuracy_train,
                'accuracy_test': accuracy_test,
                'accuracy_per_label': accuracy_per_label,
                'labels': labels
            }, cls=NumpyEncoder))


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """

    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32,
                              np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):  #### This is the fix
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def main(_):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)-7s %(levelname)-7s %(message)s'
    )
    logger.info('tf version: {}'.format(tf.__version__))

    parser = argparse.ArgumentParser(description='Run Dobot WebAPI.')
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--hidden_size', type=int, default=7, help="Number of units in hidden layer.")
    parser.add_argument('--epochs', type=int, default=50, help="Number of epochs of training")
    parser.add_argument('--learning_rate', type=float, default=1e-3)
    parser.add_argument('--keep_prob', type=float, default=1.0)
    parser.add_argument('--active_test_mode', default=False, action='store_true', help='Set True for testing')
    parser.add_argument('--data_dir', type=str, default='output', help="Directory for training data.")
    parser.add_argument('--test_dir', type=str, default='output', help="Directory for test data.")
    parser.add_argument('--log_dir', type=str, default='log', help="Directory for TensorBoard logs.")
    parser.add_argument('--train_dir', type=str, default='train', help="Directory for checkpoints.")
    parser.add_argument('--plot_dir', type=str, default='plots', help="Directory for accuracy plot data")

    args = parser.parse_args()

    data_dir = args.data_dir
    readerTrain = TrainingFeaturesDataReader(data_dir, features_file_name='features.json')
    trainingset = DataSet.from_reader(readerTrain)
    testingset = None

    if (args.active_test_mode):
        test_dir = args.test_dir
        readerTest = TrainingFeaturesDataReader(test_dir, features_file_name='testfeatures.json')
        testingset = DataSet.from_reader(readerTest)

    train_config = TrainingConfig(
        epochs=args.epochs,
        batch_size=args.batch_size,
        optimizer_class=tf.train.RMSPropOptimizer,
        optimizer_args={"learning_rate": args.learning_rate},
        keep_prob=args.keep_prob,
    )

    params = model.ModelParams(
        labels=trainingset.labels,
        hidden_size=args.hidden_size,
        features_size=trainingset.feature_size()
    )

    if not tf.gfile.Exists(args.train_dir):
        tf.gfile.MakeDirs(args.train_dir)

    if not tf.gfile.Exists(args.log_dir):
        tf.gfile.MakeDirs(args.log_dir)

    if not tf.gfile.Exists(args.plot_dir):
        tf.gfile.MakeDirs(args.plot_dir)

    with tf.gfile.FastGFile(os.path.join(args.train_dir, 'params.json'), 'w') as f:
        f.write(params.to_json())

    with tf.gfile.FastGFile(os.path.join(args.log_dir, 'training.json'), 'w') as f:
        f.write(train_config.to_json())

    if args.active_test_mode:
        trainer = Trainer(
            train_config=train_config,
            model_params=params,
            train_dir=args.train_dir,
            log_dir=args.log_dir,
            plot_dir=args.plot_dir,
            test_dir=args.test_dir
        )
        trainer.train(trainingset, testingset)
    else:
        trainer = Trainer(
            train_config=train_config,
            model_params=params,
            train_dir=args.train_dir,
            log_dir=args.log_dir,
            plot_dir=args.plot_dir
        )
        trainer.train(trainingset)


if __name__ == '__main__':
    tf.app.run()
