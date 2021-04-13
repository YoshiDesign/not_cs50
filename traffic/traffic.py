import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """

    all_inputs = tuple([[],[]])
    for d in os.listdir(data_dir):

        # Ignoring Mac Junk
        if d == ".DS_Store":
            continue

        # print(os.path.join(data_dir, d))

        # nd_array = np.ndarray(shape=())
        for f in os.listdir(os.path.join(data_dir, d)):

            # Ignoring Mac Junk
            if d == ".DS_Store":
                continue

            # Load and resize the image
            img = cv2.imread(os.path.join(data_dir,d,f), cv2.IMREAD_UNCHANGED)
            # img = np.ndarray(shape=(img.shape), buffer=img.__array__())    Nope

            # Resize the Mat data and store in a numpy array
            img = np.array(
                cv2.resize( img, (IMG_WIDTH, IMG_HEIGHT) )
            )

            # cv2.imshow("Hello", img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            # exit()

            all_inputs[0].append(img)
            all_inputs[1].append(d)

    # Shuffle the data prior to training - Good practice 
    # even tho TF does it by default
    # Violates the spec
    # from sklearn.utils import shuffle
    # shuffle_mat, shuffle_lab = \
    #     shuffle(all_inputs[0], all_inputs[1])

    # return [shuffle_mat, shuffle_lab]
    return all_inputs


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    # tf.debugging.set_log_device_placement(True)

    model = tf.keras.models.Sequential([
        # Input layer
        tf.keras.layers.Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding = 'same', input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)),
        # tf.keras.layers.MaxPool2D(pool_size=(2, 2), strides=1),
        tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding = 'same'),
        # tf.keras.layers.MaxPool2D(pool_size=(2, 2), strides=1),   
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(units=NUM_CATEGORIES, activation='softmax'),
    ])

    # model.summary()
    
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

if __name__ == "__main__":
    main()
