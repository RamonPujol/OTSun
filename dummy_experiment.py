import io, os
import logging


def experiment(data, folder):
    destfile = folder + '.output'
    with io.open(destfile, 'w', encoding='utf8') as fp:
        fp.write(u"Experiment not found\n")
        fp.write(u"Data given:\n----\n")
        for key in data:
            fp.write(u"%s: %s\n" % (key, data[key]))
        fp.write(u"\nUploaded files:\n----\n")
        for uploaded_filename in os.listdir(folder):
            fp.write(u"%s\n" % (uploaded_filename,))
    return destfile
