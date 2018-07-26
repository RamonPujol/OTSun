import json
import os
import logging
import zipfile
import importlib

logger = logging.getLogger(__name__)

def make_zipfile(output_filename, source_dir):
    relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as myzip:
        for root, dirs, files in os.walk(source_dir):
            # add directory (needed for empty dirs)
            myzip.write(root, os.path.relpath(root, relroot))
            for thefile in files:
                filename = os.path.join(root, thefile)
                if os.path.isfile(filename): # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot), thefile)
                    myzip.write(filename, arcname)

def process_experiment(datafile, root_folder):
    # Take data from datafile and files from folder
    try:
        with open(datafile, 'r') as fp:
            data = json.load(fp)
    except IOError:
        data = {}

    # Do the work!
    experiment_id = data.get('experiment', None)

    try:
        module = importlib.import_module('experiments.'+experiment_id)
        exp_callable = module.experiment
    except:
        raise ValueError('The experiment is not implemented', experiment_id)

    logger.info("calling %s for %s from process %s",
                experiment_id,
                data['identifier'],
                os.getpid())
    exp_callable(data, root_folder)
    logger.info("computation finished for %s", data['identifier'])
    output_folder = os.path.join(root_folder, 'output')
    output_zip = os.path.join(root_folder, 'output.zip')
    make_zipfile(output_zip, output_folder)

def run_processor(datafile, root_folder):
    # Take data from datafile and files from folder
    try:
        with open(datafile, 'r') as fp:
            data = json.load(fp)
    except IOError:
        data = {}

    # Do the work!
    processor_id = data.get('processor', None)

    try:
        module = importlib.import_module('processors.'+processor_id)
        proc_callable = module.processor
    except:
        raise ValueError('The processor is not implemented', processor_id)

    logger.info('processor is ' + processor_id)
    logger.info(str(locals()))
    logger.info("calling:" + processor_id)
    new_data = proc_callable(data, root_folder)
    return new_data

