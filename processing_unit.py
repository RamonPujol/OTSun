import io
import json
import os
import logging
import pkgutil
import experiments

logging.getLogger().setLevel(logging.DEBUG)

for importer, modname, ispkg in pkgutil.iter_modules(experiments.__path__):
    logging.info("Found submodule %s (is a package: %s)" % (modname, ispkg))
    string = "from experiments.%s import experiment as %s" % (modname, modname)
    exec string

# from experiments.dummy_experiment import experiment as experiment1
# from experiments.experiment1par import experiment as experiment1par
# from experiments.dummy_experiment import experiment as dummy_experiment


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
        logging.info('experiment is ' + experiment_id)
        logging.info(str(locals()))
        callable_experiment = globals()[experiment_id]
        logging.info("calling:" + experiment_id)
        callable_experiment(data, root_folder)
    else:
        raise ValueError('The experiment is not implemented', experiment_id)
