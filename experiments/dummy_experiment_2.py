"""
This is an example of how to program an experiment to be run by the web app.
Guidelines:
* The name of the file must be the identifier given in the companion template
* It must implement a method experiment(data, rootfolder).
** data is a dictionary with the data given by the user
** rootfolder is the name of the root folder of the experiment
* The files uploaded by the user are in rootfolder/files
* The output files must be put in rootfolder/output
* In the file rootfolder/status.json you must write a json file with the percentage of computation that is completed
"""
import io, os, shutil
import json
from time import sleep
import logging

logger = logging.getLogger(__name__)

def experiment(data, root_folder):
    dest_folder = os.path.join(root_folder, 'output')
    os.makedirs(dest_folder)
    dest_file = os.path.join(dest_folder,'data.log')
    with io.open(dest_file, 'w', encoding='utf8') as fp:
        fp.write(u"This is the Dummy experiment\n")
        fp.write(u"Data given:\n----\n")
        for key in data:
            fp.write(u"%s: %s\n" % (key, data[key]))
        fp.write(u"\nUploaded files:\n----\n")
        for uploaded_filename in os.listdir(root_folder):
            fp.write(u"%s\n" % (uploaded_filename,))

    other_file = os.path.join(dest_folder, 'otherfile')
    with io.open(other_file, 'w', encoding='utf8') as fp:
        fp.write(u"Hola!")

#    shutil.make_archive(dest_folder, 'zip', dest_folder)

    status_file = os.path.join(root_folder, 'status.json')
    data_status = {'percentage':0, 'status':'started'}

    for _ in range(100):
        data_status['status'] = 'running'
        data_status['percentage'] += 1
        with open(status_file, 'w') as fp:
            json.dump(data_status, fp)
        logger.debug("completed: %s", data_status['percentage'])
        sleep(0.1)
    data_status['status'] = 'finished'
    data_status['percentage'] = 100
    with open(status_file, 'w') as fp:
        json.dump(data_status, fp)


