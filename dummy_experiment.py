"""
This is an example of how to program an experiment to be run by the web app.
Guidelines:
* The name of the file must be the identifier given in the companion template
* It must implement a method experiment(data, rootfolder).
** data is a dictionary with the data given by the user
** rootfolder is the name of the root folder of the experiment
* The files uploaded by the user are in rootfolder/files
* The (zip) file sent back to the user will be rootfolder/output.zip
* In the file rootfolder/status.json you must write a json file with the percentage of computation that is completed
"""
import io, os, shutil
import json
from time import sleep
import logging


def experiment(data, root_folder):
    dest_folder = os.path.join(root_folder, 'output')
    os.makedirs(dest_folder)
    dest_file = os.path.join(dest_folder,'data.log')
    with io.open(dest_file, 'w', encoding='utf8') as fp:
        fp.write(u"Experiment not found\n")
        fp.write(u"Data given:\n----\n")
        for key in data:
            fp.write(u"%s: %s\n" % (key, data[key]))
        fp.write(u"\nUploaded files:\n----\n")
        for uploaded_filename in os.listdir(root_folder):
            fp.write(u"%s\n" % (uploaded_filename,))
    shutil.make_archive(dest_folder, 'zip', dest_folder)

    status_file = os.path.join(root_folder, 'status.json')
    data_status = {'percentage':0}

    for _ in range(100):
        data_status['percentage'] += 1
        with open(status_file, 'w') as fp:
            json.dump(data_status, fp)
        sleep(0.1)


