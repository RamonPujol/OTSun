import io
import json
import os
import logging
import pkgutil
import experiments
import zipfile

logger = logging.getLogger(__name__)

for importer, modname, ispkg in pkgutil.iter_modules(experiments.__path__):
    logger.info("Found submodule %s (is a package: %s)" % (modname, ispkg))
    string = "from experiments.%s import experiment as %s" % (modname, modname)
    exec string

# from experiments.dummy_experiment import experiment as experiment1
# from experiments.experiment1par import experiment as experiment1par
# from experiments.dummy_experiment import experiment as dummy_experiment

def make_zipfile(output_filename, source_dir):
    relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(source_dir):
            # add directory (needed for empty dirs)
            zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename): # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    zip.write(filename, arcname)

def process_input(datafile, root_folder):
    # Take data from datafile and files from folder
    try:
        with open(datafile, 'r') as fp:
            data = json.load(fp)
    except IOError:
        data = {}

    # Do the work!
    experiment_id = data.get('experiment', None)
    callable_experiment = globals().get(experiment_id, None)
    if callable_experiment:
        logger.info('experiment is ' + experiment_id)
        logger.info(str(locals()))
        callable_experiment = globals()[experiment_id]
        logger.info("calling:" + experiment_id)
        callable_experiment(data, root_folder)
    else:
        raise ValueError('The experiment is not implemented', experiment_id)
    output_folder = os.path.join(root_folder, 'output')
    output_zip = os.path.join(root_folder, 'output.zip')
    make_zipfile(output_zip, output_folder)

