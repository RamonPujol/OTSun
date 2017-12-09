from __future__ import print_function
from flask import Flask, request, redirect, render_template, send_from_directory
from uuid import uuid4
import os
import json
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import threading
from time import sleep
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp'
URL_ROOT = None


def save_data(data, identifier):
    dirname = os.path.join(UPLOAD_FOLDER, identifier)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    filename = os.path.join(dirname, 'data.txt')
    try:
        with open(filename, 'r') as fp:
            saved_data = json.load(fp)
    except IOError:
        saved_data = {}
    saved_data.update(data)
    with open(filename, 'w') as fp:
        json.dump(saved_data, fp)


def save_file(the_file, identifier, filename):
    dirname = os.path.join(UPLOAD_FOLDER, identifier)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    the_file.save(os.path.join(dirname, filename))


def load_data(identifier):
    dirname = os.path.join(UPLOAD_FOLDER, identifier)
    filename = os.path.join(dirname, 'data.txt')
    try:
        with open(filename, 'r') as fp:
            saved_data = json.load(fp)
    except IOError:
        saved_data = {}
    return saved_data


def send_mail(toaddr, identifier):
    fromaddr = "pysunscene@gmail.com"
    frompasswd = "uibdmidfis"

    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Results of computation of PySunScene"

    body = """\
    <html>
    Get your results at:
    <a href="%s">link</a>
    </html>
    """ % (URL_ROOT + 'results/' + identifier)

    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, frompasswd)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


def process_request(identifier):
    # Get data
    data = load_data(identifier)
    # Do the work
    sleep(1)
    dirname = os.path.join(UPLOAD_FOLDER, identifier)
    destfile = os.path.join(UPLOAD_FOLDER, identifier+'.output')
    with open(destfile, 'w') as fp:
        for key in data:
            fp.write("%s: %s\n" % (key, data[key]))
        for uploaded_filename in os.listdir(dirname):
            fp.write("File %s\n" % (uploaded_filename,))
    # Send mail with link
    send_mail(toaddr=data['email'], identifier=identifier)


@app.route('/')
def hello():
    global URL_ROOT
    if URL_ROOT is None:
        URL_ROOT = request.url_root
    return redirect('/node/start')


@app.route('/node/<name>/<identifier>', methods=['GET', 'POST'])
@app.route('/node/<name>', methods=['GET', 'POST'])
def node(name, identifier=None):
    if request.method == 'GET':
        return render_template(name + ".html", identifier=identifier)
    if request.method == 'POST':
        data = request.form.to_dict()
        if identifier is None:
            identifier = str(uuid4())
        fileids = request.files
        for fileid in fileids:
            the_file = request.files[fileid]
            filename = the_file.filename
            filename = secure_filename(filename)
            save_file(the_file, identifier, filename)
            data[fileid] = filename
        save_data(data, identifier)
        if 'next_step' in data:
            return redirect('node/' + data['next_step'] + '/' + identifier)
        else:
            return redirect('end/' + identifier)


@app.route('/end/<identifier>')
def end_process(identifier):
    compute_thread = threading.Thread(target=process_request, args=(identifier,))
    compute_thread.start()
    return render_template("end.html")


@app.route('/results/<identifier>', methods=['GET'])
@app.route('/results/')
def send_file(identifier=None):
    if identifier is None:
        return "No process job specified"
    return send_from_directory(UPLOAD_FOLDER, identifier + '.output')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, threaded=True)
