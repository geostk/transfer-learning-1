import glob
import pickle
from configparser import ConfigParser

from transfer_learning.fingerprint.processing import FingerprintCalculatorResnet
from transfer_learning.fingerprint.processing import calculate as fingerprint_calculate
from transfer_learning.similarity.similarity import calculate as similarity_calculate
from transfer_learning.data import Data, DataCollection
from transfer_learning.cutout import CutoutCollection
from transfer_learning.cutout.generators import BasicCutoutGenerator

fc_save = FingerprintCalculatorResnet().save()

config = ConfigParser()
config.read('config.ini')

#
# Load the data
#

print('Going to calculate the sliding window cutouts')
sliding_window_cutouts = BasicCutoutGenerator(output_size=224, step_size=400)

print('Going to load the HST Heritage data')
data = DataCollection()
cutouts = CutoutCollection()
for filename in glob.glob('../../data/heritage/*.???'):

    #
    # Load the data
    #

    print('   processing {}'.format(filename))
    image_data = Data(location=filename, radec=(-32, 12), meta={})
    image_data.get_data()
    data.add(image_data)

    #
    #  Create the cutouts
    #
    cutouts = cutouts + sliding_window_cutouts.create_cutouts(data)
    print('created {} cutouts'.format(len(cutouts)))

#
#  Compute the fingerprints for each cutout
#
print('Calculate the fingerprint for each cutout')
fingerprints = fingerprint_calculate(cutouts, fc_save)

#
#  Compute the similarity metrics
#
print('Calculating the tSNE similarity')
similarity_tsne = similarity_calculate(fingerprints, 'tsne')
with open('similarity_tsne.pck', 'wb') as fp:
    pickle.dump(similarity_tsne.save(), fp)

print('Calculating the Jaccard similarity')
similarity_jaccard = similarity_calculate(fingerprints, 'jaccard')
with open('similarity_jaccard.pck', 'wb') as fp:
    pickle.dump(similarity_jaccard.save(), fp)
