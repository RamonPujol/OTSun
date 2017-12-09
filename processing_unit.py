import io
import json
import os


def process_input(datafile, folder):
    # Take data from datafile and files from folder and write the output to folder+'.output'
    destfile = folder+'.output'
    try:
        with open(datafile, 'r') as fp:
            data = json.load(fp)
    except IOError:
        data = {}

    with io.open(destfile, 'w', encoding='utf8') as fp:
        fp.write(u"Data given:\n----\n")
        for key in data:
            fp.write(u"%s: %s\n" % (key, data[key]))
        fp.write(u"\nUploaded files:\n----\n")
        for uploaded_filename in os.listdir(folder):
            fp.write(u"%s\n" % (uploaded_filename,))
