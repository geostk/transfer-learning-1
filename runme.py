import uuid
import glob
import time
import os
import numpy as np

from data import Data
from data_processing import MedianFilterData, ZoomData
from fingerprint import FingerprintResnet
from similarity import tSNE

import logging
logging.basicConfig(format='%(levelname)-6s: %(name)-10s %(asctime)-15s  %(message)s')
log = logging.getLogger("Runme")
log.setLevel(logging.INFO)

def rgb2plot(data):
    """
    Convert the input data to RGB. This is basically clipping and cropping the intensity range for display

    :param data:
    :return:
    """

    mindata, maxdata = np.percentile(data[np.isfinite(data)], (0.01, 99.0))
    return np.clip((data - mindata) / (maxdata-mindata) * 255, 0, 255).astype(np.uint8)

import matplotlib.pyplot as plt

# input_file_pattern = '/Users/crjones/christmas/hubble/Carina/data/carina.tiff'
# output_directory = '/tmp/resnet_acs/'

input_file_pattern = '/Users/crjones/christmas/hubble/ACS_Halpha/data/*/*fits.gz'
output_directory = '/tmp/acs_halpha'

input_files = glob.glob(input_file_pattern)

stepsize = 112

if len(glob.glob(os.path.join(output_directory, '*pck'))) == 0:
    tl = TransferLearning()

    fingerprints = []

    fingerprint_resnet = FingerprintResnet()

    # # calculate fingerpirnts for median filtered
    log.info('Setting up median filter data')
    data_processing = [MedianFilterData((5,5,1))]
    data = Data(fingerprint_resnet, data_processing)
    data.set_files(input_files)
    fingerprints = data.calculate(stepsize=stepsize)
    data.save(output_directory)

    # calculate fingerprints for median filtered and sub-sampled
    log.info('Setting up median filter, zoom 2 data')
    data_processing = [MedianFilterData((5,5,1)), ZoomData(2)]
    data_median_supersample = Data(fingerprint_resnet, data_processing)
    data_median_supersample.set_files(input_files)
    fingerprints_median_supersample = data_median_supersample.calculate(stepsize=stepsize)
    data_median_supersample.save(output_directory)

    # calcualte finterprints for median fitlered and super-sampled
    log.info('Setting up median filter, zoom 0.5 data')
    data_processing = [MedianFilterData((5,5,1)), ZoomData(0.5)]
    data_median_subsample = Data(fingerprint_resnet, data_processing)
    data_median_subsample.set_files(input_files)
    fingerprints_median_subsample = data_median_subsample.calculate(stepsize=stepsize)
    data_median_subsample.save(output_directory)

    data = [data, data_median_supersample, data_median_subsample]
    fingerprints = [fingerprints, fingerprints_median_supersample, fingerprints_median_subsample]

    tl.save(output_directory)

else:
    files = glob.glob(os.path.join(output_directory, 'data_*pck'))

    fingerprints = []
    for file in files:

        data = Data.load(file)
        log.info('Loaded data {}'.format(data))

        fingerprints.extend(data.fingerprints)

    tsne_similarity = tSNE(fingerprints)
    tsne_similarity.calculate(fingerprints)

    plt.figure(1)
    plt.clf()
    axis = plt.axes([0.05, 0.05, 0.45, 0.45])

    sub_windows = []
    for row in range(3):
        for col in range(3):
            # rect = [left, bottom, width, height]
            tt = plt.axes([0.5 + 0.17 * col, 0.75 - 0.25 * row, 0.15, 0.15])
            tt.set_xticks([])
            tt.set_yticks([])
            sub_windows.append(tt)

    while True:

        axis.cla()
        tsne_similarity.displayY(axis)

        point = plt.ginput(1)

        if point:
            close_fingerprints = tsne_similarity.find_similar(point)
            for ii, (distance, fingerprint) in enumerate(close_fingerprints):
                print(fingerprint)
                sub_windows[ii].imshow( rgb2plot(
                    fingerprint['data'].display(fingerprint['filename'],
                                                fingerprint['row_center'],
                                                fingerprint['column_center'])
                ))
                sub_windows[ii].set_title('{} ({}, {})'.format(
                    os.path.basename(fingerprint['filename']),
                    fingerprint['row_center'],
                    fingerprint['column_center']), fontsize=8)
        else:
            break


#tl.display(fingerprints)