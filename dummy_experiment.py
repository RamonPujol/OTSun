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


