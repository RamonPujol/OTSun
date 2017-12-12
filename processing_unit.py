import io
import json
import os
import logging

logging.getLogger().setLevel(logging.DEBUG)

def exp1(data,folder):
    lambda1 = float(data['lambda1'])
    lambda2 = float(data['lambda1'])
    lambdad = float(data['lambdadelta'])

    destfile = folder + '.output'
    with io.open(destfile, 'w', encoding='utf8') as fp:
        fp.write("{}{}{}{}".format(lambda1,lambda2,lambdad,lambda2-lambda1))

def process_input(datafile, folder):
    # Take data from datafile and files from folder and write the output to folder+'.output'
    try:
        with open(datafile, 'r') as fp:
            data = json.load(fp)
    except IOError:
        data = {}

    # Do the work!
    experiment_id = data['experiment']
    try:
        logging.info('experiment is '+ experiment_id)
        callable = locals()[experiment_id]
        logging.info("calling:" + experiment_id)
        callable(data, folder)
    except:
        destfile = folder + '.output'
        with io.open(destfile, 'w', encoding='utf8') as fp:
            fp.write(u"Data given:\n----\n")
            for key in data:
                fp.write(u"%s: %s\n" % (key, data[key]))
            fp.write(u"\nUploaded files:\n----\n")
            for uploaded_filename in os.listdir(folder):
                fp.write(u"%s\n" % (uploaded_filename,))
