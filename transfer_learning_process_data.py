import imageio
import numpy as np
import uuid

from astropy.io import fits

import utils
from data_processing import DataProcessing
from fingerprint import Fingerprint
from cutouts import Cutouts

import progressbar

import logging
logging.basicConfig(format='%(levelname)-6s: %(name)-10s %(asctime)-15s  %(message)s')
log = logging.getLogger("TransferLearningProcessData")
log.setLevel(logging.DEBUG)


class TransferLearningProcessData:
    """
    This contains data processed on a file using one type of data_processing and once calculate is called
    will contain the fingerprints for each cutout.
    """

    def __init__(self, filename, data_processing):

        self._uuid = str(uuid.uuid4())
        self._filename = filename
        self._data_processing = [DataProcessing.load_parameters(x) for x in data_processing]
        self._processed_data = self._load_image_data(filename)

        # Set in the calculate function
        self._cutout_creator = None
        self._fingerprint_calculator = None
        self._fingerprints = []

    @property
    def data_processing(self):
        return self._data_processing

    @property
    def filename(self):
        return self._filename

    @property
    def fingerprints(self):
        return self._fingerprints

    def _load_image_data(self, filename):
        """
        Load the file and apply the processing.

        :param filename:
        :return:
        """
        if any(filename.lower().endswith(s) for s in ['tiff', 'tif', 'jpg']):
            log.debug('Loading TIFF/JPG file {}'.format(filename))
            data = np.array(imageio.imread(filename))
        elif 'fits' in filename:
            log.debug('Loading FITS file {}'.format(filename))
            data = fits.open(filename)[1].data
            log.debug('FITS data is {}'.format(data))

            # There are some cases where the data might be NaN or Inf.  In those cases we'll set to 0.
            data[~np.isfinite(data)] = 0
        else:
            log.warning('Could not determine filetype for {}'.format(filename))
            return []

        # Apply the data processing to the loaded dataset
        for dp in self._data_processing:
            log.debug('Doing pre-processing {}, input data shape {}'.format(dp, data.shape))
            data = dp.process(data)
            log.debug('    Now input data shape {}'.format(data.shape))


        # Make RGB (3 channel) if only gray scale (single channel)
        if len(data.shape) == 2:
            data = utils.gray2rgb(data)

        return data

    def calculate(self, cutout_creator, fingerprint_calculator):
        """
        Calculate the fingerprints for each cutout based on the cutout creator and fingerprint calculator.

        :param cutout_creator:
        :param fingerprint_calculator:
        :return:
        """

        log.info("Calculating fingerprints using {} and {}".format(cutout_creator, fingerprint_calculator))

        self._fingerprints = []

        self._cutout_creator = cutout_creator
        self._fingerprint_calculator = fingerprint_calculator

        for row_min, row_max, col_min, col_max, td in self._cutout_creator.create_cutouts(self._processed_data):

            predictions = self._fingerprint_calculator.calculate(td)

            self._fingerprints.append({
                'row_min': row_min,
                'row_max': row_max,
                'col_min': col_min,
                'col_max': col_max,
                'predictions': predictions
            })

    def display(self, row_minmax, col_minmax):
        """
        Send the data back to the calling routine to display the data.

        :param row_minmax:
        :param col_minmax:
        :return:
        """
        return self._processed_data[row_minmax[0]:row_minmax[1], col_minmax[0]:col_minmax[1]]

    def save(self):
        """
        Save is to a dictionary as it is used higher up the food chain.

        :return:
        """
        return {
            'uuid': self._uuid,
            'filename': self._filename,
            'data_processing': [x.save() for x in self._data_processing],
            'cutout_creator': self._cutout_creator.save(),
            'fingerprint_calculator': self._fingerprint_calculator.save(),
            'fingerprints': self._fingerprints
        }

    @staticmethod
    def load(parameters):
        tldp = TransferLearningProcessData(parameters['filename'], parameters['data_processing'])
        tldp._load(parameters)
        return tldp

    def _load(self, parameters):
        """
        Load the parameters back into the instance.  Will need to create the instances as we load them in.

        :param parameters:
        :return:
        """
        self._uuid = parameters['uuid']
        self._filename = parameters['filename']
        self._data_processing = [DataProcessing.load_parameters(x) for x in parameters['data_processing']]
        self._cutout_creator = Cutouts.load(parameters['cutout_creator'])
        self._fingerprint_calculator = Fingerprint.load_parameters(parameters['fingerprint_calculator'])
        self._fingerprints = parameters['fingerprints']

        self._load_image_data(self._filename)