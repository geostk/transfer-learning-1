import uuid
import weakref
import itertools
import numpy as np

from skimage import measure
from skimage import filters
import skimage.transform

import logging
logging.basicConfig(format='%(levelname)-6s: %(name)-10s %(asctime)-15s  %(message)s')
log = logging.getLogger("Cutouts")
log.setLevel(logging.WARNING)

class Cutouts:
    """
    Create cutouts of a set of input data.
    """

    # What is currently happening is the Cutout calculator gets created for each TransferLearningProcessData
    # instance which is not good. What we want to do is create an instance if one does not exist with the
    # specified uuid. So the "load" for Fingerprint needs to be a little smarter to check to see if an instance
    # already exists for that uuid, and if it does, return it, otherwise create a new one.
    _instances = set()

    @classmethod
    def getinstances(cls, search_uuid=None):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None and (search_uuid is None or (search_uuid is not None and search_uuid == obj.uuid)):
                print('FOUND CUTOUT INSTANCE NOT CREATING A NEW ONE!!')
                return obj
            elif obj is None:
                dead.add(ref)
        cls._instances -= dead
        return None

    def __init__(self):
        # list of data processing elements
        self._uuid = str(uuid.uuid4())

        # number of pixels around the image to include in the display
        self._image_display_margin = 50

        self._instances.add(weakref.ref(self))

    def create_cutouts(self, data):
        raise NotImplemented('Must create cutouts function')

    def save(self):
        raise NotImplemented('Must create cutouts function')

    @staticmethod
    def load_parameters(parameters):
        """
        Create an instance of the Cutout class based on the dictionary of parameters passed in.  The parameter
        parameter comes from the "save()" function of one of the implemented classes below.

        :param parameters: dictionary of information from which an instance will be created
        :return:
        """
        # First let's see if we have an instance with this UUID already created
        newinstance = Cutouts.getinstances(parameters['uuid'])

        if newinstance is None:
            for class_ in Cutouts.__subclasses__():
                if class_.__name__ == parameters['cutout_type']:

                    # If the class name matches, instantiate, pass in the parameters
                    # and return the newly created class.
                    tt = class_()
                    tt.load(parameters)
                    return tt
        else:
            return newinstance

class BasicCutouts:
    """
    The BasicCutouts class will create cutouts based on sliding window idea given a step_size.
    """

    def __init__(self, output_size, step_size):
        """
        Initialize with the output_size (assumed square at this point and a step_size

        :param output_size: cutout output size (assumed square)
        :param step_size: step size from one cutout to the next
        """

        self._output_size = output_size
        self._step_size = step_size
        self._uuid = str(uuid.uuid4())

    def __str__(self):
        """
        String representation for matplotlib title plots etc

        :return: string representation
        """

        return 'Basic Cutout (step_size={})'.format(self._step_size)

    def number_cutouts(self, data):
        """
        Number of cutouts given the data, this was implemented primarily for the progress bar.  If the create_cutouts
        function changes then this one will have to as well.

        :param data: image array of data.
        :return: number of cutouts that will be created in `create_cutouts()` below
        """

        N = self._output_size // 2

        # Determine the centers to use for the fingerprint calculation
        nrows, ncols = data.shape[:2]
        rows = range(N, nrows-N, self._step_size)
        cols = range(N, ncols-N, self._step_size)

        return len(list(itertools.product(rows, cols)))

    def create_cutouts(self, data):
        """
        Calculate the fingerprints for each subsection of the image in each file.

        :param data: Input data from which we will create the cutouts based on a sliding window.
        :return: the row start and end, column start and end and the actual numpy array of data that is the cutout
        """

        N = self._output_size // 2

        # Determine the centers to use for the fingerprint calculation
        nrows, ncols = data.shape[:2]
        rows = range(N, nrows-N, self._step_size)
        cols = range(N, ncols-N, self._step_size)

        # Run over all the rows and columns and yield the result
        for ii, (row, col) in enumerate(itertools.product(rows, cols)):
            td = data[row-N:row+N, col-N:col+N]
            yield row-N, row+N, col-N, col+N, td

    def save(self):
        """
        This method is used to create a representation of this instance of a cutout which can be saved
        in a pickle file and then later loaded.

        :return:
        """
        return {
            'cutout_type': self.__class__.__name__,
            'output_size': self._output_size,
            'step_size': self._step_size,
            'uuid': self._uuid
        }

    def _load(self, parameters):
        """
        Load the instance internal variables from the parameters dictionary

        :param parameters: dictonary of values that represent the class
        :return: nothing....
        """

        self._step_size = parameters['step_size']
        self._output_size = parameters['output_size']
        self._uuid = parameters['uuid']


