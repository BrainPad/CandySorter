import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import argparse
import json

def plot_accuracies(losses, accuracy_train, accuracy_test, accuracy_per_label, labels):
    ax = plt.subplot(111)
    ax.plot(losses, color='r', label="loss")
    ax.plot(accuracy_test, color='b', label="test accuracy")
    ax.plot(accuracy_train, color='y', label="train accuracy")

    ax.legend()
    plt.show()
    ax = plt.subplot(111)
    for i in range(len(accuracy_per_label)):
        ax.plot(accuracy_per_label[i], label=labels[i])
    ax.legend()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Display plot outputs from training')
    parser.add_argument('plotdata',
                        metavar='P',
                        type=str,
                        nargs='?',
                        default='./plots/plot_data.json',
                        help="The path to the plot data")
    args = parser.parse_args()

    with tf.gfile.FastGFile(args.plotdata, 'r') as f:
        plot_data = json.loads(f.read())

        plot_accuracies(**plot_data)


if __name__ == "__main__":
    main()
