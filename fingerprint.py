import uuid
import time
import numpy as np

from utils import gray2rgb

import logging
logging.basicConfig(format='%(levelname)-6s: %(name)-10s %(asctime)-15s  %(message)s')
log = logging.getLogger("Fingerprint")
log.setLevel(logging.INFO)


class Fingerprint:
    def __init__(self):
        self._uuid = str(uuid.uuid4())
        self._predictions = []

    def save(self, output_directory):
        raise NotImplementedError("Please Implement this method")

    @staticmethod
    def select_fingerprint():
        """
        The function will display all the fingerprinting methods and return a class
        of the one of interest.  This can then be used to construct the class and
        to use in further calculations.

        :return:  selected class
        """
        subclasses = Fingerprint.__subclasses__()

        selected = False
        N = 0
        while not selected:
            # Show the fingerprints in order to allow for the person to select one
            print('Select a pre-trained network to use (q to quit:')
            for ii, x in enumerate(subclasses):
                print('   {}) {}'.format(ii, x.__str__()))
                N = ii

            s = input('Select Number > ')

            if s == 'q':
                return

            try:
                s = int(s)
                if s >= 0 and s < N:
                    # create fingerprint
                    return subclasses[s]
            except:
                pass

    @staticmethod
    def load_parameters(parameters):
        for class_ in Fingerprint.__subclasses__():
            if class_.__name__ == parameters['class_name']:
                tt = class_()
                tt.load(parameters)
                return tt

    def load(self, parameters):
        # nothing to do for now
        pass

class FingerprintResnet(Fingerprint):

    def __init__(self, max_fingerprints=200):
        super(FingerprintResnet, self).__init__()

        from keras.applications.resnet50 import ResNet50
        self._resnet50_model = ResNet50(weights='imagenet')

        self._max_fingerprints = max_fingerprints

    def __str__(self):
        return 'Fingerprint (renet50, imagenet)'

    def calculate(self, data):
        from keras.applications.resnet50 import preprocess_input as preprocess_input
        from keras.applications.resnet50 import decode_predictions as decode_predictions

        start_time = time.time()

        # Set the data into the expected format
        if len(data.shape) < 3:
            x = gray2rgb(data)
        else:
            x = data.astype(np.float64)

        # Set the data into the expected format
        x = np.expand_dims(x, axis=0)

        # Do keras model image pre-processing
        x = preprocess_input(x)

        # There was an error at one point when the image was completely 0
        # In this case I just set a single prediction with low weight.
        # TODO:  Check to see if this is still an issue.
        if np.sum(np.abs(x)) > 0.0001:
            preds = self._resnet50_model.predict(x)
            # decode the results into a list of tuples (class, description, probability)
            # (one such list for each sample in the batch)
            self._predictions = decode_predictions(preds, top=self._max_fingerprints)[0]
        else:
            self._predictions = [('test', 'beaver', 0.0000000000001), ]

        end_time = time.time()
        log.debug('Predictions: {}'.format(self._predictions[:10]))
        log.info('Calculate {} predictions took {}s'.format(len(self._predictions), end_time - start_time))

        return self._predictions

    def save(self):
        return {
            'class_name': self.__class__.__name__,
            'parameters': {
            }
        }



class FingerprintVGG16(Fingerprint):

    def __init__(self, max_fingerprints=200):
        super(FingerprintVGG16, self).__init__()

        from keras.applications.vgg16 import VGG16
        self._vgg16_model = VGG16(weights='imagenet')

        self._max_fingerprints = max_fingerprints

    def __str__(self):
        return 'Fingerprint (vgg16, imagenet)'

    def calculate(self, data):
        from keras.applications.vgg16 import preprocess_input
        from keras.applications.vgg16 import decode_predictions

        start_time = time.time()

        # Set the data into the expected format
        if len(data.shape) < 3:
            x = gray2rgb(data)
        else:
            x = data.astype(np.float64)

        # Set the data into the expected format
        x = np.expand_dims(x, axis=0)

        # Do keras model image pre-processing
        x = preprocess_input(x)

        # There was an error at one point when the image was completely 0
        # In this case I just set a single prediction with low weight.
        # TODO:  Check to see if this is still an issue.
        if np.sum(np.abs(x)) > 0.0001:
            preds = model.predict(x)
            # decode the results into a list of tuples (class, description, probability)
            # (one such list for each sample in the batch)
            self._predictions = decode_predictions(preds, top=self._max_fingerprints)[0]
        else:
            self._predictions = [('test', 'beaver', 0.0000000000001), ]

        end_time = time.time()
        log.debug('Predictions: {}'.format(self._predictions[:10]))
        log.info('Calculate {} predictions took {}s'.format(len(self._predictions), end_time - start_time))

        return self._predictions

    def save(self):
        return {
            'class_name': self.__class__.__name__,
            'parameters': {
            }
        }


