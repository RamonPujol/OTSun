"""
This is an example of how to program an experiment to be run by the web app.
Guidelines:
* The name of the file must be the identifier given in the companion template
* It must implement a method experiment(data, folder).
** data is a dictionary with the data given by the user
** folder is the name of the folder where to find the files uploaded files by the user
* The files sent back to the user (in a zip file) will be those found in the folder folder+'.output'
* In the file folder+'status' you must write a json file with the percentage of computation that is completed
"""
import io, os, shutil
import json
from time import sleep
import logging


def experiment(data, folder):
    destfolder = folder + '.output'
    os.makedirs(destfolder)
    destfile = os.path.join(destfolder,'data.log')
    with io.open(destfile, 'w', encoding='utf8') as fp:
        fp.write(u"Experiment not found\n")
        fp.write(u"Data given:\n----\n")
        for key in data:
            fp.write(u"%s: %s\n" % (key, data[key]))
        fp.write(u"\nUploaded files:\n----\n")
        for uploaded_filename in os.listdir(folder):
            fp.write(u"%s\n" % (uploaded_filename,))
    shutil.make_archive(folder, 'zip', destfolder)
    statusfile = folder + '.status'
    data_status = {'percentage':0}

    for _ in range(100):
        data_status['percentage'] += 1
        with open(statusfile, 'w') as fp:
            json.dump(data_status, fp)
        sleep(1)


