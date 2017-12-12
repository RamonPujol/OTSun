import io, os, shutil
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
