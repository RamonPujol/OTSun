# Will be deleted in next commit
import json
import os
import logging
import zipfile
import importlib
import otsun
from autologging import TRACE

logger = logging.getLogger(__name__)


def make_zipfile(output_filename, source_dir):
    """
    Creates a zipfile from the contents of a folder

    Args:
        output_filename: str with full path where the zip file has to be written
        source_dir: str with full path of folder to be compressed
    """
    relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as myzip:
        for root, dirs, files in os.walk(source_dir):
            # add directory (needed for empty dirs)
            myzip.write(root, os.path.relpath(root, relroot))
            for thefile in files:
                filename = os.path.join(root, thefile)
                if os.path.isfile(filename):  # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot), thefile)
                    myzip.write(filename, arcname)


def run_experiment(datafile, root_folder):
    # Take data from datafile and load the experiment
    try:
        with open(datafile, 'r') as fp:
            data = json.load(fp)
    except IOError:
        data = {}

    experiment_id = data.get('experiment', None)
    if not experiment_id:
        raise ValueError('No experiment requested')

    try:
        module = importlib.import_module('.experiments.'+experiment_id, 'webappsunscene')
        exp_callable = module.experiment
    except (ImportError, AttributeError):
        raise ValueError('The experiment is not implemented', experiment_id)

    # Make log file and write logs from this module, the experiment and otsun
    fh = logging.FileHandler(os.path.join(root_folder, "computations.log"))
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s:%(name)s:%(funcName)s:%(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    try:
        module_logger = module.logger
        module_logger.addHandler(fh)
    except AttributeError:
        pass

    otsun_logger = otsun.logger
    otsun_logger.setLevel(TRACE)
    fh.setLevel(TRACE)
    otsun_logger.addHandler(fh)

    # Run the experiment
    logger.info("calling %s for %s from process %s",
                experiment_id,
                data['identifier'],
                os.getpid())
    exp_callable(data, root_folder)
    logger.info("computation finished for %s", data['identifier'])

    # Create zipfile with results
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
    except (ImportError, AttributeError):
        raise ValueError('The processor is not implemented', processor_id)

    logger.info('processor is ' + processor_id)
    logger.info(str(locals()))
    logger.info("calling:" + processor_id)
    new_data = proc_callable(data, root_folder)
    return new_data
