import os
import glob
import shutil
from configparser import ConfigParser

from transfer_learning.fingerprint.processing import FingerprintCalculatorResnet
from transfer_learning.fingerprint.processing import calculate as fingerprint_calculate
from transfer_learning.similarity.similarity import calculate as similarity_calculate
from transfer_learning.data import Data
from transfer_learning.cutout.generators import BasicCutoutGenerator
from transfer_learning.database import get_database

fc_save = FingerprintCalculatorResnet().save()

config = ConfigParser()
config.read('config.ini')

# Create the database
print('Going to setup the database in {}'.format(config['database']['filename']))

if os.path.isdir(config['database']['filename']):
    shutil.rmtree(config['database']['filename'])
db = get_database(config['database']['type'], config['database']['filename'])

#
# Load the data
#

print('Going to calculate the sliding window cutouts')
sliding_window_cutouts = BasicCutoutGenerator(output_size=224, step_size=400)

print('Going to load the HST Heritage data')
all_cutouts = []
for filename in glob.glob('../../data/heritage/*.???'):
    print('   processing {}'.format(filename))
    image_data = Data(location=filename, radec=(-32, 12), meta={})
    image_data.get_data()
    db.save('data', image_data)

    #
    #  Create the cutouts
    #
    cutouts = sliding_window_cutouts.create_cutouts(image_data)
    print('created {} cutouts'.format(len(cutouts)))
    [db.save('cutout', cutout) for cutout in cutouts]

    all_cutouts.extend(cutouts)

#
#  Compute the fingerprints for each cutout
#
print('Calculate the fingerprint for each cutout')
fingerprints = fingerprint_calculate(all_cutouts, fc_save)
print([str(x) for x in fingerprints])
[db.save('fingerprint', fingerprint) for fingerprint in fingerprints]

#
#  Compute the similarity metrics
#
print('Calculating the tSNE similarity')
similarity_tsne = similarity_calculate(fingerprints, 'tsne')
db.save('similarity', similarity_tsne)

# print('Calculating the jaccard similarity')
# similarity_jaccard = similarity_calculate(fingerprints, 'jaccard')