class FingerprintVGG19(Fingerprint):

    def __init__(self, max_fingerprints=200):
        super(FingerprintVGG19, self).__init__()

        from keras.applications.vgg19 import VGG19
        self._vgg19_model = VGG19(weights='imagenet')

        self._max_fingerprints = max_fingerprints

    def __str__(self):
        return 'Fingerprint (vgg19, imagenet)'

    def calculate(self, data):
        from keras.applications.vgg19 import preprocess_input
        from keras.applications.vgg19 import decode_predictions

        start_time = time.time()

        # Set the data into the expected format
        if len(data.shape) < 3:
            x = gray2rgb(data)
        else:
            x = data.astype(np.float64)

        # Set the data into the expected format
        x = np.expand_dims(x, axis=0)

        # Do keras model image pre-processing
        x = preprocess_input(x)

        # There was an error at one point when the image was completely 0
        # In this case I just set a single prediction with low weight.
        # TODO:  Check to see if this is still an issue.
        if np.sum(np.abs(x)) > 0.0001:
            preds = model.predict(x)
            # decode the results into a list of tuples (class, description, probability)
            # (one such list for each sample in the batch)
            self._predictions = decode_predictions(preds, top=self._max_fingerprints)[0]
        else:
            self._predictions = [('test', 'beaver', 0.0000000000001), ]

        end_time = time.time()
        log.debug('Predictions: {}'.format(self._predictions[:10]))
        log.info('Calculate {} predictions took {}s'.format(len(self._predictions), end_time - start_time))

        return self._predictions

    def save(self):
        return {
            'class_name': self.__class__.__name__,
            'parameters': {
            }
        }


class FingerprintInceptionV3(Fingerprint):

    def __init__(self, max_fingerprints=200):
        super(FingerprintInceptionV3, self).__init__()

        from keras.applications.inception_v3 import InceptionV3
        self._model = InceptionV3(weights='imagenet')

        self._max_fingerprints = max_fingerprints

    def __str__(self):
        return 'Fingerprint (inception_v3, imagenet)'

    def calculate(self, data):
        from keras.applications.inception_v3 import preprocess_input
        from keras.applications.inception_v3 import decode_predictions

        start_time = time.time()

        # Set the data into the expected format
        if len(data.shape) < 3:
            x = gray2rgb(data)
        else:
            x = data.astype(np.float64)

        # Set the data into the expected format
        x = np.expand_dims(x, axis=0)

        # Do keras model image pre-processing
        x = preprocess_input(x)

        # There was an error at one point when the image was completely 0
        # In this case I just set a single prediction with low weight.
        # TODO:  Check to see if this is still an issue.
        if np.sum(np.abs(x)) > 0.0001:
            preds = self._model.predict(x)
            # decode the results into a list of tuples (class, description, probability)
            # (one such list for each sample in the batch)
            self._predictions = decode_predictions(preds, top=self._max_fingerprints)[0]
        else:
            self._predictions = [('test', 'beaver', 0.0000000000001), ]

        end_time = time.time()
        log.debug('Predictions: {}'.format(self._predictions[:10]))
        log.info('Calculate {} predictions took {}s'.format(len(self._predictions), end_time - start_time))

        return self._predictions

    def save(self):
        return {
            'class_name': self.__class__.__name__,
            'parameters': {
            }
        }



class FingerprintInceptionResNetV2(Fingerprint):

    def __init__(self, max_fingerprints):
        super(FingerprintInceptionResNetV2, self).__init__()

        from keras.applications.inception_resnet_v2 import InceptionResNetV2
        self._model = InceptionResNetV2(weights='imagenet')

        self._max_fingerprints = max_fingerprints

    def __str__(self):
        return 'Fingerprint (inception_resnet_v2, imagenet)'

    def calculate(self, data):
        from keras.applications.inception_resnet_v2 import preprocess_input
        from keras.applications.inception_resnet_v2 import decode_predictions

        start_time = time.time()

        # Set the data into the expected format
        if len(data.shape) < 3:
            x = gray2rgb(data)
        else:
            x = data.astype(np.float64)

        # Set the data into the expected format
        x = np.expand_dims(x, axis=0)

        # Do keras model image pre-processing
        x = preprocess_input(x)

        # There was an error at one point when the image was completely 0
        # In this case I just set a single prediction with low weight.
        # TODO:  Check to see if this is still an issue.
        if np.sum(np.abs(x)) > 0.0001:
            preds = model.predict(x)
            # decode the results into a list of tuples (class, description, probability)
            # (one such list for each sample in the batch)
            self._predictions = decode_predictions(preds, top=self._max_fingerprints)[0]
        else:
            self._predictions = [('test', 'beaver', 0.0000000000001), ]

        end_time = time.time()
        log.debug('Predictions: {}'.format(self._predictions[:10]))
        log.info('Calculate {} predictions took {}s'.format(len(self._predictions), end_time - start_time))

        return self._predictions

    def save(self):
        return {
            'class_name': self.__class__.__name__,
            'parameters': {
            }
        }
