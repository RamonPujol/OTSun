import io
import json
import os
import logging

logging.getLogger().setLevel(logging.DEBUG)

from experiment1 import experiment as experiment1
from dummy_experiment import experiment as dummy_experiment

def process_input(datafile, folder):
    # Take data from datafile and files from folder
    try:
        with open(datafile, 'r') as fp:
            data = json.load(fp)
    except IOError:
        data = {}

    # Do the work!
    experiment_id = data.get('experiment', None)
    callable = globals().get(experiment_id, None)
    if callable:
        logging.info('experiment is '+ experiment_id)
        logging.info(str(locals()))
        callable = globals()[experiment_id]
        logging.info("calling:" + experiment_id)
        callable(data, folder)
    else:
        raise ValueError('The experiment is not implemented', experiment_id)
