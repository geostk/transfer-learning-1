import sys
from collections import OrderedDict
import numpy as np
import threading
import itertools

from tldist.celery import app
from celery import group
import logging
import json
import time

from tldist.similarity.processing import calculate as similarity_calculate
from .processing import tSNE, Jaccard, Distance

FORMAT = '%(levelname)-8s %(asctime)-15s %(name)-10s %(message)s'
logging.basicConfig(format=FORMAT)
log = logging.getLogger('similarity')
log.setLevel(logging.DEBUG)


def similarity_celery(fingerprints, sim):
    """
    Similarity calculator using celery for job queue/running.
    """
    log.info('')

    # Create and run the job queue
    job = group([
        calculate.s(fingerprints, sim)
    ])
    celery_result = job.apply_async(serializer='pickle')

    # Show the progress (not really needed)
    counts = OrderedDict({x.id: 0 for x in celery_result.children})
    while not celery_result.ready():

        # We only need to display every 100ms or so, maybe less really
        time.sleep(0.1)
        for x in celery_result.children:
            if x.state == 'PROGRESS' and hasattr(x, 'info') and 'progress' in x.info:
                counts[x.id] = x.info['progress']

        print('\r{}'.format([v for k, v in counts.items()]), end='')

    # Get the results (will be a list of lists)
    r = celery_result.get()

    # In this case, there is a list returned with one dict element. If this
    # changes in the future then we'll have to modify this to be something different.
    return r[0]


@app.task
def calculate(fingerprints, similarity_calculator):
    """
    Similarity calculator.
    """
    return similarity_calculate(fingerprints, similarity_calculator)