class FullImageCutout:
    """
    The FullImageCutout class will create a single cutout based on resizing the input image to the output size.
    """

    def __init__(self, output_size):
        """
        Initialize with the output_size (assumed square at this point and a step_size

        :param output_size: cutout output size (assumed square)
        :param step_size: step size from one cutout to the next
        """

        self._output_size = output_size
        self._uuid = str(uuid.uuid4())

    def __str__(self):
        """
        String representation for matplotlib title plots etc

        :return: string representation
        """

        return 'Full Image Cutout'

    def number_cutouts(self, data):
        """
        Number of cutouts given the data, this was implemented primarily for the progress bar.  If the create_cutouts
        function changes then this one will have to as well.

        :param data: image array of data.
        :return: number of cutouts that will be created in `create_cutouts()` below
        """

        return 1

    def create_cutouts(self, data):
        """
        Calculate the fingerprints for the image in each file.

        :param data: Input data from which we will create the cutouts based on a sliding window.
        :return: the row start and end, column start and end and the actual numpy array of data that is the cutout
        """

        td = skimage.transform.resize(data, [self._output_size, self._output_size])
        yield 0, self._output_size, 0, self._output_size, td

    def save(self):
        """
        This method is used to create a representation of this instance of a cutout which can be saved
        in a pickle file and then later loaded.

        :return:
        """
        return {
            'cutout_type': self.__class__.__name__,
            'output_size': self._output_size,
            'uuid': self._uuid
        }

    def _load(self, parameters):
        """
        Load the instance internal variables from the parameters dictionary

        :param parameters: dictonary of values that represent the class
        :return: nothing....
        """

        self._output_size = parameters['output_size']
        self._uuid = parameters['uuid']


class BlobCutouts:
    """
    Blob cutouts is a little different way of creating cutouts. Rather than doing a sliding window we are going
    to use some image processing and labeling.  The basic algorithm is to smooth the image, label the connected
    components and then return 224x224 cutouts based on the center of each connected component.
    """

    def __init__(self, output_size, mean_threshold=2.0, gaussian_smoothing_sigma=10, label_padding=80):
        """
        Initialize the labeled connected component cutout creator.

        :param output_size: Output size, assumed square at this point
        :param mean_threshold: Signal threshold passed in to the labeling in order to determine connectedness
        :param gaussian_smoothing_sigma: Amount of smoothing to apply to the image before labeling
        :param label_padding: How much do we want to padd around the output image.
        """

        # list of data processing elements
        self._output_size = output_size
        self._mean_threshold = mean_threshold
        self._gaussian_smoothing_sigma = gaussian_smoothing_sigma
        self._label_padding = label_padding
        self._uuid = str(uuid.uuid4())

    def __str__(self):
        """
        String representation for matplotlib titles etc.

        :return:
        """
        return 'Blob Cutout (mean_threshold={}, gaussian_smoothign_sigma={})'.format(self._mean_threshold,
                                                                                     self._gaussian_smoothing_sigma)
    def number_cutouts(self, data):
        """
        Number of cutouts given the data, this was implemented primarily for the progress bar.  If the create_cutouts
        function changes then this one will have to as well.

        :param data: image array of data.
        :return: number of cutouts that will be created in `create_cutouts()` below
        """

        gray_image = np.dot(data[:, :, :3], [0.299, 0.587, 0.114])
        im = filters.gaussian_filter(gray_image, sigma=self._gaussian_smoothing_sigma)
        blobs = im > self._mean_threshold * im.mean()
        blobs_labels = measure.label(blobs, background=0)

        return blobs_labels.max()

    def create_cutouts(self, data):
        """
        This will create a number of cutouts. Each cutout is based on a connected component labeling of the image
        after a little smoothing. This is a reasonably standard method of doing the connnected component labeling.

        :param data: Input data
        :param mean_threshold: Threshold applied to mean in order to clip background
        :param gaussian_smoothing_sigma: How much smoothing should be applied to the image
        :param label_padding: Padding around the labeled cutout.
        :return:
        """

        # Find the blobs - make gray scale, smooth, find blobs, then label them
        gray_image = np.dot(data[:, :, :3], [0.299, 0.587, 0.114])
        im = filters.gaussian_filter(gray_image, sigma=self._gaussian_smoothing_sigma)
        blobs = im > self._mean_threshold * im.mean()
        blobs_labels = measure.label(blobs, background=0)

        # Loop over the blobs
        for ii in range(1, blobs_labels.max()):
            b = blobs_labels == ii

            # Find the extent of the image
            rows, cols = np.nonzero(b)
            min_row, max_row, mean_row = int(rows.min()), int(rows.max()), int(rows.mean())
            min_col, max_col, mean_col = int(cols.min()), int(cols.max()), int(cols.mean())

            log.debug('label mins and maxs {} {}   {} {}'.format(min_row, max_row, min_col, max_col))

            # Pad the blob a bit
            min_row = max(min_row - self._label_padding, 0)
            max_row = min(max_row + self._label_padding, data.shape[0])
            min_col = max(min_col - self._label_padding, 0)
            max_col = min(max_col + self._label_padding, data.shape[1])

            log.debug('label mins and maxs with padding {} {}   {} {}'.format(min_row, max_row, min_col, max_col))

            # Correct so it is square
            rr = max_row - min_row
            cc = max_col - min_col
            if rr > cc:
                min_col = min_col - (rr - cc) // 2
                max_col = max_col - (rr - cc) // 2
            else:
                min_row = min_row - (cc - rr) // 2
                max_row = max_row - (cc - rr) // 2

            # If the cutout extends outside the original image then we are going to drop it for now
            # TODO: Need to create a way to shift the cutout if outside the original image.
            if min_row < 0 or min_col < 0 or max_row >= data.shape[0] or max_col >= data.shape[1]:
                continue

            log.debug('Cutting out {} {}   {} {}'.format(min_row, max_row, min_col, max_col))

            # Resize the image and return
            td = skimage.transform.resize(data[min_row:max_row, min_col:max_col],
                                          [self._output_size, self._output_size])

            # This will need to match the standard return method for cutouts.
            yield min_row, max_row, min_col, max_col, td

    def save(self):
        """
        Save the variables in this instance to a dictionary so it can be saved for later importing and recreation.

        :return: dictionary of parameters
        """
        return {
            'cutout_type': self.__class__.__name__,
            'output_size': self._output_size,
            'mean_threshold': self._mean_threshold,
            'gaussian_smoothing_sigma': self._gaussian_smoothing_sigma,
            'label_padding': self._label_padding,
            'uuid': self._uuid
        }

    def _load(self, parameters):
        """
        Load the dictionary of parameters in order to re-create this instance. The parameters will come from the
        above save command.

        :param parameters: dictionary of parameters
        :return: nothing....
        """

        self._output_size = parameters['output_size']
        self._gaussian_smoothing_sigma = parameters['gaussian_smoothing_sigma']
        self._label_padding = parameters['label_padding']
        self._mean_threshold = parameters['mean_threshold']
        self._uuid = parameters['uuid']